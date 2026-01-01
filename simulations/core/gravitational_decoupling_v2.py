"""
Gravitational Decoupling Simulation v2 - Physics Grounded
Models frequency-induced weight reduction using real acoustic physics

Key difference from v1: Uses actual sound pressure levels (dB), 
material vibration mechanics, and acoustic energy calculations
"""

import numpy as np
from scipy.integrate import odeint
from dataclasses import dataclass
from typing import Dict, Tuple, Optional
import matplotlib.pyplot as plt
from pathlib import Path
from .acoustic_physics import (
    AcousticProperties, MaterialVibration, MATERIAL_PRESETS,
    acoustic_force_on_object, coupling_intensity_from_vibration,
    required_spl_for_intensity
)

# Constants
PHI = (1 + np.sqrt(5)) / 2  # Golden ratio
EARTH_G = 9.81  # m/s²
HBAR = 1.054571817e-34  # J·s


@dataclass
class PhysicsBasedTest:
    """Test parameters using real physical units"""
    material_name: str  # Which material preset to use
    mass: float  # kg
    frequency: float  # Hz
    sound_pressure_level: float  # dB SPL
    duration: float = 60.0  # seconds
    timesteps: int = 1000
    observation_coupling: float = 0.1  # Minimum coupling (can't go below this)
    
    def get_material(self) -> MaterialVibration:
        """Get material properties, scaled to correct mass"""
        mat = MATERIAL_PRESETS.get(self.material_name, MATERIAL_PRESETS['aluminum'])
        # Scale to correct mass
        mat.mass = self.mass
        return mat


def geometric_evolution(t: float, phi: float = PHI) -> float:
    """Golden ratio geometric evolution over time"""
    return 1.0 + 0.1 * np.sin(2 * np.pi * phi * t / 60)


def maintenance_function(t: float) -> float:
    """Maintenance term - gradual strengthening"""
    return 1.0 - 0.2 * np.exp(-t / 30)


def resonance_function(frequency: float) -> float:
    """
    How well frequency resonates with gravitational field
    Peak at Schumann resonance (7.83 Hz) and harmonics
    """
    # Schumann and harmonics
    schumann_response = np.exp(-((frequency - 7.83)**2) / (2 * 1.5**2))
    
    # Alpha band (8-12 Hz)
    alpha_response = 0.7 * np.exp(-((frequency - 10)**2) / (2 * 2**2))
    
    # Ultra-low (0.5-2 Hz)
    ultra_low_response = 0.5 * np.exp(-((frequency - 1)**2) / (2 * 0.5**2))
    
    return max(schumann_response, alpha_response, ultra_low_response)


def coupling_derivative(coupling: float, t: float, acoustic: AcousticProperties, 
                       material: MaterialVibration, observation: float) -> float:
    """
    Rate of change of gravitational coupling based on acoustic vibration
    
    coupling: current coupling coefficient (1.0 = full gravity, 0.0 = weightless)
    """
    # Calculate actual vibration from sound
    force = acoustic_force_on_object(acoustic, material)
    amplitude = material.displacement_amplitude(force, acoustic.frequency)
    
    # Convert vibration to decoupling intensity
    intensity = coupling_intensity_from_vibration(amplitude, acoustic.frequency, material)
    
    # Frequency resonance with gravitational field
    freq_response = resonance_function(acoustic.frequency)
    
    # Geometric and maintenance terms
    G_t = geometric_evolution(t)
    M_t = maintenance_function(t)
    
    # Decoupling strength (from user's equations)
    decoupling_rate = -intensity * freq_response * G_t * M_t
    
    # Restoration toward baseline (coupling wants to return to 1.0)
    restoration_rate = 0.05 * (1.0 - coupling)
    
    # Can't go below observation threshold
    if coupling <= observation and decoupling_rate < 0:
        decoupling_rate = 0
    
    return decoupling_rate + restoration_rate


