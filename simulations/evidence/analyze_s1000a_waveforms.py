"""
Analyze Mars InSight S1000a Event for Predicted 15 mHz Signal

Looking for the Mars equivalent of Tohoku's 38 mHz mystery signal:
- Earth (30 km crust): 38 mHz signal appearing 5-7 min after quake
- Mars (50 km crust): Predicted 15 mHz signal appearing 5-10 min after quake

Target: Sol 1000, S1000a (largest marsquake ever recorded)
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from pathlib import Path
import warnings
import pandas as pd
from datetime import datetime, timedelta

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

# Constants
PREDICTED_MARS_FREQ_MHZ = 15.0  # mHz
PREDICTED_MARS_FREQ_HZ = PREDICTED_MARS_FREQ_MHZ / 1000  # Hz
PREDICTED_PERIOD = 1.0 / PREDICTED_MARS_FREQ_HZ  # seconds (~67 seconds)

# Event information from catalog
S1000A_SOL = 1000
S1000A_MAGNITUDE = 4.2


def load_mars_waveforms(data_dir='data/mars_insight'):
    """
    Load Mars InSight waveform data for sol 1000
    
    Expected files: CSV files with BHU, BHV, BHW components (VBB sensor)
    """
    data_path = Path(data_dir)
    
    print("="*80)
    print("LOADING MARS INSIGHT S1000A DATA")
    print("="*80)
    
    # Look for CSV data files
    files = list(data_path.glob("*.csv"))
    
    if not files:
        print(f"\n❌ No CSV files found in {data_path.absolute()}")
        return None
    
    print(f"\n📁 Found {len(files)} file(s):")
    for f in files:
        print(f"   - {f.name}")
    
    # Load each component
    components = {}
    
    for file in files:
        try:
            # Determine component from filename
            filename = file.name.lower()
            if 'bhu' in filename:
                comp_name = 'BHU'
            elif 'bhv' in filename:
                comp_name = 'BHV'
            elif 'bhw' in filename:
                comp_name = 'BHW'
            else:
                continue
            
            print(f"\n📖 Reading {comp_name}...")
            
            # Parse metadata from header first
            sample_rate = None
            start_time = None
            scale_factor = None
            
            with open(file, 'r') as f:
                for line in f:
                    if not line.startswith('#'):
                        break
                    if 'sample_rate_hz' in line:
                        sample_rate = float(line.split(':')[1].strip())
                    elif 'start_time' in line:
                        start_time = line.split(':', 1)[1].strip()
                    elif 'scale_factor' in line:
                        scale_factor = float(line.split(':')[1].strip())
            
            # Read CSV, skipping comment lines and header row
            df = pd.read_csv(file, comment='#', skiprows=0)
            
            # Handle header row if present
            if 'Time' in df.columns or df.columns[0] == 'Time':
                # Already has column names
                pass
            else:
                # First row might be header
                if isinstance(df.iloc[0, 1], str) and 'Sample' in str(df.iloc[0, 1]):
                    df = df.iloc[1:].reset_index(drop=True)
                    df.columns = ['Time', 'Sample']
            
            # Convert samples to float and then to physical units (m/s)
            data = pd.to_numeric(df.iloc[:, 1], errors='coerce').values / scale_factor
            
            components[comp_name] = {
                'data': data,
                'sample_rate': sample_rate,
                'start_time': datetime.fromisoformat(start_time.replace('Z', '+00:00')),
                'n_samples': len(data)
            }
            
            print(f"   ✓ Loaded {len(data)} samples")
            print(f"   Sample rate: {sample_rate} Hz")
            print(f"   Start time: {start_time}")
            print(f"   Duration: {len(data)/sample_rate/60:.1f} minutes")
            
        except Exception as e:
            print(f"\n❌ Error reading {file.name}: {e}")
            continue
    
    if not components:
        print("\n❌ Failed to load any components")
        return None
    
    return components


def find_event_time(components, method='amplitude'):
    """
    Find the main event time in the waveform
    
    Simple approach: Look for maximum amplitude
    S1000a is known to occur on 2021-09-18 (sol 1000)
    """
    print("\n" + "="*80)
    print("FINDING MAIN EVENT TIME")
    print("="*80)
    
    # Use BHU (vertical) component if available
    comp_name = 'BHU' if 'BHU' in components else list(components.keys())[0]
    comp = components[comp_name]
    
    print(f"\nUsing component: {comp_name}")
    
    # Find maximum amplitude
    data = comp['data']
    max_idx = np.argmax(np.abs(data))
    event_time = comp['start_time'] + timedelta(seconds=max_idx / comp['sample_rate'])
    
    print(f"Main event detected at: {event_time}")
    print(f"Maximum amplitude: {data[max_idx]:.2e} m/s")
    print(f"Time from start: {max_idx / comp['sample_rate'] / 60:.1f} minutes")
    
    return event_time, comp


def extract_time_windows(components, event_time):
    """
    Extract pre-event (baseline) and post-event windows
    
    Pre-event: 10 minutes before event
    Post-event: 5-20 minutes after event (where we expect 15 mHz signal)
    """
    print("\n" + "="*80)
    print("EXTRACTING TIME WINDOWS")
    print("="*80)
    
    # Pre-event baseline (10 minutes before)
    pre_start = event_time - timedelta(minutes=10)
    pre_end = event_time - timedelta(minutes=1)  # 1 minute before (avoid main event)
    
    # Post-event target window (5-20 minutes after)
    post_start = event_time + timedelta(minutes=5)
    post_end = event_time + timedelta(minutes=20)
    
    print(f"\n📊 Time windows:")
    print(f"   Pre-event (baseline):  {pre_start} to {pre_end}")
    print(f"   Post-event (target):   {post_start} to {post_end}")
    
    # Extract windows for each component
    windows = {}
    
    for comp_name, comp in components.items():
        start_time = comp['start_time']
        sample_rate = comp['sample_rate']
        data = comp['data']
        
        # Convert times to sample indices
        pre_start_idx = int((pre_start - start_time).total_seconds() * sample_rate)
        pre_end_idx = int((pre_end - start_time).total_seconds() * sample_rate)
        post_start_idx = int((post_start - start_time).total_seconds() * sample_rate)
        post_end_idx = int((post_end - start_time).total_seconds() * sample_rate)
        
        # Clip to valid range
        pre_start_idx = max(0, pre_start_idx)
        pre_end_idx = min(len(data), pre_end_idx)
        post_start_idx = max(0, post_start_idx)
        post_end_idx = min(len(data), post_end_idx)
        
        windows[comp_name] = {
            'pre': data[pre_start_idx:pre_end_idx],
            'post': data[post_start_idx:post_end_idx],
            'sample_rate': sample_rate
        }
        
        print(f"\n   {comp_name}:")
        print(f"      Pre-event:  {len(windows[comp_name]['pre'])} samples ({len(windows[comp_name]['pre'])/sample_rate:.1f} s)")
        print(f"      Post-event: {len(windows[comp_name]['post'])} samples ({len(windows[comp_name]['post'])/sample_rate:.1f} s)")
    
    return windows


def spectral_analysis(data, fs, label="Signal"):
    """
    Perform spectral analysis on a data array
    Focus on 10-30 mHz range (predicted Mars frequency)
    """
    # Detrend
    data_detrended = signal.detrend(data)
    
    # Compute power spectral density
    freqs, psd = signal.welch(data_detrended, fs=fs, 
                               nperseg=min(8192, len(data)//4),
                               scaling='density')
    
    # Convert to mHz
    freqs_mhz = freqs * 1000
    
    # Focus on target range (10-30 mHz)
    target_range = (freqs_mhz >= 10) & (freqs_mhz <= 30)
    
    # Find peak in target range
    if np.any(target_range):
        peak_idx = target_range.nonzero()[0][np.argmax(psd[target_range])]
        peak_freq = freqs_mhz[peak_idx]
        peak_power = psd[peak_idx]
        
        # Background level
        bg_power = np.median(psd[target_range])
        snr = peak_power / bg_power if bg_power > 0 else 0
    else:
        peak_freq = 0
        peak_power = 0
        snr = 0
    
    return {
        'freqs_mhz': freqs_mhz,
        'psd': psd,
        'peak_freq': peak_freq,
        'peak_power': peak_power,
        'snr': snr,
        'label': label
    }


def analyze_for_mystery_signal(windows):
    """
    Compare pre-event and post-event spectra
    Look for 15 mHz peak appearing in post-event window
    """
    print("\n" + "="*80)
    print("SPECTRAL ANALYSIS - SEARCHING FOR 15 mHz SIGNAL")
    print("="*80)
    
    # Use BHU (vertical) component if available
    comp_name = 'BHU' if 'BHU' in windows else list(windows.keys())[0]
    window = windows[comp_name]
    
    print(f"\nAnalyzing component: {comp_name}")
    
    # Analyze both windows
    results_pre = spectral_analysis(window['pre'], window['sample_rate'], "Pre-event (baseline)")
    results_post = spectral_analysis(window['post'], window['sample_rate'], "Post-event (target)")
    
    # Compare
    print(f"\n📊 RESULTS:")
    print(f"\n   Pre-event (baseline):")
    print(f"      Peak frequency: {results_pre['peak_freq']:.1f} mHz")
    print(f"      Peak power: {results_pre['peak_power']:.2e}")
    print(f"      SNR: {results_pre['snr']:.2f}")
    
    print(f"\n   Post-event (target window):")
    print(f"      Peak frequency: {results_post['peak_freq']:.1f} mHz")
    print(f"      Peak power: {results_post['peak_power']:.2e}")
    print(f"      SNR: {results_post['snr']:.2f}")
    
    # Check if post-event peak matches prediction
    freq_match = abs(results_post['peak_freq'] - PREDICTED_MARS_FREQ_MHZ) < 5  # Within 5 mHz
    enhancement = results_post['peak_power'] / results_pre['peak_power'] if results_pre['peak_power'] > 0 else 0
    
    print(f"\n🎯 PREDICTION CHECK:")
    print(f"   Predicted frequency: {PREDICTED_MARS_FREQ_MHZ} mHz")
    print(f"   Observed peak: {results_post['peak_freq']:.1f} mHz")
    print(f"   Match: {'✓ YES' if freq_match else '✗ NO'} (within ±5 mHz)")
    print(f"   Enhancement: {enhancement:.2f}× baseline")
    
    if freq_match and enhancement > 1.5:
        print(f"\n{'='*80}")
        print("🎉 POSSIBLE DETECTION!")
        print("="*80)
        print("Post-event signal shows:")
        print(f"  • Peak near predicted {PREDICTED_MARS_FREQ_MHZ} mHz")
        print(f"  • {enhancement:.1f}× stronger than baseline")
        print("  • Appearing 5-20 minutes after main event")
        print("\n→ This matches the Tohoku pattern!")
        print("→ Cross-planetary validation of frequency scaling framework")
    elif freq_match:
        print(f"\n⚠️  Peak frequency matches prediction but enhancement is weak")
        print("   May need better noise filtering or different time window")
    else:
        print(f"\n❌ No clear signal at predicted frequency")
        print("   Possible reasons:")
        print("   • Signal may be too weak")
        print("   • Wrong time window")
        print("   • Need different analysis approach")
        print("   • Prediction may need refinement")
    
    return results_pre, results_post, window


def visualize_results(results_pre, results_post, window):
    """
    Create comprehensive visualization
    """
    fig, axes = plt.subplots(3, 2, figsize=(16, 12))
    fig.suptitle('Mars S1000a Event Analysis: Searching for 15 mHz Signal', 
                 fontsize=14, fontweight='bold')
    
    # Plot 1: Pre-event waveform
    ax1 = axes[0, 0]
    time_pre = np.arange(len(window['pre'])) / window['sample_rate']
    ax1.plot(time_pre, window['pre'], 'b-', linewidth=0.5)
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Velocity (m/s)')
    ax1.set_title('Pre-event Waveform (Baseline)')
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Post-event waveform
    ax2 = axes[0, 1]
    time_post = np.arange(len(window['post'])) / window['sample_rate']
    ax2.plot(time_post, window['post'], 'r-', linewidth=0.5)
    ax2.set_xlabel('Time (s)')
    ax2.set_ylabel('Velocity (m/s)')
    ax2.set_title('Post-event Waveform (5-20 min after S1000a)')
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Pre-event spectrum
    ax3 = axes[1, 0]
    target_range_pre = (results_pre['freqs_mhz'] >= 5) & (results_pre['freqs_mhz'] <= 50)
    ax3.semilogy(results_pre['freqs_mhz'][target_range_pre], 
                 results_pre['psd'][target_range_pre], 'b-', linewidth=1)
    ax3.axvline(PREDICTED_MARS_FREQ_MHZ, color='green', linestyle='--', 
                linewidth=2, label=f'Predicted {PREDICTED_MARS_FREQ_MHZ} mHz')
    ax3.set_xlabel('Frequency (mHz)')
    ax3.set_ylabel('Power Spectral Density')
    ax3.set_title('Pre-event Spectrum')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: Post-event spectrum
    ax4 = axes[1, 1]
    target_range_post = (results_post['freqs_mhz'] >= 5) & (results_post['freqs_mhz'] <= 50)
    ax4.semilogy(results_post['freqs_mhz'][target_range_post], 
                 results_post['psd'][target_range_post], 'r-', linewidth=1)
    ax4.axvline(PREDICTED_MARS_FREQ_MHZ, color='green', linestyle='--', 
                linewidth=2, label=f'Predicted {PREDICTED_MARS_FREQ_MHZ} mHz')
    ax4.axvline(results_post['peak_freq'], color='orange', linestyle=':', 
                linewidth=2, label=f'Observed peak {results_post["peak_freq"]:.1f} mHz')
    ax4.set_xlabel('Frequency (mHz)')
    ax4.set_ylabel('Power Spectral Density')
    ax4.set_title('Post-event Spectrum')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    # Plot 5: Comparison (zoomed to target range)
    ax5 = axes[2, 0]
    zoom_range_pre = (results_pre['freqs_mhz'] >= 10) & (results_pre['freqs_mhz'] <= 30)
    zoom_range_post = (results_post['freqs_mhz'] >= 10) & (results_post['freqs_mhz'] <= 30)
    ax5.semilogy(results_pre['freqs_mhz'][zoom_range_pre], 
                 results_pre['psd'][zoom_range_pre], 'b-', linewidth=2, label='Pre-event', alpha=0.7)
    ax5.semilogy(results_post['freqs_mhz'][zoom_range_post], 
                 results_post['psd'][zoom_range_post], 'r-', linewidth=2, label='Post-event', alpha=0.7)
    ax5.axvline(PREDICTED_MARS_FREQ_MHZ, color='green', linestyle='--', 
                linewidth=2, label=f'Predicted {PREDICTED_MARS_FREQ_MHZ} mHz')
    ax5.set_xlabel('Frequency (mHz)')
    ax5.set_ylabel('Power Spectral Density')
    ax5.set_title('Pre vs Post Comparison (Target Range)')
    ax5.legend()
    ax5.grid(True, alpha=0.3)
    
    # Plot 6: Summary text
    ax6 = axes[2, 1]
    ax6.axis('off')
    
    enhancement = results_post['peak_power'] / results_pre['peak_power'] if results_pre['peak_power'] > 0 else 0
    freq_match = abs(results_post['peak_freq'] - PREDICTED_MARS_FREQ_MHZ) < 5
    
    summary = f"""
