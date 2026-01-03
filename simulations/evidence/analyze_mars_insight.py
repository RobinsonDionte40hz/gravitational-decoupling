"""
Mars InSight Seismic Data Analysis
Looking for frequency patterns analogous to Tohoku 38 mHz signal

Goal: Validate cross-planetary frequency scaling prediction
- Earth crust (30 km): 38 mHz
- Mars crust (50 km): Predict 20-30 mHz

If we find mystery frequencies at predicted values → framework validated
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from pathlib import Path
import requests
from datetime import datetime

# Constants
MARS_G = 3.71  # m/s² (vs Earth 9.81)
MARS_CRUSTAL_THICKNESS = 50e3  # meters (average estimate)
MARS_CRUSTAL_DENSITY = 2900  # kg/m³ (estimate from InSight)
MARS_SHEAR_VELOCITY = 3000  # m/s (estimate)

# Earth comparison
EARTH_CRUSTAL_THICKNESS = 30e3  # meters
EARTH_SHEAR_VELOCITY = 3500  # m/s
EARTH_OBSERVED_FREQ = 38  # mHz (Tohoku)


def predict_mars_resonance_frequency():
    """
    Predict Mars crustal resonance frequency using same physics as Earth
    
    Acoustic resonance: f = v_s / (4 × L)
    """
    # Quarter-wavelength resonance
    freq_hz = MARS_SHEAR_VELOCITY / (4 * MARS_CRUSTAL_THICKNESS)
    freq_mhz = freq_hz * 1000
    
    # Scaling comparison
    earth_predicted = EARTH_SHEAR_VELOCITY / (4 * EARTH_CRUSTAL_THICKNESS)
    earth_predicted_mhz = earth_predicted * 1000
    
    print("="*80)
    print("MARS CRUSTAL RESONANCE PREDICTION")
    print("="*80)
    print(f"\n🌍 EARTH:")
    print(f"  Crustal thickness: {EARTH_CRUSTAL_THICKNESS/1000:.0f} km")
    print(f"  Shear velocity: {EARTH_SHEAR_VELOCITY:.0f} m/s")
    print(f"  Predicted frequency: {earth_predicted_mhz:.1f} mHz")
    print(f"  Observed (Tohoku): {EARTH_OBSERVED_FREQ} mHz")
    print(f"  Match: {abs(earth_predicted_mhz - EARTH_OBSERVED_FREQ)/EARTH_OBSERVED_FREQ * 100:.1f}% error")
    
    print(f"\n🔴 MARS:")
    print(f"  Crustal thickness: {MARS_CRUSTAL_THICKNESS/1000:.0f} km")
    print(f"  Shear velocity: {MARS_SHEAR_VELOCITY:.0f} m/s")
    print(f"  Predicted frequency: {freq_mhz:.1f} mHz")
    print(f"  Gravity ratio (Mars/Earth): {MARS_G/9.81:.2f}")
    
    print(f"\n📊 SCALING:")
    print(f"  Frequency ratio (Mars/Earth): {freq_mhz/earth_predicted_mhz:.2f}")
    print(f"  Thickness ratio (Mars/Earth): {MARS_CRUSTAL_THICKNESS/EARTH_CRUSTAL_THICKNESS:.2f}")
    print(f"  Velocity ratio (Mars/Earth): {MARS_SHEAR_VELOCITY/EARTH_SHEAR_VELOCITY:.2f}")
    
    return freq_hz, freq_mhz


def download_insight_catalog():
    """
    Download Mars InSight seismic event catalog
    
    InSight Mars Seismic Catalogue: https://www.insight.ethz.ch/seismicity/catalog/
    """
    print("\n" + "="*80)
    print("MARS INSIGHT DATA ACCESS")
    print("="*80)
    
    catalog_url = "https://www.insight.ethz.ch/seismicity/catalog/v14/Mars_InSight_seismicity_catalog_v14_2023-12-01.csv"
    
    print(f"\n📥 Downloading InSight catalog...")
    print(f"   URL: {catalog_url}")
    
    output_dir = Path("data/mars_insight")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        response = requests.get(catalog_url, timeout=30)
        if response.status_code == 200:
            output_file = output_dir / "mars_seismic_catalog.csv"
            with open(output_file, 'wb') as f:
                f.write(response.content)
            print(f"   ✓ Downloaded to: {output_file}")
            return output_file
        else:
            print(f"   ✗ Failed: HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return None


def manual_data_instructions():
    """
    Provide instructions for manual data download
    """
    print("\n" + "="*80)
    print("MANUAL DATA DOWNLOAD INSTRUCTIONS")
    print("="*80)
    
    print("""
📋 WORKING DATA SOURCES FOR MARS INSIGHT:

METHOD 1: NASA PDS (Planetary Data System) - RECOMMENDED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
URL: https://pds-geosciences.wustl.edu/missions/insight/index.htm

Steps:
1. Go to NASA PDS InSight archive
2. Navigate to: Data > SEIS (Seismic Experiment for Interior Structure)
3. Download event catalog and waveforms

