"""
Batch Analysis of Multiple Marsquakes for Statistical Validation

Analyzes 10-20 marsquake events to test if the 15 mHz signal pattern
is statistically significant across multiple events.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta
import json
import warnings

warnings.filterwarnings('ignore')

# Constants
PREDICTED_MARS_FREQ_MHZ = 15.0
TARGET_FREQ_RANGE = (10, 30)  # mHz


class MarsquakeAnalyzer:
    """Analyze individual marsquake events for frequency patterns"""
    
    def __init__(self, data_dir='data/mars_insight'):
        self.data_dir = Path(data_dir)
        self.components = None
        
    def load_data(self, start_date, duration_hours=24):
        """Load Mars data for a specific time period"""
        # For now, we'll work with the sol 1000 data we have
        # In a real implementation, you'd load different date ranges
        
        files = list(self.data_dir.glob("*.csv"))
        if not files:
            return None
            
        components = {}
        
        for file in files:
            try:
                filename = file.name.lower()
                if 'bhu' in filename:
                    comp_name = 'BHU'
                elif 'bhv' in filename:
                    comp_name = 'BHV'
                elif 'bhw' in filename:
                    comp_name = 'BHW'
                else:
                    continue
                
                # Parse metadata
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
                
                # Read data
                df = pd.read_csv(file, comment='#', skiprows=0)
                
                if 'Time' in df.columns or df.columns[0] == 'Time':
                    pass
                else:
                    if isinstance(df.iloc[0, 1], str) and 'Sample' in str(df.iloc[0, 1]):
                        df = df.iloc[1:].reset_index(drop=True)
                        df.columns = ['Time', 'Sample']
                
                data = pd.to_numeric(df.iloc[:, 1], errors='coerce').values / scale_factor
                
                components[comp_name] = {
                    'data': data,
                    'sample_rate': sample_rate,
                    'start_time': datetime.fromisoformat(start_time.replace('Z', '+00:00')),
                    'n_samples': len(data)
                }
                
            except Exception as e:
                print(f"Error loading {file.name}: {e}")
                continue
        
        self.components = components
        return components
    
    def find_event(self, event_time=None):
        """Find event time (either provided or by max amplitude)"""
        if event_time:
            return event_time
        
        # Find by max amplitude
        comp_name = 'BHU' if 'BHU' in self.components else list(self.components.keys())[0]
        comp = self.components[comp_name]
        
        data = comp['data']
        max_idx = np.argmax(np.abs(data))
        event_time = comp['start_time'] + timedelta(seconds=max_idx / comp['sample_rate'])
        
        return event_time
    
    def extract_windows(self, event_time):
        """Extract pre-event and post-event time windows"""
        comp_name = 'BHU' if 'BHU' in self.components else list(self.components.keys())[0]
        comp = self.components[comp_name]
        
        # Time windows
        pre_start = event_time - timedelta(minutes=10)
        pre_end = event_time - timedelta(minutes=1)
        post_start = event_time + timedelta(minutes=5)
        post_end = event_time + timedelta(minutes=20)
        
        # Convert to sample indices
        start_time = comp['start_time']
        sample_rate = comp['sample_rate']
        data = comp['data']
        
        pre_start_idx = int((pre_start - start_time).total_seconds() * sample_rate)
        pre_end_idx = int((pre_end - start_time).total_seconds() * sample_rate)
        post_start_idx = int((post_start - start_time).total_seconds() * sample_rate)
        post_end_idx = int((post_end - start_time).total_seconds() * sample_rate)
        
        # Clip to valid range
        pre_start_idx = max(0, pre_start_idx)
        pre_end_idx = min(len(data), pre_end_idx)
        post_start_idx = max(0, post_start_idx)
        post_end_idx = min(len(data), post_end_idx)
        
        return {
            'pre': data[pre_start_idx:pre_end_idx],
            'post': data[post_start_idx:post_end_idx],
            'sample_rate': sample_rate
        }
    
    def spectral_analysis(self, data, fs):
        """Compute power spectral density"""
        data_detrended = signal.detrend(data)
        
        freqs, psd = signal.welch(data_detrended, fs=fs,
                                   nperseg=min(8192, len(data)//4),
                                   scaling='density')
        
        freqs_mhz = freqs * 1000
        
        # Find peak in target range
        target_range = (freqs_mhz >= TARGET_FREQ_RANGE[0]) & (freqs_mhz <= TARGET_FREQ_RANGE[1])
        
        if np.any(target_range):
            peak_idx = target_range.nonzero()[0][np.argmax(psd[target_range])]
            peak_freq = freqs_mhz[peak_idx]
            peak_power = psd[peak_idx]
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
            'snr': snr
        }
    
    def analyze_event(self, event_id, event_time=None):
        """Complete analysis of a single event"""
        if self.components is None:
            return None
        
        # Find event time
        detected_time = self.find_event(event_time)
        
        # Extract windows
        windows = self.extract_windows(detected_time)
        
        # Spectral analysis
        results_pre = self.spectral_analysis(windows['pre'], windows['sample_rate'])
        results_post = self.spectral_analysis(windows['post'], windows['sample_rate'])
        
        # Calculate enhancement
        enhancement = results_post['peak_power'] / results_pre['peak_power'] if results_pre['peak_power'] > 0 else 0
        
        # Check frequency match
        freq_match = abs(results_post['peak_freq'] - PREDICTED_MARS_FREQ_MHZ) < 5
        
        return {
            'event_id': event_id,
            'event_time': detected_time.isoformat(),
            'pre_peak_freq': results_pre['peak_freq'],
            'pre_peak_power': results_pre['peak_power'],
            'pre_snr': results_pre['snr'],
            'post_peak_freq': results_post['peak_freq'],
            'post_peak_power': results_post['peak_power'],
            'post_snr': results_post['snr'],
            'enhancement': enhancement,
            'freq_match': freq_match,
            'error_mhz': abs(results_post['peak_freq'] - PREDICTED_MARS_FREQ_MHZ)
        }


class ControlAnalyzer:
    """Analyze random time windows for control comparison"""
    
    def __init__(self, data_dir='data/mars_insight'):
        self.data_dir = Path(data_dir)
        self.components = None
        
    def load_data(self):
        """Load full dataset"""
        analyzer = MarsquakeAnalyzer(self.data_dir)
        self.components = analyzer.load_data(None)
        return self.components is not None
    
    def extract_random_window(self, duration_minutes=15):
        """Extract a random time window (no earthquake)"""
        comp_name = 'BHU' if 'BHU' in self.components else list(self.components.keys())[0]
        comp = self.components[comp_name]
        
        data = comp['data']
        sample_rate = comp['sample_rate']
        
        # Random start point (avoid edges)
        window_samples = int(duration_minutes * 60 * sample_rate)
        max_start = len(data) - window_samples - 1000
        
        if max_start < 1000:
            return None
        
        start_idx = np.random.randint(1000, max_start)
        window_data = data[start_idx:start_idx + window_samples]
        
        return {
            'data': window_data,
            'sample_rate': sample_rate
        }
    
    def analyze_random_windows(self, n_windows=20):
        """Analyze multiple random windows for comparison"""
        if self.components is None:
            if not self.load_data():
                return None
        
        results = []
        
        for i in range(n_windows):
            window = self.extract_random_window()
            
            if window is None:
                continue
            
            # Spectral analysis
            data_detrended = signal.detrend(window['data'])
            freqs, psd = signal.welch(data_detrended, fs=window['sample_rate'],
                                       nperseg=min(8192, len(window['data'])//4),
                                       scaling='density')
            
            freqs_mhz = freqs * 1000
            target_range = (freqs_mhz >= TARGET_FREQ_RANGE[0]) & (freqs_mhz <= TARGET_FREQ_RANGE[1])
            
            if np.any(target_range):
                peak_idx = target_range.nonzero()[0][np.argmax(psd[target_range])]
                peak_freq = freqs_mhz[peak_idx]
                peak_power = psd[peak_idx]
                bg_power = np.median(psd[target_range])
                snr = peak_power / bg_power if bg_power > 0 else 0
            else:
                peak_freq = 0
                peak_power = 0
                snr = 0
            
            results.append({
                'window_id': i,
                'peak_freq': peak_freq,
                'peak_power': peak_power,
                'snr': snr,
                'error_from_prediction': abs(peak_freq - PREDICTED_MARS_FREQ_MHZ)
            })
        
        return results


def visualize_batch_results(event_results, control_results):
    """Create comprehensive visualization of batch analysis"""
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('Batch Mars Analysis: Multiple Events + Controls', fontsize=16, fontweight='bold')
    
    # Convert to arrays
    event_freqs = [r['post_peak_freq'] for r in event_results]
    event_enhancements = [r['enhancement'] for r in event_results]
    event_errors = [r['error_mhz'] for r in event_results]
    
    control_freqs = [r['peak_freq'] for r in control_results]
    control_errors = [r['error_from_prediction'] for r in control_results]
    
    # Plot 1: Frequency Distribution
    ax1 = axes[0, 0]
    ax1.hist(event_freqs, bins=15, alpha=0.7, label='Post-Event', color='red', edgecolor='black')
    ax1.hist(control_freqs, bins=15, alpha=0.7, label='Random (Control)', color='blue', edgecolor='black')
    ax1.axvline(PREDICTED_MARS_FREQ_MHZ, color='green', linestyle='--', linewidth=2, label='Predicted 15 mHz')
    ax1.set_xlabel('Peak Frequency (mHz)')
    ax1.set_ylabel('Count')
    ax1.set_title('Frequency Distribution: Events vs Controls')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Enhancement Ratios
    ax2 = axes[0, 1]
    event_ids = range(len(event_results))
    ax2.bar(event_ids, event_enhancements, color='orange', edgecolor='black', alpha=0.7)
    ax2.axhline(1.5, color='red', linestyle='--', linewidth=2, label='S1000a Enhancement')
    ax2.axhline(1.0, color='gray', linestyle=':', linewidth=1, label='No Enhancement')
    ax2.set_xlabel('Event ID')
    ax2.set_ylabel('Enhancement Ratio')
    ax2.set_title('Post-Event Signal Enhancement')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Error from Prediction
    ax3 = axes[0, 2]
    ax3.boxplot([event_errors, control_errors], labels=['Post-Event', 'Random Control'])
    ax3.set_ylabel('Error from 15 mHz (mHz)')
    ax3.set_title('Prediction Error Distribution')
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: Statistical Comparison
    ax4 = axes[1, 0]
    stats_text = f"""
