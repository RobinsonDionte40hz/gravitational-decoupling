"""
Safety Distance Analysis for Acoustic Levitation Device
Calculate danger zones and safe operating distances
"""

import numpy as np
import matplotlib.pyplot as plt

# Constants
P_REF = 20e-6  # Pa
C_SOUND = 343  # m/s
RHO_AIR = 1.225  # kg/m³

def spl_from_pressure(pressure_pa):
    """Convert pressure (Pa) to SPL (dB)"""
    return 20 * np.log10(pressure_pa / P_REF)

def pressure_from_spl(spl_db):
    """Convert SPL (dB) to pressure (Pa)"""
    return P_REF * 10**(spl_db / 20)

def acoustic_pressure_at_distance(
    source_pressure_pa,
    source_radius_m,
    distance_m,
    frequency_hz=10
):
    """
    Acoustic pressure decay with distance
    
    Near field (close): complicated interference patterns
    Far field (>1 wavelength): 1/r decay for point source
    
    At 10 Hz: wavelength = 34.3m, so we're in near-field for construction distances
    Use spherical spreading with near-field correction
    """
    wavelength = C_SOUND / frequency_hz
    
    # Near field extends to ~2-3 wavelengths for resonant source
    near_field_distance = 2 * wavelength
    
    if distance_m < source_radius_m:
        # Inside source - use source pressure
        return source_pressure_pa
    
    elif distance_m < near_field_distance:
        # Near field - slower decay, standing wave effects
        # Approximate as 1/sqrt(r) decay
        decay_factor = np.sqrt(source_radius_m / distance_m)
        return source_pressure_pa * decay_factor
    
    else:
        # Far field - 1/r decay (inverse square law for intensity = 1/r² for pressure)
        decay_factor = source_radius_m / distance_m
        return source_pressure_pa * decay_factor

def safety_zones(block_size_m=0.05, source_pressure_pa=3000):
    """
    Calculate safety zone boundaries
    
    Safety thresholds:
    - 200 Pa (150 dB): Instant death / severe injury
    - 100 Pa (140 dB): Ear damage, disorientation
    - 20 Pa (120 dB): Pain threshold
    - 2 Pa (100 dB): Hearing protection required
    - 0.2 Pa (80 dB): Safe for extended exposure
    """
    distances = np.linspace(0, 50, 1000)  # 0 to 50 meters
    pressures = []
    
    for d in distances:
        p = acoustic_pressure_at_distance(
            source_pressure_pa,
            block_size_m / 2,  # Use half block size as source radius
            d,
            frequency_hz=10
        )
        pressures.append(p)
    
    pressures = np.array(pressures)
    spls = spl_from_pressure(pressures)
    
    # Find safety zone boundaries
    zones = {
        'instant_death': None,      # >200 Pa (150 dB)
        'severe_injury': None,      # >100 Pa (140 dB)
        'pain_damage': None,        # >20 Pa (120 dB)
        'hearing_protection': None, # >2 Pa (100 dB)
        'safe': None               # <0.2 Pa (80 dB)
    }
    
    thresholds = {
        'instant_death': 200,
        'severe_injury': 100,
        'pain_damage': 20,
        'hearing_protection': 2,
        'safe': 0.2
    }
    
    for zone_name, threshold in thresholds.items():
        idx = np.where(pressures < threshold)[0]
        if len(idx) > 0:
            zones[zone_name] = distances[idx[0]]
    
    return distances, pressures, spls, zones