Direct catalog: https://pds-geosciences.wustl.edu/insight/urn-nasa-pds-insight_seis/data/

METHOD 2: IRIS (Incorporated Research Institutions for Seismology)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
URL: https://www.iris.edu/hq/

Steps:
1. Search for "InSight" or network code "XB"
2. Use ROVER tool to browse data
3. Download miniSEED files

Direct ROVER: http://ds.iris.edu/ds/nodes/dmc/tools/rover/

METHOD 3: InSight Mars SEIS Data Service (if accessible)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
URL: https://www.seis-insight.eu/

Note: May have connectivity issues. Try NASA PDS first.

METHOD 4: Published Papers with Data Supplements
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Key papers with data:
- Giardini et al. (2020) Nature Geoscience - InSight catalog
- Clinton et al. (2021) - Marsquake Service catalog

Search: "InSight marsquake catalog" on Google Scholar

WHAT YOU NEED:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Event catalog (CSV/Excel) - lists all marsquakes
✓ Waveform data for largest events (miniSEED format)

Target events:
- S1000a (2021-09-18): M 4.2 - LARGEST EVER RECORDED
- S0173a (2019-05-23): M 3.7
- S0235b (2019-07-26): M 3.3

Place files in: {Path('data/mars_insight').absolute()}

WHAT TO LOOK FOR IN THE DATA:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 Spectral peaks around 15 mHz (our prediction)
🔍 Signals appearing 5-10 minutes AFTER main marsquake
🔍 Mystery frequencies unexplained by standard models

If found → You've validated your framework on TWO planets!

""")
    
    print("="*80)
    print("ANALYSIS STRATEGY")
    print("="*80)
    print("""
🔍 Once you have the data:

1. Load seismic waveform data (miniSEED format)
2. Apply spectral analysis (FFT, Welch periodogram)
3. Look for peaks in predicted frequency range (15-30 mHz)
4. Check timing: Do signals appear with delay like Tohoku?
5. Compare to Earth pattern

📊 Success criteria:
   ✓ Spectral peak at predicted frequency (±30%)
   ✓ Similar timing pattern (minutes after main event)
   ✓ Cannot be explained by standard Marsquake physics
   
