"""
RINEX 3 Parser - Extract pseudorange time series for analysis

This extracts raw pseudoranges which we can use to detect timing anomalies
that might indicate gravitational field changes.
"""

import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from collections import defaultdict
import struct

def parse_rinex3_observations(rinex_file, max_epochs=None):
    """Parse RINEX 3 observation file"""
    
    print(f"Parsing {rinex_file}...")
    
    # Parse header
    header_info = {}
    obs_types = {}
    
    with open(rinex_file, 'r') as f:
        for line in f:
            if 'END OF HEADER' in line:
                break
            
            if 'APPROX POSITION XYZ' in line:
                coords = line[:60].split()
                header_info['position'] = [float(x) for x in coords[:3]]
            
            elif 'INTERVAL' in line:
                header_info['interval'] = float(line.split()[0])
            
            elif 'SYS / # / OBS TYPES' in line:
                sys = line[0]
                if sys not in obs_types:
                    obs_types[sys] = []
                types = line[7:60].split()
                obs_types[sys].extend(types)
    
    print(f"  Position: {header_info.get('position', 'Unknown')}")
    print(f"  Interval: {header_info.get('interval', 1.0)} sec")
    print(f"  Systems: {list(obs_types.keys())}")
    
    # Parse epochs
    epochs = []
    satellite_data = defaultdict(lambda: {'C1': [], 'L1': [], 'time': []})
    
    with open(rinex_file, 'r') as f:
        in_header = True
        epoch_time = 0
        epoch_sats = []
        epoch_dt = None
        line_in_epoch = 0
        
        for line in f:
            if in_header:
                if 'END OF HEADER' in line:
                    in_header = False
                continue
            
            # Epoch header: YY MM DD HH MM SS.SSSSSSS  flag  num_sats
            # RINEX 3 compact format (no > marker)
            if len(line) > 26 and line[0:2].strip().isdigit():
                try:
                    parts = line.split()
                    if len(parts) >= 8:
                        year = int(parts[0])
                        if year < 100:
                            year += 2000
                        month = int(parts[1])
                        day = int(parts[2])
                        hour = int(parts[3])
                        minute = int(parts[4])
                        second = float(parts[5])
                        flag = int(parts[6])
                        num_sats = int(parts[7])
                        
                        if flag != 0:  # Skip non-OK epochs
                            continue
                        
                        epoch_dt = datetime(year, month, day, hour, minute, int(second))
                        epoch_time = (hour * 3600 + minute * 60 + second)
                        
                        epochs.append(epoch_dt)
                        epoch_sats = []
                        line_in_epoch = 0
                        
                        if max_epochs and len(epochs) > max_epochs:
                            break
                except (ValueError, IndexError):
                    pass
            
            # Satellite observation line: SNN <observations>
            elif len(line) > 3 and line[0] in 'GREJCIS':
                sat = line[:3].strip()
                obs_str = line[3:].rstrip()
                
                # Parse observations (16-char fields)
                observations = []
                for i in range(0, len(obs_str), 16):
                    field = obs_str[i:i+16].strip()
                    if field:
                        try:
                            observations.append(float(field.split()[0]))
                        except (ValueError, IndexError):
                            observations.append(np.nan)
                    else:
                        observations.append(np.nan)
                
                # Store C1 (code/pseudorange) and L1 (phase) if available
                if len(observations) >= 1 and not np.isnan(observations[0]):
                    satellite_data[sat]['C1'].append(observations[0])
                    satellite_data[sat]['L1'].append(observations[1] if len(observations) > 1 else np.nan)
                    satellite_data[sat]['time'].append(epoch_time)
    
    print(f"\n  Parsed {len(epochs)} epochs")
    print(f"  Tracked {len(satellite_data)} satellites")
    
    return epochs, satellite_data, header_info


def analyze_timing_anomalies(epochs, satellite_data):
    """
    Analyze for timing anomalies that could indicate gravitational effects
    
    Focus on:
    1. Sudden phase jumps across multiple satellites (correlated)
    2. Drift patterns in pseudorange residuals
    3. Timing variations
    """
    
    print("\n" + "="*70)
    print("TIMING ANOMALY ANALYSIS")
    print("="*70)
    
    # Convert satellite data to arrays
    results = {}
    
    for sat, data in satellite_data.items():
        if len(data['C1']) < 100:
            continue
        
        times = np.array(data['time'])
        ranges = np.array(data['C1'])
        
        # Remove linear trend (satellite motion)
        p = np.polyfit(times, ranges, 1)
        trend = np.polyval(p, times)
        residuals = ranges - trend
        
        # Stats
        std_resid = np.std(residuals)
        mean_range = np.mean(ranges)
        
        # Look for jumps
        diffs = np.diff(residuals)
        max_jump = np.max(np.abs(diffs)) if len(diffs) > 0 else 0
        
        results[sat] = {
            'n_obs': len(ranges),
            'mean_range': mean_range,
            'std_residual': std_resid,
            'max_jump': max_jump,
            'times': times,
            'residuals': residuals
        }
    
    # Sort by anomaly score
    sorted_sats = sorted(results.items(), 
                        key=lambda x: x[1]['std_residual'], 
                        reverse=True)
    
    print(f"\nAnalyzed {len(results)} satellites with sufficient data")
    print(f"\nTop 15 by residual variability:")
    print(f"{'Sat':<6} {'N Obs':<8} {'Mean Range (km)':<16} {'Std Resid (m)':<15} {'Max Jump (m)':<12}")
    print("-"*75)
    
    for sat, stats in sorted_sats[:15]:
        print(f"{sat:<6} {stats['n_obs']:<8} {stats['mean_range']/1000:>13.1f}   "
              f"{stats['std_residual']:>12.4f}   {stats['max_jump']:>10.4f}")
    
    return results