def main():
    print("="*80)
    print("ACOUSTIC LEVITATION DEVICE - SAFETY DISTANCE ANALYSIS")
    print("="*80)
    
    # Your device parameters
    block_size = 0.05  # 5cm block
    
    # Corrected pressure calculation:
    # Base: 120 dB = 20 Pa
    # Standing wave amplification: 2× (antinode) × √50 (Q-factor) ≈ 14.1×
    # Result: ~280 Pa external acoustic pressure
    source_pressure = 280  # Pa at block center (corrected from 3000)
    
    print(f"\nDevice Parameters:")
    print(f"Block size: {block_size*100:.1f} cm")
    print(f"Peak pressure at block: {source_pressure:.0f} Pa ({spl_from_pressure(source_pressure):.1f} dB)")
    print(f"Frequency: 10 Hz (infrasound)")
    print(f"Wavelength: 34.3 m")
    
    distances, pressures, spls, zones = safety_zones(block_size, source_pressure)
    
    print(f"\n{'='*80}")
    print("SAFETY ZONES (distances from block center)")
    print(f"{'='*80}")
    
    print(f"\n🔴 INSTANT DEATH ZONE (>150 dB, >200 Pa):")
    if zones['instant_death']:
        print(f"   0 to {zones['instant_death']:.2f} meters ({zones['instant_death']*3.281:.1f} feet)")
    else:
        print(f"   Extends beyond 50m!")
    
    print(f"\n🟠 SEVERE INJURY ZONE (>140 dB, >100 Pa):")
    if zones['severe_injury']:
        print(f"   0 to {zones['severe_injury']:.2f} meters ({zones['severe_injury']*3.281:.1f} feet)")
    else:
        print(f"   Extends beyond 50m!")
    
    print(f"\n🟡 PAIN/DAMAGE ZONE (>120 dB, >20 Pa):")
    if zones['pain_damage']:
        print(f"   0 to {zones['pain_damage']:.2f} meters ({zones['pain_damage']*3.281:.1f} feet)")
        print(f"   >> MINIMUM SAFE DISTANCE FOR REMOTE OPERATION <<")
    else:
        print(f"   Extends beyond 50m!")
    
    print(f"\n🟢 HEARING PROTECTION REQUIRED (>100 dB, >2 Pa):")
    if zones['hearing_protection']:
        print(f"   0 to {zones['hearing_protection']:.2f} meters ({zones['hearing_protection']*3.281:.1f} feet)")
    
    print(f"\n✅ SAFE ZONE (<80 dB, <0.2 Pa):")
    if zones['safe']:
        print(f"   Beyond {zones['safe']:.2f} meters ({zones['safe']*3.281:.1f} feet)")
    
    # Remote operation feasibility
    print(f"\n{'='*80}")
    print("REMOTE OPERATION FEASIBILITY")
    print(f"{'='*80}")
    
    remote_distances = [3, 5, 10, 15, 20, 30]  # meters
    print(f"\n{'Distance':<12} {'Pressure':<15} {'SPL':<12} {'Safety Level'}")
    print(f"{'-'*60}")
    
    for d in remote_distances:
        p = acoustic_pressure_at_distance(source_pressure, block_size/2, d, 10)
        spl = spl_from_pressure(p)
        
        if p > 200:
            safety = "💀 LETHAL"
        elif p > 100:
            safety = "🔴 SEVERE INJURY"
        elif p > 20:
            safety = "🟠 PAIN/DAMAGE"
        elif p > 2:
            safety = "🟡 PPE REQUIRED"
        elif p > 0.2:
            safety = "🟢 SAFE (SHORT)"
        else:
            safety = "✅ SAFE"
        
        print(f"{d}m ({d*3.281:.1f}ft)  {p:8.2f} Pa      {spl:6.1f} dB    {safety}")
    
    # Visualization
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Distance vs Pressure
    ax1.semilogy(distances * 3.281, pressures, 'b-', linewidth=2)
    ax1.axhline(200, color='red', linestyle='--', label='Death (200 Pa)', linewidth=2)
    ax1.axhline(100, color='orange', linestyle='--', label='Severe injury (100 Pa)', linewidth=2)
    ax1.axhline(20, color='yellow', linestyle='--', label='Pain threshold (20 Pa)', linewidth=2)
    ax1.axhline(2, color='lightgreen', linestyle='--', label='PPE required (2 Pa)', linewidth=2)
    ax1.axhline(0.2, color='green', linestyle='--', label='Safe (0.2 Pa)', linewidth=2)
    
    ax1.set_xlabel('Distance from Block (feet)', fontsize=12)
    ax1.set_ylabel('Acoustic Pressure (Pa)', fontsize=12)
    ax1.set_title('Pressure Decay with Distance', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    ax1.set_xlim(0, 100)
    
    # Distance vs SPL
    ax2.plot(distances * 3.281, spls, 'b-', linewidth=2)
    ax2.axhline(150, color='red', linestyle='--', label='Death (150 dB)', linewidth=2)
    ax2.axhline(140, color='orange', linestyle='--', label='Severe injury (140 dB)', linewidth=2)
    ax2.axhline(120, color='yellow', linestyle='--', label='Pain (120 dB)', linewidth=2)
    ax2.axhline(100, color='lightgreen', linestyle='--', label='PPE (100 dB)', linewidth=2)
    ax2.axhline(80, color='green', linestyle='--', label='Safe (80 dB)', linewidth=2)
    
    ax2.set_xlabel('Distance from Block (feet)', fontsize=12)
    ax2.set_ylabel('Sound Pressure Level (dB)', fontsize=12)
    ax2.set_title('SPL Decay with Distance', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    ax2.set_xlim(0, 100)
    ax2.set_ylim(60, 180)
    
    plt.tight_layout()
    plt.savefig('safety_distance_analysis.png', dpi=300, bbox_inches='tight')
    print(f"\nVisualization saved to: safety_distance_analysis.png")
    
    # Practical recommendations
    print(f"\n{'='*80}")
    print("PRACTICAL RECOMMENDATIONS FOR CONSTRUCTION USE")
    print(f"{'='*80}")
    
    print(f"\n✅ RECOMMENDED SETUP:")
    print(f"   1. Operator distance: 30+ feet (10+ meters) with hearing protection")
    print(f"   2. Remote control: Radio or long wired controller")
    print(f"   3. Block manipulation: Robotic arm or pole-mounted tools")
    print(f"   4. Exclusion zone: 50+ feet (15+ meters) for bystanders")
    print(f"   5. Warning sirens: Before activation")
    print(f"   6. Line of sight: Video feed or direct visual (from safe distance)")
    
    print(f"\n⚠️  INFRASOUND SPECIAL CONCERNS:")
    print(f"   - 10 Hz penetrates walls and barriers easily")
    print(f"   - Can't hear it, so no warning sensation")
    print(f"   - Resonates with human organs (disorientation, nausea)")
    print(f"   - Recommend: Ultrasonic frequency shift for better containment")
    
    print(f"\n🔧 REMOTE MANIPULATION OPTIONS:")
    print(f"   Option A: Magnetic/mechanical gripper on pole (20+ ft)")
    print(f"   Option B: Cable/pulley system with remote winch")
    print(f"   Option C: Multi-axis robotic arm (industrial)")
    print(f"   Option D: Drone-mounted gripper (if block light enough)")
    
    plt.show()

if __name__ == "__main__":
    main()
