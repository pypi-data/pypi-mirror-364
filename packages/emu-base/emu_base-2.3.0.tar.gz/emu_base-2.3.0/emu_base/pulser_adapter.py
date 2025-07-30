from typing import Tuple, Sequence, Any
from enum import Enum
import torch
import math
import pulser
from pulser.noise_model import NoiseModel
from pulser.register.base_register import BaseRegister, QubitId
from pulser.backend.config import EmulationConfig
from emu_base.jump_lindblad_operators import get_lindblad_operators

KB_PER_RUBIDIUM_MASS = 95.17241379310344  # J/K/kg
KEFF = 8.7  # µm^-1, conversion from atom velocity to detuning


class HamiltonianType(Enum):
    Rydberg = 1
    XY = 2


SUPPORTED_NOISES: dict = {
    HamiltonianType.Rydberg: {
        "amplitude",
        "dephasing",
        "relaxation",
        "depolarizing",
        "doppler",
        "eff_noise",
        "SPAM",
        # "leakage",
    },
    HamiltonianType.XY: {
        "dephasing",
        "depolarizing",
        "eff_noise",
        "SPAM",
    },  # , "leakage"},
}


def _get_qubit_positions(
    register: BaseRegister,
) -> list[torch.Tensor]:
    """Conversion from pulser Register to emu-mps register (torch type).
    Each element will be given as [Rx,Ry,Rz]"""

    positions = [
        position.as_tensor().to(dtype=torch.float64)
        for position in register.qubits.values()
    ]
    if len(positions[0]) == 2:
        return [torch.cat((position, torch.zeros(1))) for position in positions]
    return positions


def _rydberg_interaction(sequence: pulser.Sequence) -> torch.Tensor:
    """
    Returns the Rydberg interaction matrix from the qubit positions.
        Uᵢⱼ=C₆/|rᵢ-rⱼ|⁶

    see Pulser
    [documentation](https://pulser.readthedocs.io/en/stable/conventions.html#interaction-hamiltonian).
    """

    nqubits = len(sequence.register.qubit_ids)
    c6 = sequence.device.interaction_coeff
    positions = _get_qubit_positions(sequence.register)

    interaction_matrix = torch.zeros(nqubits, nqubits, dtype=torch.float64)
    for i in range(nqubits):
        for j in range(i + 1, nqubits):
            rij = torch.dist(positions[i], positions[j])
            interaction_matrix[[i, j], [j, i]] = c6 / rij**6
    return interaction_matrix


def _xy_interaction(sequence: pulser.Sequence) -> torch.Tensor:
    """
    Returns the XY interaction matrix from the qubit positions.
        Uᵢⱼ=C₃(1−3cos(𝜃ᵢⱼ)²)/|rᵢ-rⱼ|³
    with
        cos(𝜃ᵢⱼ) = (rᵢ-rⱼ)·m/|m||rᵢ-rⱼ|

    see Pulser
    [documentation](https://pulser.readthedocs.io/en/stable/conventions.html#interaction-hamiltonian).
    """

    nqubits = len(sequence.register.qubit_ids)
    c3 = sequence.device.interaction_coeff_xy
    mag_field = torch.tensor(sequence.magnetic_field, dtype=torch.float64)
    mag_field /= mag_field.norm()
    positions = _get_qubit_positions(sequence.register)

    interaction_matrix = torch.zeros(nqubits, nqubits, dtype=torch.float64)
    for i in range(nqubits):
        for j in range(i + 1, nqubits):
            rij = torch.dist(positions[i], positions[j])
            cos_ij = torch.dot(positions[i] - positions[j], mag_field) / rij
            interaction_matrix[[i, j], [j, i]] = c3 * (1 - 3 * cos_ij**2) / rij**3
    return interaction_matrix


def _get_amp_factors(
    samples: pulser.sampler.SequenceSamples,
    amp_sigma: float,
    laser_waist: float | None,
    qubit_positions: list[torch.Tensor],
    q_ids: tuple[str, ...],
) -> dict[int, torch.Tensor]:
    def perp_dist(pos: torch.Tensor, axis: torch.Tensor) -> Any:
        return torch.linalg.vector_norm(pos - torch.vdot(pos, axis) * axis)

    times_to_amp_factors: dict[int, torch.Tensor] = {}
    for ch, ch_samples in samples.channel_samples.items():
        ch_obj = samples._ch_objs[ch]
        prop_dir = torch.tensor(
            ch_obj.propagation_dir or [0.0, 1.0, 0.0], dtype=torch.float64
        )
        prop_dir /= prop_dir.norm()

        # each channel has a noise on its laser amplitude
        # we assume each channel has the same noise amplitude currently
        # the hardware currently has only a global channel anyway
        sigma_factor = (
            1.0
            if amp_sigma == 0.0
            else torch.max(torch.tensor(0), torch.normal(1.0, amp_sigma, (1,))).item()
        )
        for slot in ch_samples.slots:
            factors = (
                torch.tensor(
                    [
                        math.exp(-((perp_dist(x, prop_dir) / laser_waist) ** 2))
                        for x in qubit_positions
                    ],
                    dtype=torch.float64,
                )  # the lasers have a gaussian profile perpendicular to the propagation direction
                if laser_waist and ch_obj.addressing == "Global"
                else torch.ones(
                    len(q_ids), dtype=torch.float64
                )  # but for a local channel, this does not matter
            )

            # add the amplitude noise for the targeted qubits
            factors[[x in slot.targets for x in q_ids]] *= sigma_factor

            for i in range(slot.ti, slot.tf):
                if i in times_to_amp_factors:  # multiple local channels at the same time
                    # pulser enforces that no two lasers target the same qubit simultaneously
                    # so only a single factor will be != 1.0 for each qubit
                    times_to_amp_factors[i] = factors * times_to_amp_factors[i]
                else:
                    times_to_amp_factors[i] = factors
    return times_to_amp_factors


