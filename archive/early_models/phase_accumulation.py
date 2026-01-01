"""
Phase Coherence Accumulation Model
Models gravitational decoupling as phase/information pattern, not energy transfer

Key concept: Each acoustic cycle deposits a "phase increment" that accumulates
until threshold is reached → state transition → decoupling triggers
"""

import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import Dict, Tuple, Optional
from .acoustic_physics import AcousticProperties, MaterialVibration, MATERIAL_PRESETS

# Constants
PHI = (1 + np.sqrt(5)) / 2  # Golden ratio
HBAR = 1.054571817e-34  # J·s
EARTH_G = 9.81  # m/s²


@dataclass
class PhaseAccumulationParams:
    """Parameters for phase accumulation model"""
    material_name: str
    mass: float  # kg
    frequency: float  # Hz
    sound_pressure_level: float  # dB
    coherence_time: float  # seconds - how long phase persists
    phase_threshold: float = 1000.0  # Accumulated phase units needed for decoupling
    duration: float = 3600.0  # seconds
    timesteps: int = 10000


def phase_increment_per_cycle(
    acoustic: AcousticProperties,
    material: MaterialVibration,
    frequency: float
) -> float:
    """
    Calculate phase increment deposited per acoustic cycle
    
    Not energy - pure phase/information contribution
    Depends on:
    - Frequency match to resonances (Schumann, alpha, material natural freq)
    - Sound pressure (louder = stronger phase imprint)
    - Material properties (some materials hold phase better)
    """
    # Frequency resonance factors
    # Schumann resonance (7.83 Hz)
    schumann_match = np.exp(-((frequency - 7.83)**2) / (2 * 1.5**2))
    
    # Alpha band (10 Hz)
    alpha_match = np.exp(-((frequency - 10)**2) / (2 * 2**2))
    
    # Material natural frequency (way higher, but still some coupling)
    nat_freq = material.natural_frequency()
    # Use harmonic relationship - does infrasound match harmonic?
    harmonic_number = nat_freq / frequency
    harmonic_closeness = np.abs(harmonic_number - np.round(harmonic_number))
    harmonic_match = 0.1 * np.exp(-harmonic_closeness * 10)
    
    # Best match wins
    freq_match = max(schumann_match, alpha_match, harmonic_match)
    
    # Pressure influence (normalized, 120 dB = 1.0)
    pressure_factor = acoustic.pressure_pascals() / 2.0  # 2 Pa = 120 dB reference
    pressure_factor = np.clip(pressure_factor, 0.01, 10.0)
    
    # Material phase receptivity
    # Lower damping = better phase retention
    material_factor = 1.0 / (1.0 + material.damping_coefficient)
    
    # Base phase increment (arbitrary units)
    base_increment = 0.1
    
    # Total phase per cycle
    phase_per_cycle = base_increment * freq_match * pressure_factor * material_factor
    
    return phase_per_cycle


def geometric_evolution_factor(t: float) -> float:
    """Golden ratio geometric evolution from your equations"""
    return 1.0 + 0.15 * np.sin(2 * np.pi * PHI * t / 60)


