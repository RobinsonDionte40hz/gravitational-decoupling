"""
Fetch Jupiter Orbital Elements from NASA JPL Horizons
For validation of orbital stability claims

Uses astroquery to access JPL Horizons ephemeris system
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

try:
    from astroquery.jplhorizons import Horizons
    HORIZONS_AVAILABLE = True
except ImportError:
    HORIZONS_AVAILABLE = False
    print("WARNING: astroquery not installed. Install with: pip install astroquery")


def fetch_jupiter_orbital_elements(start_date='2024-02-01', end_date='2025-02-01', step='1d'):
    """
    Fetch Jupiter orbital elements from JPL Horizons
    
    Parameters:
    -----------
    start_date : str
        Start date in YYYY-MM-DD format
    end_date : str
        End date in YYYY-MM-DD format
    step : str
        Time step (e.g., '1d' for daily, '1h' for hourly)
    
    Returns:
    --------
    pd.DataFrame with orbital elements
    """
    
    if not HORIZONS_AVAILABLE:
        print("\nERROR: astroquery module required")
        print("Install with: pip install astroquery")
        return None
    
    print("="*80)
    print("FETCHING JUPITER ORBITAL DATA FROM NASA JPL HORIZONS")
    print("="*80)
    print(f"\nTarget: Jupiter (599)")
    print(f"Time range: {start_date} to {end_date}")
    print(f"Step size: {step}")
    print(f"Observer: Solar System Barycenter (@0)")
    
    try:
        # Create Horizons query
        # Jupiter NAIF ID: 599
        # Observer: Solar System Barycenter (0)
        obj = Horizons(id='599', 
                       location='@0',  # Solar system barycenter
                       epochs={'start': start_date, 
                              'stop': end_date, 
                              'step': step})
        
        print("\nQuerying JPL Horizons... (this may take 30-60 seconds)")
        
        # Get orbital elements
        # Elements table includes: a, e, i, Omega, omega, M, etc.
        el = obj.elements()
        
        print(f"✓ Successfully retrieved {len(el)} data points")
        
        # Convert to pandas DataFrame
        df = el.to_pandas()
        
        # Select and rename key columns
        columns_of_interest = {
            'datetime_jd': 'julian_date',
            'datetime_str': 'date_time',
            'e': 'eccentricity',
            'a': 'semi_major_axis',  # AU
            'incl': 'inclination',  # degrees
            'Omega': 'ascending_node',  # degrees
            'w': 'arg_perihelion',  # degrees
            'M': 'mean_anomaly',  # degrees
            'Q': 'aphelion',  # AU
            'q': 'perihelion',  # AU
            'P': 'orbital_period',  # days
            'n': 'mean_motion'  # deg/day
        }
        
        # Keep only available columns
        available_cols = {k: v for k, v in columns_of_interest.items() if k in df.columns}
        df_clean = df[list(available_cols.keys())].copy()
        df_clean.columns = list(available_cols.values())
        
        # Convert date string to datetime
        # Horizons format: "A.D. 2024-Feb-01 00:00:00.0000"
        if 'date_time' in df_clean.columns:
            # Remove "A.D." prefix and parse
            df_clean['date'] = df_clean['date_time'].str.replace('A.D. ', '').apply(
                lambda x: pd.to_datetime(x, format='%Y-%b-%d %H:%M:%S.%f')
            )
        
        print("\n--- Data Summary ---")
        print(f"Date range: {df_clean['date'].min()} to {df_clean['date'].max()}")
        print(f"\nOrbital Elements Retrieved:")
        for col in df_clean.columns:
            if col not in ['julian_date', 'date_time', 'date']:
                if col in df_clean.columns:
                    print(f"  {col}: {df_clean[col].mean():.9f} (mean)")
        
        return df_clean
        
    except Exception as e:
        print(f"\nERROR fetching data: {e}")
        print("\nTroubleshooting:")
        print("1. Check internet connection")
        print("2. Verify astroquery is installed: pip install astroquery")
        print("3. Try later if JPL Horizons is down")
        return None


def save_orbital_data(df, output_dir='c:/Users/ROB/Files/Projects/decoup/data'):
    """
    Save orbital elements to CSV
    """
    if df is None:
        print("No data to save")
        return None
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    filename = output_path / 'jupiter_orbital_elements_2024_2025.csv'
    
    df.to_csv(filename, index=False)
    print(f"\n✓ Data saved to: {filename}")
    print(f"  Rows: {len(df)}")
    print(f"  Columns: {len(df.columns)}")
    
    return filename


def quick_analysis(df):
    """
    Quick statistical analysis of orbital elements
    """
    if df is None:
        return
    
    print("\n" + "="*80)
    print("QUICK STATISTICAL ANALYSIS")
    print("="*80)
    
    if 'eccentricity' in df.columns:
        e = df['eccentricity']
        print(f"\nEccentricity Statistics:")
        print(f"  Mean:   {e.mean():.9f}")
        print(f"  Std:    {e.std():.9f}")
        print(f"  Min:    {e.min():.9f}")
        print(f"  Max:    {e.max():.9f}")
        print(f"  Range:  {e.max() - e.min():.9f}")
        
        # Calculate variation
        e_diff = e.diff().abs()
        print(f"\n  Mean daily change: {e_diff.mean():.9f}")
        print(f"  Max daily change:  {e_diff.max():.9f}")
        
        # Find largest perturbations
        print(f"\n  Largest perturbations (|Δe| > {e_diff.mean() + 2*e_diff.std():.9f}):")
        threshold = e_diff.mean() + 2 * e_diff.std()
        large_changes = df[e_diff > threshold]
        
        if len(large_changes) > 0:
            print(f"    Found {len(large_changes)} events")
            for idx in large_changes.index[:5]:  # Show first 5
                if idx > 0:
                    date = df.loc[idx, 'date']
                    e_before = df.loc[idx-1, 'eccentricity']
                    e_after = df.loc[idx, 'eccentricity']
                    change = e_after - e_before
                    print(f"    {date}: {e_before:.9f} → {e_after:.9f} (Δe = {change:+.9f})")
        else:
            print(f"    No large perturbations detected")
    
    if 'semi_major_axis' in df.columns:
        a = df['semi_major_axis']
        print(f"\nSemi-major Axis Statistics:")
        print(f"  Mean:   {a.mean():.9f} AU")
        print(f"  Std:    {a.std():.9f} AU")
        print(f"  Range:  {a.max() - a.min():.9f} AU")


def verify_april_event(df):
    """
    Check if we can verify the April 15-17, 2024 event mentioned in orbital-stability-analysis.txt
    
    Claimed:
    - Initial: EC = 0.04820734143
    - Perturbed: EC = 0.04837645562
    - Recovered: EC = 0.04828425790
    """
    if df is None:
        return
    
    print("\n" + "="*80)
    print("VERIFYING APRIL 15-17, 2024 EVENT")
    print("="*80)
    
    # Filter to April 2024
    df['date'] = pd.to_datetime(df['date'])
    april_data = df[(df['date'] >= '2024-04-15') & (df['date'] <= '2024-04-17')]
    
    if len(april_data) == 0:
        print("WARNING: No data found for April 15-17, 2024")
        return
    
    print(f"\nData for April 15-17, 2024:")
    print(april_data[['date', 'eccentricity']].to_string(index=False))
    
    if len(april_data) >= 3:
        e_values = april_data['eccentricity'].values
        print(f"\nClaimed values from orbital-stability-analysis.txt:")
        print(f"  April 15: EC = 0.04820734143")
        print(f"  April 16: EC = 0.04837645562 (perturbed)")
        print(f"  April 17: EC = 0.04828425790 (recovered)")
        
        print(f"\nActual Horizons data:")
        print(f"  April 15: EC = {e_values[0]:.11f}")
        if len(e_values) > 1:
            print(f"  April 16: EC = {e_values[1]:.11f}")
        if len(e_values) > 2:
            print(f"  April 17: EC = {e_values[2]:.11f}")
        
        # Check if values match within reasonable precision
        claimed_15 = 0.04820734143
        if abs(e_values[0] - claimed_15) < 0.0001:
            print(f"\n✓ April 15 value matches (within 0.0001)")
        else:
            print(f"\n⚠ April 15 value differs by {abs(e_values[0] - claimed_15):.9f}")


def main():
    """
    Main execution
    """
    print("\n" + "="*80)
    print("JUPITER ORBITAL ELEMENTS FETCHER")
    print("="*80)
    print("\nThis script fetches Jupiter's orbital elements from NASA JPL Horizons")
    print("for the period February 2024 - February 2025 to validate")
    print("orbital stability claims in the framework.")
    
    # Fetch data
    df = fetch_jupiter_orbital_elements(
        start_date='2024-02-01',
        end_date='2025-02-01',
        step='1d'  # Daily measurements
    )
    
    if df is not None:
        # Save to CSV
        save_orbital_data(df)
        
        # Quick analysis
        quick_analysis(df)
        
        # Verify April event
        verify_april_event(df)
        
        print("\n" + "="*80)
        print("NEXT STEPS")
        print("="*80)
        print("1. Data saved to CSV ✓")
        print("2. Ready for perturbation event detection")
        print("3. Ready for recovery time analysis")
        print("4. Ready for classical theory comparison")
        
        return df
    else:
        print("\n" + "="*80)
        print("INSTALLATION REQUIRED")
        print("="*80)
        print("\nRun this command:")
        print("  pip install astroquery")
        print("\nThen run this script again.")
        
        return None


if __name__ == "__main__":
    main()
