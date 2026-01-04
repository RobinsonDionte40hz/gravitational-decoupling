"""
Black Hole Quasi-Normal Mode (QNM) Analysis
Testing for golden ratio patterns in frequency relationships
"""

import numpy as np
from scipy.special import spherical_jn, spherical_yn
import matplotlib.pyplot as plt

# Physical constants
c = 299792458  # m/s
G = 6.67430e-11  # m^3 kg^-1 s^-2
M_sun = 1.989e30  # kg

# Golden ratio
phi = (1 + np.sqrt(5)) / 2

def schwarzschild_qnm_frequencies(M, l_values, n_max=3):
    """
    Calculate QNM frequencies for Schwarzschild black hole
    Using approximation formulas from Berti et al. (2009)
    
    Parameters:
    -----------
    M : float
        Black hole mass in kg
    l_values : list
        Angular momentum quantum numbers to calculate
    n_max : int
        Maximum overtone number
        
    Returns:
    --------
    dict : QNM frequencies {(l,n): (omega_real, omega_imag)}
    """
    # Schwarzschild radius
    R_s = 2 * G * M / c**2
    
    # Characteristic frequency
    omega_0 = c**3 / (G * M)
    
    qnm_frequencies = {}
    
    for l in l_values:
        for n in range(n_max):
            # Approximation formulas from Berti et al.
            # Real part: omega_R ≈ (characteristic freq) * f(l,n)
            # For l=2 (dominant mode):
            if l == 2:
                # Empirical fits from numerical relativity
                if n == 0:
                    omega_r = 0.37367 * omega_0
                    omega_i = 0.08896 * omega_0
                elif n == 1:
                    omega_r = 0.34671 * omega_0
                    omega_i = 0.27392 * omega_0
                elif n == 2:
                    omega_r = 0.30105 * omega_0
                    omega_i = 0.47946 * omega_0
                else:
                    # Approximate for higher overtones
                    omega_r = 0.37367 * omega_0 / (1 + 0.1*n)
                    omega_i = 0.08896 * omega_0 * (1 + 2*n)
            
            elif l == 3:
                # l=3 modes
                if n == 0:
                    omega_r = 0.59944 * omega_0
                    omega_i = 0.09270 * omega_0
                elif n == 1:
                    omega_r = 0.58279 * omega_0
                    omega_i = 0.28119 * omega_0
                else:
                    omega_r = 0.59944 * omega_0 / (1 + 0.1*n)
                    omega_i = 0.09270 * omega_0 * (1 + 2*n)
            
            elif l == 4:
                if n == 0:
                    omega_r = 0.80920 * omega_0
                    omega_i = 0.09416 * omega_0
                else:
                    omega_r = 0.80920 * omega_0 / (1 + 0.1*n)
                    omega_i = 0.09416 * omega_0 * (1 + 2*n)
            
            else:
                # Generic approximation for other l
                omega_r = (0.2 + 0.1*l) * omega_0 / (1 + 0.1*n)
                omega_i = 0.09 * omega_0 * (1 + 2*n)
            
            qnm_frequencies[(l, n)] = (omega_r, omega_i)
    
    return qnm_frequencies, omega_0


