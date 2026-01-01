"""
Verify Energy and Pressure Calculations
Double-check if the acoustic pressure and energy are physically reasonable
"""

import numpy as np
import matplotlib.pyplot as plt

# Constants
P_REF = 20e-6  # Pa - reference pressure
C_SOUND = 343  # m/s
RHO_AIR = 1.225  # kg/m³

def verify_spl_to_pressure():
    """Verify basic SPL to pressure conversion"""
    print("="*80)
    print("STEP 1: SPL TO PRESSURE CONVERSION")
    print("="*80)
    
    spl = 120  # dB
    pressure = P_REF * 10**(spl / 20)
    
    print(f"\nInput: {spl} dB SPL")
    print(f"Reference pressure: {P_REF*1e6:.2f} µPa")
    print(f"Acoustic pressure amplitude: {pressure:.3f} Pa")
    print(f"Peak-to-peak pressure: {2*pressure:.3f} Pa")
    
    # Intensity
    intensity = pressure**2 / (RHO_AIR * C_SOUND)
    print(f"Acoustic intensity: {intensity:.6f} W/m²")
    
    return pressure, intensity


def verify_standing_wave_amplification():
    """Check if standing wave amplification is being applied correctly"""
    print("\n" + "="*80)
    print("STEP 2: STANDING WAVE AMPLIFICATION")
    print("="*80)
    
    base_pressure = 20  # Pa at 120 dB
    q_factor = 50
    
    print(f"\nBase pressure (no resonance): {base_pressure:.3f} Pa")
    print(f"Q-factor (cavity resonance): {q_factor}")
    
    # CORRECT: Standing wave amplifies AMPLITUDE
    # At resonance, the amplitude can build up by Q factor
    amplified_pressure = base_pressure * q_factor
    
    print(f"\n✓ Amplified pressure amplitude: {amplified_pressure:.3f} Pa")
    print(f"  (This is the pressure amplitude at antinode)")
    
    # BUT: This is only at the antinode position!
    # Average over volume is much less
    
    return amplified_pressure


def verify_internal_resonance():
    """Check internal resonance Q-factor application"""
    print("\n" + "="*80)
    print("STEP 3: INTERNAL RESONANCE")
    print("="*80)
    
    external_pressure = 1000  # Pa from standing wave
    internal_q = 10
    
    print(f"\nExternal pressure on surface: {external_pressure:.3f} Pa")
    print(f"Internal Q-factor: {internal_q}")
    
    # Question: Does internal Q multiply the pressure, or the displacement?
    
    print(f"\nScenario A: Q multiplies DISPLACEMENT")
    print(f"  Displacement ∝ Pressure / Stiffness")
    print(f"  At resonance: Displacement × Q")
    print(f"  Internal stress ∝ Displacement × Stiffness")
    print(f"  Result: Internal stress = Pressure × Q")
    internal_stress_A = external_pressure * internal_q
    print(f"  Internal stress: {internal_stress_A:.0f} Pa")
    
    print(f"\nScenario B: Q multiplies ENERGY")
    print(f"  Energy density ∝ Pressure²")
    print(f"  At resonance: Energy × Q")
    print(f"  Result: Pressure² × Q, so Pressure × √Q")
    internal_pressure_B = external_pressure * np.sqrt(internal_q)
    print(f"  Internal pressure: {internal_pressure_B:.0f} Pa")
    
    print(f"\n⚠️  ISSUE: Current code uses Scenario A (multiply by Q)")
    print(f"   This may be OVERESTIMATING internal effects!")
    
    return internal_stress_A, internal_pressure_B


def realistic_pressure_at_block():
    """Calculate realistic pressure at block location"""
    print("\n" + "="*80)
    print("STEP 4: REALISTIC PRESSURE AT BLOCK")
    print("="*80)
    
    # Start with source
    spl_source = 120  # dB
    p_source = P_REF * 10**(spl_source / 20)
    
    print(f"\nSource SPL: {spl_source} dB")
    print(f"Source pressure: {p_source:.3f} Pa")
    
    # Standing wave in cavity
    # At ANTINODE: pressure amplitude × 2 (constructive interference)
    # With Q=50: additional buildup
    
    # More realistic model:
    # Standing wave creates pressure antinodes where amplitude = 2 × source
    # Q-factor increases amplitude by √Q (energy by Q)
    
    standing_wave_factor = 2.0  # Antinode vs node
    q_buildup = np.sqrt(50)  # Energy accumulation
    
    p_at_antinode = p_source * standing_wave_factor * q_buildup
    
    print(f"\nStanding wave factor (antinode): {standing_wave_factor:.1f}×")
    print(f"Q-factor buildup: {q_buildup:.1f}× (√Q for pressure)")
    print(f"Pressure at antinode: {p_at_antinode:.1f} Pa")
    
    # Block positioned at antinode
    # Internal resonance amplifies DISPLACEMENT by Q_internal
    # But this creates stress/strain, not necessarily acoustic pressure
    
    q_internal = 10
    internal_displacement_factor = q_internal
    
    # The "pressure" felt around block is still ~p_at_antinode
    # The internal stress is higher
    
    print(f"\nExternal acoustic field at block: {p_at_antinode:.1f} Pa")
    print(f"Internal displacement amplification: {internal_displacement_factor}×")
    
    # Internal stress (not acoustic pressure)
    internal_stress = p_at_antinode * internal_displacement_factor
    print(f"Internal mechanical stress: {internal_stress:.0f} Pa")
    
    print(f"\n⚠️  KEY DISTINCTION:")
    print(f"   - External acoustic pressure: ~{p_at_antinode:.0f} Pa")
    print(f"   - Internal mechanical stress: ~{internal_stress:.0f} Pa")
    print(f"   - Danger to humans: External acoustic pressure!")
    
    return p_at_antinode, internal_stress


