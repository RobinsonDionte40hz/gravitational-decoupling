"""
Analyze 2011 Tohoku Earthquake GPS Data
Looking for 38 mHz gravitational decoupling signature

Earthquake: 2011-03-11 05:46:23 UTC (14:46:23 JST)
Expected signature:
- 38 mHz oscillation (26 second period)
- Onset 5-7 minutes AFTER mainshock
- Duration ~2 minutes
- Vertical (UP) component primarily affected
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from datetime import datetime, timedelta
from pathlib import Path
import glob

# Earthquake time
QUAKE_TIME_UTC = datetime(2011, 3, 11, 5, 46, 23)
QUAKE_GPS_WEEK = 1626
QUAKE_GPS_SECONDS = 20783  # seconds into GPS week

def parse_kin_file(filepath):
    """Parse kinematic position file"""
    
    data = []
    station_name = None
    
    with open(filepath, 'r') as f:
        for line in f:
            if line.startswith(' STATION'):
                continue
            if line.startswith('---'):
                continue
            if 'LOCAL GEODETIC' in line:
                continue
            if line.strip() == '':
                continue
            
            parts = line.split()
            if len(parts) >= 7:
                try:
                    station = parts[0]
                    week = int(parts[1])
                    seconds = float(parts[2])
                    ns = float(parts[3])  # North/South (m)
                    ew = float(parts[4])  # East/West (m)
                    up = float(parts[5])  # Vertical UP (m)
                    flag = parts[6]
                    
                    if station_name is None:
                        station_name = station
                    
                    data.append({
                        'week': week,
                        'seconds': seconds,
                        'ns': ns,
                        'ew': ew,
                        'up': up,
                        'flag': flag
                    })
                except (ValueError, IndexError):
                    pass
    
    if not data:
        return None, None
    
    # Convert to arrays
    seconds = np.array([d['seconds'] for d in data])
    up = np.array([d['up'] for d in data])
    ns = np.array([d['ns'] for d in data])
    ew = np.array([d['ew'] for d in data])
    
    return station_name, {
        'seconds': seconds,
        'up': up,
        'ns': ns,
        'ew': ew,
        'time_relative_quake': seconds - QUAKE_GPS_SECONDS
    }


def analyze_station_for_38mhz(station_name, data, plot=False):
    """
    Look for 38 mHz signal in vertical component
    Focus on 5-10 minutes after mainshock
    """
    
    time_rel = data['time_relative_quake']
    up = data['up']
    
    # Focus on window: 5-15 minutes after quake
    window_start = 5 * 60  # 5 minutes
    window_end = 15 * 60   # 15 minutes
    
    idx = np.where((time_rel >= window_start) & (time_rel <= window_end))[0]
    
    if len(idx) < 100:
        return None
    
    up_window = up[idx]
    time_window = time_rel[idx]
    
    # Remove linear trend
    p = np.polyfit(time_window, up_window, 1)
    trend = np.polyval(p, time_window)
    up_detrended = up_window - trend
    
    # Compute power spectral density
    sample_rate = 10  # Hz (0.1 sec sampling)
    freqs, psd = signal.welch(up_detrended, fs=sample_rate, 
                               nperseg=min(512, len(up_detrended)//2))
    
    # Convert to mHz
    freqs_mhz = freqs * 1000
    
    # Look for peak around 38 mHz (target frequency)
    target_freq = 38  # mHz
    idx_range = np.where((freqs_mhz > 30) & (freqs_mhz < 50))[0]
    
    if len(idx_range) < 3:
        return None
    
    peak_idx = idx_range[np.argmax(psd[idx_range])]
    peak_freq = freqs_mhz[peak_idx]
    peak_power = psd[peak_idx]
    
    # Background power
    bg_idx = np.where((freqs_mhz > 20) & (freqs_mhz < 60))[0]
    bg_power = np.median(psd[bg_idx])
    snr = peak_power / bg_power if bg_power > 0 else 0
    
    # Also check time domain - look for ~26 second oscillations
    # Bandpass filter around 38 mHz
    sos = signal.butter(4, [0.030, 0.050], btype='bandpass', fs=sample_rate, output='sos')
    up_filtered = signal.sosfilt(sos, up_detrended)
    amplitude = np.std(up_filtered)
    
    result = {
        'station': station_name,
        'peak_freq_mhz': peak_freq,
        'peak_power': peak_power,
        'snr': snr,
        'amplitude_mm': amplitude * 1000,  # Convert to mm
        'n_samples': len(up_detrended)
    }
    
    if plot and snr > 1.5:
        fig, axes = plt.subplots(3, 1, figsize=(14, 10))
        
        # Full time series
        axes[0].plot(time_rel / 60, up * 1000, 'b-', linewidth=0.5, alpha=0.7)
        axes[0].axvline(0, color='r', linestyle='--', label='Mainshock', linewidth=2)
        axes[0].axvspan(5, 15, alpha=0.2, color='yellow', label='Analysis window')
        axes[0].set_xlabel('Time after earthquake (minutes)')
        axes[0].set_ylabel('Vertical displacement (mm)')
        axes[0].set_title(f'Station {station_name} - Full Record')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        
        # Analysis window
        axes[1].plot(time_window / 60, up_filtered * 1000, 'g-', linewidth=1)
        axes[1].set_xlabel('Time after earthquake (minutes)')
        axes[1].set_ylabel('Filtered vertical (mm)')
        axes[1].set_title(f'Bandpass 30-50 mHz (around 38 mHz target)')
        axes[1].grid(True, alpha=0.3)
        
        # Power spectrum
        axes[2].semilogy(freqs_mhz, psd, 'b-', linewidth=1, alpha=0.7)
        axes[2].axvline(38, color='r', linestyle='--', label='38 mHz (Tohoku signal)', linewidth=2)
        axes[2].axvline(peak_freq, color='g', linestyle=':', label=f'Peak: {peak_freq:.1f} mHz', linewidth=2)
        axes[2].set_xlabel('Frequency (mHz)')
        axes[2].set_ylabel('Power Spectral Density')
        axes[2].set_title(f'Spectrum (SNR={snr:.2f})')
        axes[2].set_xlim(10, 100)
        axes[2].legend()
        axes[2].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f'tohoku_{station_name}_analysis.png', dpi=150)
        print(f"  Saved plot: tohoku_{station_name}_analysis.png")
        plt.close()
    
    return result


def main(data_dir):
    """Analyze all stations"""
    
    print("="*70)
    print("2011 TOHOKU EARTHQUAKE - GPS GRAVITATIONAL ANOMALY ANALYSIS")
    print("="*70)
    print(f"\nSearching for 38 mHz signal (26 second period)")
    print(f"Expected onset: 5-7 minutes after mainshock")
    print(f"Expected duration: ~2 minutes")
    print(f"\nEarthquake: {QUAKE_TIME_UTC} UTC")
    print(f"GPS time: Week {QUAKE_GPS_WEEK}, {QUAKE_GPS_SECONDS} seconds\n")
    
    kin_files = glob.glob(f"{data_dir}/*.KIN")
    print(f"Found {len(kin_files)} station files\n")
    
    results = []
    
    # Analyze subset first
    for i, filepath in enumerate(kin_files[:50]):  # First 50 stations
        station_name, data = parse_kin_file(filepath)
        
        if data is None:
            continue
        
        result = analyze_station_for_38mhz(station_name, data, plot=(i < 3))
        
        if result:
            results.append(result)
        
        if (i + 1) % 10 == 0:
            print(f"  Processed {i+1} stations...")
    
    print(f"\n✓ Analyzed {len(results)} stations with sufficient data\n")
    
    # Sort by SNR
    results.sort(key=lambda x: x['snr'], reverse=True)
    
    print("="*70)
    print("TOP 20 STATIONS BY 38 mHz SIGNAL STRENGTH")
    print("="*70)
    print(f"{'Station':<8} {'Peak (mHz)':<12} {'SNR':<8} {'Amplitude (mm)':<15} {'N Samples':<10}")
    print("-"*70)
    
    for r in results[:20]:
        print(f"{r['station']:<8} {r['peak_freq_mhz']:>10.1f}   {r['snr']:>6.2f}   "
              f"{r['amplitude_mm']:>13.3f}   {r['n_samples']:>8}")
    
    # Statistics
    print("\n" + "="*70)
    print("STATISTICAL ANALYSIS")
    print("="*70)
    
    peak_freqs = [r['peak_freq_mhz'] for r in results]
    snrs = [r['snr'] for r in results]
    
    print(f"\nPeak frequency distribution:")
    print(f"  Mean: {np.mean(peak_freqs):.1f} mHz")
    print(f"  Median: {np.median(peak_freqs):.1f} mHz")
    print(f"  Std: {np.std(peak_freqs):.1f} mHz")
    print(f"  Target: 38 mHz")
    
    # How many stations show peak within ±5 mHz of 38?
    near_target = [r for r in results if abs(r['peak_freq_mhz'] - 38) < 5]
    print(f"\nStations with peak within ±5 mHz of 38 mHz: {len(near_target)} ({100*len(near_target)/len(results):.1f}%)")
    
    # How many show SNR > 2 (significant signal)?
    significant = [r for r in results if r['snr'] > 2]
    print(f"Stations with SNR > 2: {len(significant)} ({100*len(significant)/len(results):.1f}%)")
    
    # Combined: near 38 mHz AND high SNR
    strong_signal = [r for r in results if abs(r['peak_freq_mhz'] - 38) < 5 and r['snr'] > 1.5]
    print(f"\n⚠ STRONG 38 mHz CANDIDATES: {len(strong_signal)} stations")
    
    if strong_signal:
        print("\nStations showing potential gravitational decoupling signature:")
        for r in strong_signal[:10]:
            print(f"  {r['station']}: {r['peak_freq_mhz']:.1f} mHz, SNR={r['snr']:.2f}, Amp={r['amplitude_mm']:.2f} mm")
    
    print("\n" + "="*70)
    print("INTERPRETATION")
    print("="*70)
    print("\nIf gravitational decoupling occurred:")
    print("  • Many stations should show 38 mHz peak")
    print("  • Signal appears 5-7 min after mainshock")
    print("  • Lasts ~2 minutes")
    print("  • Vertical component primarily affected")
    print("  • Non-localized (regional phenomenon)")
    
    if len(strong_signal) > 10:
        print(f"\n✓ SIGNIFICANT DETECTION: {len(strong_signal)} stations show signal!")
        print("  This matches the published mystery signal.")
    elif len(near_target) > 15:
        print(f"\n⚠ MODERATE SIGNAL: {len(near_target)} stations near 38 mHz")
        print("  Suggests possible weak effect.")
    else:
        print(f"\n✗ Weak or no detection in this sample")
        print(f"  May need full dataset or different processing.")
    
    print("="*70)
    
    return results


if __name__ == "__main__":
    import sys
    
    data_dir = "/c/Users/ROB/Downloads/repository"
    
    if len(sys.argv) > 1:
        data_dir = sys.argv[1]
    
    if not Path(data_dir).exists():
        print(f"Error: Directory not found: {data_dir}")
        print(f"\nUsage: python analyze_tohoku_gps.py [data_directory]")
        sys.exit(1)
    
    results = main(data_dir)