def _get_delta_offset(nqubits: int, temperature: float) -> torch.Tensor:
    """
    The delta values are shifted due to atomic velocities.
    The atomic velocities follow the Maxwell distribution
    https://en.wikipedia.org/wiki/Maxwell%E2%80%93Boltzmann_distribution
    and then a given residual velocity is converted to a delta offset per
    https://en.wikipedia.org/wiki/Doppler_broadening
    """
    if temperature == 0.0:
        return torch.zeros(nqubits, dtype=torch.float64)
    t = temperature * 1e-6  # microKelvin -> Kelvin
    sigma = KEFF * math.sqrt(KB_PER_RUBIDIUM_MASS * t)
    return torch.normal(0.0, sigma, (nqubits,))


def _extract_omega_delta_phi(
    *,
    sequence: pulser.Sequence,
    target_times: list[int],
    with_modulation: bool,
    laser_waist: float | None,
    amp_sigma: float,
    temperature: float,
) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """
    Samples the Pulser sequence and returns a tuple of tensors (omega, delta, phi)
    containing:
    - omega[i, q] = amplitude at time i * dt for qubit q
    - delta[i, q] = detuning at time i * dt for qubit q
    - phi[i, q] = phase at time i * dt for qubit q

    if laser_waist is w_0 != None, the omega values coming from the global pulse channel
    will me modulated as $\\Omega_i=\\Omega_i e^{-r_i^2/w_0^2}$
    """

    if with_modulation and sequence._slm_mask_targets:
        raise NotImplementedError(
            "Simulation of sequences combining an SLM mask and output "
            "modulation is not supported."
        )

    q_ids = sequence.register.qubit_ids

    samples = pulser.sampler.sample(
        sequence,
        modulation=with_modulation,
        extended_duration=sequence.get_duration(include_fall_time=with_modulation),
    )
    sequence_dict = samples.to_nested_dict(all_local=True, samples_type="tensor")["Local"]

    if "ground-rydberg" in sequence_dict and len(sequence_dict) == 1:
        locals_a_d_p = sequence_dict["ground-rydberg"]
    elif "XY" in sequence_dict and len(sequence_dict) == 1:
        locals_a_d_p = sequence_dict["XY"]
    else:
        raise ValueError("Only `ground-rydberg` and `mw_global` channels are supported.")

    nsamples = len(target_times) - 1
    omega = torch.zeros(
        nsamples,
        len(q_ids),
        dtype=torch.complex128,
    )

    delta = torch.zeros(
        nsamples,
        len(q_ids),
        dtype=torch.complex128,
    )
    phi = torch.zeros(
        nsamples,
        len(q_ids),
        dtype=torch.complex128,
    )
    qubit_positions = _get_qubit_positions(sequence.register)

    times_to_amp_factors = _get_amp_factors(
        samples, amp_sigma, laser_waist, qubit_positions, q_ids
    )

    omega_1 = torch.zeros_like(omega[0])
    omega_2 = torch.zeros_like(omega[0])
    max_duration = sequence.get_duration(include_fall_time=with_modulation)

    for i in range(nsamples):
        t = (target_times[i] + target_times[i + 1]) / 2
        # The sampled values correspond to the start of each interval
        # To maximize the order of the solver, we need the values in the middle
        if math.ceil(t) < max_duration:
            # If we're not the final step, approximate this using linear interpolation
            # Note that for dt even, t1=t2
            t1 = math.floor(t)
            t2 = math.ceil(t)
            for q_pos, q_id in enumerate(q_ids):
                omega_1[q_pos] = locals_a_d_p[q_id]["amp"][t1]
                omega_2[q_pos] = locals_a_d_p[q_id]["amp"][t2]
                delta[i, q_pos] = (
                    locals_a_d_p[q_id]["det"][t1] + locals_a_d_p[q_id]["det"][t2]
                ) / 2.0
                phi[i, q_pos] = (
                    locals_a_d_p[q_id]["phase"][t1] + locals_a_d_p[q_id]["phase"][t2]
                ) / 2.0
            # omegas at different times need to have the laser waist applied independently
            omega_1 *= times_to_amp_factors.get(t1, 1.0)
            omega_2 *= times_to_amp_factors.get(t2, 1.0)
            omega[i] = 0.5 * (omega_1 + omega_2)
        else:
            # We're in the final step and dt=1, approximate this using linear extrapolation
            # we can reuse omega_1 and omega_2 from before
            for q_pos, q_id in enumerate(q_ids):
                delta[i, q_pos] = (
                    3.0 * locals_a_d_p[q_id]["det"][t2] - locals_a_d_p[q_id]["det"][t1]
                ) / 2.0
                phi[i, q_pos] = (
                    3.0 * locals_a_d_p[q_id]["phase"][t2]
                    - locals_a_d_p[q_id]["phase"][t1]
                ) / 2.0
            omega[i] = torch.clamp(0.5 * (3 * omega_2 - omega_1).real, min=0.0)

    doppler_offset = _get_delta_offset(len(q_ids), temperature)
    delta += doppler_offset
    return omega, delta, phi


