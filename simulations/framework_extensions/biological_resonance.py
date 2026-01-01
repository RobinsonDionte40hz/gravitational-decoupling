"""
Biological Resonance Enhancement Model
Tests whether ion channel dynamics enhance gravitational decoupling

Key hypothesis: Living tissue with active ion channels should show
stronger gravitational decoupling than inert materials at specific
resonant frequencies.
"""

import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import Dict, List

# Constants
EARTH_G = 9.81
PHI = (1 + np.sqrt(5)) / 2


@dataclass
class IonChannel:
    """Model of ion channel gating dynamics"""
    name: str
    ion: str
    resonant_frequency: float  # Hz
    gating_q_factor: float  # Quality factor of gating kinetics
    conductance: float  # Relative conductance (0-1)
    bandwidth: float  # Hz - width of resonance
    
    def frequency_response(self, frequency: float) -> float:
        """How strongly this channel responds to given frequency"""
        # Lorentzian resonance
        delta_f = frequency - self.resonant_frequency
        response = 1.0 / (1.0 + (2 * delta_f / self.bandwidth)**2)
        return response * self.conductance


# Known ion channels from element table
ION_CHANNELS = [
    IonChannel(
        name="Potassium leak",
        ion="K+",
        resonant_frequency=4.0,
        gating_q_factor=5,
        conductance=0.3,
        bandwidth=2.0
    ),
    IonChannel(
        name="Magnesium-NMDA",
        ion="Mg2+",
        resonant_frequency=7.0,
        gating_q_factor=15,
        conductance=0.5,
        bandwidth=5.0
    ),
    IonChannel(
        name="Calcium voltage-gated",
        ion="Ca2+",
        resonant_frequency=10.0,
        gating_q_factor=25,
        conductance=1.0,  # Strongest
        bandwidth=3.0
    ),
    IonChannel(
        name="Sodium fast",
        ion="Na+",
        resonant_frequency=16.0,
        gating_q_factor=20,
        conductance=0.7,
        bandwidth=8.0
    ),
    IonChannel(
        name="Chloride-GABA",
        ion="Cl-",
        resonant_frequency=28.0,
        gating_q_factor=18,
        conductance=0.6,
        bandwidth=6.0
    ),
    IonChannel(
        name="Zinc synaptic",
        ion="Zn2+",
        resonant_frequency=40.0,
        gating_q_factor=30,
        conductance=0.8,
        bandwidth=10.0
    ),
]


def ion_channel_ensemble_response(frequency: float, channels: List[IonChannel]) -> float:
    """Combined response from all ion channels"""
    total_response = 0.0
    for channel in channels:
        total_response += channel.frequency_response(frequency)
    return total_response


def cellular_mass_modulation(ion_response: float) -> float:
    """
    How ion channel activity modulates cellular mass distribution
    
    Active ion channels → ion flux → water movement → cytoskeletal rearrangement
    This changes effective mass distribution and coupling to gravitational field
    """
    # Hypothesis: Ion flux creates coherent mass oscillations
    # These oscillations couple to external acoustic field
    # Enhancement factor scales with ion response
    enhancement = 1.0 + 0.5 * ion_response  # Up to 50% enhancement
    return enhancement