def plot_sample_satellite(sat_data, sat_name):
    """Plot sample satellite to visualize data quality"""
    
    if sat_name not in sat_data:
        print(f"\nSatellite {sat_name} not found")
        return
    
    data = sat_data[sat_name]
    times = np.array(data['time'])
    ranges = np.array(data['C1'])
    
    # Detrend
    p = np.polyfit(times, ranges, 1)
    trend = np.polyval(p, times)
    residuals = ranges - trend
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    # Raw pseudorange
    ax1.plot(times/3600, ranges/1000, 'b-', linewidth=0.5)
    ax1.set_xlabel('Time (hours)')
    ax1.set_ylabel('Pseudorange (km)')
    ax1.set_title(f'Satellite {sat_name} - Raw Pseudorange')
    ax1.grid(True, alpha=0.3)
    
    # Residuals
    ax2.plot(times/3600, residuals, 'r-', linewidth=0.5)
    ax2.set_xlabel('Time (hours)')
    ax2.set_ylabel('Residual (m)')
    ax2.set_title(f'Satellite {sat_name} - Detrended Residuals')
    ax2.grid(True, alpha=0.3)
    ax2.axhline(0, color='k', linestyle='--', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f'gnss_{sat_name}_analysis.png', dpi=150)
    print(f"\n  Saved plot: gnss_{sat_name}_analysis.png")
    plt.close()


def compute_time_series_spectrum(residuals, times, sat_name):
    """
    Compute frequency spectrum to look for 38 mHz oscillation
    (the 2011 Tohoku mystery signal frequency)
    """
    
    from scipy import signal
    
    # Ensure uniform sampling
    dt = np.median(np.diff(times))
    
    if dt > 2:  # More than 2 second gaps
        print(f"  {sat_name}: Data gaps too large for spectrum analysis")
        return None
    
    # Compute PSD
    freqs, psd = signal.welch(residuals, fs=1/dt, nperseg=min(1024, len(residuals)//4))
    
    # Convert to mHz
    freqs_mhz = freqs * 1000
    
    # Look for peak near 38 mHz (26 second period)
    target_freq = 38  # mHz
    idx_range = np.where((freqs_mhz > 30) & (freqs_mhz < 50))[0]
    
    if len(idx_range) > 0:
        peak_idx = idx_range[np.argmax(psd[idx_range])]
        peak_freq = freqs_mhz[peak_idx]
        peak_power = psd[peak_idx]
        
        return {
            'freqs_mhz': freqs_mhz,
            'psd': psd,
            'peak_freq': peak_freq,
            'peak_power': peak_power
        }
    
    return None


if __name__ == "__main__":
    import sys
    
    rinex_file = "AB180050.22O"
    
    if len(sys.argv) > 1:
        rinex_file = sys.argv[1]
    
    print("="*70)
    print("RINEX 3 GNSS ANALYSIS FOR GRAVITATIONAL ANOMALIES")
    print("="*70)
    
    # Parse data (limit to first 10000 epochs for speed)
    epochs, satellite_data, header = parse_rinex3_observations(rinex_file, max_epochs=86400)
    
    if not satellite_data:
        print("\nNo data parsed - check RINEX format")
        sys.exit(1)
    
    # Analyze timing
    results = analyze_timing_anomalies(epochs, satellite_data)
    
    # Plot best satellite
    if results:
        best_sat = max(results.items(), key=lambda x: x[1]['n_obs'])[0]
        print(f"\nPlotting satellite with most data: {best_sat}")
        plot_sample_satellite(satellite_data, best_sat)
    
    print("\n" + "="*70)
    print("✓ Analysis complete!")
    print("\nNext steps:")
    print("  1. Process with RTKLIB PPP for precise positions")
    print("  2. Extract vertical (height) time series")
    print("  3. Look for 38 mHz oscillations (Tohoku signal)")
    print("  4. Check for time-delayed onset (5-10 min)")
    print("="*70)
