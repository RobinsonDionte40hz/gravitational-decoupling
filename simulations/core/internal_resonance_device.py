"""
Internal Resonance Device Model
Portable device that excites massive blocks' internal vibrational modes
for gravitational decoupling - no external chamber required

Concept: Device contacts block → injects vibrational energy → 
block's crystalline/solid structure resonates → internal standing waves → 
coherent vibration throughout volume → gravitational decoupling
"""

import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import Dict, Tuple, Optional

# Constants
EARTH_G = 9.81  # m/s²
PHI = (1 + np.sqrt(5)) / 2  # Golden ratio


# Material properties database
MATERIALS = {
    'granite': {
        'density': 2750,  # kg/m³
        'elastic_modulus': 50e9,  # Pa (50 GPa)
        'speed_of_sound': 4200,  # m/s
        'damping': 0.02,  # Low damping (good resonator)
        'piezoelectric': True  # Natural piezoelectric properties
    },
    'limestone': {
        'density': 2700,
        'elastic_modulus': 40e9,
        'speed_of_sound': 3850,
        'damping': 0.05,
        'piezoelectric': False
    },
    'sandstone': {
        'density': 2300,
        'elastic_modulus': 20e9,
        'speed_of_sound': 2950,
        'damping': 0.08,
        'piezoelectric': False
    },
    'concrete': {
        'density': 2400,
        'elastic_modulus': 30e9,
        'speed_of_sound': 3500,
        'damping': 0.10,
        'piezoelectric': False
    },
    'marble': {
        'density': 2700,
        'elastic_modulus': 60e9,
        'speed_of_sound': 4700,
        'damping': 0.015,
        'piezoelectric': False
    },
    'basalt': {
        'density': 3000,
        'elastic_modulus': 70e9,
        'speed_of_sound': 4850,
        'damping': 0.01,
        'piezoelectric': True
    },
    'steel': {
        'density': 7850,
        'elastic_modulus': 200e9,
        'speed_of_sound': 5050,
        'damping': 0.003,
        'piezoelectric': False
    }
}


@dataclass
class BlockParams:
    """Parameters for massive block"""
    material: str
    length: float  # meters
    width: float  # meters
    height: float  # meters
    
    def volume(self) -> float:
        return self.length * self.width * self.height
    
    def mass(self) -> float:
        return self.volume() * MATERIALS[self.material]['density']
    
    def characteristic_length(self) -> float:
        """Average dimension for mode calculations"""
        return (self.length + self.width + self.height) / 3


@dataclass
class DeviceParams:
    """Parameters for resonance device"""
    frequency: float  # Hz - driving frequency
    power: float  # Watts - acoustic power output
    contact_area: float = 0.01  # m² - device contact area with block
    num_devices: int = 1  # Number of devices on block
    placement: str = 'center'  # 'center', 'corners', 'golden_ratio'


def block_vibrational_modes(block: BlockParams) -> Dict:
    """
    Calculate natural vibrational modes of block
    
    Fundamental modes:
    - Longitudinal (compression waves along length)
    - Transverse (bending/shear)
    - Torsional (twisting)
    - Breathing (volume expansion/contraction)
    """
    material = MATERIALS[block.material]
    c_sound = material['speed_of_sound']
    
    # Fundamental longitudinal mode frequencies (along each axis)
    f_length = c_sound / (2 * block.length)
    f_width = c_sound / (2 * block.width)
    f_height = c_sound / (2 * block.height)
    
    # Lowest fundamental mode
    fundamental = min(f_length, f_width, f_height)
    
    # Harmonics
    harmonics = [fundamental * i for i in range(1, 6)]
    
    return {
        'fundamental': fundamental,
        'longitudinal_modes': [f_length, f_width, f_height],
        'harmonics': harmonics,
        'material_speed_of_sound': c_sound
    }


