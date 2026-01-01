"""
GNSS Data Analysis using georinex library

Extract and analyze GNSS observations to look for gravitational anomalies.
"""

import numpy as np
import matplotlib.pyplot as plt
import georinex as gr
from pathlib import Path

def analyze_gnss_data(rinex_file):
    """Load and analyze RINEX data"""
    
    print("="*70)
    print("GNSS GRAVITATIONAL ANOMALY ANALYSIS")
    print("="*70)
    print(f"\nLoading: {rinex_file}")
    
    # Load RINEX data
    try:
        obs = gr.load(rinex_file)
        print(f"\n✓ Loaded RINEX data")
        print(f"  Shape: {obs.dims}")
        print(f"  Time span: {obs.time[0].values} to {obs.time[-1].values}")
        print(f"  Satellites: {len(obs.sv)}")
        print(f"  Observable types: {list(obs.data_vars)}")
    except Exception as e:
        print(f"\n✗ Error loading RINEX: {e}")
        return None
    
    # Extract pseudorange data (C1 or C1C)
    print("\n" + "="*70)
    print("PSEUDORANGE ANALYSIS")
    print("="*70)
    
    # Try to find pseudorange observable
    pr_var = None
    for var in ['C1', 'C1C', 'C1W', 'P1']:
        if var in obs.data_vars:
            pr_var = var
            break
    
    if not pr_var:
        print("\n✗ No pseudorange observable found")
        print(f"  Available: {list(obs.data_vars)}")
        return obs
    
    print(f"\nUsing pseudorange: {pr_var}")
    
    # Analyze each satellite
    results = {}
    
    for sv in obs.sv.values:
        pr_data = obs[pr_var].sel(sv=sv).values
        
        # Remove NaN
        valid = ~np.isnan(pr_data)
        if np.sum(valid) < 100:
            continue
        
        pr_valid = pr_data[valid]
        time_valid = np.arange(len(pr_data))[valid]
        
        # Detrend (remove satellite motion)
        p = np.polyfit(time_valid, pr_valid, 1)
        trend = np.polyval(p, time_valid)
        residuals = pr_valid - trend
        
        # Statistics
        std_resid = np.std(residuals)
        max_jump = np.max(np.abs(np.diff(residuals)))
        
        results[sv] = {
            'n_obs': len(pr_valid),
            'std_residual': std_resid,
            'max_jump': max_jump,
            'mean_range': np.mean(pr_valid),
            'residuals': residuals,
            'times': time_valid
        }
    
    # Display results
    print(f"\nAnalyzed {len(results)} satellites")
    
    sorted_sats = sorted(results.items(), key=lambda x: x[1]['n_obs'], reverse=True)
    
    print(f"\nTop 20 satellites by observation count:")
    print(f"{'Sat':<6} {'N Obs':<8} {'Mean Range (km)':<16} {'Std Resid (m)':<15} {'Max Jump (m)':<12}")
    print("-"*75)
    
    for sv, stats in sorted_sats[:20]:
        print(f"{sv:<6} {stats['n_obs']:<8} {stats['mean_range']/1000:>13.1f}   "
              f"{stats['std_residual']:>12.4f}   {stats['max_jump']:>10.4f}")
    
    # Plot best satellite
    if results:
        best_sv = sorted_sats[0][0]
        plot_satellite_data(results[best_sv], best_sv, obs)
    
    return obs, results


def plot_satellite_data(sat_data, sv_name, obs):
    """Plot satellite residuals"""
    
    times = sat_data['times']
    residuals = sat_data['residuals']
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8))
    
    # Time series
    ax1.plot(times, residuals, 'b-', linewidth=0.5, alpha=0.7)
    ax1.set_xlabel('Epoch number')
    ax1.set_ylabel('Pseudorange Residual (m)')
    ax1.set_title(f'Satellite {sv_name} - Detrended Pseudorange')
    ax1.grid(True, alpha=0.3)
    ax1.axhline(0, color='k', linestyle='--', alpha=0.3)
    
    # Histogram
    ax2.hist(residuals, bins=50, edgecolor='black', alpha=0.7)
    ax2.set_xlabel('Residual (m)')
    ax2.set_ylabel('Count')
    ax2.set_title(f'Distribution (σ = {np.std(residuals):.3f} m)')
    ax2.grid(True, alpha=0.3)
    ax2.axvline(0, color='r', linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    outfile = f'gnss_analysis_{sv_name}.png'
    plt.savefig(outfile, dpi=150)
    print(f"\n✓ Saved plot: {outfile}")
    plt.close()


def analyze_for_tohoku_signal(results, sample_rate=1.0):
    """
    Look for 38 mHz oscillation (26 second period)
    - This is the frequency of the 2011 Tohoku mystery signal
    """
    
    print("\n" + "="*70)
    print("FREQUENCY ANALYSIS - Looking for 38 mHz (Tohoku signal)")
    print("="*70)
    
    from scipy import signal
    
    target_freq_mhz = 38  # mHz (26 second period)
    
    for sv, data in list(results.items())[:5]:  # Check first 5 satellites
        residuals = data['residuals']
        
        if len(residuals) < 512:
            continue
        
        # Compute power spectral density
        freqs, psd = signal.welch(residuals, fs=sample_rate, 
                                   nperseg=min(1024, len(residuals)//2))
        
        # Convert to mHz
        freqs_mhz = freqs * 1000
        
        # Look for peak around 38 mHz
        idx_range = np.where((freqs_mhz > 30) & (freqs_mhz < 50))[0]
        
        if len(idx_range) > 5:
            peak_idx = idx_range[np.argmax(psd[idx_range])]
            peak_freq = freqs_mhz[peak_idx]
            peak_power = psd[peak_idx]
            
            # Compare to background
            bg_power = np.median(psd[idx_range])
            snr = peak_power / bg_power
            
            print(f"\n{sv}:")
            print(f"  Peak frequency: {peak_freq:.1f} mHz (target: 38 mHz)")
            print(f"  Peak power: {peak_power:.3e}")
            print(f"  SNR: {snr:.2f}")
            
            if snr > 2:
                print(f"  ⚠ Possible signal detected!")
    
    print("\nNote: This is raw pseudorange data. For definitive detection,")
    print("need PPP-processed positions (vertical component).")


if __name__ == "__main__":
    import sys
    
    rinex_file = "AB180050.22O"
    
    if len(sys.argv) > 1:
        rinex_file = sys.argv[1]
    
    if not Path(rinex_file).exists():
        print(f"Error: File not found: {rinex_file}")
        sys.exit(1)
    
    # Analyze
    result = analyze_gnss_data(rinex_file)
    
    if result is not None:
        if isinstance(result, tuple):
            obs, sat_results = result
            analyze_for_tohoku_signal(sat_results)
        
        print("\n" + "="*70)
        print("✓ ANALYSIS COMPLETE")
        print("="*70)
        print("\n📊 What we found:")
        print("  • Raw pseudorange residuals extracted")
        print("  • Timing anomalies analyzed")
        print("  • Frequency analysis performed")
        
        print("\n🎯 Next steps for gravitational anomaly detection:")
        print("  1. Process with RTKLIB PPP → get precise XYZ positions")
        print("  2. Extract vertical (Z) component time series")
        print("  3. Look for 38 mHz oscillations in height")
        print("  4. Check for 5-10 minute time-delayed onset")
        print("  5. Compare to seismic/gravitational decoupling predictions")
        
        print("\n📄 See: TOHOKU_EARTHQUAKE_EVIDENCE.md for theory")
        print("="*70)
