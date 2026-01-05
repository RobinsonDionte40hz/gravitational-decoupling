"""
Analyze 2004 Sumatra-Andaman Earthquake Seismic Data
Looking for crustal resonance signature analogous to Tohoku 38 mHz signal

Earthquake: 2004-12-26 00:58:53 UTC (M9.1-9.3)
Expected signature:
- 18-25 mHz oscillation (~40-55 second period)
- Onset 5-10 minutes AFTER mainshock
- Duration ~10-15 minutes
- Non-localized (detected teleseismically)

CRITICAL: This is DIFFERENT from Earth's normal modes (<10 mHz)
We are looking for CRUSTAL resonance, not whole-Earth oscillations
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from datetime import datetime, timedelta
from pathlib import Path
import glob

# Earthquake parameters
QUAKE_TIME_UTC = datetime(2004, 12, 26, 0, 58, 53)
QUAKE_MAG = 9.15  # Average of estimates
QUAKE_LOCATION = "3.316°N, 95.854°E"

# Crustal parameters for Sumatra region
SUMATRA_CRUSTAL_THICKNESS = 37.5e3  # meters (35-40 km range)
SUMATRA_SHEAR_VELOCITY = 3200  # m/s
EXPECTED_FREQ_MHZ = (SUMATRA_SHEAR_VELOCITY / (4 * SUMATRA_CRUSTAL_THICKNESS)) * 1000
FREQ_RANGE_MHZ = (15, 30)  # Search range around prediction

# Time windows (relative to mainshock)
PRE_EVENT_WINDOW = (-15*60, -5*60)  # -15 to -5 minutes (baseline)
POST_EVENT_WINDOW = (5*60, 15*60)   # +5 to +15 minutes (expected signal)

# For comparison: Earth's normal modes are MUCH LOWER frequency
EARTH_NORMAL_MODES = {
    '0S0': 0.815,   # mHz (20.5 min period) - "breathing" mode
    '0S2': 0.309,   # mHz (54 min period) - "football" mode
    '0S3': 0.469,   # mHz
}

print("="*80)
print("2004 SUMATRA-ANDAMAN EARTHQUAKE - CRUSTAL RESONANCE ANALYSIS")
print("="*80)
print(f"\nEarthquake: {QUAKE_TIME_UTC} UTC")
print(f"Magnitude: Mw {QUAKE_MAG}")
print(f"Location: {QUAKE_LOCATION}")
print(f"\n🎯 FRAMEWORK PREDICTION:")
print(f"  Crustal thickness: {SUMATRA_CRUSTAL_THICKNESS/1000:.1f} km")
print(f"  Shear velocity: {SUMATRA_SHEAR_VELOCITY} m/s")
print(f"  Expected frequency: {EXPECTED_FREQ_MHZ:.1f} mHz")
print(f"  Search range: {FREQ_RANGE_MHZ[0]}-{FREQ_RANGE_MHZ[1]} mHz")
print(f"\n⏱️  EXPECTED TIMING:")
print(f"  Signal onset: 5-10 minutes after mainshock")
print(f"  Duration: 10-15 minutes")
print(f"  Baseline period: 15-5 minutes before (for comparison)")
print(f"\n⚠️  NOTE: Earth's normal modes are <1 mHz - we're looking at 18-25 mHz!")
print("="*80)


def read_sac_ascii(filepath):
    """
    Read SAC ASCII format file
    
    SAC ASCII format:
    - First 30 lines: Header (5 floats per line for lines 1-14, 5 ints for 15-22, text for rest)
    - Remaining lines: Data (5 floats per line)
    
    Returns:
    - times: time array in seconds
    - data: amplitude array
    - header: dictionary with metadata
    """
    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()
        
        # SAC ASCII header is exactly 30 lines
        # Line 1: delta, depmin, depmax, scale, odelta
        # Line 2: b, e, o, a, internal1
        # Line 11: dist, az, baz, gcarc, internal2
        # Lines 15-22: Integer header
        # Lines 23-30: Text header
        
        header = {}
        
        # Parse first header line to get delta (sampling interval)
        values = [float(x) for x in lines[0].split()]
        delta = values[0]  # Sampling interval in seconds
        header['delta'] = delta
        header['depmin'] = values[1] if values[1] != -12345 else None
        header['depmax'] = values[2] if values[2] != -12345 else None
        
        # Parse second header line to get b (begin time)
        values = [float(x) for x in lines[1].split()]
        b = values[0]  # Begin time
        header['b'] = b
        header['e'] = values[1] if values[1] != -12345 else None
        
        # Parse 11th line to get distance
        values = [float(x) for x in lines[10].split()]
        header['dist'] = values[0] if values[0] != -12345 else None  # km
        header['az'] = values[1] if values[1] != -12345 else None    # azimuth
        header['baz'] = values[2] if values[2] != -12345 else None   # back azimuth
        header['gcarc'] = values[3] if values[3] != -12345 else None # great circle distance (degrees)
        
        # Parse station name from text header (line 23)
        station_line = lines[22].strip()
        header['station'] = station_line.split()[0] if station_line else 'UNKNOWN'
        
        # Data starts at line 31 (index 30) - after all header lines
        data_lines = []
        for line in lines[30:]:
            try:
                values = [float(x) for x in line.split()]
                data_lines.extend(values)
            except ValueError:
                # Skip any remaining text lines
                continue
        
        data = np.array(data_lines)
        
        # Create time array
        times = np.arange(len(data)) * delta + b
        
        dist_str = f"{header['gcarc']:.1f}°" if header['gcarc'] else "unknown"
        print(f"  Read {len(data)} samples from {filepath.name}")
        print(f"  Station: {header['station']}, Distance: {dist_str}")
        print(f"  dt={delta}s ({1/delta:.1f} Hz), duration={times[-1]-times[0]:.1f}s")
        
        return times, data, header
        
    except Exception as e:
        print(f"  Error reading {filepath}: {e}")
        import traceback
        traceback.print_exc()
        return None, None, None


def analyze_station_for_sumatra_signal(station_name, times, data, quake_time, plot=False):
    """
    Analyze single station for 18-25 mHz crustal resonance signal
    
    This is analogous to analyze_station_for_38mhz from Tohoku analysis
    but adapted for Sumatra's predicted frequency
    """
    
    # Determine time relative to earthquake
    # Assume data starts at or before earthquake
    # (In real SAC files, this will be in the header)
    
    # For now, assume data is centered on earthquake
    # We'll refine this when we see actual SAC format
    
    # Extract pre-event baseline (for noise comparison)
    sample_rate = 1.0 / np.median(np.diff(times))
    
    # Detrend
    data_detrended = signal.detrend(data)
    
    # Compute power spectral density
    freqs, psd = signal.welch(data_detrended, fs=sample_rate,
                               nperseg=min(8192, len(data)//4),
                               scaling='density')
    
    # Convert to mHz
    freqs_mhz = freqs * 1000
    
    # Find peak in target range (18-25 mHz for Sumatra)
    target_range = (freqs_mhz >= FREQ_RANGE_MHZ[0]) & (freqs_mhz <= FREQ_RANGE_MHZ[1])
    
    if not np.any(target_range):
        return None
    
    peak_idx = target_range.nonzero()[0][np.argmax(psd[target_range])]
    peak_freq = freqs_mhz[peak_idx]
    peak_power = psd[peak_idx]
    
    # Calculate SNR (compare to background)
    bg_idx = np.where((freqs_mhz > 10) & (freqs_mhz < 60))[0]
    bg_power = np.median(psd[bg_idx])
    snr = peak_power / bg_power if bg_power > 0 else 0
    
    # Bandpass filter around predicted frequency
    sos = signal.butter(4, [FREQ_RANGE_MHZ[0]/1000, FREQ_RANGE_MHZ[1]/1000], 
                        btype='bandpass', fs=sample_rate, output='sos')
    filtered = signal.sosfilt(sos, data_detrended)
    amplitude = np.std(filtered)
    
    result = {
        'station': station_name,
        'peak_freq_mhz': peak_freq,
        'peak_power': peak_power,
        'snr': snr,
        'amplitude': amplitude,
        'n_samples': len(data),
        'sample_rate': sample_rate
    }
    
    # Plot if requested
    if plot:
        fig, axes = plt.subplots(3, 1, figsize=(14, 10))
        
        # Plot 1: Time series
        ax = axes[0]
        ax.plot(times/60, data_detrended, 'b-', linewidth=0.5, alpha=0.7)
        ax.set_xlabel('Time (minutes)')
        ax.set_ylabel('Amplitude (detrended)')
        ax.set_title(f'{station_name} - Vertical Component Time Series')
        ax.grid(True, alpha=0.3)
        
        # Plot 2: Frequency spectrum
        ax = axes[1]
        ax.semilogy(freqs_mhz, psd, 'b-', linewidth=1, alpha=0.7)
        ax.axvspan(FREQ_RANGE_MHZ[0], FREQ_RANGE_MHZ[1], color='yellow', alpha=0.2, 
                   label=f'Target range ({FREQ_RANGE_MHZ[0]}-{FREQ_RANGE_MHZ[1]} mHz)')
        ax.axvline(EXPECTED_FREQ_MHZ, color='r', linestyle='--', 
                   label=f'Predicted: {EXPECTED_FREQ_MHZ:.1f} mHz')
        ax.axvline(peak_freq, color='g', linestyle='--', 
                   label=f'Observed: {peak_freq:.1f} mHz')
        
        # Mark Earth's normal modes for comparison
        for mode_name, mode_freq in EARTH_NORMAL_MODES.items():
            ax.axvline(mode_freq, color='purple', linestyle=':', alpha=0.5)
            ax.text(mode_freq, ax.get_ylim()[1]*0.5, mode_name, 
                   rotation=90, va='bottom', fontsize=8, color='purple')
        
        ax.set_xlabel('Frequency (mHz)')
        ax.set_ylabel('Power Spectral Density')
        ax.set_title(f'Spectrum - SNR={snr:.2f}')
        ax.set_xlim(0, 60)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Plot 3: Filtered time series
        ax = axes[2]
        ax.plot(times/60, filtered, 'g-', linewidth=0.8)
        ax.set_xlabel('Time (minutes)')
        ax.set_ylabel('Amplitude (filtered)')
        ax.set_title(f'Bandpass Filtered ({FREQ_RANGE_MHZ[0]}-{FREQ_RANGE_MHZ[1]} mHz)')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f'outputs/visualizations/sumatra_2004_{station_name}_analysis.png', 
                    dpi=150, bbox_inches='tight')
        plt.close()
    
    return result


def main(data_dir):
    """Analyze Sumatra 2004 SAC files"""
    
    print(f"\nSearching for SAC files in: {data_dir}")
    
    # Look for SAC ASCII files (various possible extensions)
    sac_patterns = ['*.sac', '*.SAC', '*.SACA', '*.sac.txt', '*.ascii']
    sac_files = []
    for pattern in sac_patterns:
        sac_files.extend(glob.glob(f"{data_dir}/{pattern}"))
    
    print(f"Found {len(sac_files)} SAC files\n")
    
    if len(sac_files) == 0:
        print("❌ No SAC files found!")
        print("\nExpected file location:")
        print("  Place SAC ASCII files in: data/sumatra_2004/")
        print("  Or specify path with: python analyze_sumatra_2004.py <path>")
        return
    
    results = []
    
    # Analyze each station
    for i, filepath in enumerate(sac_files[:20]):  # First 20 stations
        filepath = Path(filepath)
        station_name = filepath.stem
        
        print(f"[{i+1}/{min(20, len(sac_files))}] Analyzing {station_name}...")
        
        times, data, header = read_sac_ascii(filepath)
        
        if data is None:
            continue
        
        # Analyze for Sumatra signal
        result = analyze_station_for_sumatra_signal(
            station_name, times, data, QUAKE_TIME_UTC, 
            plot=(i < 5)  # Plot first 5 stations
        )
        
        if result is not None:
            results.append(result)
            print(f"  ✓ Peak: {result['peak_freq_mhz']:.1f} mHz, SNR: {result['snr']:.2f}")
    
    # Summary statistics
    if len(results) > 0:
        print("\n" + "="*80)
        print("SUMMARY STATISTICS")
        print("="*80)
        
        peak_freqs = [r['peak_freq_mhz'] for r in results]
        snrs = [r['snr'] for r in results]
        
        print(f"\nAnalyzed {len(results)} stations successfully")
        print(f"\nPeak Frequency Statistics:")
        print(f"  Mean: {np.mean(peak_freqs):.1f} mHz")
        print(f"  Median: {np.median(peak_freqs):.1f} mHz")
        print(f"  Std Dev: {np.std(peak_freqs):.1f} mHz")
        print(f"  Predicted: {EXPECTED_FREQ_MHZ:.1f} mHz")
        print(f"  Error: {abs(np.median(peak_freqs) - EXPECTED_FREQ_MHZ):.1f} mHz ({abs(np.median(peak_freqs) - EXPECTED_FREQ_MHZ)/EXPECTED_FREQ_MHZ*100:.1f}%)")
        
        print(f"\nSNR Statistics:")
        print(f"  Mean: {np.mean(snrs):.2f}")
        print(f"  Median: {np.median(snrs):.2f}")
        print(f"  Max: {np.max(snrs):.2f}")
        
        # Find strong candidates
        strong_signal = [r for r in results 
                        if abs(r['peak_freq_mhz'] - EXPECTED_FREQ_MHZ) < 5 
                        and r['snr'] > 1.5]
        
        print(f"\n⚠️  STRONG CANDIDATES (freq within 5 mHz, SNR > 1.5): {len(strong_signal)}")
        
        if strong_signal:
            print("\nStations showing potential gravitational decoupling signature:")
            for r in strong_signal[:10]:
                print(f"  {r['station']}: {r['peak_freq_mhz']:.1f} mHz, SNR={r['snr']:.2f}")
        
        # Comparison to other events
        print("\n" + "="*80)
        print("CROSS-EVENT COMPARISON")
        print("="*80)
        print(f"\n{'Event':<20} {'Magnitude':<12} {'Predicted':<15} {'Observed':<15} {'Error':<10}")
        print("-"*80)
        print(f"{'Tohoku 2011':<20} {'M9.0':<12} {'29.2 mHz':<15} {'38 mHz':<15} {'23%':<10}")
        print(f"{'Mars S1000a':<20} {'M4.2':<12} {'15.0 mHz':<15} {'13.3 mHz':<15} {'11%':<10}")
        print(f"{'Sumatra 2004':<20} {f'M{QUAKE_MAG}':<12} {f'{EXPECTED_FREQ_MHZ:.1f} mHz':<15} {f'{np.median(peak_freqs):.1f} mHz':<15} {f'{abs(np.median(peak_freqs) - EXPECTED_FREQ_MHZ)/EXPECTED_FREQ_MHZ*100:.1f}%':<10}")
        
        print("\n" + "="*80)
        print("INTERPRETATION")
        print("="*80)
        print("\nIf crustal resonance signal is present:")
        print("  ✓ Frequency should match prediction (18-25 mHz)")
        print("  ✓ Signal should appear 5-10 minutes after mainshock")
        print("  ✓ SNR should be elevated (>1.5)")
        print("  ✓ Pattern should be non-localized (many stations)")
        print("\nCompare to:")
        print("  • Tohoku 2011: Unilateral rupture → 38 mHz signal detected ✓")
        print("  • Chile 2010: Bilateral rupture → no signal detected ✗")
        print("  • Sumatra 2004: Unilateral rupture → signal expected ✓")
        print("\nFramework prediction: Unilateral rupture creates coherent vibration")
        print("→ Gravitational coupling modulation → Crustal resonance")
        print("="*80)
    
    else:
        print("\n❌ No successful analyses")


if __name__ == "__main__":
    import sys
    
    # Default data directory
    data_dir = "data/sumatra_2004"
    
    # Allow command-line override
    if len(sys.argv) > 1:
        data_dir = sys.argv[1]
    
    # Check if directory exists
    if not Path(data_dir).exists():
        print(f"Creating directory: {data_dir}")
        Path(data_dir).mkdir(parents=True, exist_ok=True)
        print("\n📥 Place your SAC ASCII files in this directory")
        print("   Then run: python analyze_sumatra_2004.py")
    else:
        main(data_dir)