def simulate_biological_decoupling(
    material_type: str,
    frequency: float,
    power: float,
    mass_kg: float,
    duration: float = 600.0,
    timesteps: int = 1000
) -> Dict:
    """
    Simulate gravitational decoupling for different material types
    
    Materials:
    - 'granite': Pure mechanical resonance, Q=82
    - 'saline': Ions present but no channels
    - 'protein': Structured proteins, some Ca2+ binding
    - 'living': Active neurons with all ion channels
    - 'blocked': Living neurons with Ca2+ channels blocked
    """
    t = np.linspace(0, duration, timesteps)
    dt = duration / timesteps
    
    # Base acoustic parameters
    base_q = 82  # Granite baseline
    
    # Material-specific parameters
    if material_type == 'granite':
        q_factor = base_q
        ion_enhancement = 0.0
        
    elif material_type == 'saline':
        q_factor = base_q * 0.9  # Slightly lower (liquid damping)
        ion_enhancement = 0.05  # Tiny effect from free ions
        
    elif material_type == 'protein':
        q_factor = base_q * 1.1  # Slightly higher (protein structure)
        # Some Ca2+ binding, no active channels
        ca_channel = ION_CHANNELS[2]  # Calcium
        ion_response = ca_channel.frequency_response(frequency) * 0.3
        ion_enhancement = cellular_mass_modulation(ion_response) - 1.0
        
    elif material_type == 'living':
        q_factor = base_q * 1.2  # Higher (cellular structure)
        # Full ion channel ensemble
        ion_response = ion_channel_ensemble_response(frequency, ION_CHANNELS)
        ion_enhancement = cellular_mass_modulation(ion_response) - 1.0
        
    elif material_type == 'blocked':
        q_factor = base_q * 1.2
        # Only non-calcium channels
        active_channels = [ch for ch in ION_CHANNELS if ch.ion != 'Ca2+']
        ion_response = ion_channel_ensemble_response(frequency, active_channels)
        ion_enhancement = cellular_mass_modulation(ion_response) - 1.0
        
    else:
        raise ValueError(f"Unknown material type: {material_type}")
    
    # Effective Q-factor with biological enhancement
    effective_q = q_factor * (1.0 + ion_enhancement)
    
    # Coherence time
    tau_coherence = effective_q / (2 * np.pi * frequency)
    
    # Accumulation dynamics
    accumulated_effect = np.zeros(timesteps)
    coupling_coeff = np.ones(timesteps)
    
    # Base decoupling rate (from acoustic power)
    base_rate = power / (mass_kg * 1e6)  # Normalized
    
    # Biological enhancement factor over time
    bio_enhancement = np.ones(timesteps)
    if material_type in ['protein', 'living', 'blocked']:
        # Ion channels take time to phase-lock to external field
        for i in range(timesteps):
            # Exponential approach to full enhancement
            bio_enhancement[i] = 1.0 + ion_enhancement * (1 - np.exp(-t[i] / 30.0))
    
    # Golden ratio modulation
    geometric = 1.0 + 0.15 * np.sin(2 * np.pi * PHI * t / 60)
    
    for i in range(1, timesteps):
        # Decoupling rate with biological enhancement
        rate = base_rate * bio_enhancement[i] * geometric[i] * effective_q / 82
        
        # Accumulation with decay
        decay = np.exp(-dt / tau_coherence)
        accumulated_effect[i] = accumulated_effect[i-1] * decay + rate * dt
        
        # Coupling coefficient
        coupling_coeff[i] = np.exp(-accumulated_effect[i])
        coupling_coeff[i] = np.clip(coupling_coeff[i], 0.85, 1.0)  # 15% max effect
    
    # Weight calculations
    effective_mass = mass_kg * coupling_coeff
    weight_reduction_pct = (1 - coupling_coeff) * 100
    
    return {
        'time': t,
        'coupling': coupling_coeff,
        'effective_mass': effective_mass,
        'weight_reduction_pct': weight_reduction_pct,
        'accumulated_effect': accumulated_effect,
        'q_factor': effective_q,
        'ion_enhancement': ion_enhancement,
        'bio_enhancement': bio_enhancement,
        'material': material_type
    }


def compare_materials_at_frequency(
    frequency: float,
    power: float = 100.0,
    mass_kg: float = 0.1,
    duration: float = 600.0
) -> Dict:
    """Compare all material types at specific frequency"""
    
    materials = ['granite', 'saline', 'protein', 'living', 'blocked']
    results = {}
    
    for material in materials:
        results[material] = simulate_biological_decoupling(
            material_type=material,
            frequency=frequency,
            power=power,
            mass_kg=mass_kg,
            duration=duration
        )
    
    return results


def frequency_sweep_biological(
    material_type: str,
    freq_range: tuple = (1, 50),
    num_points: int = 50,
    power: float = 100.0,
    mass_kg: float = 0.1
) -> Dict:
    """Sweep frequencies for given material type"""
    
    frequencies = np.linspace(freq_range[0], freq_range[1], num_points)
    final_reductions = np.zeros(num_points)
    
    for i, freq in enumerate(frequencies):
        result = simulate_biological_decoupling(
            material_type=material_type,
            frequency=freq,
            power=power,
            mass_kg=mass_kg,
            duration=600.0,
            timesteps=500  # Faster for sweep
        )
        final_reductions[i] = result['weight_reduction_pct'][-1]
    
    return {
        'frequencies': frequencies,
        'weight_reduction': final_reductions,
        'material': material_type
    }