def simulate_phase_accumulation(params: PhaseAccumulationParams) -> Dict:
    """
    Simulate pure phase accumulation over time
    
    Phase builds up cycle-by-cycle, decays based on coherence time
    When threshold reached → decoupling state triggers
    """
    material = MATERIAL_PRESETS[params.material_name]
    material.mass = params.mass
    
    acoustic = AcousticProperties(
        frequency=params.frequency,
        sound_pressure_level=params.sound_pressure_level
    )
    
    # Time array
    t = np.linspace(0, params.duration, params.timesteps)
    dt = params.duration / params.timesteps
    
    # Phase accumulation array
    accumulated_phase = np.zeros(params.timesteps)
    accumulated_phase[0] = 0
    
    # Decoupling state (0 = normal gravity, 1 = fully decoupled)
    decoupling_state = np.zeros(params.timesteps)
    
    # Gravitational coupling (1 = full gravity, 0 = weightless)
    coupling = np.ones(params.timesteps)
    
    # Phase per cycle
    phase_per_cycle = phase_increment_per_cycle(acoustic, material, params.frequency)
    cycles_per_second = params.frequency
    
    # Track when threshold is reached
    threshold_reached = False
    threshold_time = None
    
    # Simulate accumulation
    for i in range(1, params.timesteps):
        # Geometric amplification
        G_t = geometric_evolution_factor(t[i])
        
        # Phase decay (exponential)
        decay_factor = np.exp(-dt / params.coherence_time)
        
        # New phase added this timestep
        phase_added = phase_per_cycle * cycles_per_second * dt * G_t
        
        # Update accumulated phase
        accumulated_phase[i] = accumulated_phase[i-1] * decay_factor + phase_added
        
        # Check if threshold reached
        if accumulated_phase[i] >= params.phase_threshold and not threshold_reached:
            threshold_reached = True
            threshold_time = t[i]
            print(f"Phase threshold reached at t = {threshold_time:.2f} seconds!")
        
        # Decoupling state based on accumulated phase
        # Smooth transition as threshold is approached
        decoupling_state[i] = accumulated_phase[i] / params.phase_threshold
        decoupling_state[i] = np.clip(decoupling_state[i], 0, 1)
        
        # Coupling decreases as decoupling state increases
        # Once fully decoupled (state = 1), coupling → 0
        coupling[i] = 1.0 - decoupling_state[i]
    
    # Calculate weight
    weight_kg = params.mass * EARTH_G * coupling
    weight_grams = weight_kg * 1000
    
    return {
        'time': t,
        'accumulated_phase': accumulated_phase,
        'decoupling_state': decoupling_state,
        'coupling': coupling,
        'weight_grams': weight_grams,
        'phase_per_cycle': phase_per_cycle,
        'cycles_per_second': cycles_per_second,
        'threshold_reached': threshold_reached,
        'threshold_time': threshold_time,
        'params': params,
        'acoustic': acoustic,
        'material': material
    }