def simulate_gravitational_decoupling(params: PhysicsBasedTest) -> Dict:
    """
    Run gravitational decoupling simulation with real acoustic physics
    
    Returns dict with:
    - time: time points
    - coupling: gravitational coupling over time
    - weight: effective weight in grams
    - vibration_amplitude: physical vibration in meters
    - acoustic_intensity: decoupling intensity from vibration
    - acoustic_properties: AcousticProperties object
    """
    material = params.get_material()
    acoustic = AcousticProperties(
        frequency=params.frequency,
        sound_pressure_level=params.sound_pressure_level,
        distance_from_source=0.1
    )
    
    # Time points
    t = np.linspace(0, params.duration, params.timesteps)
    
    # Initial coupling (full gravity)
    coupling_0 = 1.0
    
    # Solve ODE
    coupling = odeint(
        lambda c, t_val: coupling_derivative(c, t_val, acoustic, material, params.observation_coupling),
        coupling_0,
        t
    ).flatten()
    
    # Calculate weight
    weight_kg = params.mass * EARTH_G * coupling
    weight_grams = weight_kg * 1000
    
    # Calculate vibration amplitude at each timestep
    force = acoustic_force_on_object(acoustic, material)
    vibration = material.displacement_amplitude(force, params.frequency)
    vibration_array = np.full_like(t, vibration)
    
    # Calculate decoupling intensity at each timestep
    intensity = coupling_intensity_from_vibration(vibration, params.frequency, material)
    intensity_array = np.full_like(t, intensity)
    
    return {
        'time': t,
        'coupling': coupling,
        'weight_grams': weight_grams,
        'vibration_amplitude': vibration_array,
        'acoustic_intensity': intensity_array,
        'acoustic_properties': acoustic,
        'material': material,
        'params': params
    }