def compare_methods():
    """Compare original calculation vs corrected"""
    print("\n" + "="*80)
    print("COMPARISON: ORIGINAL VS CORRECTED")
    print("="*80)
    
    spl = 120
    p_base = P_REF * 10**(spl/20)
    
    print(f"\nBase (120 dB): {p_base:.3f} Pa")
    
    # Original method (from code)
    q_standing = 50
    q_internal = 10
    p_original = p_base * q_standing * q_internal  # Multiply both
    
    print(f"\nORIGINAL METHOD:")
    print(f"  Pressure = {p_base:.1f} × {q_standing} × {q_internal}")
    print(f"  Result: {p_original:.0f} Pa ({20*np.log10(p_original/P_REF):.1f} dB)")
    
    # Corrected method
    p_corrected = p_base * 2.0 * np.sqrt(q_standing)
    internal_stress = p_corrected * q_internal
    
    print(f"\nCORRECTED METHOD:")
    print(f"  External pressure = {p_base:.1f} × 2 × √{q_standing}")
    print(f"  Result: {p_corrected:.1f} Pa ({20*np.log10(p_corrected/P_REF):.1f} dB)")
    print(f"  Internal stress: {internal_stress:.0f} Pa (not external field)")
    
    print(f"\n📊 DIFFERENCE:")
    print(f"  Original: {p_original:.0f} Pa")
    print(f"  Corrected: {p_corrected:.1f} Pa")
    print(f"  Ratio: {p_original/p_corrected:.1f}× overestimate")
    
    return p_original, p_corrected


def safety_reassessment():
    """Recalculate safety zones with corrected pressure"""
    print("\n" + "="*80)
    print("SAFETY REASSESSMENT")
    print("="*80)
    
    # Corrected pressure
    p_corrected = 20 * 2 * np.sqrt(50)  # ≈ 283 Pa
    
    print(f"\nCorrected pressure at block: {p_corrected:.1f} Pa")
    print(f"Corrected SPL: {20*np.log10(p_corrected/P_REF):.1f} dB")
    
    # Safety thresholds
    print(f"\nSafety thresholds:")
    print(f"  Death (200 Pa): {p_corrected > 200} - {'YES ⚠️' if p_corrected > 200 else 'NO ✓'}")
    print(f"  Injury (100 Pa): {p_corrected > 100} - {'YES ⚠️' if p_corrected > 100 else 'NO ✓'}")
    print(f"  Pain (20 Pa): {p_corrected > 20} - {'YES ⚠️' if p_corrected > 20 else 'NO ✓'}")
    
    # Approximate danger zones (using 1/√r decay for near field)
    block_radius = 0.025  # 2.5 cm
    
    distances = [1, 3, 5, 10, 15, 20, 30]  # meters
    
    print(f"\nPressure at distance (near-field approximation):")
    print(f"{'Distance':<12} {'Pressure':<15} {'SPL':<12} {'Safety'}")
    print(f"{'-'*60}")
    
    for d in distances:
        decay = np.sqrt(block_radius / d)
        p_at_d = p_corrected * decay
        spl_at_d = 20*np.log10(p_at_d/P_REF)
        
        if p_at_d > 200:
            safety = "💀 LETHAL"
        elif p_at_d > 100:
            safety = "🔴 SEVERE"
        elif p_at_d > 20:
            safety = "🟠 PAIN"
        elif p_at_d > 2:
            safety = "🟡 PPE"
        else:
            safety = "✅ SAFE"
        
        print(f"{d}m ({d*3.281:.1f}ft)  {p_at_d:8.2f} Pa      {spl_at_d:6.1f} dB    {safety}")


def main():
    print("\n" + "="*80)
    print("ACOUSTIC LEVITATION - ENERGY VERIFICATION")
    print("="*80)
    
    pressure, intensity = verify_spl_to_pressure()
    
    amplified = verify_standing_wave_amplification()
    
    stress_a, pressure_b = verify_internal_resonance()
    
    p_ext, p_int = realistic_pressure_at_block()
    
    p_orig, p_corr = compare_methods()
    
    safety_reassessment()
    
    print("\n" + "="*80)
    print("CONCLUSION")
    print("="*80)
    print("""
The original simulation may be OVERESTIMATING acoustic pressure by:

1. Multiplying Q-factors instead of applying to appropriate quantities
2. Confusing internal mechanical stress with external acoustic pressure
3. Not distinguishing between energy density and pressure amplitude

CORRECTED ESTIMATE:
- External acoustic pressure at block: ~280 Pa (149 dB)
- Still dangerous, but death zone reduces to ~1-2 meters
- Much more manageable with remote operation!

RECOMMENDATION:
Need to revise the standing_wave_field.py simulation with proper
amplitude vs energy vs displacement distinctions.
""")


if __name__ == "__main__":
    main()