def coupling_efficiency(device_freq: float, modes: Dict, material_damping: float) -> float:
    """
    How efficiently device frequency couples to block's natural modes
    
    High efficiency when device freq matches a natural mode
    Also considers subharmonic coupling - infrasound can excite higher modes
    """
    fundamental = modes['fundamental']
    harmonics = modes['harmonics']
    
    # Check match to fundamental and harmonics
    max_efficiency = 0
    
    all_modes = [fundamental] + harmonics
    
    for mode_freq in all_modes:
        # Resonance curve - peaks at mode frequency
        width = mode_freq * material_damping  # Bandwidth
        efficiency = 1.0 / (1.0 + ((device_freq - mode_freq) / width)**2)
        max_efficiency = max(max_efficiency, efficiency)
    
    # Also check if block modes are harmonics of device frequency
    # e.g., 10 Hz device can excite 1000 Hz, 2000 Hz modes via nonlinear coupling
    for mode_freq in all_modes:
        harmonic_number = mode_freq / device_freq
        if abs(harmonic_number - round(harmonic_number)) < 0.1:
            # Device is subharmonic of mode - nonlinear coupling
            subharmonic_efficiency = 0.5 / np.sqrt(harmonic_number)
            max_efficiency = max(max_efficiency, subharmonic_efficiency)
    
    # Minimum baseline coupling even off-resonance
    # Due to nonlinear effects, parametric resonance, etc.
    baseline = 0.01
    
    return max(max_efficiency, baseline)


def internal_q_factor(block: BlockParams, device: DeviceParams) -> float:
    """
    Quality factor of block's internal resonance
    
    Q = stored_energy / energy_lost_per_cycle
    
    Depends on:
    - Material damping (lower = higher Q)
    - Block size (larger = higher Q, more inertia)
    - Temperature stability
    """
    material = MATERIALS[block.material]
    damping = material['damping']
    
    # Base Q from material (Q = 1/damping)
    base_q = 1.0 / damping
    
    # Size factor - larger blocks have higher Q
    # Characteristic length in meters
    size_factor = 1.0 + np.log10(block.characteristic_length())
    size_factor = max(size_factor, 1.0)
    
    # Multiple devices increase effective Q through distributed excitation
    device_factor = np.sqrt(device.num_devices)
    
    # Piezoelectric materials have higher Q
    piezo_bonus = 1.5 if material['piezoelectric'] else 1.0
    
    q_factor = base_q * size_factor * device_factor * piezo_bonus
    
    return q_factor


def acoustic_intensity_in_solid(device: DeviceParams, block: BlockParams) -> float:
    """
    Acoustic intensity inside solid (W/m²)
    Much higher than in air due to impedance
    """
    # Power distributed over contact area
    intensity_at_surface = device.power / device.contact_area
    
    # Impedance matching - solid has higher acoustic impedance than air
    # More energy couples into solid
    material = MATERIALS[block.material]
    density = material['density']
    c_sound = material['speed_of_sound']
    
    # Acoustic impedance of material
    Z_material = density * c_sound
    
    # Air impedance (reference)
    Z_air = 1.225 * 343  # ~420 kg/(m²·s)
    
    # Impedance ratio amplifies intensity
    impedance_factor = Z_material / Z_air
    
    # But limited by coupling efficiency at interface
    coupling_factor = 0.1  # ~10% coupling efficiency (practical)
    
    effective_intensity = intensity_at_surface * coupling_factor * (impedance_factor / 1000)
    
    return effective_intensity