def visualize_phase_accumulation(results: Dict, save_path: Optional[str] = None):
    """Create visualization of phase accumulation dynamics"""
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    fig.suptitle('Phase Coherence Accumulation Model - Pattern Matching Mechanism', 
                 fontsize=16, fontweight='bold')
    
    t = results['time']
    params = results['params']
    
    # 1. Phase accumulation
    ax1 = axes[0, 0]
    ax1.plot(t, results['accumulated_phase'], 'blue', linewidth=2)
    ax1.axhline(y=params.phase_threshold, color='red', linestyle='--', 
                linewidth=2, label='Threshold')
    if results['threshold_reached']:
        ax1.axvline(x=results['threshold_time'], color='green', linestyle=':', 
                   linewidth=2, label=f"Reached at {results['threshold_time']:.1f}s")
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Accumulated Phase (units)')
    ax1.set_title('Phase Accumulation Over Time')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Decoupling state
    ax2 = axes[0, 1]
    ax2.plot(t, results['decoupling_state'], 'green', linewidth=2)
    ax2.set_xlabel('Time (s)')
    ax2.set_ylabel('Decoupling State (0-1)')
    ax2.set_title('Decoupling State Transition')
    ax2.set_ylim([-0.05, 1.05])
    ax2.grid(True, alpha=0.3)
    
    # 3. Weight reduction
    ax3 = axes[0, 2]
    initial_weight = params.mass * 1000
    ax3.plot(t, results['weight_grams'], 'purple', linewidth=2)
    ax3.axhline(y=initial_weight, color='red', linestyle='--', label='Original weight')
    ax3.set_xlabel('Time (s)')
    ax3.set_ylabel('Weight (g)')
    ax3.set_title('Effective Weight')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. Coupling coefficient
    ax4 = axes[1, 0]
    ax4.plot(t, results['coupling'], 'orange', linewidth=2)
    ax4.axhline(y=1.0, color='red', linestyle='--', label='Full gravity')
    ax4.axhline(y=0.0, color='blue', linestyle='--', label='Weightless')
    ax4.set_xlabel('Time (s)')
    ax4.set_ylabel('Gravitational Coupling')
    ax4.set_title('Coupling Coefficient')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    # 5. Parameters table
    ax5 = axes[1, 1]
    ax5.axis('off')
    
    acoustic = results['acoustic']
    material = results['material']
    
    params_text = f"""SIMULATION PARAMETERS

Material: {params.material_name}
Mass: {params.mass * 1000:.1f} g
Frequency: {params.frequency:.2f} Hz
SPL: {params.sound_pressure_level:.0f} dB
Pressure: {acoustic.pressure_pascals():.3f} Pa

Phase Dynamics:
  Phase/cycle: {results['phase_per_cycle']:.6f} units
  Cycles/sec: {results['cycles_per_second']:.1f} Hz
  Phase/sec: {results['phase_per_cycle'] * results['cycles_per_second']:.6f}
  Coherence time: {params.coherence_time:.2e} s
  Threshold: {params.phase_threshold:.1f} units

Material Properties:
  Natural freq: {material.natural_frequency():.2f} Hz
  Damping: {material.damping_coefficient:.2f}
  Elastic modulus: {material.elastic_modulus/1e9:.1f} GPa
"""
    
    ax5.text(0.05, 0.95, params_text, transform=ax5.transAxes, fontsize=9,
             verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    # 6. Results summary
    ax6 = axes[1, 2]
    ax6.axis('off')
    
    final_phase = results['accumulated_phase'][-1]
    final_weight = results['weight_grams'][-1]
    max_weight_reduction = initial_weight - final_weight
    reduction_pct = (max_weight_reduction / initial_weight) * 100
    
    summary_text = f"""RESULTS SUMMARY

Duration: {params.duration:.0f} seconds ({params.duration/60:.1f} min)

Final Phase: {final_phase:.2f} / {params.phase_threshold:.0f}
Progress: {(final_phase/params.phase_threshold)*100:.1f}%

Weight Change:
  Initial: {initial_weight:.2f} g
  Final: {final_weight:.2f} g
  Reduction: {max_weight_reduction:.2f} g ({reduction_pct:.1f}%)

"""
    
    if results['threshold_reached']:
        summary_text += f"✓ THRESHOLD REACHED\n"
        summary_text += f"  Time: {results['threshold_time']:.1f} seconds\n"
        summary_text += f"  Decoupling achieved!\n"
    else:
        time_to_threshold = params.phase_threshold / (results['phase_per_cycle'] * results['cycles_per_second'])
        # Account for decay
        if params.coherence_time < time_to_threshold:
            # Will reach equilibrium before threshold
            equilibrium_phase = results['phase_per_cycle'] * results['cycles_per_second'] * params.coherence_time
            if equilibrium_phase < params.phase_threshold:
                summary_text += f"✗ THRESHOLD NOT REACHABLE\n"
                summary_text += f"  Max phase (equilibrium): {equilibrium_phase:.2f}\n"
                summary_text += f"  Coherence time too short\n"
            else:
                summary_text += f"○ THRESHOLD PENDING\n"
                summary_text += f"  Estimated time: {time_to_threshold:.1f} s\n"
        else:
            summary_text += f"○ THRESHOLD PENDING\n"
            summary_text += f"  Estimated time: {time_to_threshold:.1f} s\n"
    
    summary_text += f"\nKEY INSIGHT:\n"
    summary_text += f"Phase accumulation depends on:\n"
    summary_text += f"• Frequency resonance match\n"
    summary_text += f"• Coherence time vs decay rate\n"
    summary_text += f"• SPL (phase imprint strength)\n"
    summary_text += f"• Material damping (phase retention)\n"
    
    ax6.text(0.05, 0.95, summary_text, transform=ax6.transAxes, fontsize=9,
             verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved to {save_path}")
    
    return fig


def frequency_scan_phase(
    material_name: str = 'aluminum',
    mass: float = 0.1,
    spl: float = 120,
    coherence_time: float = 1e-3,
    freq_range: Tuple[float, float] = (0.1, 20),
    num_points: int = 100
) -> Dict:
    """
    Scan frequencies to find which accumulate phase fastest
    """
    frequencies = np.linspace(freq_range[0], freq_range[1], num_points)
    time_to_threshold = []
    final_phases = []
    phase_rates = []
    
    for freq in frequencies:
        params = PhaseAccumulationParams(
            material_name=material_name,
            mass=mass,
            frequency=freq,
            sound_pressure_level=spl,
            coherence_time=coherence_time,
            phase_threshold=1000.0,
            duration=600.0,  # 10 minutes
            timesteps=5000
        )
        
        results = simulate_phase_accumulation(params)
        
        final_phases.append(results['accumulated_phase'][-1])
        phase_rate = results['phase_per_cycle'] * results['cycles_per_second']
        phase_rates.append(phase_rate)
        
        # Estimate time to threshold
        equilibrium_phase = phase_rate * coherence_time
        if equilibrium_phase >= params.phase_threshold:
            # Will reach threshold
            t_thresh = params.phase_threshold / phase_rate
        else:
            # Won't reach
            t_thresh = np.inf
        
        time_to_threshold.append(t_thresh)
    
    return {
        'frequencies': frequencies,
        'time_to_threshold': np.array(time_to_threshold),
        'final_phases': np.array(final_phases),
        'phase_rates': np.array(phase_rates),
        'material': material_name,
        'spl': spl,
        'coherence_time': coherence_time
    }


if __name__ == "__main__":
    print("="*80)
    print("PHASE COHERENCE ACCUMULATION MODEL")
    print("="*80)
    
    # Test: aluminum at 10 Hz, 120 dB, 1ms coherence
    params = PhaseAccumulationParams(
        material_name='aluminum',
        mass=0.1,
        frequency=10.0,
        sound_pressure_level=120,
        coherence_time=1e-3,  # 1 millisecond
        phase_threshold=1000.0,
        duration=600.0,  # 10 minutes
        timesteps=10000
    )
    
    print(f"\nTest: {params.mass*1000}g {params.material_name}")
    print(f"Frequency: {params.frequency} Hz")
    print(f"SPL: {params.sound_pressure_level} dB")
    print(f"Coherence time: {params.coherence_time*1000} ms")
    print(f"Phase threshold: {params.phase_threshold}")
    
    results = simulate_phase_accumulation(params)
    
    print(f"\nPhase per cycle: {results['phase_per_cycle']:.6f}")
    print(f"Phase per second: {results['phase_per_cycle'] * results['cycles_per_second']:.6f}")
    print(f"Final accumulated phase: {results['accumulated_phase'][-1]:.2f}")
    print(f"Final weight: {results['weight_grams'][-1]:.2f} g")
    
    visualize_phase_accumulation(results, save_path='phase_accumulation_test.png')
    
    print("\n" + "="*80)
    print("FREQUENCY SCAN")
    print("="*80)
    
    scan = frequency_scan_phase(
        material_name='aluminum',
        mass=0.1,
        spl=120,
        coherence_time=1e-3,
        freq_range=(0.1, 20),
        num_points=100
    )
    
    best_idx = np.argmin(scan['time_to_threshold'])
    best_freq = scan['frequencies'][best_idx]
    best_time = scan['time_to_threshold'][best_idx]
    
    if best_time < np.inf:
        print(f"\nBest frequency: {best_freq:.2f} Hz")
        print(f"Time to threshold: {best_time:.2f} seconds ({best_time/60:.2f} minutes)")
    else:
        print(f"\nNo frequency reaches threshold with current parameters")
        print(f"Best frequency (highest phase): {best_freq:.2f} Hz")
        print(f"Max phase achievable: {scan['final_phases'][best_idx]:.2f}")
    
    print("\n" + "="*80)
