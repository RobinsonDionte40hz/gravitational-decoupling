"""
Atomic Frequency Coupling Models
Test different physical models to predict ion channel resonance frequencies
from atomic properties

Goal: Determine if frequency channels are emergent from atomic properties
or if atoms tune into pre-existing fundamental channels
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from dataclasses import dataclass
from typing import Dict, List

# Physical constants
AMU_TO_KG = 1.66054e-27  # kg
E_CHARGE = 1.602e-19  # Coulombs
EPSILON_0 = 8.854e-12  # F/m
H_BAR = 1.055e-34  # J·s
K_B = 1.381e-23  # J/K


@dataclass
class IonData:
    """Properties of biologically relevant ions"""
    symbol: str
    mass_amu: float
    ionic_radius_pm: float  # picometers
    charge: int
    electron_config: str
    orbital_type: str  # s, p, d, f
    measured_freq_hz: float  # Measured biological coupling
    freq_range: tuple  # (min, max) Hz
    confidence: str  # HIGH, MEDIUM, LOW
    
    @property
    def mass_kg(self):
        return self.mass_amu * AMU_TO_KG
    
    @property
    def radius_m(self):
        return self.ionic_radius_pm * 1e-12
    
    @property
    def charge_density(self):
        """Charge per volume (C/m³)"""
        volume = (4/3) * np.pi * self.radius_m**3
        return abs(self.charge) * E_CHARGE / volume
    
    @property
    def charge_to_mass_ratio(self):
        """Charge/mass ratio"""
        return abs(self.charge) / self.mass_amu
    
    @property
    def surface_charge_density(self):
        """Charge per surface area"""
        area = 4 * np.pi * self.radius_m**2
        return abs(self.charge) * E_CHARGE / area


# Measured ion channel data
IONS = [
    IonData("K+", 39.10, 138, +1, "[Ar]", "s", 6.0, (4, 8), "HIGH"),
    IonData("Mg2+", 24.31, 72, +2, "[Ne]", "s", 9.5, (7, 12), "HIGH"),
    IonData("Ca2+", 40.08, 100, +2, "[Ar]", "s", 15.0, (10, 20), "HIGH"),
    IonData("Na+", 22.99, 102, +1, "[Ne]", "s", 22.5, (15, 30), "MEDIUM"),
    IonData("Cl-", 35.45, 181, -1, "[Ar]", "p", 27.5, (25, 30), "MEDIUM"),
    IonData("Zn2+", 65.38, 74, +2, "[Ar]3d10", "d", 35.0, (30, 40), "HIGH"),
    IonData("Cu2+", 63.55, 73, +2, "[Ar]3d9", "d", 22.5, (15, 30), "MEDIUM"),
    IonData("Fe2+", 55.85, 78, +2, "[Ar]3d6", "d", 9.5, (4, 15), "MEDIUM"),
]


def model_mass_spring(ion: IonData, k_scale=1e6) -> float:
    """
    Model A: Simple mass-spring oscillator
    f = (1/2π) × sqrt(k/m)
    
    Assumes spring constant k scales with charge and inverse radius
    """
    # Electrostatic binding: k ~ Z × e² / r²
    k = k_scale * abs(ion.charge) * E_CHARGE**2 / ion.radius_m**2
    omega = np.sqrt(k / ion.mass_kg)
    freq = omega / (2 * np.pi)
    return freq


def model_charge_density(ion: IonData, scale=1e-26) -> float:
    """
    Model B: Charge density determines frequency
    Higher charge density → faster oscillations
    """
    freq = scale * ion.charge_density
    return freq


def model_plasma_frequency(ion: IonData, concentration=0.1) -> float:
    """
    Model C: Plasma frequency in ionic solution
    ω_p = sqrt(n × e² / (ε₀ × m))
    
    concentration: molar concentration
    """
    # Convert molar to number density
    avogadro = 6.022e23
    n = concentration * avogadro * 1000  # particles/m³
    
    omega_p = np.sqrt(n * E_CHARGE**2 / (EPSILON_0 * ion.mass_kg))
    freq = omega_p / (2 * np.pi)
    return freq


def model_electron_orbital(ion: IonData) -> float:
    """
    Model D: Electron orbital harmonics
    Different orbital types have different characteristic frequencies
    """
    # Base frequency from Rydberg formula scaled to Hz range
    rydberg_const = 1.097e7  # m^-1
    
    # Orbital type factors (empirical - to be fitted)
    orbital_factors = {
        's': 1.0,   # Simple spherical
        'p': 1.5,   # Angular momentum
        'd': 3.0,   # Complex d-orbitals
        'f': 4.0    # Even more complex
    }
    
    factor = orbital_factors.get(ion.orbital_type, 1.0)
    
    # Scale to biological frequency range
    # Use charge state and orbital complexity
    freq = factor * abs(ion.charge) * 10  # Empirical scaling
    
    return freq


def model_combined_linear(params, mass, charge, radius, orbital_complexity):
    """
    Combined linear model: f = a×(Z/m) + b×(Z/r) + c×orbital + d
    """
    a, b, c, d = params
    return a * (charge/mass) + b * (charge/radius) + c * orbital_complexity + d


def analyze_all_models():
    """Test all models against measured data"""
    
    print("="*80)
    print("ATOMIC FREQUENCY COUPLING - MODEL PREDICTIONS")
    print("="*80)
    
    results = {}
    
    # Extract measured data
    symbols = [ion.symbol for ion in IONS]
    measured = np.array([ion.measured_freq_hz for ion in IONS])
    
    print("\n📊 MEASURED DATA:")
    print(f"{'Ion':<8} {'Mass (amu)':<12} {'Radius (pm)':<12} {'Charge':<8} {'Orbital':<10} {'Measured (Hz)':<15}")
    print("-"*80)
    for ion in IONS:
        print(f"{ion.symbol:<8} {ion.mass_amu:<12.2f} {ion.ionic_radius_pm:<12.0f} "
              f"{ion.charge:+3d}      {ion.orbital_type:<10} {ion.measured_freq_hz:<15.1f}")
    
    # Model A: Mass-Spring
    print("\n" + "="*80)
    print("MODEL A: MASS-SPRING OSCILLATOR")
    print("="*80)
    
    # Try different k_scale values to find best fit
    best_k = None
    best_error = float('inf')
    
    for k_scale in np.logspace(4, 8, 50):
        pred = np.array([model_mass_spring(ion, k_scale) for ion in IONS])
        error = np.mean((pred - measured)**2)
        if error < best_error:
            best_error = error
            best_k = k_scale
    
    pred_mass_spring = np.array([model_mass_spring(ion, best_k) for ion in IONS])
    rmse_mass_spring = np.sqrt(np.mean((pred_mass_spring - measured)**2))
    
    print(f"Best k_scale: {best_k:.2e}")
    print(f"RMSE: {rmse_mass_spring:.2f} Hz")
    print("\nPredictions:")
    for ion, pred in zip(IONS, pred_mass_spring):
        error_pct = abs(pred - ion.measured_freq_hz) / ion.measured_freq_hz * 100
        print(f"  {ion.symbol:<8} Predicted: {pred:>8.1f} Hz  |  Measured: {ion.measured_freq_hz:>6.1f} Hz  |  Error: {error_pct:>5.1f}%")
    
    results['mass_spring'] = {'predictions': pred_mass_spring, 'rmse': rmse_mass_spring}
    
    # Model B: Charge Density
    print("\n" + "="*80)
    print("MODEL B: CHARGE DENSITY")
    print("="*80)
    
    best_scale = None
    best_error = float('inf')
    
    for scale in np.logspace(-28, -24, 50):
        pred = np.array([model_charge_density(ion, scale) for ion in IONS])
        error = np.mean((pred - measured)**2)
        if error < best_error:
            best_error = error
            best_scale = scale
    
    pred_charge_density = np.array([model_charge_density(ion, best_scale) for ion in IONS])
    rmse_charge_density = np.sqrt(np.mean((pred_charge_density - measured)**2))
    
    print(f"Best scale: {best_scale:.2e}")
    print(f"RMSE: {rmse_charge_density:.2f} Hz")
    print("\nPredictions:")
    for ion, pred in zip(IONS, pred_charge_density):
        error_pct = abs(pred - ion.measured_freq_hz) / ion.measured_freq_hz * 100
        print(f"  {ion.symbol:<8} Predicted: {pred:>8.1f} Hz  |  Measured: {ion.measured_freq_hz:>6.1f} Hz  |  Error: {error_pct:>5.1f}%")
    
    results['charge_density'] = {'predictions': pred_charge_density, 'rmse': rmse_charge_density}
    
    # Model C: Plasma Frequency
    print("\n" + "="*80)
    print("MODEL C: PLASMA FREQUENCY")
    print("="*80)
    
    best_conc = None
    best_error = float('inf')
    
    for conc in np.logspace(-15, -8, 50):
        pred = np.array([model_plasma_frequency(ion, conc) for ion in IONS])
        error = np.mean((pred - measured)**2)
        if error < best_error:
            best_error = error
            best_conc = conc
    
    pred_plasma = np.array([model_plasma_frequency(ion, best_conc) for ion in IONS])
    rmse_plasma = np.sqrt(np.mean((pred_plasma - measured)**2))
    
    print(f"Best concentration: {best_conc:.2e} M")
    print(f"RMSE: {rmse_plasma:.2f} Hz")
    print("\nPredictions:")
    for ion, pred in zip(IONS, pred_plasma):
        error_pct = abs(pred - ion.measured_freq_hz) / ion.measured_freq_hz * 100
        print(f"  {ion.symbol:<8} Predicted: {pred:>8.1f} Hz  |  Measured: {ion.measured_freq_hz:>6.1f} Hz  |  Error: {error_pct:>5.1f}%")
    
    results['plasma'] = {'predictions': pred_plasma, 'rmse': rmse_plasma}
    
    # Model D: Electron Orbital
    print("\n" + "="*80)
    print("MODEL D: ELECTRON ORBITAL HARMONICS")
    print("="*80)
    
    pred_orbital = np.array([model_electron_orbital(ion) for ion in IONS])
    rmse_orbital = np.sqrt(np.mean((pred_orbital - measured)**2))
    
    print(f"RMSE: {rmse_orbital:.2f} Hz")
    print("\nPredictions:")
    for ion, pred in zip(IONS, pred_orbital):
        error_pct = abs(pred - ion.measured_freq_hz) / ion.measured_freq_hz * 100
        print(f"  {ion.symbol:<8} Predicted: {pred:>8.1f} Hz  |  Measured: {ion.measured_freq_hz:>6.1f} Hz  |  Error: {error_pct:>5.1f}%")
    
    results['orbital'] = {'predictions': pred_orbital, 'rmse': rmse_orbital}
    
    # Summary
    print("\n" + "="*80)
    print("MODEL COMPARISON")
    print("="*80)
    print(f"{'Model':<25} {'RMSE (Hz)':<15} {'Relative Performance':<20}")
    print("-"*80)
    
    best_rmse = min(r['rmse'] for r in results.values())
    for name, result in results.items():
        relative = result['rmse'] / best_rmse
        stars = "★" * int(5 / relative) if relative > 0 else "★★★★★"
        print(f"{name:<25} {result['rmse']:<15.2f} {stars:<20}")
    
    return results, IONS, measured


def visualize_results(results, ions, measured):
    """Create comprehensive visualization of all models"""
    
    fig = plt.figure(figsize=(16, 12))
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
    
    # Main comparison plot
    ax_main = fig.add_subplot(gs[0, :])
    x = np.arange(len(ions))
    width = 0.15
    
    ax_main.bar(x - 2*width, measured, width, label='Measured', color='black', alpha=0.7)
    ax_main.bar(x - width, results['mass_spring']['predictions'], width, 
                label='Mass-Spring', alpha=0.7)
    ax_main.bar(x, results['charge_density']['predictions'], width, 
                label='Charge Density', alpha=0.7)
    ax_main.bar(x + width, results['plasma']['predictions'], width, 
                label='Plasma Freq', alpha=0.7)
    ax_main.bar(x + 2*width, results['orbital']['predictions'], width, 
                label='Orbital', alpha=0.7)
    
    ax_main.set_xlabel('Ion')
    ax_main.set_ylabel('Frequency (Hz)')
    ax_main.set_title('Model Predictions vs Measured Frequencies', fontweight='bold', fontsize=14)
    ax_main.set_xticks(x)
    ax_main.set_xticklabels([ion.symbol for ion in ions])
    ax_main.legend()
    ax_main.grid(True, alpha=0.3, axis='y')
    
    # Scatter plots for each model
    model_names = ['mass_spring', 'charge_density', 'plasma', 'orbital']
    model_titles = ['Mass-Spring', 'Charge Density', 'Plasma Frequency', 'Orbital Harmonics']
    
    for idx, (name, title) in enumerate(zip(model_names, model_titles)):
        ax = fig.add_subplot(gs[1 + idx//2, idx%2])
        pred = results[name]['predictions']
        
        ax.scatter(measured, pred, s=100, alpha=0.6)
        
        # Perfect prediction line
        min_val = min(measured.min(), pred.min())
        max_val = max(measured.max(), pred.max())
        ax.plot([min_val, max_val], [min_val, max_val], 'r--', alpha=0.5, label='Perfect')
        
        # Labels
        for ion, m, p in zip(ions, measured, pred):
            ax.annotate(ion.symbol, (m, p), fontsize=8, alpha=0.7)
        
        ax.set_xlabel('Measured (Hz)')
        ax.set_ylabel('Predicted (Hz)')
        ax.set_title(f'{title} (RMSE: {results[name]["rmse"]:.1f} Hz)')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    # Property correlations
    ax_corr = fig.add_subplot(gs[2, 2])
    
    # Test simple correlations
    mass_arr = np.array([ion.mass_amu for ion in ions])
    radius_arr = np.array([ion.ionic_radius_pm for ion in ions])
    charge_arr = np.array([abs(ion.charge) for ion in ions])
    
    corr_mass = np.corrcoef(mass_arr, measured)[0, 1]
    corr_radius = np.corrcoef(radius_arr, measured)[0, 1]
    corr_charge = np.corrcoef(charge_arr, measured)[0, 1]
    corr_charge_mass = np.corrcoef(charge_arr/mass_arr, measured)[0, 1]
    
    correlations = {
        'Mass': corr_mass,
        'Radius': corr_radius,
        'Charge': corr_charge,
        'Charge/Mass': corr_charge_mass
    }
    
    bars = ax_corr.bar(correlations.keys(), correlations.values(), alpha=0.7)
    ax_corr.axhline(0, color='black', linewidth=0.5)
    ax_corr.set_ylabel('Correlation Coefficient')
    ax_corr.set_title('Property Correlations', fontweight='bold')
    ax_corr.set_ylim(-1, 1)
    ax_corr.grid(True, alpha=0.3, axis='y')
    
    # Color bars by strength
    for bar, val in zip(bars, correlations.values()):
        if abs(val) > 0.5:
            bar.set_color('green')
        elif abs(val) > 0.3:
            bar.set_color('yellow')
        else:
            bar.set_color('red')
    
    plt.suptitle('Atomic Frequency Coupling Analysis', fontsize=16, fontweight='bold', y=0.995)
    plt.savefig('outputs/visualizations/atomic_frequency_models.png', dpi=300, bbox_inches='tight')
    print(f"\n✓ Visualization saved to outputs/visualizations/atomic_frequency_models.png")
    
    return correlations


def test_orbital_type_effect(ions, measured):
    """Test if orbital type (s vs d) matters"""
    
    print("\n" + "="*80)
    print("ORBITAL TYPE ANALYSIS")
    print("="*80)
    
    s_ions = [(ion, m) for ion, m in zip(ions, measured) if ion.orbital_type == 's']
    d_ions = [(ion, m) for ion, m in zip(ions, measured) if ion.orbital_type == 'd']
    p_ions = [(ion, m) for ion, m in zip(ions, measured) if ion.orbital_type == 'p']
    
    print(f"\ns-orbital ions (n={len(s_ions)}):")
    for ion, freq in s_ions:
        print(f"  {ion.symbol:<8} {freq:>6.1f} Hz")
    
    print(f"\nd-orbital ions (n={len(d_ions)}):")
    for ion, freq in d_ions:
        print(f"  {ion.symbol:<8} {freq:>6.1f} Hz")
    
    print(f"\np-orbital ions (n={len(p_ions)}):")
    for ion, freq in p_ions:
        print(f"  {ion.symbol:<8} {freq:>6.1f} Hz")
    
    if len(s_ions) > 0 and len(d_ions) > 0:
        s_mean = np.mean([f for _, f in s_ions])
        d_mean = np.mean([f for _, f in d_ions])
        
        print(f"\nMean frequency:")
        print(f"  s-orbitals: {s_mean:.1f} Hz")
        print(f"  d-orbitals: {d_mean:.1f} Hz")
        print(f"  Ratio (d/s): {d_mean/s_mean:.2f}×")
        
        if d_mean > s_mean * 1.5:
            print("\n→ d-orbital ions show significantly higher frequencies!")
            print("→ Electron orbital structure MATTERS")


if __name__ == "__main__":
    # Run analysis
    results, ions, measured = analyze_all_models()
    
    # Visualize
    correlations = visualize_results(results, ions, measured)
    
    # Test orbital effect
    test_orbital_type_effect(ions, measured)
    
    # Final conclusions
    print("\n" + "="*80)
    print("CONCLUSIONS")
    print("="*80)
    
    best_model = min(results.items(), key=lambda x: x[1]['rmse'])
    print(f"\n✓ Best simple model: {best_model[0].upper()} (RMSE: {best_model[1]['rmse']:.2f} Hz)")
    
    print("\n📊 Key Findings:")
    print(f"  • Strongest correlation: {max(correlations.items(), key=lambda x: abs(x[1]))}")
    
    if best_model[1]['rmse'] < 5:
        print("\n→ EMERGENT: Atomic properties predict frequencies well")
        print("→ Channels arise from matter's oscillation properties")
    elif best_model[1]['rmse'] < 10:
        print("\n→ PARTIAL: Some correlation but significant unexplained variance")
        print("→ May indicate co-creative mechanism")
    else:
        print("\n→ FUNDAMENTAL: No simple atomic model explains frequencies")
        print("→ Atoms may tune into pre-existing channel structure")
    
    print("\n" + "="*80)