STATISTICAL SUMMARY
{'='*40}

Events Analyzed: {len(event_results)}
Control Windows: {len(control_results)}

POST-EVENT FREQUENCIES:
  Mean: {np.mean(event_freqs):.2f} mHz
  Std:  {np.std(event_freqs):.2f} mHz
  Median: {np.median(event_freqs):.2f} mHz
  
CONTROL FREQUENCIES:
  Mean: {np.mean(control_freqs):.2f} mHz
  Std:  {np.std(control_freqs):.2f} mHz
  Median: {np.median(control_freqs):.2f} mHz

PREDICTION ERROR:
  Events: {np.mean(event_errors):.2f} ± {np.std(event_errors):.2f} mHz
  Control: {np.mean(control_errors):.2f} ± {np.std(control_errors):.2f} mHz

ENHANCEMENT:
  Mean: {np.mean(event_enhancements):.2f}×
  Events > 1.5×: {sum(1 for e in event_enhancements if e > 1.5)}/{len(event_enhancements)}
"""
    ax4.text(0.05, 0.95, stats_text, transform=ax4.transAxes, fontsize=10,
             verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
    ax4.axis('off')
    
    # Plot 5: Frequency vs Enhancement
    ax5 = axes[1, 1]
    ax5.scatter(event_freqs, event_enhancements, s=100, alpha=0.7, color='red', edgecolor='black', label='Events')
    ax5.axvline(PREDICTED_MARS_FREQ_MHZ, color='green', linestyle='--', linewidth=2, alpha=0.5)
    ax5.axhline(1.5, color='orange', linestyle='--', linewidth=2, alpha=0.5)
    ax5.set_xlabel('Peak Frequency (mHz)')
    ax5.set_ylabel('Enhancement Ratio')
    ax5.set_title('Frequency vs Enhancement Correlation')
    ax5.legend()
    ax5.grid(True, alpha=0.3)
    
    # Plot 6: Cumulative Distribution
    ax6 = axes[1, 2]
    event_errors_sorted = np.sort(event_errors)
    control_errors_sorted = np.sort(control_errors)
    ax6.plot(event_errors_sorted, np.linspace(0, 1, len(event_errors_sorted)), 
             'r-', linewidth=2, label='Post-Event')
    ax6.plot(control_errors_sorted, np.linspace(0, 1, len(control_errors_sorted)),
             'b-', linewidth=2, label='Random Control')
    ax6.set_xlabel('Error from Prediction (mHz)')
    ax6.set_ylabel('Cumulative Probability')
    ax6.set_title('Cumulative Error Distribution')
    ax6.legend()
    ax6.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    output_dir = Path('outputs/visualizations')
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / 'mars_batch_analysis.png'
    
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\n✓ Batch visualization saved to: {output_file}")
    
    plt.show()


def run_batch_analysis():
    """Run complete batch analysis"""
    print("="*80)
    print("MARS BATCH ANALYSIS: MULTIPLE EVENTS + CONTROL")
    print("="*80)
    
    # For now, we only have S1000a data
    # In a full implementation, you'd load multiple events
    print("\n⚠️  NOTE: Currently only S1000a data is available")
    print("   This demonstrates the analysis pipeline for when more data is loaded\n")
    
    # Analyze S1000a (our single event for now)
    print("Analyzing S1000a event...")
    analyzer = MarsquakeAnalyzer()
    components = analyzer.load_data(None)
    
    if components:
        result = analyzer.analyze_event('S1000a')
        event_results = [result]
        
        print(f"\n✓ S1000a Analysis:")
        print(f"   Post-event peak: {result['post_peak_freq']:.1f} mHz")
        print(f"   Enhancement: {result['enhancement']:.2f}×")
        print(f"   Error: {result['error_mhz']:.2f} mHz")
    else:
        print("✗ Failed to load event data")
        return
    
    # Run control analysis
    print("\n" + "="*80)
    print("CONTROL ANALYSIS: Random Time Windows")
    print("="*80)
    
    control = ControlAnalyzer()
    if control.load_data():
        print("\nAnalyzing 20 random time windows (no earthquakes)...")
        control_results = control.analyze_random_windows(20)
        
        print(f"\n✓ Control Analysis Complete:")
        print(f"   Windows analyzed: {len(control_results)}")
        print(f"   Mean frequency: {np.mean([r['peak_freq'] for r in control_results]):.1f} mHz")
        print(f"   Mean error: {np.mean([r['error_from_prediction'] for r in control_results]):.1f} mHz")
    else:
        print("✗ Failed to load control data")
        return
    
    # Visualize results
    print("\n" + "="*80)
    print("GENERATING VISUALIZATION")
    print("="*80)
    
    visualize_batch_results(event_results, control_results)
    
    # Save results to JSON
    output_dir = Path('outputs')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Convert bool to int for JSON serialization
    event_results_clean = []
    for r in event_results:
        r_copy = r.copy()
        r_copy['freq_match'] = int(r_copy['freq_match'])
        event_results_clean.append(r_copy)
    
    results_data = {
        'event_results': event_results_clean,
        'control_results': control_results,
        'analysis_date': datetime.now().isoformat(),
        'predicted_frequency_mhz': PREDICTED_MARS_FREQ_MHZ
    }
    
    with open(output_dir / 'batch_analysis_results.json', 'w') as f:
        json.dump(results_data, f, indent=2)
    
    print("\n✓ Results saved to: outputs/batch_analysis_results.json")
    
    # Statistical test
    print("\n" + "="*80)
    print("STATISTICAL SIGNIFICANCE")
    print("="*80)
    
    event_errors = [r['error_mhz'] for r in event_results]
    control_errors = [r['error_from_prediction'] for r in control_results]
    
    from scipy.stats import mannwhitneyu
    
    if len(event_results) > 1 and len(control_results) > 1:
        statistic, p_value = mannwhitneyu(event_errors, control_errors, alternative='less')
        print(f"\nMann-Whitney U test:")
        print(f"  H0: Event errors = Control errors")
        print(f"  H1: Event errors < Control errors (closer to prediction)")
        print(f"  Statistic: {statistic}")
        print(f"  p-value: {p_value:.4f}")
        
        if p_value < 0.05:
            print(f"\n  ✓ SIGNIFICANT: Events are closer to prediction than random (p < 0.05)")
        else:
            print(f"\n  ✗ NOT SIGNIFICANT: No statistical difference (p ≥ 0.05)")
    else:
        print("\n⚠️  Need more events for statistical test")
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)
    print("\nNext steps:")
    print("1. Obtain additional marsquake data from InSight archive")
    print("2. Re-run this script with multiple events")
    print("3. Statistical power increases with N > 10 events")


if __name__ == "__main__":
    run_batch_analysis()