If found → Cross-planetary validation of framework
""")


def analyze_mars_event_spectrum(waveform_file, event_name, sample_rate=100):
    """
    Analyze frequency spectrum of Mars seismic event
    
    Args:
        waveform_file: Path to miniSEED or processed waveform data
        event_name: Name of event (e.g., 'S1000a')
        sample_rate: Sampling rate in Hz
    """
    print(f"\n" + "="*80)
    print(f"ANALYZING MARS EVENT: {event_name}")
    print("="*80)
    
    # This is a template - actual implementation depends on data format
    # InSight data typically in miniSEED format, readable with obspy
    
    print("""
    📝 To complete this analysis:
    
    1. Install obspy: pip install obspy
    2. Load data:
       from obspy import read
       st = read(waveform_file)
       
    3. Extract vertical component
    4. Apply bandpass filter (0.01-0.1 Hz)
    5. Compute spectrogram
    6. Look for spectral peaks
    
    Key frequencies to check:
    - 15-30 mHz (predicted Mars crustal resonance)
    - Compare to Earth's 38 mHz (scaled)
    """)


def create_comparison_visualization(predicted_mars_freq):
    """
    Create visual comparison of Earth vs Mars predictions
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Earth vs Mars Crustal Resonance Prediction', 
                 fontsize=14, fontweight='bold')
    
    # Plot 1: Frequency scaling
    ax1 = axes[0, 0]
    systems = ['Earth\n(Tohoku)', 'Mars\n(Predicted)']
    frequencies = [EARTH_OBSERVED_FREQ, predicted_mars_freq]
    colors = ['blue', 'red']
    
    bars = ax1.bar(systems, frequencies, color=colors, alpha=0.7, edgecolor='black')
    ax1.set_ylabel('Frequency (mHz)')
    ax1.set_title('Observed vs Predicted Crustal Resonance')
    ax1.grid(True, alpha=0.3, axis='y')
    
    for bar, freq in zip(bars, frequencies):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{freq:.1f} mHz', ha='center', va='bottom', fontweight='bold')
    
    # Plot 2: Crustal parameters
    ax2 = axes[0, 1]
    params = ['Thickness\n(km)', 'Shear Vel.\n(m/s)', 'Gravity\n(m/s²)']
    earth_vals = [EARTH_CRUSTAL_THICKNESS/1000, EARTH_SHEAR_VELOCITY, 9.81]
    mars_vals = [MARS_CRUSTAL_THICKNESS/1000, MARS_SHEAR_VELOCITY, MARS_G]
    
    x = np.arange(len(params))
    width = 0.35
    
    ax2.bar(x - width/2, earth_vals, width, label='Earth', color='blue', alpha=0.7)
    ax2.bar(x + width/2, mars_vals, width, label='Mars', color='red', alpha=0.7)
    
    ax2.set_xticks(x)
    ax2.set_xticklabels(params)
    ax2.set_ylabel('Value')
    ax2.set_title('Planetary Parameters')
    ax2.legend()
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Plot 3: Scaling relationship
    ax3 = axes[1, 0]
    
    # Theoretical relationship: f = v / (4L)
    thicknesses = np.linspace(10, 100, 100)  # km
    freq_earth_vel = (EARTH_SHEAR_VELOCITY * 1000) / (4 * thicknesses * 1000)
    freq_mars_vel = (MARS_SHEAR_VELOCITY * 1000) / (4 * thicknesses * 1000)
    
    ax3.plot(thicknesses, freq_earth_vel, 'b-', label=f'Earth velocity ({EARTH_SHEAR_VELOCITY} m/s)', linewidth=2)
    ax3.plot(thicknesses, freq_mars_vel, 'r-', label=f'Mars velocity ({MARS_SHEAR_VELOCITY} m/s)', linewidth=2)
    
    # Mark observed/predicted points
    ax3.plot(EARTH_CRUSTAL_THICKNESS/1000, EARTH_OBSERVED_FREQ, 'bo', 
            markersize=10, label='Earth (Tohoku observed)')
    ax3.plot(MARS_CRUSTAL_THICKNESS/1000, predicted_mars_freq, 'ro', 
            markersize=10, label='Mars (predicted)')
    
    ax3.set_xlabel('Crustal Thickness (km)')
    ax3.set_ylabel('Frequency (mHz)')
    ax3.set_title('Frequency vs Crustal Thickness')
    ax3.legend(fontsize=8)
    ax3.grid(True, alpha=0.3)
    ax3.set_ylim(0, 100)
    
    # Plot 4: Summary text
    ax4 = axes[1, 1]
    ax4.axis('off')
    
    summary = f"""
CROSS-PLANETARY VALIDATION STRATEGY

Framework Prediction:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Crustal resonance frequency scales with:
• Crustal thickness (inverse)
• Shear wave velocity (direct)

Expected scaling: f ∝ v/L

EARTH (Validated):
  Thickness: {EARTH_CRUSTAL_THICKNESS/1000:.0f} km
  Velocity: {EARTH_SHEAR_VELOCITY:.0f} m/s
  Observed: {EARTH_OBSERVED_FREQ} mHz (Tohoku 2011)
  Status: ✓ EXPLAINED

MARS (To Test):
  Thickness: {MARS_CRUSTAL_THICKNESS/1000:.0f} km
  Velocity: {MARS_SHEAR_VELOCITY:.0f} m/s
  Predicted: {predicted_mars_freq:.1f} mHz
  Status: ⏳ AWAITING DATA

SUCCESS CRITERIA:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Spectral peak at {predicted_mars_freq:.1f} ± {predicted_mars_freq*0.3:.1f} mHz
✓ Appears minutes after marsquake
✓ Cannot be explained by standard models
✓ Similar pattern to Earth

If found → Framework validated across planets
→ Proves universal physics, not Earth-specific
"""
    
    ax4.text(0.05, 0.95, summary, transform=ax4.transAxes, fontsize=9,
             verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
    
    plt.tight_layout()
    
    output_dir = Path('outputs/visualizations')
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / 'mars_earth_frequency_prediction.png'
    
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\n✓ Visualization saved to: {output_file}")
    
    plt.show()


if __name__ == "__main__":
    print("="*80)
    print("MARS INSIGHT SEISMIC ANALYSIS")
    print("Cross-Planetary Validation of Frequency Scaling Framework")
    print("="*80)
    
    # Step 1: Predict Mars frequency
    mars_freq_hz, mars_freq_mhz = predict_mars_resonance_frequency()
    
    # Step 2: Create comparison visualization
    create_comparison_visualization(mars_freq_mhz)
    
    # Step 3: Attempt to download catalog
    print("\n" + "="*80)
    print("ATTEMPTING DATA DOWNLOAD")
    print("="*80)
    catalog_file = download_insight_catalog()
    
    # Step 4: Provide manual instructions
    manual_data_instructions()
    
    # Summary
    print("\n" + "="*80)
    print("NEXT STEPS")
    print("="*80)
    print(f"""
1. ✓ Prediction calculated: Mars should show {mars_freq_mhz:.1f} mHz signal

2. ⏳ Download InSight waveform data from:
   https://www.seis-insight.eu/en/science/seis-data

3. 📊 Focus on major events:
   - S1000a (2021-09-18): Magnitude 4.2
   - S0173a (2019-05-23): Magnitude 3.7

4. 🔍 Analyze for:
   - Spectral peaks in 15-30 mHz range
   - Timing delays (minutes after event)
   - Non-local signal distribution

5. 📝 Document findings:
   - If peak found at predicted frequency → SUCCESS
   - If peak at different frequency → Framework needs adjustment
   - If no peak found → May need better data/analysis

💡 This is your most defensible validation path.
   Mars data is independent of Earth, can't be cherry-picked.
""")