def visualize_results(results: Dict, save_path: Optional[Path] = None):
    """Create comprehensive visualization of results"""
    fig, axes = plt.subplots(3, 2, figsize=(14, 12))
    fig.suptitle('Physics-Grounded Gravitational Decoupling Simulation', fontsize=16, fontweight='bold')
    
    t = results['time']
    params = results['params']
    acoustic = results['acoustic_properties']
    material = results['material']
    
    # 1. Weight over time
    ax1 = axes[0, 0]
    initial_weight = params.mass * 1000  # grams
    ax1.plot(t, results['weight_grams'], 'b-', linewidth=2)
    ax1.axhline(y=initial_weight, color='r', linestyle='--', label='Original weight')
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Weight (g)')
    ax1.set_title('Effective Weight on Scale')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # 2. Coupling coefficient
    ax2 = axes[0, 1]
    ax2.plot(t, results['coupling'], 'g-', linewidth=2)
    ax2.axhline(y=1.0, color='r', linestyle='--', label='Full gravity')
    ax2.axhline(y=0.0, color='orange', linestyle='--', label='Weightless')
    ax2.set_xlabel('Time (s)')
    ax2.set_ylabel('Coupling Coefficient')
    ax2.set_title('Gravitational Coupling')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    # 3. Vibration amplitude
    ax3 = axes[1, 0]
    vibration_um = results['vibration_amplitude'] * 1e6  # Convert to micrometers
    ax3.plot(t, vibration_um, 'purple', linewidth=2)
    ax3.set_xlabel('Time (s)')
    ax3.set_ylabel('Amplitude (µm)')
    ax3.set_title('Physical Vibration Amplitude')
    ax3.grid(True, alpha=0.3)
    
    # 4. Decoupling intensity
    ax4 = axes[1, 1]
    ax4.plot(t, results['acoustic_intensity'], 'orange', linewidth=2)
    ax4.set_xlabel('Time (s)')
    ax4.set_ylabel('Intensity (0-1)')
    ax4.set_title('Decoupling Intensity from Vibration')
    ax4.grid(True, alpha=0.3)
    
    # 5. Acoustic properties (text)
    ax5 = axes[2, 0]
    ax5.axis('off')
    
    pressure_pa = acoustic.pressure_pascals()
    intensity_wm2 = acoustic.intensity()
    wavelength = acoustic.wavelength()
    particle_disp = acoustic.particle_displacement() * 1000  # mm
    
    force = acoustic_force_on_object(acoustic, material)
    
    text = f"""ACOUSTIC PARAMETERS:
Frequency: {params.frequency:.2f} Hz
Sound Pressure Level: {params.sound_pressure_level:.1f} dB
Pressure: {pressure_pa:.3f} Pa
Intensity: {intensity_wm2:.6f} W/m²
Wavelength: {wavelength:.2f} m
Air Particle Displacement: {particle_disp:.4f} mm

MATERIAL RESPONSE:
Material: {params.material_name}
Mass: {params.mass*1000:.1f} g
Natural Frequency: {material.natural_frequency():.2f} Hz
Force Applied: {force:.6f} N
Vibration: {vibration_um[0]:.4f} µm
Resonance Factor: {material.resonance_amplification(params.frequency):.2f}x
"""
    
    ax5.text(0.05, 0.95, text, transform=ax5.transAxes, fontsize=10,
             verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    # 6. Summary statistics (text)
    ax6 = axes[2, 1]
    ax6.axis('off')
    
    max_reduction = initial_weight - results['weight_grams'].min()
    max_reduction_pct = (max_reduction / initial_weight) * 100
    final_weight = results['weight_grams'][-1]
    min_coupling = results['coupling'].min()
    
    summary = f"""RESULTS SUMMARY:
Initial Weight: {initial_weight:.2f} g
Final Weight: {final_weight:.2f} g
Maximum Reduction: {max_reduction:.2f} g ({max_reduction_pct:.1f}%)

Minimum Coupling: {min_coupling:.6f}
Decoupling Intensity: {results['acoustic_intensity'][0]:.6f}

Frequency Resonance: {resonance_function(params.frequency):.4f}

INTERPRETATION:
"""
    
    if max_reduction_pct > 100:
        summary += "⚠️ LEVITATION predicted (>100% reduction)\n"
        summary += "This suggests anti-gravity effect.\n"
    elif max_reduction_pct > 50:
        summary += "✓ SIGNIFICANT decoupling effect\n"
        summary += "Object becomes substantially lighter.\n"
    elif max_reduction_pct > 10:
        summary += "✓ MODERATE decoupling effect\n"
        summary += "Measurable weight reduction.\n"
    elif max_reduction_pct > 1:
        summary += "○ WEAK decoupling effect\n"
        summary += "Small but detectable change.\n"
    else:
        summary += "✗ NO SIGNIFICANT EFFECT\n"
        summary += "Acoustic vibration too weak.\n"
    
    ax6.text(0.05, 0.95, summary, transform=ax6.transAxes, fontsize=10,
             verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Plot saved to {save_path}")
    
    return fig


def test_frequency_sweep(
    material_name: str = 'aluminum',
    mass: float = 0.1,
    spl: float = 100,
    freq_range: Tuple[float, float] = (0.1, 20),
    num_points: int = 50
) -> Dict:
    """
    Sweep through frequency range to find optimal decoupling
    
    Returns dict with frequencies, max weight reductions, and vibration amplitudes
    """
    frequencies = np.linspace(freq_range[0], freq_range[1], num_points)
    max_reductions = []
    vibration_amplitudes = []
    decoupling_intensities = []
    
    for freq in frequencies:
        params = PhysicsBasedTest(
            material_name=material_name,
            mass=mass,
            frequency=freq,
            sound_pressure_level=spl,
            duration=60.0,
            timesteps=500
        )
        
        results = simulate_gravitational_decoupling(params)
        
        initial_weight = mass * 1000
        max_reduction = initial_weight - results['weight_grams'].min()
        max_reductions.append(max_reduction)
        vibration_amplitudes.append(results['vibration_amplitude'][0])
        decoupling_intensities.append(results['acoustic_intensity'][0])
    
    return {
        'frequencies': frequencies,
        'max_reductions': np.array(max_reductions),
        'vibration_amplitudes': np.array(vibration_amplitudes),
        'decoupling_intensities': np.array(decoupling_intensities),
        'material': material_name,
        'spl': spl,
        'mass': mass
    }


if __name__ == "__main__":
    print("="*70)
    print("PHYSICS-GROUNDED GRAVITATIONAL DECOUPLING")
    print("="*70)
    
    # Test with aluminum at 100 dB, 10 Hz
    params = PhysicsBasedTest(
        material_name='aluminum',
        mass=0.1,  # 100g
        frequency=10.0,
        sound_pressure_level=100,
        duration=60.0
    )
    
    print(f"\nTesting {params.mass*1000}g {params.material_name} object")
    print(f"Frequency: {params.frequency} Hz")
    print(f"Sound Pressure Level: {params.sound_pressure_level} dB")
    
    results = simulate_gravitational_decoupling(params)
    
    initial_weight = params.mass * 1000
    max_reduction = initial_weight - results['weight_grams'].min()
    max_reduction_pct = (max_reduction / initial_weight) * 100
    
    print(f"\nInitial weight: {initial_weight:.2f} g")
    print(f"Minimum weight: {results['weight_grams'].min():.2f} g")
    print(f"Maximum reduction: {max_reduction:.2f} g ({max_reduction_pct:.1f}%)")
    print(f"Minimum coupling: {results['coupling'].min():.6f}")
    print(f"Vibration amplitude: {results['vibration_amplitude'][0]*1e6:.4f} µm")
    print(f"Decoupling intensity: {results['acoustic_intensity'][0]:.6f}")
    
    # Save visualization
    output_path = Path('gravity_physics_test.png')
    visualize_results(results, save_path=output_path)
    
    print(f"\nVisualization saved to {output_path}")
    print("="*70)
