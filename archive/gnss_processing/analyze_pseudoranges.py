"""
Basic GNSS Analysis Without External Tools

This script analyzes raw RINEX pseudorange data to look for patterns
that might indicate gravitational anomalies, without requiring PPP processing.

While not as accurate as PPP, we can detect:
1. Sudden phase/pseudorange jumps
2. Unexpected satellite geometry changes
3. Clock drift anomalies
4. Patterns in observation residuals

These could be indirect indicators of gravitational field modulation.
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
import re


def parse_rinex_header(file_path):
    """Extract header information from RINEX file"""
    header_info = {}
    
    with open(file_path, 'r') as f:
        for line in f:
            if 'END OF HEADER' in line:
                break
            
            if 'APPROX POSITION XYZ' in line:
                coords = line[:60].split()
                header_info['position_xyz'] = [float(x) for x in coords[:3]]
            
            elif 'INTERVAL' in line:
                header_info['interval'] = float(line.split()[0])
            
            elif 'TIME OF FIRST OBS' in line:
                parts = line[:43].split()
                header_info['first_epoch'] = datetime(
                    int(parts[0]), int(parts[1]), int(parts[2]),
                    int(parts[3]), int(parts[4]), int(float(parts[5]))
                )
    
    return header_info


def compute_satellite_elevation(sat_xyz, receiver_xyz):
    """
    Compute approximate satellite elevation angle
    
    When gravitational coupling changes, apparent satellite positions
    might show anomalies (though small).
    """
    # Convert to local ENU frame (simplified)
    dx = np.array(sat_xyz) - np.array(receiver_xyz)
    r = np.linalg.norm(dx)
    
    if r == 0:
        return 0
    
    # Approximate elevation (simplified, assumes flat Earth locally)
    lat = np.arcsin(receiver_xyz[2] / np.linalg.norm(receiver_xyz))
    
    # Local vertical component
    up = dx[2] / r
    elevation = np.arcsin(up) * 180 / np.pi
    
    return elevation


def analyze_clock_drift(epochs, pseudoranges_by_sat):
    """
    Analyze clock drift patterns
    
    Gravitational time dilation changes if g changes!
    Clock drift = (geometric range - pseudorange) / c
    
    If gravitational coupling weakens, clock behavior might show
    unexpected patterns (though very small effect).
    """
    
    print("\n" + "="*70)
    print("CLOCK DRIFT ANALYSIS")
    print("="*70)
    
    # For each satellite, track how pseudorange changes over time
    drift_patterns = {}
    
    for sat, data in pseudoranges_by_sat.items():
        if len(data) < 100:  # Need sufficient data
            continue
        
        times = np.array([d[0] for d in data])
        ranges = np.array([d[1] for d in data])
        
        # Remove trend (satellite motion)
        coeffs = np.polyfit(times, ranges, 2)  # Quadratic fit
        trend = np.polyval(coeffs, times)
        residuals = ranges - trend
        
        # Look for anomalous patterns
        std_resid = np.std(residuals)
        max_jump = np.max(np.abs(np.diff(residuals)))
        
        drift_patterns[sat] = {
            'std_residual': std_resid,
            'max_jump': max_jump,
            'mean_range': np.mean(ranges),
            'n_obs': len(ranges)
        }
    
    # Sort by anomaly score
    anomaly_scores = {sat: d['std_residual'] * d['max_jump'] 
                      for sat, d in drift_patterns.items()}
    
    sorted_sats = sorted(anomaly_scores.items(), key=lambda x: x[1], reverse=True)
    
    print(f"\nAnalyzed {len(drift_patterns)} satellites")
    print(f"\nTop 10 anomalous satellites (by residual pattern):")
    print(f"{'Sat':<6} {'Std Resid (m)':<15} {'Max Jump (m)':<15} {'N Obs':<10}")
    print("-"*60)
    
    for sat, score in sorted_sats[:10]:
        d = drift_patterns[sat]
        print(f"{sat:<6} {d['std_residual']:>12.3f}   {d['max_jump']:>12.3f}   {d['n_obs']:>8}")
    
    return drift_patterns


def analyze_multipath_patterns(epochs, pseudoranges_by_sat, phases_by_sat):
    """
    Analyze multipath (difference between code and phase measurements)
    
    If gravitational field changes affect signal propagation differently
    for different frequencies, might see anomalies in multipath pattern.
    """
    
    print("\n" + "="*70)
    print("MULTIPATH PATTERN ANALYSIS")
    print("="*70)
    
    multipath_data = {}
    
    # For satellites with both code and phase
    common_sats = set(pseudoranges_by_sat.keys()) & set(phases_by_sat.keys())
    
    for sat in common_sats:
        code_data = pseudoranges_by_sat[sat]
        phase_data = phases_by_sat[sat]
        
        # Match by epoch
        code_dict = {d[0]: d[1] for d in code_data}
        phase_dict = {d[0]: d[1] for d in phase_data}
        
        common_epochs = set(code_dict.keys()) & set(phase_dict.keys())
        
        if len(common_epochs) < 50:
            continue
        
        times = sorted(common_epochs)
        # Multipath = Code - Phase (simplified, ignores ambiguities)
        # This is just a relative pattern indicator
        multipath = [code_dict[t] - phase_dict[t] for t in times]
        
        # Remove slow trend
        if len(multipath) > 10:
            from scipy import signal
            multipath_detrended = signal.detrend(multipath)
            
            std_mp = np.std(multipath_detrended)
            max_mp = np.max(np.abs(multipath_detrended))
            
            multipath_data[sat] = {
                'std': std_mp,
                'max': max_mp,
                'n_obs': len(times)
            }
    
    if multipath_data:
        sorted_mp = sorted(multipath_data.items(), 
                          key=lambda x: x[1]['std'], reverse=True)
        
        print(f"\nAnalyzed {len(multipath_data)} satellites")
        print(f"\nTop 10 by multipath variability:")
        print(f"{'Sat':<6} {'Std (m)':<12} {'Max (m)':<12} {'N Obs':<10}")
        print("-"*50)
        
        for sat, d in sorted_mp[:10]:
            print(f"{sat:<6} {d['std']:>9.3f}   {d['max']:>9.3f}   {d['n_obs']:>8}")
    else:
        print("\nInsufficient phase data for multipath analysis")
    
    return multipath_data


def detect_sudden_jumps(epochs, data_by_sat, threshold_sigma=5):
    """
    Detect sudden jumps in observables that might indicate
    gravitational field transients.
    """
    
    print("\n" + "="*70)
    print(f"SUDDEN JUMP DETECTION (>{threshold_sigma}σ)")
    print("="*70)
    
    all_jumps = []
    
    for sat, data in data_by_sat.items():
        if len(data) < 10:
            continue
        
        times = np.array([d[0] for d in data])
        values = np.array([d[1] for d in data])
        
        # Compute differences
        diffs = np.diff(values)
        
        if len(diffs) < 5:
            continue
        
        # Remove outliers for std calculation
        median_diff = np.median(np.abs(diffs))
        std_diff = np.std(diffs[np.abs(diffs) < 3 * median_diff])
        
        # Find jumps
        jump_indices = np.where(np.abs(diffs) > threshold_sigma * std_diff)[0]
        
        for idx in jump_indices:
            all_jumps.append({
                'time': times[idx],
                'satellite': sat,
                'magnitude': diffs[idx],
                'sigma': diffs[idx] / std_diff
            })
    
    if all_jumps:
        # Sort by time
        all_jumps.sort(key=lambda x: x['time'])
        
        print(f"\nDetected {len(all_jumps)} significant jumps")
        print(f"\nFirst 20 jumps:")
        print(f"{'Time (s)':<12} {'Sat':<6} {'Jump (m)':<12} {'Sigma':<10}")
        print("-"*50)
        
        for jump in all_jumps[:20]:
            print(f"{jump['time']:<12.1f} {jump['satellite']:<6} "
                  f"{jump['magnitude']:>9.3f}   {jump['sigma']:>7.1f}σ")
        
        # Look for correlated jumps (multiple satellites at same time)
        time_bins = defaultdict(list)
        for jump in all_jumps:
            time_bin = int(jump['time'] / 60)  # 1-minute bins
            time_bins[time_bin].append(jump)
        
        correlated = {t: jumps for t, jumps in time_bins.items() if len(jumps) > 3}
        
        if correlated:
            print(f"\n⚠ CORRELATED JUMPS DETECTED (multiple satellites):")
            for time_bin, jumps in sorted(correlated.items())[:5]:
                print(f"\nTime ~{time_bin} minutes:")
                for jump in jumps:
                    print(f"  {jump['satellite']}: {jump['magnitude']:>8.3f} m "
                          f"({jump['sigma']:.1f}σ)")
        
    else:
        print("\nNo significant jumps detected")
    
    return all_jumps


def main(rinex_file):
    """
    Main analysis pipeline for raw RINEX data
    """
    
    print("="*70)
    print("RAW RINEX ANOMALY ANALYSIS")
    print("(Without PPP Processing)")
    print("="*70)
    
    print(f"\nInput file: {rinex_file}")
    
    # Parse header
    header = parse_rinex_header(rinex_file)
    print(f"\nStation position (XYZ): {header.get('position_xyz', 'Unknown')}")
    print(f"Sampling interval: {header.get('interval', 'Unknown')} seconds")
    print(f"First epoch: {header.get('first_epoch', 'Unknown')}")
    
    # Parse data (simplified - just get pseudoranges and phases)
    print("\nParsing observations...")
    
    pseudoranges = defaultdict(list)  # {sat: [(time, range), ...]}
    phases = defaultdict(list)
    
    epoch_time = 0
    current_sat = None
    
    with open(rinex_file, 'r') as f:
        in_header = True
        
        for line in f:
            if 'END OF HEADER' in line:
                in_header = False
                continue
            
            if in_header:
                continue
            
            # Epoch line (starts with >)
            if line.startswith('>'):
                parts = line.split()
                if len(parts) >= 6:
                    year = int(parts[1])
                    month = int(parts[2])
                    day = int(parts[3])
                    hour = int(parts[4])
                    minute = int(parts[5])
                    second = float(parts[6])
                    
                    # Time since first epoch (seconds)
                    epoch_dt = datetime(year, month, day, hour, minute, int(second))
                    epoch_time = (epoch_dt - header['first_epoch']).total_seconds()
            
            # Observation line (satellite + data)
            elif len(line) > 3 and line[0] in 'GREJCIS':
                sat = line[:3].strip()
                obs_str = line[3:]
                
                # Parse observables (16-char fields)
                observables = [obs_str[i:i+16].strip() for i in range(0, len(obs_str), 16)]
                
                # First few are typically: C1, L1, S1, C2, L2, S2, ...
                # C = code (pseudorange), L = phase, S = signal strength
                
                if len(observables) >= 1 and observables[0]:
                    try:
                        pr = float(observables[0])
                        pseudoranges[sat].append((epoch_time, pr))
                    except ValueError:
                        pass
                
                if len(observables) >= 2 and observables[1]:
                    try:
                        phase = float(observables[1])
                        phases[sat].append((epoch_time, phase))
                    except ValueError:
                        pass
    
    print(f"\n✓ Parsed {len(pseudoranges)} satellites")
    print(f"  Total pseudorange observations: {sum(len(v) for v in pseudoranges.values())}")
    print(f"  Total phase observations: {sum(len(v) for v in phases.values())}")
    
    # Run analyses
    drift_patterns = analyze_clock_drift(epoch_time, pseudoranges)
    
    if phases:
        multipath_data = analyze_multipath_patterns(epoch_time, pseudoranges, phases)
    
    jumps = detect_sudden_jumps(epoch_time, pseudoranges)
    
    # Summary
    print("\n" + "="*70)
    print("ANALYSIS SUMMARY")
    print("="*70)
    
    print("\n🔍 What we looked for:")
    print("  • Clock drift anomalies (gravitational time dilation)")
    print("  • Multipath pattern changes (propagation anomalies)")
    print("  • Sudden jumps (field transients)")
    print("  • Correlated events across satellites")
    
    print("\n📊 Findings:")
    print(f"  • {len(drift_patterns)} satellites analyzed for drift")
    print(f"  • {len(jumps)} significant jumps detected")
    
    if jumps:
        correlated_times = defaultdict(int)
        for jump in jumps:
            time_bin = int(jump['time'] / 60)
            correlated_times[time_bin] += 1
        
        max_corr = max(correlated_times.values())
        if max_corr > 3:
            print(f"  • ⚠ Up to {max_corr} satellites showed jumps in same minute")
            print(f"    (Could indicate real geophysical event!)")
    
    print("\n💡 Next steps:")
    print("  1. Process with PPP for precise positions")
    print("  2. Extract vertical time series")
    print("  3. Analyze for 38 mHz oscillations")
    print("  4. Correlate with seismic activity")
    print("  5. Compare to gravitational decoupling predictions")
    
    print("\n" + "="*70)
    
    return pseudoranges, phases, jumps


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python analyze_pseudoranges.py <RINEX_FILE>")
        print("\nExample:")
        print("  python analyze_pseudoranges.py AB180050.22O")
        sys.exit(1)
    
    rinex_file = sys.argv[1]
    
    if not Path(rinex_file).exists():
        print(f"Error: File not found: {rinex_file}")
        sys.exit(1)
    
    try:
        from scipy import signal
    except ImportError:
        print("⚠ scipy not installed - multipath detrending will be skipped")
        print("  Install with: pip install scipy")
    
    pseudoranges, phases, jumps = main(rinex_file)