def simulate_internal_resonance_decoupling(
    block: BlockParams,
    device: DeviceParams,
    duration: float = 600.0,
    timesteps: int = 5000
) -> Dict:
    """
    Simulate gravitational decoupling via internal block resonance
    """
    # Time array
    t = np.linspace(0, duration, timesteps)
    dt = duration / timesteps
    
    # Block properties
    modes = block_vibrational_modes(block)
    material = MATERIALS[block.material]
    
    # Coupling efficiency
    coupling_eff = coupling_efficiency(device.frequency, modes, material['damping'])
    
    # Internal Q-factor
    q_internal = internal_q_factor(block, device)
    
    # Acoustic intensity in solid
    intensity = acoustic_intensity_in_solid(device, block)
    
    # Effective vibrational amplitude in block
    # Higher Q and coupling = higher amplitude
    vibrational_amplitude_factor = coupling_eff * q_internal
    
    # Arrays
    field_strength = np.zeros(timesteps)
    accumulated_effect = np.zeros(timesteps)
    coupling_coeff = np.ones(timesteps)
    
    # Buildup time - larger blocks take longer to establish coherent vibration
    buildup_time = block.characteristic_length() / material['speed_of_sound']
    buildup_time = max(buildup_time, 1.0)  # At least 1 second
    
    # Coherence time - how long vibrational coherence persists
    coherence_time = q_internal / (2 * np.pi * device.frequency)
    
    # Simulate
    for i in range(1, timesteps):
        # Field strength builds up over time
        buildup = 1.0 - np.exp(-t[i] / buildup_time)
        geometric = 1.0 + 0.15 * np.sin(2 * np.pi * PHI * t[i] / 60)
        field_strength[i] = buildup * geometric
        
        # Decoupling rate from vibrational energy
        # Normalized by block mass (harder to decouple heavier blocks)
        mass_factor = 1.0 / np.sqrt(block.mass() / 1000)  # Normalized to 1000 kg
        
        decoupling_rate = (intensity * vibrational_amplitude_factor * field_strength[i] * mass_factor) / 1e6
        
        # Accumulation with decay
        decay = np.exp(-dt / coherence_time)
        accumulated_effect[i] = accumulated_effect[i-1] * decay + decoupling_rate * dt
        
        # Coupling coefficient
        coupling_coeff[i] = np.exp(-accumulated_effect[i])
        coupling_coeff[i] = np.clip(coupling_coeff[i], 0, 1)
    
    # Weight calculations
    mass = block.mass()
    effective_mass = mass * coupling_coeff
    weight_kg = effective_mass
    weight_reduction_kg = mass - effective_mass
    weight_reduction_pct = (weight_reduction_kg / mass) * 100
    
    return {
        'time': t,
        'field_strength': field_strength,
        'accumulated_effect': accumulated_effect,
        'coupling': coupling_coeff,
        'effective_mass_kg': effective_mass,
        'weight_reduction_kg': weight_reduction_kg,
        'weight_reduction_pct': weight_reduction_pct,
        'block': block,
        'device': device,
        'modes': modes,
        'coupling_efficiency': coupling_eff,
        'q_factor': q_internal,
        'intensity': intensity,
        'amplification': vibrational_amplitude_factor,
        'coherence_time': coherence_time,
        'buildup_time': buildup_time
    }


