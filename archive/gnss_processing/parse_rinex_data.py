"""
Parse RINEX 2.11 Observation Data for Gravitational Anomaly Detection
Station: AB18 (Alaska)
Date: January 5, 2022
"""

import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from scipy import signal

def parse_rinex_header(file_path):
    """Parse RINEX header to extract metadata"""
    header = {}
    obs_types = []
    
    with open(file_path, 'r') as f:
        for line in f:
            if 'END OF HEADER' in line:
                break
                
            if 'RINEX VERSION' in line:
                header['version'] = line[:20].strip()
            elif 'MARKER NAME' in line:
                header['marker'] = line[:60].strip()
            elif 'APPROX POSITION XYZ' in line:
                x, y, z = line[:60].split()
                header['position'] = [float(x), float(y), float(z)]
            elif 'INTERVAL' in line:
                header['interval'] = float(line[:10].strip())
            elif 'TIME OF FIRST OBS' in line:
                parts = line[:60].split()
                header['first_obs'] = datetime(int(parts[0]), int(parts[1]), 
                                               int(parts[2]), int(parts[3]), 
                                               int(parts[4]), int(float(parts[5])))
            elif '# / TYPES OF OBSERV' in line:
                # Parse observation types (L1, L2, C1, P2, etc.)
                n_types_str = line[:6].strip()
                if n_types_str:
                    n_types = int(n_types_str)
                types_str = line[10:60]
                obs_types.extend(types_str.split())
                
    header['obs_types'] = obs_types
    return header

def ecef_to_geodetic(x, y, z):
    """Convert ECEF coordinates to geodetic (lat, lon, height)"""
    a = 6378137.0  # WGS84 semi-major axis
    e2 = 0.00669437999014  # WGS84 first eccentricity squared
    
    lon = np.arctan2(y, x)
    p = np.sqrt(x**2 + y**2)
    lat = np.arctan2(z, p * (1 - e2))
    
    # Iterate to improve latitude
    for _ in range(5):
        N = a / np.sqrt(1 - e2 * np.sin(lat)**2)
        h = p / np.cos(lat) - N
        lat = np.arctan2(z, p * (1 - e2 * N / (N + h)))
    
    N = a / np.sqrt(1 - e2 * np.sin(lat)**2)
    h = p / np.cos(lat) - N
    
    return np.degrees(lat), np.degrees(lon), h

def parse_rinex_observations(file_path, max_epochs=None):
    """
    Parse RINEX observation epochs
    Returns: times, epochs data
    """
    print(f"\nParsing RINEX observations from {file_path}...")
    
    epochs = []
    times = []
    in_header = True
    epoch_count = 0
    
    with open(file_path, 'r') as f:
        for line in f:
            # Skip header
            if in_header:
                if 'END OF HEADER' in line:
                    in_header = False
                continue
            
            # Check if this is an epoch header line
            # Format: YY MM DD HH MM SS.SSSSSSS  EPOCH FLAG  NUM_SAT
            if len(line) > 26 and line[0] == ' ' and line[1:3].strip().isdigit():
                try:
                    # Parse epoch time
                    yy = int(line[1:3])
                    mm = int(line[4:6])
                    dd = int(line[7:9])
                    hh = int(line[10:12])
                    mn = int(line[13:15])
                    ss = float(line[16:26])
                    
                    year = 2000 + yy if yy < 80 else 1900 + yy
                    epoch_time = datetime(year, mm, dd, hh, mn, int(ss))
                    epoch_time += timedelta(seconds=ss - int(ss))
                    
                    # Epoch flag (0 = OK, 1 = power failure, etc.)
                    epoch_flag = int(line[28:29])
                    
                    # Number of satellites
                    n_sat = int(line[29:32])
                    
                    times.append(epoch_time)
                    epochs.append({
                        'time': epoch_time,
                        'flag': epoch_flag,
                        'n_sat': n_sat,
                        'satellites': []
                    })
                    
                    epoch_count += 1
                    if epoch_count % 1000 == 0:
                        print(f"  Parsed {epoch_count} epochs... ({epoch_time})")
                    
                    if max_epochs and epoch_count >= max_epochs:
                        break
                        
                except (ValueError, IndexError) as e:
                    continue
    
    print(f"\n✓ Parsed {epoch_count} observation epochs")
    return times, epochs

def analyze_timing(times, epochs):
    """Analyze timing consistency and gaps"""
    if len(times) < 2:
        print("Not enough epochs for timing analysis")
        return
    
    # Calculate time differences
    time_diffs = []
    for i in range(1, len(times)):
        dt = (times[i] - times[i-1]).total_seconds()
        time_diffs.append(dt)
    
    time_diffs = np.array(time_diffs)
    
    print(f"\n" + "="*70)
    print("TIMING ANALYSIS")
    print("="*70)
    print(f"Total epochs: {len(times)}")
    print(f"Time span: {times[0]} to {times[-1]}")
    print(f"Duration: {(times[-1] - times[0]).total_seconds() / 3600:.2f} hours")
    print(f"\nSampling interval:")
    print(f"  Mean: {np.mean(time_diffs):.3f} seconds")
    print(f"  Median: {np.median(time_diffs):.3f} seconds")
    print(f"  Std dev: {np.std(time_diffs):.3f} seconds")
    print(f"  Min: {np.min(time_diffs):.3f} seconds")
    print(f"  Max: {np.max(time_diffs):.3f} seconds")
    
    # Find gaps
    gaps = np.where(time_diffs > 2.0)[0]
    if len(gaps) > 0:
        print(f"\n⚠️  Found {len(gaps)} data gaps (>2 seconds):")
        for idx in gaps[:10]:  # Show first 10
            print(f"    {times[idx]} -> {times[idx+1]}: {time_diffs[idx]:.1f} sec gap")
        if len(gaps) > 10:
            print(f"    ... and {len(gaps) - 10} more gaps")
    
    # Satellite counts
    sat_counts = [e['n_sat'] for e in epochs]
    print(f"\nSatellite tracking:")
    print(f"  Mean: {np.mean(sat_counts):.1f} satellites")
    print(f"  Min: {np.min(sat_counts)} satellites")
    print(f"  Max: {np.max(sat_counts)} satellites")
    
    return time_diffs, sat_counts

