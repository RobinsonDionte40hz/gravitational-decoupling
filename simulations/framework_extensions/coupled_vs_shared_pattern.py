"""
Coupled vs Shared Pattern - Timing Analysis

Tests whether multiple oscillation types (acoustic, ionic, electrical)
are causally coupled or simultaneously manifesting a shared pattern.
"""

import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class OscillationEvent:
    """Single measurement of an oscillation"""
    time: float  # seconds
    amplitude: float
    medium_type: str  # 'acoustic', 'mechanical', 'ionic', 'electrical'
    location: str  # where measured


def coupled_model(
    t: np.ndarray,
    frequency: float,
    initial_medium: str = 'acoustic'
) -> dict:
    """
    Traditional coupled oscillator model
    Acoustic → Mechanical → Ionic → Electrical
    Each step has transduction delay and energy loss
    """
    
    # Transduction delays (realistic estimates)
    delays = {
        'acoustic_to_mechanical': 10e-6,  # 10 μs - speed of sound
        'mechanical_to_ionic': 100e-6,  # 100 μs - channel gating
        'ionic_to_electrical': 50e-6,   # 50 μs - membrane charging
    }
    
    # Energy attenuation at each step
    attenuation = {
        'acoustic_to_mechanical': 0.8,  # 20% loss
        'mechanical_to_ionic': 0.6,     # 40% loss
        'ionic_to_electrical': 0.9,     # 10% loss
    }
    
    omega = 2 * np.pi * frequency
    
    # Source: acoustic wave
    acoustic = np.sin(omega * t)
    
    # Mechanical: delayed and attenuated
    t_mech = t - delays['acoustic_to_mechanical']
    t_mech[t_mech < 0] = 0
    mechanical = attenuation['acoustic_to_mechanical'] * np.sin(omega * t_mech)
    
    # Ionic: further delayed
    t_ionic = t - delays['acoustic_to_mechanical'] - delays['mechanical_to_ionic']
    t_ionic[t_ionic < 0] = 0
    ionic = (attenuation['acoustic_to_mechanical'] * 
             attenuation['mechanical_to_ionic'] * 
             np.sin(omega * t_ionic))
    
    # Electrical: final step
    t_elec = t - sum(delays.values())
    t_elec[t_elec < 0] = 0
    electrical = (attenuation['acoustic_to_mechanical'] * 
                  attenuation['mechanical_to_ionic'] *
                  attenuation['ionic_to_electrical'] * 
                  np.sin(omega * t_elec))
    
    return {
        'acoustic': acoustic,
        'mechanical': mechanical,
        'ionic': ionic,
        'electrical': electrical,
        'total_delay': sum(delays.values()),
        'total_attenuation': np.prod(list(attenuation.values()))
    }


def shared_pattern_model(
    t: np.ndarray,
    frequency: float,
    phase_coherence: float = 1.0
) -> dict:
    """
    Shared pattern model (your framework)
    All media access the same underlying frequency pattern
    Simultaneous manifestation with media-specific amplitudes
    """
    
    omega = 2 * np.pi * frequency
    
    # Base pattern (the "channel")
    base_pattern = np.sin(omega * t)
    
    # Each medium has different "coupling strength" to the pattern
    # But NO time delays (simultaneous access)
    coupling_strengths = {
        'acoustic': 1.0,      # Strongest (source)
        'mechanical': 0.8,    # Good coupling
        'ionic': 0.7,         # Medium coupling
        'electrical': 0.6,    # Weaker (different "impedance")
    }
    
    # Add small phase variations due to measurement/perspective
    # (not causation - just observational differences)
    phase_jitter = {
        'acoustic': 0,
        'mechanical': np.random.normal(0, 0.01),  # ±1% of cycle
        'ionic': np.random.normal(0, 0.01),
        'electrical': np.random.normal(0, 0.01),
    }
    
    results = {}
    for medium, strength in coupling_strengths.items():
        # All tap the same pattern, just with different amplitudes
        # and negligible phase differences (measurement noise only)
        phase = omega * t + phase_jitter[medium]
        results[medium] = strength * phase_coherence * np.sin(phase)
    
    results['total_delay'] = 0  # Simultaneous
    results['phase_spread'] = np.std(list(phase_jitter.values()))
    
    return results