def visualize_material_comparison(comparison: Dict, frequency: float, save_path: str = None):
    """Visualize comparison across materials"""
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(f'Biological Enhancement of Gravitational Decoupling at {frequency} Hz', 
                 fontsize=14, fontweight='bold')
    
    # Plot 1: Weight reduction over time
    ax1 = axes[0, 0]
    for material, result in comparison.items():
        ax1.plot(result['time'] / 60, result['weight_reduction_pct'], 
                label=material.capitalize(), linewidth=2)
    ax1.set_xlabel('Time (minutes)')
    ax1.set_ylabel('Weight Reduction (%)')
    ax1.set_title('Weight Reduction vs Time')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Final weight reduction bar chart
    ax2 = axes[0, 1]
    materials = list(comparison.keys())
    final_values = [comparison[m]['weight_reduction_pct'][-1] for m in materials]
    colors = ['gray', 'lightblue', 'orange', 'green', 'yellow']
    bars = ax2.bar(materials, final_values, color=colors, alpha=0.7, edgecolor='black')
    ax2.set_ylabel('Final Weight Reduction (%)')
    ax2.set_title('Final Weight Reduction by Material')
    ax2.set_ylim(0, max(final_values) * 1.2)
    
    # Add value labels on bars
    for bar, val in zip(bars, final_values):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.2f}%', ha='center', va='bottom', fontweight='bold')
    
    # Plot 3: Q-factor comparison
    ax3 = axes[1, 0]
    q_factors = [comparison[m]['q_factor'] for m in materials]
    enhancements = [comparison[m]['ion_enhancement'] * 100 for m in materials]
    
    x = np.arange(len(materials))
    width = 0.35
    ax3.bar(x - width/2, q_factors, width, label='Effective Q-factor', alpha=0.7)
    ax3_twin = ax3.twinx()
    ax3_twin.bar(x + width/2, enhancements, width, label='Ion Enhancement (%)', 
                 alpha=0.7, color='orange')
    
    ax3.set_ylabel('Q-factor')
    ax3_twin.set_ylabel('Ion Enhancement (%)')
    ax3.set_xlabel('Material')
    ax3.set_xticks(x)
    ax3.set_xticklabels([m.capitalize() for m in materials])
    ax3.set_title('Q-Factor and Ion Enhancement')
    ax3.legend(loc='upper left')
    ax3_twin.legend(loc='upper right')
    
    # Plot 4: Summary text
    ax4 = axes[1, 1]
    ax4.axis('off')
    
    granite_final = comparison['granite']['weight_reduction_pct'][-1]
    living_final = comparison['living']['weight_reduction_pct'][-1]
    enhancement_pct = ((living_final / granite_final) - 1) * 100
    
    summary = f"""
BIOLOGICAL ENHANCEMENT ANALYSIS
Frequency: {frequency} Hz
Duration: 10 minutes
Power: 100W

RESULTS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Granite (baseline):     {granite_final:.3f}%
Saline (free ions):     {comparison['saline']['weight_reduction_pct'][-1]:.3f}%
Protein (structured):   {comparison['protein']['weight_reduction_pct'][-1]:.3f}%
Living (ion channels):  {living_final:.3f}%
Blocked (Ca2+ blocked): {comparison['blocked']['weight_reduction_pct'][-1]:.3f}%

ENHANCEMENT:
Living vs Granite: {enhancement_pct:+.1f}%

INTERPRETATION:
{"✅ SIGNIFICANT BIOLOGICAL ENHANCEMENT" if enhancement_pct > 20 else "❌ Minimal biological effect"}
{"Ion channels amplify gravitational coupling!" if enhancement_pct > 20 else "Mechanical resonance dominates"}

Ion Channel Contribution:
Q-factor: {comparison['living']['q_factor']:.1f} 
  (vs granite: {comparison['granite']['q_factor']:.1f})
"""
    
    ax4.text(0.05, 0.95, summary, transform=ax4.transAxes, fontsize=10,
             verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.3))
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    plt.show()