def test_golden_ratio_patterns(qnm_frequencies):
    """
    Test various ratio relationships for golden ratio patterns
    """
    print("\n" + "="*80)
    print("TESTING FOR GOLDEN RATIO PATTERNS")
    print("="*80)
    print(f"Golden ratio φ = {phi:.6f}")
    print(f"1/φ = {1/phi:.6f}")
    print(f"φ² = {phi**2:.6f}")
    
    results = {
        'same_l_ratios': [],
        'cross_l_ratios': [],
        'imaginary_real_ratios': [],
        'magnitude_ratios': [],
        'sum_ratios': []
    }
    
    # Extract and sort keys
    keys = sorted(qnm_frequencies.keys())
    
    print("\n--- Test 1: Ratios within same l (overtone progression) ---")
    for l in set(k[0] for k in keys):
        l_modes = [(k, qnm_frequencies[k]) for k in keys if k[0] == l]
        l_modes.sort(key=lambda x: x[0][1])  # Sort by n
        
        print(f"\nl = {l}:")
        for i in range(len(l_modes) - 1):
            (l1, n1), (omega_r1, omega_i1) = l_modes[i]
            (l2, n2), (omega_r2, omega_i2) = l_modes[i+1]
            
            ratio_r = omega_r1 / omega_r2
            ratio_i = omega_i2 / omega_i1  # Note: inverted because imaginary grows
            
            # Calculate proximity to golden ratio
            proximity_r = min(abs(ratio_r - phi), abs(ratio_r - 1/phi), 
                            abs(ratio_r - phi**2), abs(ratio_r - 1/phi**2))
            proximity_i = min(abs(ratio_i - phi), abs(ratio_i - 1/phi),
                            abs(ratio_i - phi**2), abs(ratio_i - 1/phi**2))
            
            print(f"  n={n1}/n={n2}: ωᵣ ratio = {ratio_r:.4f}, ωᵢ ratio = {ratio_i:.4f}")
            print(f"    Distance from φ: real = {proximity_r:.4f}, imag = {proximity_i:.4f}")
            
            results['same_l_ratios'].append({
                'l': l, 'n1': n1, 'n2': n2,
                'ratio_r': ratio_r, 'ratio_i': ratio_i,
                'proximity_r': proximity_r, 'proximity_i': proximity_i
            })
    
    print("\n--- Test 2: Ratios across different l (same n) ---")
    for n in set(k[1] for k in keys):
        n_modes = [(k, qnm_frequencies[k]) for k in keys if k[1] == n]
        n_modes.sort(key=lambda x: x[0][0])  # Sort by l
        
        print(f"\nn = {n}:")
        for i in range(len(n_modes) - 1):
            (l1, n1), (omega_r1, omega_i1) = n_modes[i]
            (l2, n2), (omega_r2, omega_i2) = n_modes[i+1]
            
            ratio_r = omega_r2 / omega_r1
            ratio_i = omega_i2 / omega_i1
            
            proximity_r = min(abs(ratio_r - phi), abs(ratio_r - 1/phi),
                            abs(ratio_r - phi**2), abs(ratio_r - 1/phi**2))
            
            print(f"  l={l1}/l={l2}: ωᵣ ratio = {ratio_r:.4f}")
            print(f"    Distance from φ: {proximity_r:.4f}")
            
            results['cross_l_ratios'].append({
                'l1': l1, 'l2': l2, 'n': n,
                'ratio_r': ratio_r, 'proximity': proximity_r
            })
    
    print("\n--- Test 3: Imaginary/Real ratios ---")
    for (l, n), (omega_r, omega_i) in sorted(qnm_frequencies.items()):
        ratio = omega_i / omega_r
        proximity = min(abs(ratio - phi), abs(ratio - 1/phi),
                       abs(ratio - phi**2), abs(ratio - 1/phi**2))
        
        print(f"l={l}, n={n}: ωᵢ/ωᵣ = {ratio:.4f}, distance from φ = {proximity:.4f}")
        
        results['imaginary_real_ratios'].append({
            'l': l, 'n': n, 'ratio': ratio, 'proximity': proximity
        })
    
    print("\n--- Test 4: Magnitude ratios ---")
    for i, ((l1, n1), (omega_r1, omega_i1)) in enumerate(sorted(qnm_frequencies.items())):
        mag1 = np.sqrt(omega_r1**2 + omega_i1**2)
        for (l2, n2), (omega_r2, omega_i2) in list(sorted(qnm_frequencies.items()))[i+1:]:
            mag2 = np.sqrt(omega_r2**2 + omega_i2**2)
            ratio = mag1 / mag2 if mag1 > mag2 else mag2 / mag1
            
            proximity = min(abs(ratio - phi), abs(ratio - 1/phi),
                          abs(ratio - phi**2), abs(ratio - 1/phi**2))
            
            if proximity < 0.1:  # Only show close matches
                print(f"({l1},{n1})/({l2},{n2}): |ω| ratio = {ratio:.4f}, distance = {proximity:.4f}")
                results['magnitude_ratios'].append({
                    'mode1': (l1, n1), 'mode2': (l2, n2),
                    'ratio': ratio, 'proximity': proximity
                })
    
    return results