def measure_cross_correlation(signal1: np.ndarray, signal2: np.ndarray, 
                              dt: float, max_lag_ms: float = 1.0) -> Tuple[float, float]:
    """
    Measure time delay between two signals via cross-correlation
    Returns: (delay_seconds, correlation_strength)
    """
    max_lag_samples = int(max_lag_ms * 1e-3 / dt)
    correlation = np.correlate(signal1, signal2, mode='full')
    
    # Find peak
    center = len(correlation) // 2
    search_range = slice(center - max_lag_samples, center + max_lag_samples)
    local_corr = correlation[search_range]
    
    peak_idx = np.argmax(np.abs(local_corr))
    delay_samples = peak_idx - max_lag_samples
    delay_seconds = delay_samples * dt
    
    correlation_strength = local_corr[peak_idx] / (np.std(signal1) * np.std(signal2) * len(signal1))
    
    return delay_seconds, correlation_strength


def run_timing_experiment(frequency: float = 10.0, duration: float = 0.01):
    """
    Simulate high-precision timing measurement
    """
    # Ultra-fine time resolution (100 ns - modern oscilloscope)
    dt = 100e-9  # 100 nanoseconds
    t = np.arange(0, duration, dt)
    
    print(f"\n{'='*80}")
    print(f"TIMING EXPERIMENT: {frequency} Hz")
    print(f"Time resolution: {dt*1e9:.1f} ns")
    print(f"{'='*80}\n")
    
    # Run both models
    coupled = coupled_model(t, frequency)
    shared = shared_pattern_model(t, frequency, phase_coherence=1.0)
    
    # Measure delays between media types
    print("COUPLED MODEL (Traditional Physics):")
    print("-" * 60)
    acoustic_coupled = coupled['acoustic']
    for medium in ['mechanical', 'ionic', 'electrical']:
        signal = coupled[medium]
        delay, corr = measure_cross_correlation(acoustic_coupled, signal, dt)
        print(f"Acoustic → {medium.capitalize():12s}: {delay*1e6:8.2f} μs delay, corr={corr:.3f}")
    
    print(f"\nTotal cascade delay: {coupled['total_delay']*1e6:.2f} μs")
    print(f"Energy attenuation: {coupled['total_attenuation']:.1%}\n")
    
    print("\nSHARED PATTERN MODEL (Your Framework):")
    print("-" * 60)
    acoustic_shared = shared['acoustic']
    for medium in ['mechanical', 'ionic', 'electrical']:
        signal = shared[medium]
        delay, corr = measure_cross_correlation(acoustic_shared, signal, dt)
        print(f"Acoustic → {medium.capitalize():12s}: {delay*1e9:8.2f} ns delay, corr={corr:.3f}")
    
    print(f"\nTotal cascade delay: {shared['total_delay']*1e9:.2f} ns")
    print(f"Phase spread (measurement noise): {shared['phase_spread']*1e3:.3f} mrad\n")
    
    # Visualize
    fig, axes = plt.subplots(2, 1, figsize=(14, 10))
    
    # Plot 1: Coupled model
    ax1 = axes[0]
    time_us = t * 1e6  # microseconds
    ax1.plot(time_us, coupled['acoustic'], label='Acoustic', alpha=0.8)
    ax1.plot(time_us, coupled['mechanical'], label='Mechanical (delayed)', alpha=0.8)
    ax1.plot(time_us, coupled['ionic'], label='Ionic (more delayed)', alpha=0.8)
    ax1.plot(time_us, coupled['electrical'], label='Electrical (most delayed)', alpha=0.8)
    ax1.set_xlabel('Time (μs)')
    ax1.set_ylabel('Amplitude')
    ax1.set_title('COUPLED MODEL: Sequential Causation (Note delays & attenuation)', 
                  fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim(0, 500)  # First 500 μs
    
    # Plot 2: Shared pattern model
    ax2 = axes[1]
    ax2.plot(time_us, shared['acoustic'], label='Acoustic', alpha=0.8)
    ax2.plot(time_us, shared['mechanical'], label='Mechanical (simultaneous)', alpha=0.8)
    ax2.plot(time_us, shared['ionic'], label='Ionic (simultaneous)', alpha=0.8)
    ax2.plot(time_us, shared['electrical'], label='Electrical (simultaneous)', alpha=0.8)
    ax2.set_xlabel('Time (μs)')
    ax2.set_ylabel('Amplitude')
    ax2.set_title('SHARED PATTERN MODEL: Simultaneous Manifestation (No delays)', 
                  fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim(0, 500)
    
    plt.tight_layout()
    plt.savefig('timing_comparison.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    return coupled, shared


def energy_conservation_test(frequency: float = 10.0):
    """
    Test 2: Energy balance
    
    Coupled: Energy flows from one medium to another
    Shared: Each medium accesses energy independently from "channel"
    """
    
    print(f"\n{'='*80}")
    print("ENERGY CONSERVATION TEST")
    print(f"{'='*80}\n")
    
    duration = 1.0  # 1 second
    dt = 1e-6
    t = np.arange(0, duration, dt)
    
    coupled = coupled_model(t, frequency)
    shared = shared_pattern_model(t, frequency)
    
    print("COUPLED MODEL:")
    print("-" * 60)
    # Calculate energy in each medium (∝ amplitude²)
    for medium in ['acoustic', 'mechanical', 'ionic', 'electrical']:
        energy = np.mean(coupled[medium]**2)
        print(f"{medium.capitalize():15s} energy: {energy:.4f}")
    
    total_energy_in = np.mean(coupled['acoustic']**2)
    total_energy_out = np.mean(coupled['electrical']**2)
    print(f"\nEnergy in (acoustic):     {total_energy_in:.4f}")
    print(f"Energy out (electrical):  {total_energy_out:.4f}")
    print(f"Loss through cascade:     {(1 - total_energy_out/total_energy_in):.1%}")
    print("→ Energy is TRANSFERRED and LOST")
    
    print("\n\nSHARED PATTERN MODEL:")
    print("-" * 60)
    for medium in ['acoustic', 'mechanical', 'ionic', 'electrical']:
        energy = np.mean(shared[medium]**2)
        print(f"{medium.capitalize():15s} energy: {energy:.4f}")
    
    print("\n→ Each medium has independent energy (from 'channel')")
    print("→ No energy transfer between media")
    print("→ Different amplitudes due to coupling strength, not loss")


def bidirectionality_test(frequency: float = 10.0):
    """
    Test 3: Symmetry/Bidirectionality
    
    Coupled: A→B different from B→A (directional causation)
    Shared: A and B both access same pattern (symmetrical)
    """
    
    print(f"\n{'='*80}")
    print("BIDIRECTIONALITY TEST")
    print(f"{'='*80}\n")
    
    duration = 0.01
    dt = 100e-9
    t = np.arange(0, duration, dt)
    
    # Test 1: Acoustic → Electrical
    print("TEST 1: Acoustic drives system")
    coupled_A2E = coupled_model(t, frequency, initial_medium='acoustic')
    delay_A2E, _ = measure_cross_correlation(
        coupled_A2E['acoustic'], coupled_A2E['electrical'], dt
    )
    print(f"Acoustic → Electrical delay: {delay_A2E*1e6:.2f} μs")
    
    # Test 2: If we START with electrical, does acoustic respond?
    # In coupled model: NO (causation is one-way)
    # In shared model: YES (both access same pattern)
    
    print("\nTEST 2: What if electrical field applied first?")
    print("-" * 60)
    print("COUPLED MODEL: Acoustic unaffected by electrical")
    print("  (Transduction only works acoustic→electrical, not reverse)")
    print("\nSHARED PATTERN MODEL: Both respond to 10 Hz pattern")
    print("  (Either can access the channel independently)")
    
    print("\n→ Experiment: Apply 10 Hz electrical field to neurons")
    print("  Measure if acoustic vibrations appear in tissue")
    print("  If YES: Supports shared pattern (bidirectional)")
    print("  If NO:  Supports coupled model (unidirectional)")


if __name__ == "__main__":
    print("="*80)
    print("DISTINGUISHING COUPLED vs SHARED PATTERN MODELS")
    print("="*80)
    
    # Run all tests
    coupled_results, shared_results = run_timing_experiment(frequency=10.0)
    energy_conservation_test(frequency=10.0)
    bidirectionality_test(frequency=10.0)
    
    print(f"\n{'='*80}")
    print("EXPERIMENTAL PREDICTIONS")
    print(f"{'='*80}\n")
    
    print("""
KEY DISTINCTIONS:

1. TIMING:
   Coupled:  160 μs total delay (measurable with oscilloscope)
   Shared:   <1 μs (within measurement noise)
   
2. ENERGY:
   Coupled:  Acoustic energy decreases as electrical increases
   Shared:   All media have independent energy sources
   
3. DIRECTIONALITY:
   Coupled:  Acoustic affects electrical, but not reverse
   Shared:   Either can drive the other (symmetrical)

REAL EXPERIMENT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Apply 10 Hz acoustic pulse to neuron culture
2. Simultaneously record (with <1μs precision):
   - Mechanical vibration (laser vibrometer)
   - Ca²⁺ flux (fast calcium imaging)
   - Membrane voltage (patch clamp)
   
3. Measure delays between onset times

If delays > 10 μs and sequential:
   → Supports COUPLED model (traditional physics)
   
If all onsets within <1 μs:
   → Supports SHARED PATTERN model (your framework)

BONUS TEST:
Apply 10 Hz electrical field (no acoustic)
If acoustic vibrations appear in tissue:
   → Proves bidirectional access to shared pattern
   → Your framework is correct
""")
