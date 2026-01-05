"""
Analyze Apollo lunar seismometer data for crustal resonance signals.

Framework Prediction:
- Lunar crust thickness: ~35 km
- Sound velocity in lunar crust: ~4000 m/s
- Expected resonance: f = v/(4L) = 4000/(4*35000) = 28.6 mHz
- Search range: 25-33 mHz

Data: Apollo PSE continuous waveform data in GeoCSV format
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from pathlib import Path
import csv


def read_apollo_csv(filepath):
    """Read Apollo PSE GeoCSV format data."""
    metadata = {}
    time_data = []
    amplitude_data = []
    
    with open(filepath, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if not row:
                continue
            
            # Parse metadata from header
            if row[0].startswith('#'):
                line = ','.join(row)
                if 'sample_rate_hz:' in line:
                    metadata['sample_rate'] = float(line.split(':')[1].strip())
                elif 'start_time:' in line:
                    metadata['start_time'] = line.split(':', 1)[1].strip()
                elif 'sample_count:' in line:
                    metadata['sample_count'] = int(line.split(':')[1].strip())
                elif 'SID:' in line:
                    metadata['station'] = line.split(':')[1].strip()
                continue
            
            # Skip header row
            if row[0] == 'Time':
                continue
            
            # Parse data
            try:
                time_data.append(row[0])
                amplitude_data.append(int(row[1]))
            except (ValueError, IndexError):
                continue
    
    return np.array(amplitude_data), metadata


def analyze_moonquake_signal(filepath, expected_freq=28.6, freq_range=(25, 33)):
    """
    Analyze a single Apollo PSE file for crustal resonance signal.
    
    Args:
        filepath: Path to Apollo CSV file
        expected_freq: Expected resonance frequency in mHz
        freq_range: Tuple of (min, max) frequency range to search in mHz
    """
    print(f"\n{'='*80}")
    print(f"Analyzing: {Path(filepath).name}")
    print(f"{'='*80}")
    
    # Read data
    amplitude, metadata = read_apollo_csv(filepath)
    sample_rate = metadata['sample_rate']
    station = metadata.get('station', 'Unknown')
    
    print(f"Station: {station}")
    print(f"Sample rate: {sample_rate} Hz")
    print(f"Total samples: {len(amplitude)}")
    print(f"Duration: {len(amplitude)/sample_rate/3600:.1f} hours")
    
    # Detrend and normalize
    amplitude = signal.detrend(amplitude)
    amplitude = amplitude / np.std(amplitude)
    
    # Compute power spectral density using Welch's method
    # Use longer segments for better frequency resolution in mHz range
    nperseg = int(sample_rate * 3600)  # 1-hour segments
    
    freqs, psd = signal.welch(
        amplitude,
        fs=sample_rate,
        nperseg=nperseg,
        noverlap=nperseg//2,
        window='hann',
        scaling='density'
    )
    
    # Convert to mHz
    freqs_mhz = freqs * 1000
    
    # Focus on frequency range of interest
    freq_mask = (freqs_mhz >= freq_range[0]) & (freqs_mhz <= freq_range[1])
    target_freqs = freqs_mhz[freq_mask]
    target_psd = psd[freq_mask]
    
    if len(target_freqs) == 0:
        print("ERROR: No data in target frequency range!")
        return None
    
    # Find peak in target range
    peak_idx = np.argmax(target_psd)
    peak_freq = target_freqs[peak_idx]
    peak_power = target_psd[peak_idx]
    
    # Calculate baseline (median of surrounding frequencies)
    baseline_mask = ((freqs_mhz >= 15) & (freqs_mhz < freq_range[0])) | \
                    ((freqs_mhz > freq_range[1]) & (freqs_mhz <= 45))
    baseline_psd = psd[baseline_mask]
    baseline_power = np.median(baseline_psd) if len(baseline_psd) > 0 else np.median(target_psd)
    
    # Signal-to-noise ratio
    snr = peak_power / baseline_power
    
    # Frequency error
    freq_error_pct = abs(peak_freq - expected_freq) / expected_freq * 100
    
    print(f"\nResults:")
    print(f"  Expected frequency: {expected_freq:.1f} mHz")
    print(f"  Peak frequency: {peak_freq:.2f} mHz")
    print(f"  Frequency error: {freq_error_pct:.1f}%")
    print(f"  Peak power: {peak_power:.2e}")
    print(f"  Baseline power: {baseline_power:.2e}")
    print(f"  SNR: {snr:.2f}")
    
    # Create visualization
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    # Full spectrum
    spectrum_mask = (freqs_mhz >= 10) & (freqs_mhz <= 50)
    ax1.semilogy(freqs_mhz[spectrum_mask], psd[spectrum_mask], 'b-', linewidth=0.8)
    ax1.axvline(expected_freq, color='r', linestyle='--', linewidth=2, label=f'Expected ({expected_freq:.1f} mHz)')
    ax1.axvline(peak_freq, color='g', linestyle='--', linewidth=2, label=f'Observed ({peak_freq:.2f} mHz)')
    ax1.axvspan(freq_range[0], freq_range[1], alpha=0.2, color='yellow', label='Search range')
    ax1.set_xlabel('Frequency (mHz)', fontsize=12)
    ax1.set_ylabel('Power Spectral Density', fontsize=12)
    ax1.set_title(f'{station} - Full Spectrum (10-50 mHz)', fontsize=14, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Zoomed view of target range
    ax2.plot(target_freqs, target_psd, 'b-', linewidth=1.5)
    ax2.axvline(expected_freq, color='r', linestyle='--', linewidth=2, label=f'Expected ({expected_freq:.1f} mHz)')
    ax2.axvline(peak_freq, color='g', linestyle='--', linewidth=2, label=f'Peak ({peak_freq:.2f} mHz)')
    ax2.axhline(baseline_power, color='gray', linestyle=':', linewidth=1.5, label=f'Baseline (SNR={snr:.2f})')
    ax2.fill_between(target_freqs, 0, target_psd, alpha=0.3)
    ax2.set_xlabel('Frequency (mHz)', fontsize=12)
    ax2.set_ylabel('Power Spectral Density', fontsize=12)
    ax2.set_title(f'Target Range ({freq_range[0]}-{freq_range[1]} mHz) - Error: {freq_error_pct:.1f}%', fontsize=14, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save plot
    output_dir = Path('outputs/visualizations/lunar')
    output_dir.mkdir(parents=True, exist_ok=True)
    output_filename = output_dir / f"{Path(filepath).stem}_spectrum.png"
    plt.savefig(output_filename, dpi=150, bbox_inches='tight')
    print(f"\nPlot saved: {output_filename}")
    plt.close()
    
    return {
        'station': station,
        'filename': Path(filepath).name,
        'peak_freq_mhz': peak_freq,
        'expected_freq_mhz': expected_freq,
        'freq_error_pct': freq_error_pct,
        'peak_power': peak_power,
        'baseline_power': baseline_power,
        'snr': snr,
        'duration_hours': len(amplitude)/sample_rate/3600
    }


def main():
    """Analyze all Apollo moonquake data files."""
    data_dir = Path('data/lunar')
    csv_files = sorted(data_dir.glob('*.csv'))
    
    if not csv_files:
        print("No CSV files found in data/lunar/")
        return
    
    print(f"Found {len(csv_files)} Apollo PSE data files")
    print(f"\nLunar Crustal Resonance Prediction:")
    print(f"  Crust thickness: 35 km")
    print(f"  Sound velocity: 4000 m/s")
    print(f"  Expected frequency: 28.6 mHz")
    print(f"  Search range: 25-33 mHz")
    
    results = []
    for csv_file in csv_files:
        try:
            result = analyze_moonquake_signal(csv_file)
            if result:
                results.append(result)
        except Exception as e:
            print(f"\nERROR analyzing {csv_file.name}: {e}")
            continue
    
    # Summary
    if results:
        print(f"\n{'='*80}")
        print("SUMMARY OF ALL ANALYSES")
        print(f"{'='*80}")
        print(f"Total files analyzed: {len(results)}")
        
        peak_freqs = [r['peak_freq_mhz'] for r in results]
        freq_errors = [r['freq_error_pct'] for r in results]
        snrs = [r['snr'] for r in results]
        
        print(f"\nPeak Frequencies:")
        print(f"  Median: {np.median(peak_freqs):.2f} mHz")
        print(f"  Mean: {np.mean(peak_freqs):.2f} mHz ± {np.std(peak_freqs):.2f}")
        print(f"  Range: {np.min(peak_freqs):.2f} - {np.max(peak_freqs):.2f} mHz")
        
        print(f"\nFrequency Errors:")
        print(f"  Median: {np.median(freq_errors):.1f}%")
        print(f"  Mean: {np.mean(freq_errors):.1f}% ± {np.std(freq_errors):.1f}")
        
        print(f"\nSignal-to-Noise Ratios:")
        print(f"  Median: {np.median(snrs):.2f}")
        print(f"  Mean: {np.mean(snrs):.2f} ± {np.std(snrs):.2f}")
        
        print(f"\nIndividual Results:")
        for r in results:
            print(f"  {r['filename']}: {r['peak_freq_mhz']:.2f} mHz (error: {r['freq_error_pct']:.1f}%, SNR: {r['snr']:.2f})")
    
    print(f"\n{'='*80}")


if __name__ == '__main__':
    main()