def plot_timing_analysis(times, time_diffs, sat_counts):
    """Create timing visualization"""
    
    fig, axes = plt.subplots(3, 1, figsize=(14, 10))
    
    # Plot 1: Sampling interval over time
    elapsed = [(t - times[0]).total_seconds() / 3600 for t in times[1:]]
    axes[0].plot(elapsed, time_diffs, 'b-', linewidth=0.5, alpha=0.7)
    axes[0].axhline(1.0, color='r', linestyle='--', label='Expected (1 Hz)')
    axes[0].set_ylabel('Sampling Interval (s)')
    axes[0].set_title('GNSS Data Sampling Consistency - AB18 Station (Alaska)')
    axes[0].grid(True, alpha=0.3)
    axes[0].legend()
    axes[0].set_ylim([0, min(5, np.max(time_diffs))])
    
    # Plot 2: Satellite count over time
    elapsed_full = [(t - times[0]).total_seconds() / 3600 for t in times]
    axes[1].plot(elapsed_full, sat_counts, 'g-', linewidth=0.8)
    axes[1].set_ylabel('Number of Satellites')
    axes[1].set_title('Satellite Tracking Over Time')
    axes[1].grid(True, alpha=0.3)
    axes[1].set_ylim([0, max(sat_counts) + 2])
    
    # Plot 3: Histogram of sampling intervals
    axes[2].hist(time_diffs, bins=100, color='purple', alpha=0.7, edgecolor='black')
    axes[2].axvline(1.0, color='r', linestyle='--', linewidth=2, label='Expected (1 Hz)')
    axes[2].set_xlabel('Sampling Interval (seconds)')
    axes[2].set_ylabel('Count')
    axes[2].set_title('Distribution of Sampling Intervals')
    axes[2].set_xlim([0.9, 1.1])
    axes[2].grid(True, alpha=0.3)
    axes[2].legend()
    
    plt.tight_layout()
    plt.savefig('rinex_timing_analysis.png', dpi=150, bbox_inches='tight')
    print(f"\n✓ Saved timing plot: rinex_timing_analysis.png")
    
    return fig

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python parse_rinex_data.py <rinex_file>")
        print("\nExample:")
        print("  python parse_rinex_data.py AB180050.22O")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    print("="*70)
    print("RINEX OBSERVATION DATA PARSER")
    print("For Gravitational Anomaly Detection")
    print("="*70)
    
    # Parse header
    print("\nParsing header...")
    header = parse_rinex_header(file_path)
    
    print(f"\nStation: {header.get('marker', 'Unknown')}")
    print(f"RINEX Version: {header.get('version', 'Unknown')}")
    print(f"First observation: {header.get('first_obs', 'Unknown')}")
    print(f"Sampling interval: {header.get('interval', 'Unknown')} seconds")
    
    if 'position' in header:
        x, y, z = header['position']
        lat, lon, h = ecef_to_geodetic(x, y, z)
        print(f"\nStation position:")
        print(f"  ECEF: X={x:.3f}, Y={y:.3f}, Z={z:.3f} m")
        print(f"  Geodetic: {lat:.6f}°N, {lon:.6f}°E, {h:.2f}m")
    
    print(f"\nObservation types: {', '.join(header.get('obs_types', [])[:10])}")
    if len(header.get('obs_types', [])) > 10:
        print(f"  ... and {len(header['obs_types']) - 10} more")
    
    # Parse observations (limit to reasonable number for analysis)
    max_epochs = 100000  # ~27 hours at 1 Hz
    times, epochs = parse_rinex_observations(file_path, max_epochs=max_epochs)
    
    if len(times) == 0:
        print("\n❌ No observation epochs found!")
        sys.exit(1)
    
    # Analyze timing
    time_diffs, sat_counts = analyze_timing(times, epochs)
    
    # Create plots
    if len(times) > 1:
        plot_timing_analysis(times, time_diffs, sat_counts)
    
    print("\n" + "="*70)
    print("NEXT STEPS FOR GRAVITATIONAL ANOMALY DETECTION:")
    print("="*70)
    print("1. Process with precise point positioning (PPP) to get positions")
    print("2. Extract height time series (vertical component)")
    print("3. Look for 38 mHz oscillations (period ~26 seconds)")
    print("4. Check for time-delayed accumulation (5-10 minute onset)")
    print("5. Compare with framework predictions")
    print("\nNote: Raw RINEX observations need PPP/RTK processing")
    print("      to extract meter-level position accuracy needed")
    print("      for gravitational anomaly detection.")
    print("="*70)

if __name__ == "__main__":
    main()