MARS S1000A ANALYSIS SUMMARY
{'='*40}

Event: S1000a (Sol 1000)
Magnitude: {S1000A_MAGNITUDE}
Largest marsquake ever recorded

FRAMEWORK PREDICTION:
  Mars crustal resonance: {PREDICTED_MARS_FREQ_MHZ} mHz
  (Scaled from Earth's 38 mHz)
  Expected: 5-10 min after main event

OBSERVED RESULTS:
  Post-event peak: {results_post['peak_freq']:.1f} mHz
  Enhancement: {enhancement:.2f}× baseline
  SNR: {results_post['snr']:.2f}
  
  Frequency match: {'✓ YES' if freq_match else '✗ NO'}
  
INTERPRETATION:
"""
    
    if freq_match and enhancement > 1.5:
        summary += """  🎉 POSSIBLE DETECTION
  Signal characteristics match prediction:
  • Peak near 15 mHz
  • Post-event enhancement
  • Similar to Tohoku pattern
  
  → Cross-planetary validation!
"""
    elif freq_match:
        summary += """  ⚠️ WEAK SIGNAL
  Frequency matches but enhancement weak
  May need refined analysis
"""
    else:
        summary += """  ❌ NO CLEAR SIGNAL
  Peak not at predicted frequency
  Further investigation needed
"""
    
    ax6.text(0.05, 0.95, summary, transform=ax6.transAxes, fontsize=10,
             verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
    
    plt.tight_layout()
    
    output_dir = Path('outputs/visualizations')
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / 'mars_s1000a_spectral_analysis.png'
    
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\n✓ Visualization saved to: {output_file}")
    
    plt.show()


if __name__ == "__main__":
    print("="*80)
    print("MARS S1000A SPECTRAL ANALYSIS")
    print("Searching for 15 mHz Signal (Mars equivalent of Tohoku 38 mHz)")
    print("="*80)
    
    # Load data
    components = load_mars_waveforms()
    
    if components is None:
        print("\n" + "="*80)
        print("CANNOT PROCEED - DATA LOADING FAILED")
        print("="*80)
        print("\nPlease ensure:")
        print("1. Data files are in: data/mars_insight/")
        print("2. Files are CSV format from InSight Analyst's Notebook")
    else:
        # Find main event
        event_time, comp = find_event_time(components)
        
        # Extract time windows
        windows = extract_time_windows(components, event_time)
        
        # Spectral analysis
        results_pre, results_post, window = analyze_for_mystery_signal(windows)
        
        # Visualize
        visualize_results(results_pre, results_post, window)
        
        print("\n" + "="*80)
        print("ANALYSIS COMPLETE")
        print("="*80)
        print("\nNext steps:")
        print("1. Review the visualization")
        print("2. If signal found → Document for publication")
        print("3. If not found → Try different time windows or filtering")
        print("4. Compare to Tohoku methodology")