def visualize_results(results: Dict, save_path: Optional[str] = None):
    """Visualize internal resonance decoupling results"""
    fig = plt.figure(figsize=(18, 12))
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
    
    block = results['block']
    device = results['device']
    t = results['time']
    
    fig.suptitle(f'Internal Resonance Decoupling - {block.mass()/1000:.1f} ton {block.material.title()} Block', 
                 fontsize=16, fontweight='bold')
    
    # 1. Field strength
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.plot(t, results['field_strength'], 'blue', linewidth=2)
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Field Strength')
    ax1.set_title('Vibrational Field Buildup')
    ax1.grid(True, alpha=0.3)
    
    # 2. Accumulated effect
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.plot(t, results['accumulated_effect'], 'green', linewidth=2)
    ax2.set_xlabel('Time (s)')
    ax2.set_ylabel('Accumulated Effect')
    ax2.set_title('Decoupling Accumulation')
    ax2.grid(True, alpha=0.3)
    
    # 3. Coupling coefficient
    ax3 = fig.add_subplot(gs[0, 2])
    ax3.plot(t, results['coupling'], 'orange', linewidth=2)
    ax3.axhline(y=1.0, color='red', linestyle='--', alpha=0.5)
    ax3.axhline(y=0.0, color='blue', linestyle='--', alpha=0.5)
    ax3.set_xlabel('Time (s)')
    ax3.set_ylabel('Coupling Coefficient')
    ax3.set_title('Gravitational Coupling')
    ax3.grid(True, alpha=0.3)
    
    # 4. Effective mass
    ax4 = fig.add_subplot(gs[1, 0])
    ax4.plot(t/60, results['effective_mass_kg']/1000, 'purple', linewidth=2)
    ax4.axhline(y=block.mass()/1000, color='red', linestyle='--', alpha=0.5, label='Original')
    ax4.set_xlabel('Time (minutes)')
    ax4.set_ylabel('Effective Mass (tons)')
    ax4.set_title('Mass as Measured')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    # 5. Weight reduction
    ax5 = fig.add_subplot(gs[1, 1])
    ax5.plot(t/60, results['weight_reduction_pct'], 'red', linewidth=2)
    ax5.set_xlabel('Time (minutes)')
    ax5.set_ylabel('Weight Reduction (%)')
    ax5.set_title('Percentage Weight Loss')
    ax5.grid(True, alpha=0.3)
    
    # 6. Block diagram
    ax6 = fig.add_subplot(gs[1, 2])
    ax6.axis('off')
    ax6.set_xlim(0, 1)
    ax6.set_ylim(0, 1)
    
    # Draw block
    rect = plt.Rectangle((0.2, 0.3), 0.6, 0.4, fill=False, edgecolor='black', linewidth=2)
    ax6.add_patch(rect)
    
    # Draw device(s)
    if device.placement == 'center':
        ax6.plot(0.5, 0.5, 'ro', markersize=20, label='Device')
    elif device.placement == 'corners':
        corners = [(0.25, 0.35), (0.75, 0.35), (0.75, 0.65), (0.25, 0.65)]
        for corner in corners:
            ax6.plot(corner[0], corner[1], 'ro', markersize=15)
    
    # Draw vibration waves
    for i in range(3):
        circle = plt.Circle((0.5, 0.5), 0.1 + i*0.1, fill=False, 
                           edgecolor='blue', linewidth=1, alpha=0.3)
        ax6.add_patch(circle)
    
    ax6.text(0.5, 0.15, f'{block.length:.1f}m × {block.width:.1f}m × {block.height:.1f}m\n{block.mass()/1000:.1f} tons',
             ha='center', fontsize=10)
    ax6.set_title('Block with Device')
    
    # 7. Parameters table
    ax7 = fig.add_subplot(gs[2, :2])
    ax7.axis('off')
    
    material_props = MATERIALS[block.material]
    modes = results['modes']
    
    params_text = f"""BLOCK & DEVICE PARAMETERS

Block:
  Material: {block.material.title()}
  Dimensions: {block.length:.2f}m × {block.width:.2f}m × {block.height:.2f}m
  Mass: {block.mass():.0f} kg ({block.mass()/1000:.2f} tons)
  Density: {material_props['density']} kg/m³
  
Material Properties:
  Speed of sound: {material_props['speed_of_sound']} m/s
  Elastic modulus: {material_props['elastic_modulus']/1e9:.0f} GPa
  Damping coefficient: {material_props['damping']:.3f}
  Piezoelectric: {'Yes' if material_props['piezoelectric'] else 'No'}

Vibrational Modes:
  Fundamental freq: {modes['fundamental']:.2f} Hz
  Longitudinal modes: {modes['longitudinal_modes'][0]:.1f}, {modes['longitudinal_modes'][1]:.1f}, {modes['longitudinal_modes'][2]:.1f} Hz

Device:
  Frequency: {device.frequency:.2f} Hz
  Power: {device.power:.0f} W
  Contact area: {device.contact_area*1e4:.0f} cm²
  Number of devices: {device.num_devices}
  Placement: {device.placement}

Resonance Dynamics:
  Coupling efficiency: {results['coupling_efficiency']:.4f}
  Internal Q-factor: {results['q_factor']:.0f}
  Total amplification: {results['amplification']:.0f}x
  Buildup time: {results['buildup_time']:.2f} s
  Coherence time: {results['coherence_time']:.2f} s
  Intensity in solid: {results['intensity']:.2e} W/m²
"""
    
    ax7.text(0.05, 0.95, params_text, transform=ax7.transAxes, fontsize=8,
             verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    # 8. Results summary
    ax8 = fig.add_subplot(gs[2, 2])
    ax8.axis('off')
    
    initial_mass = block.mass()
    final_mass = results['effective_mass_kg'][-1]
    max_reduction_pct = results['weight_reduction_pct'].max()
    final_reduction_pct = results['weight_reduction_pct'][-1]
    duration = results['time'][-1]
    
    summary_text = f"""RESULTS

Duration: {duration/60:.0f} minutes

Mass Change:
  Original: {initial_mass/1000:.2f} tons
  Final: {final_mass/1000:.2f} tons
  
Weight Reduction:
  Maximum: {max_reduction_pct:.2f}%
  Final: {final_reduction_pct:.2f}%
  Amount: {(initial_mass-final_mass):.0f} kg

Final coupling: {results['coupling'][-1]:.6f}

"""
    
    if final_reduction_pct > 50:
        summary_text += "✓ MAJOR EFFECT\n"
        summary_text += "Block significantly lighter\n"
        summary_text += "Could be moved with\n"
        summary_text += "much less force"
    elif final_reduction_pct > 20:
        summary_text += "✓ SIGNIFICANT EFFECT\n"
        summary_text += "Measurable reduction\n"
        summary_text += "Easier to move"
    elif final_reduction_pct > 5:
        summary_text += "○ MODERATE EFFECT\n"
        summary_text += "Detectable change\n"
    else:
        summary_text += "✗ WEAK EFFECT\n"
        summary_text += "Need higher power\n"
        summary_text += "or better coupling"
    
    ax8.text(0.05, 0.95, summary_text, transform=ax8.transAxes, fontsize=9,
             verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved to {save_path}")
    
    return fig


if __name__ == "__main__":
    print("="*80)
    print("INTERNAL RESONANCE DEVICE MODEL - MASSIVE BLOCK DECOUPLING")
    print("="*80)
    
    # Test: 2.5 ton granite block (typical pyramid block)
    block = BlockParams(
        material='granite',
        length=1.5,  # meters
        width=1.5,
        height=0.7
    )
    
    device = DeviceParams(
        frequency=10.0,  # Hz
        power=1000,  # 1 kW
        contact_area=0.05,  # 50 cm²
        num_devices=1,
        placement='center'
    )
    
    print(f"\nBlock: {block.material.title()}")
    print(f"Dimensions: {block.length}m × {block.width}m × {block.height}m")
    print(f"Mass: {block.mass():.0f} kg ({block.mass()/1000:.2f} tons)")
    print(f"\nDevice: {device.power}W at {device.frequency} Hz")
    print(f"Number of devices: {device.num_devices}")
    
    results = simulate_internal_resonance_decoupling(block, device, duration=600.0)
    
    print(f"\n--- Vibrational Modes ---")
    print(f"Fundamental: {results['modes']['fundamental']:.2f} Hz")
    print(f"Harmonics: {', '.join([f'{h:.1f}' for h in results['modes']['harmonics'][:3]])} Hz")
    
    print(f"\n--- Resonance Parameters ---")
    print(f"Coupling efficiency: {results['coupling_efficiency']:.4f}")
    print(f"Internal Q-factor: {results['q_factor']:.0f}")
    print(f"Amplification: {results['amplification']:.0f}x")
    print(f"Coherence time: {results['coherence_time']:.2f} seconds")
    
    print(f"\n--- Results After 10 Minutes ---")
    print(f"Initial mass: {block.mass()/1000:.2f} tons")
    print(f"Final mass: {results['effective_mass_kg'][-1]/1000:.2f} tons")
    print(f"Weight reduction: {results['weight_reduction_pct'][-1]:.2f}%")
    print(f"Mass reduced by: {results['weight_reduction_kg'][-1]:.0f} kg")
    
    visualize_results(results, save_path='internal_resonance_device.png')
    
    print("\n" + "="*80)