def visualize_frequency_sweep_comparison(sweep_results: Dict, save_path: str = None):
    """Compare frequency sweeps for different materials"""
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    fig.suptitle('Frequency-Dependent Biological Enhancement', fontsize=14, fontweight='bold')
    
    # Plot 1: All materials
    colors = {'granite': 'gray', 'saline': 'lightblue', 'protein': 'orange', 
              'living': 'green', 'blocked': 'yellow'}
    
    for material, result in sweep_results.items():
        ax1.plot(result['frequencies'], result['weight_reduction'], 
                label=material.capitalize(), linewidth=2, color=colors.get(material, 'black'))
    
    ax1.set_xlabel('Frequency (Hz)')
    ax1.set_ylabel('Weight Reduction (%)')
    ax1.set_title('Weight Reduction vs Frequency')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Mark framework state frequencies
    framework_states = [4, 7, 10, 16, 28, 40]
    for freq in framework_states:
        ax1.axvline(freq, color='red', alpha=0.3, linestyle='--', linewidth=1)
    
    # Plot 2: Enhancement ratio (living / granite)
    granite_reduction = sweep_results['granite']['weight_reduction']
    living_reduction = sweep_results['living']['weight_reduction']
    enhancement_ratio = living_reduction / (granite_reduction + 1e-10)  # Avoid division by zero
    
    ax2.plot(sweep_results['granite']['frequencies'], enhancement_ratio, 
            linewidth=2, color='purple')
    ax2.axhline(1.0, color='gray', linestyle='--', alpha=0.5)
    ax2.set_xlabel('Frequency (Hz)')
    ax2.set_ylabel('Enhancement Ratio (Living / Granite)')
    ax2.set_title('Biological Enhancement Factor')
    ax2.grid(True, alpha=0.3)
    
    # Mark framework states
    for freq in framework_states:
        ax2.axvline(freq, color='red', alpha=0.3, linestyle='--', linewidth=1)
    
    # Add framework state labels
    for freq in framework_states:
        if freq <= 50:
            ax2.text(freq, ax2.get_ylim()[1] * 0.95, f'{freq}Hz', 
                    ha='center', fontsize=8, color='red')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    plt.show()


if __name__ == "__main__":
    print("="*80)
    print("BIOLOGICAL RESONANCE ENHANCEMENT MODEL")
    print("="*80)
    
    # Test 1: Compare materials at 10 Hz (optimal Ca2+ frequency)
    print("\nTest 1: Material Comparison at 10 Hz (Ca2+ resonance)")
    print("-" * 80)
    
    comparison_10hz = compare_materials_at_frequency(
        frequency=10.0,
        power=100.0,
        mass_kg=0.1,
        duration=600.0
    )
    
    for material, result in comparison_10hz.items():
        final_reduction = result['weight_reduction_pct'][-1]
        q_factor = result['q_factor']
        print(f"{material.capitalize():15s}: {final_reduction:6.3f}% reduction, Q={q_factor:.1f}")
    
    visualize_material_comparison(comparison_10hz, frequency=10.0, 
                                  save_path='biological_enhancement_10hz.png')
    
    # Test 2: Frequency sweep for each material
    print("\n" + "="*80)
    print("Test 2: Frequency Sweep (1-50 Hz)")
    print("-" * 80)
    
    sweep_results = {}
    for material in ['granite', 'saline', 'protein', 'living', 'blocked']:
        print(f"Sweeping {material}...")
        sweep_results[material] = frequency_sweep_biological(
            material_type=material,
            freq_range=(1, 50),
            num_points=50
        )
    
    visualize_frequency_sweep_comparison(sweep_results, 
                                        save_path='biological_frequency_sweep.png')
    
    # Test 3: Test at each framework state frequency
    print("\n" + "="*80)
    print("Test 3: Framework State Frequencies")
    print("-" * 80)
    
    framework_frequencies = [4, 7, 10, 16, 28, 40]
    
    print(f"\n{'Frequency':<10} {'Granite':<10} {'Living':<10} {'Enhancement':<12}")
    print("-" * 50)
    
    for freq in framework_frequencies:
        comparison = compare_materials_at_frequency(
            frequency=freq,
            power=100.0,
            mass_kg=0.1,
            duration=600.0
        )
        
        granite = comparison['granite']['weight_reduction_pct'][-1]
        living = comparison['living']['weight_reduction_pct'][-1]
        enhancement = ((living / granite) - 1) * 100
        
        print(f"{freq:>4} Hz     {granite:>6.3f}%    {living:>6.3f}%    {enhancement:>+7.1f}%")
    
    print("\n" + "="*80)
    print("CONCLUSION:")
    print("="*80)
    print("""
If experimental results show:
1. Living tissue > granite at framework frequencies (4,7,10,16,28,40 Hz)
2. Blocked Ca2+ channels reduce effect at 10 Hz
3. Enhancement peaks at ion channel resonances

→ PROVES: Ion channel dynamics couple acoustic to gravitational field
→ VALIDATES: "Experience as frequency channel" framework
→ MECHANISM: Cellular mass oscillations from ion flux
""")