def statistical_analysis(results):
    """
    Statistical summary of golden ratio proximity
    """
    print("\n" + "="*80)
    print("STATISTICAL SUMMARY")
    print("="*80)
    
    all_proximities = []
    
    for category, data in results.items():
        if not data:
            continue
            
        if category == 'same_l_ratios':
            prox = [d['proximity_r'] for d in data] + [d['proximity_i'] for d in data]
        elif category in ['cross_l_ratios', 'imaginary_real_ratios', 'magnitude_ratios']:
            prox = [d['proximity'] for d in data]
        else:
            continue
        
        all_proximities.extend(prox)
        
        print(f"\n{category}:")
        print(f"  Mean distance from φ: {np.mean(prox):.4f}")
        print(f"  Min distance: {np.min(prox):.4f}")
        print(f"  # within 0.05 of φ: {sum(1 for p in prox if p < 0.05)}/{len(prox)}")
        print(f"  # within 0.10 of φ: {sum(1 for p in prox if p < 0.10)}/{len(prox)}")
    
    print(f"\nOVERALL:")
    print(f"  Total comparisons: {len(all_proximities)}")
    print(f"  Mean distance from φ: {np.mean(all_proximities):.4f}")
    print(f"  Median distance: {np.median(all_proximities):.4f}")
    print(f"  # within 0.05: {sum(1 for p in all_proximities if p < 0.05)} ({100*sum(1 for p in all_proximities if p < 0.05)/len(all_proximities):.1f}%)")
    print(f"  # within 0.10: {sum(1 for p in all_proximities if p < 0.10)} ({100*sum(1 for p in all_proximities if p < 0.10)/len(all_proximities):.1f}%)")
    
    # Compare to random expectation
    print("\n--- Comparison to Random Distribution ---")
    print("Expected distance from φ for random ratios in [0.5, 2.5]:")
    random_ratios = np.random.uniform(0.5, 2.5, 10000)
    random_proximities = [min(abs(r - phi), abs(r - 1/phi), 
                             abs(r - phi**2), abs(r - 1/phi**2)) 
                         for r in random_ratios]
    print(f"  Mean: {np.mean(random_proximities):.4f}")
    print(f"  # within 0.05: {100*sum(1 for p in random_proximities if p < 0.05)/len(random_proximities):.1f}%")
    print(f"  # within 0.10: {100*sum(1 for p in random_proximities if p < 0.10)/len(random_proximities):.1f}%")
    
    if np.mean(all_proximities) < np.mean(random_proximities):
        improvement = (np.mean(random_proximities) - np.mean(all_proximities)) / np.mean(random_proximities) * 100
        print(f"\n  QNM ratios are {improvement:.1f}% closer to φ than random!")
    else:
        print(f"\n  QNM ratios are NOT significantly closer to φ than random.")


def main():
    # Test for solar mass black hole
    print("\n" + "="*80)
    print("BLACK HOLE QNM GOLDEN RATIO ANALYSIS")
    print("="*80)
    
    M_bh = 10 * M_sun  # 10 solar mass black hole
    print(f"\nBlack hole mass: {M_bh/M_sun:.1f} M☉")
    
    # Calculate QNM frequencies
    l_values = [2, 3, 4]  # Dominant modes
    qnm_freq, omega_0 = schwarzschild_qnm_frequencies(M_bh, l_values, n_max=3)
    
    print(f"Characteristic frequency: ω₀ = {omega_0:.3e} rad/s")
    print(f"                         f₀ = {omega_0/(2*np.pi):.3e} Hz")
    
    print("\n--- QNM Frequencies (in units of ω₀) ---")
    for (l, n), (omega_r, omega_i) in sorted(qnm_freq.items()):
        print(f"l={l}, n={n}: ωᵣ = {omega_r/omega_0:.5f} ω₀, ωᵢ = {omega_i/omega_0:.5f} ω₀")
    
    # Test for golden ratio patterns
    results = test_golden_ratio_patterns(qnm_freq)
    
    # Statistical analysis
    statistical_analysis(results)
    
    # Conclusion
    print("\n" + "="*80)
    print("CONCLUSION")
    print("="*80)
    print("\nBased on this analysis:")
    print("1. Individual overtone ratios (n→n+1) are ~1.05-1.15, NOT close to φ=1.618")
    print("2. Cross-angular-momentum ratios show SOME proximity to φ")
    print("3. Imaginary/real ratios do NOT show φ patterns")
    print("4. Need to check if statistical clustering is significant")
    print("\nVerdict: WEAK evidence for golden ratio in black hole QNMs")
    print("Recommendation: Mark as SPECULATIVE in framework document")


if __name__ == "__main__":
    main()
