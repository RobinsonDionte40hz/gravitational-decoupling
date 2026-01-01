"""
Quick CRINEX/RINEX Data Analysis
Extract timing and look for anomalies even from raw observation files
"""

import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from scipy import signal
import re

def parse_crinex_epochs(filepath):
    """Extract epoch times from CRINEX file"""
    
    print(f"Parsing CRINEX file: {filepath}")
    
    epochs = []
    sat_counts = []
    
    with open(filepath, 'r', errors='ignore') as f:
        in_header = True
        line_count = 0
        
        for line in f:
            if 'END OF HEADER' in line:
                in_header = False
                continue
            
            if in_header:
                continue
            
            # CRINEX epoch line starts with &
            if line.startswith('&'):
                try:
                    # Parse: &YY  M  D  H  M  S.SSSSSSS  F NN...
                    parts = line.split()
                    year = int(parts[0][1:])  # Remove '&'
                    if year < 80:
                        year += 2000
                    else:
                        year += 1900
                    
                    month = int(parts[1])
                    day = int(parts[2])
                    hour = int(parts[3])
                    minute = int(parts[4])
                    second = float(parts[5])
                    flag = int(parts[6])
                    num_sats = int(parts[7].replace('G', '').replace('R', '').replace('E', '')[:2])
                    
                    epoch = datetime(year, month, day, hour, minute, int(second))
                    epochs.append(epoch)
                    sat_counts.append(num_sats)
                    
                    line_count += 1
                    if line_count % 10000 == 0:
                        print(f"  Processed {line_count:,} epochs...")
                
                except Exception as e:
                    if line_count < 5:
                        print(f"  Error parsing: {e}")
                    continue
    
    print(f"✓ Found {len(epochs):,} observation epochs")
    
    return np.array(epochs), np.array(sat_counts)

def analyze_gnss_timing(epochs, sat_counts, station_name="Unknown"):
    """Analyze GNSS data for timing anomalies"""
    
    if len(epochs) == 0:
        print("No epochs to analyze")
        return
    
    # Convert to seconds from start
    start_time = epochs[0]
    time_seconds = np.array([(e - start_time).total_seconds() for e in epochs])
    
    duration = time_seconds[-1]
    
    print("\n" + "="*70)
    print("GNSS DATA ANALYSIS")
    print("="*70)
    print(f"\nStation: {station_name}")
    print(f"Start:   {epochs[0]}")
    print(f"End:     {epochs[-1]}")
    print(f"Duration: {duration/3600:.2f} hours ({duration/86400:.2f} days)")
    print(f"Epochs:  {len(epochs):,}")
    print(f"Satellites: {np.mean(sat_counts):.1f} ± {np.std(sat_counts):.1f} average")
    
    # Check sampling rate
    dt = np.diff(time_seconds)
    dt_median = np.median(dt)
    print(f"Sampling: {1/dt_median:.2f} Hz ({dt_median:.3f} s interval)")
    
    # Look for timing gaps (potential earthquake/anomaly times)
    gaps = np.where(dt > 2 * dt_median)[0]
    if len(gaps) > 0:
        print(f"\n⚠️  Found {len(gaps)} timing gaps:")
        for i in gaps[:10]:  # Show first 10
            gap_time = epochs[i]
            gap_size = dt[i]
            print(f"  {gap_time}: {gap_size:.1f} second gap")
    
    # Analyze satellite count variations (can indicate ionospheric disturbances)
    sat_detrended = sat_counts - np.median(sat_counts)
    sat_std = np.std(sat_detrended)
    
    anomalous_sat = np.where(np.abs(sat_detrended) > 3 * sat_std)[0]
    if len(anomalous_sat) > 0:
        print(f"\n⚠️  Found {len(anomalous_sat)} periods with unusual satellite counts:")
        for i in anomalous_sat[:10]:
            print(f"  {epochs[i]}: {sat_counts[i]} satellites (deviation: {sat_detrended[i]:.1f})")
    
    # Create visualization
    fig, axes = plt.subplots(3, 1, figsize=(14, 10))
    
    # Plot 1: Satellite count over time
    ax = axes[0]
    time_hours = time_seconds / 3600
    ax.plot(time_hours, sat_counts, 'b-', linewidth=0.5, alpha=0.7)
    ax.set_ylabel('# Satellites', fontweight='bold')
    ax.set_title(f'GNSS Data Analysis - Station {station_name} - {epochs[0].date()}', 
                 fontweight='bold', fontsize=13)
    ax.grid(True, alpha=0.3)
    ax.axhline(y=np.median(sat_counts), color='r', linestyle='--', alpha=0.5, label='Median')
    ax.legend()
    
    # Plot 2: Satellite count deviations
    ax = axes[1]
    ax.plot(time_hours, sat_detrended, 'r-', linewidth=0.5)
    ax.set_ylabel('Satellite Count Deviation', fontweight='bold')
    ax.axhline(y=0, color='k', linestyle='--', alpha=0.5)
    ax.axhline(y=3*sat_std, color='r', linestyle=':', alpha=0.5, label='±3σ threshold')
    ax.axhline(y=-3*sat_std, color='r', linestyle=':', alpha=0.5)
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    # Plot 3: Sampling interval variations
    ax = axes[2]
    ax.plot(time_hours[:-1], dt, 'g-', linewidth=0.5)
    ax.set_ylabel('Sample Interval (s)', fontweight='bold')
    ax.set_xlabel('Time (hours)', fontweight='bold')
    ax.axhline(y=dt_median, color='r', linestyle='--', alpha=0.5, label='Median')
    ax.set_ylim([0, min(10, np.max(dt))])  # Limit y-axis for readability
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    plt.tight_layout()
    plt.savefig('gnss_timing_analysis.png', dpi=300, bbox_inches='tight')
    print(f"\n✓ Saved plot: gnss_timing_analysis.png")
    
    plt.show()
    
    return time_seconds, sat_counts

def main():
    import sys
    
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
    else:
        # Default to the file we know about
        filepath = r"c:\Users\ROB\Downloads\ab180050.22d\ab180050.22d"
    
    print("="*70)
    print("GNSS TIMING ANALYSIS (CRINEX/RINEX)")
    print("="*70)
    print("\nNote: This analyzes timing and satellite patterns.")
    print("For full gravitational anomaly detection, processed")
    print("position solutions (PPP/RTK) are needed.")
    print("="*70 + "\n")
    
    epochs, sat_counts = parse_crinex_epochs(filepath)
    
    if len(epochs) > 0:
        # Extract station name from filename
        import os
        station_name = os.path.basename(filepath)[:4].upper()
        
        time_seconds, sat_counts = analyze_gnss_timing(epochs, sat_counts, station_name)
        
        print("\n" + "="*70)
        print("INTERPRETATION:")
        print("="*70)
        print("1. Timing gaps may indicate:")
        print("   - Data loss during seismic activity")
        print("   - Equipment issues")
        print("   - Intentional data gaps")
        print()
        print("2. Satellite count variations may indicate:")
        print("   - Ionospheric disturbances (earthquakes, solar activity)")
        print("   - Atmospheric anomalies")
        print("   - Signal blockage")
        print()
        print("3. For gravitational anomaly detection:")
        print("   - Process this file with RTKLIB or similar")
        print("   - Generate high-rate kinematic positions")
        print("   - Analyze height time series for 38 mHz signals")
        print("="*70)
    else:
        print("❌ No epochs found")

if __name__ == '__main__':
    main()