_NON_LINDBLADIAN_NOISE = {"SPAM", "doppler", "amplitude"}


def _get_all_lindblad_noise_operators(
    noise_model: NoiseModel | None,
) -> list[torch.Tensor]:
    if noise_model is None:
        return []

    return [
        op
        for noise_type in noise_model.noise_types
        if noise_type not in _NON_LINDBLADIAN_NOISE
        for op in get_lindblad_operators(noise_type=noise_type, noise_model=noise_model)
    ]


def _get_target_times(
    sequence: pulser.Sequence, config: EmulationConfig, dt: int
) -> list[int]:
    sequence_duration = sequence.get_duration(include_fall_time=config.with_modulation)
    # the end value is exclusive, so add +1
    observable_times = set(range(0, sequence_duration + 1, dt))
    observable_times.add(sequence_duration)
    for obs in config.observables:
        times: Sequence[float]
        if obs.evaluation_times is not None:
            times = obs.evaluation_times
        elif config.default_evaluation_times != "Full":
            times = config.default_evaluation_times.tolist()  # type: ignore[union-attr,assignment]
        observable_times |= set([round(time * sequence_duration) for time in times])

    target_times: list[int] = list(observable_times)
    target_times.sort()
    return target_times


class PulserData:
    slm_end_time: float
    full_interaction_matrix: torch.Tensor
    masked_interaction_matrix: torch.Tensor
    omega: torch.Tensor
    delta: torch.Tensor
    phi: torch.Tensor
    hamiltonian_type: HamiltonianType
    lindblad_ops: list[torch.Tensor]
    qubit_ids: tuple[QubitId, ...]

    def __init__(self, *, sequence: pulser.Sequence, config: EmulationConfig, dt: int):
        self.qubit_ids = sequence.register.qubit_ids
        self.qubit_count = len(self.qubit_ids)
        self.target_times = _get_target_times(sequence=sequence, config=config, dt=dt)

        laser_waist = config.noise_model.laser_waist
        amp_sigma = config.noise_model.amp_sigma
        temperature = config.noise_model.temperature
        self.omega, self.delta, self.phi = _extract_omega_delta_phi(
            sequence=sequence,
            target_times=self.target_times,
            with_modulation=config.with_modulation,
            laser_waist=laser_waist,
            amp_sigma=amp_sigma,
            temperature=temperature,
        )

        addressed_basis = sequence.get_addressed_bases()[0]
        if addressed_basis == "ground-rydberg":  # for local and global
            self.hamiltonian_type = HamiltonianType.Rydberg
        elif addressed_basis == "XY":
            self.hamiltonian_type = HamiltonianType.XY
        else:
            raise ValueError(f"Unsupported basis: {addressed_basis}")

        not_supported = (
            set(config.noise_model.noise_types) - SUPPORTED_NOISES[self.hamiltonian_type]
        )
        if not_supported:
            raise NotImplementedError(
                f"Interaction mode '{self.hamiltonian_type}' does not support "
                f"simulation of noise types: {', '.join(not_supported)}."
            )

        self.lindblad_ops = _get_all_lindblad_noise_operators(config.noise_model)
        self.has_lindblad_noise: bool = self.lindblad_ops != []

        if config.interaction_matrix is not None:
            assert len(config.interaction_matrix) == self.qubit_count, (
                "The number of qubits in the register should be the same as the size of "
                "the interaction matrix"
            )

            self.full_interaction_matrix = config.interaction_matrix.as_tensor()
        elif self.hamiltonian_type == HamiltonianType.Rydberg:
            self.full_interaction_matrix = _rydberg_interaction(sequence)
        elif self.hamiltonian_type == HamiltonianType.XY:
            self.full_interaction_matrix = _xy_interaction(sequence)
        self.full_interaction_matrix[
            torch.abs(self.full_interaction_matrix) < config.interaction_cutoff
        ] = 0.0
        self.masked_interaction_matrix = self.full_interaction_matrix.clone()

        self.slm_end_time = (
            sequence._slm_mask_time[1] if len(sequence._slm_mask_time) > 1 else 0.0
        )

        # disable interaction for SLM masked qubits
        slm_targets = list(sequence._slm_mask_targets)
        for target in sequence.register.find_indices(slm_targets):
            self.masked_interaction_matrix[target] = 0.0
            self.masked_interaction_matrix[:, target] = 0.0
