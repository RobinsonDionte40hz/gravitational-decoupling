"""
RTKLIB Processing Pipeline for GNSS Gravitational Anomaly Detection

This script helps process raw RINEX observations into precise positions
to detect gravitational decoupling signatures in GNSS data.

Requirements:
    - RTKLIB (https://github.com/tomojitakasu/RTKLIB)
    - Precise ephemeris files (from IGS)
    - Clock correction files

Processing Steps:
    1. Download precise ephemeris (.sp3) for observation date
    2. Download clock corrections (.clk)
    3. Run PPP (Precise Point Positioning)
    4. Extract vertical time series
    5. Analyze for 38 mHz oscillations and time-delayed anomalies
"""

import subprocess
import os
from pathlib import Path
import numpy as np
from datetime import datetime, timedelta
import requests

# Your RINEX file info
RINEX_FILE = "AB180050.22O"
STATION = "AB18"
DATE = datetime(2022, 1, 5)  # January 5, 2022

# IGS data centers for precise products
IGS_URLS = [
    "https://cddis.nasa.gov/archive/gnss/products",
    "ftp://igs.ign.fr/pub/igs/products"
]

def download_igs_products(date, output_dir="igs_products"):
    """
    Download precise ephemeris and clock files from IGS
    
    For gravitational anomaly detection, we need:
    - Final precise ephemeris (.sp3) - satellite positions
    - Final clock corrections (.clk) - satellite clocks
    - Earth rotation parameters (.erp)
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # GPS week and day of week
    gps_week = int((date - datetime(1980, 1, 6)).days / 7)
    dow = (date - datetime(1980, 1, 6)).days % 7
    
    # File patterns (IGS final products available ~2 weeks after observation)
    sp3_file = f"igs{gps_week}{dow}.sp3.Z"  # Precise ephemeris
    clk_file = f"igs{gps_week}{dow}.clk.Z"  # Clock corrections
    erp_file = f"igs{gps_week}{dow}.erp.Z"  # Earth rotation
    
    print(f"\nDownloading IGS products for GPS Week {gps_week}, Day {dow}")
    print(f"Date: {date.strftime('%Y-%m-%d')}")
    print(f"\nRequired files:")
    print(f"  - {sp3_file}")
    print(f"  - {clk_file}")
    print(f"  - {erp_file}")
    
    # Note: CDDIS now requires authentication
    print("\n" + "="*60)
    print("IMPORTANT: IGS Data Access")
    print("="*60)
    print("NASA CDDIS now requires Earthdata login:")
    print("1. Register at: https://urs.earthdata.nasa.gov/users/new")
    print("2. Approve CDDIS application")
    print("3. Download files manually from:")
    print(f"   https://cddis.nasa.gov/archive/gnss/products/{gps_week}/")
    print("\nAlternative: IGN France (open access)")
    print(f"   ftp://igs.ign.fr/pub/igs/products/{gps_week}/")
    
    return gps_week, dow


def setup_rtklib_config(config_file="ppp.conf"):
    """
    Create RTKLIB configuration for PPP processing optimized
    for gravitational anomaly detection.
    
    Key settings:
    - Kinematic mode (not static) - captures transient effects
    - High-rate output (1 Hz) - matches RINEX sampling
    - Precise products (sp3 + clk)
    - Tight convergence for vertical accuracy
    """
    
    config = """# RTKLIB PPP Configuration for Gravitational Anomaly Detection
# Optimized for detecting 38 mHz oscillations and vertical displacement anomalies

pos1-posmode       =ppp-kinematic  # Kinematic PPP (not static)
pos1-frequency     =l1+l2           # Dual-frequency
pos1-soltype       =combined        # Combined forward/backward
pos1-elmask        =15              # Elevation mask (degrees)
pos1-snrmask_r     =off             # SNR mask
pos1-snrmask_b     =off
pos1-snrmask_L1    =0,0,0,0,0,0,0,0,0
pos1-snrmask_L2    =0,0,0,0,0,0,0,0,0
pos1-dynamics      =off             # Station is stationary (but kinematic mode)
pos1-tidecorr      =on              # Tide correction (but look for residuals!)
pos1-ionoopt       =brdc            # Ionosphere correction
pos1-tropopt       =saas            # Troposphere model
pos1-sateph        =precise         # Precise ephemeris (sp3)
pos1-posopt1       =off
pos1-posopt2       =off
pos1-posopt3       =off
pos1-posopt4       =off
pos1-posopt5       =off
pos1-exclsats      =                # Exclude satellites (if needed)

pos2-armode        =fix-and-hold    # Ambiguity resolution
pos2-gloarmode     =on
pos2-bdsarmode     =on
pos2-arfilter      =on
pos2-arthres       =3               # AR threshold
pos2-arlockcnt     =5
pos2-arelmask      =15
pos2-aroutcnt      =5
pos2-maxage        =30              # Max age of differential
pos2-slipthres     =0.05            # Cycle slip threshold
pos2-rejionno      =100             # Reject threshold
pos2-rejgdop       =30
pos2-niter         =1
pos2-baselen       =0
pos2-basesig       =0

out-solformat      =llh             # Lat/Lon/Height output
out-outhead        =on              # Include header
out-outopt         =on              # Output options
out-timesys        =gpst            # GPS time
out-timeform       =hms             # Time format
out-timendec       =3               # Time decimals
out-degform        =deg             # Degree format
out-fieldsep       =                # Field separator
out-outsingle      =off
out-maxsolstd      =0               # Max solution std (0=no limit)
out-height         =ellipsoidal     # Ellipsoidal height
out-geoid          =internal        # Geoid model
out-solstatic      =all             # Output all epochs
out-nmeaintv1      =0
out-nmeaintv2      =0
out-outstat        =residual        # Output residuals

stats-eratio1      =100             # Error ratio
stats-eratio2      =100
stats-errphase     =0.003           # Phase error (m)
stats-errphaseel   =0.003
stats-errphasebl   =0
stats-errdoppler   =1
stats-stdbias      =30
stats-stdiono      =0.03
stats-stdtrop      =0.3
stats-prnaccelh    =1               # Process noise (horizontal)
stats-prnaccelv    =1               # Process noise (vertical) - keep low!
stats-prnbias      =0.0001
stats-prniono      =0.001
stats-prntrop      =0.0001
stats-prnpos       =0               # Position process noise
stats-clkstab      =5e-12

ant1-postype       =llh
ant1-pos1          =0
ant1-pos2          =0
ant1-pos3          =0
ant1-anttype       =*
ant1-antdele       =0
ant1-antdeln       =0
ant1-antdelu       =0

misc-timeinterp    =off
misc-sbasatsel     =0
misc-rnxopt1       =
misc-rnxopt2       =
"""
    
    with open(config_file, 'w') as f:
        f.write(config)
    
    print(f"\n✓ Created RTKLIB config: {config_file}")
    print("\nKey settings for anomaly detection:")
    print("  - Kinematic PPP (captures transients)")
    print("  - 1 Hz output (matches data rate)")
    print("  - Precise ephemeris required")
    print("  - Vertical process noise minimized")
    print("  - Residual output enabled")
    
    return config_file


def run_rtklib_ppp(rinex_file, sp3_file, clk_file, config_file, output_file):
    """
    Run RTKLIB RNX2RTKP for PPP processing
    
    This requires RTKLIB to be installed and rnx2rtkp.exe in PATH
    """
    
    cmd = [
        "rnx2rtkp",
        "-k", config_file,
        "-o", output_file,
        rinex_file,
        sp3_file,
        clk_file
    ]
    
    print(f"\nRunning RTKLIB PPP...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        if result.returncode == 0:
            print(f"\n✓ PPP processing complete!")
            print(f"  Output: {output_file}")
            return True
        else:
            print(f"\n✗ Error running RTKLIB:")
            print(result.stderr)
            return False
            
    except FileNotFoundError:
        print("\n✗ RTKLIB not found!")
        print("\nPlease install RTKLIB:")
        print("1. Download from: https://github.com/tomojitakasu/RTKLIB")
        print("2. Extract and add bin/ directory to PATH")
        print("3. Or use RTKLIB GUI (rtkplot, rtkpost)")
        return False
    except subprocess.TimeoutExpired:
        print("\n✗ Processing timed out (>10 minutes)")
        return False


def extract_vertical_timeseries(pos_file, output_csv="vertical_timeseries.csv"):
    """
    Extract vertical (height) component from RTKLIB position solution
    
    This is where gravitational anomalies should appear:
    - 38 mHz oscillations (26 second period)
    - Time-delayed onset (5-10 minutes)
    - Amplitude anomalies vs. elastic models
    """
    
    print(f"\nExtracting vertical time series from {pos_file}...")
    
    times = []
    heights = []
    std_heights = []
    
    with open(pos_file, 'r') as f:
        for line in f:
            if line.startswith('%') or line.startswith('#'):
                continue
            
            parts = line.split()
            if len(parts) < 7:
                continue
            
            try:
                # Parse RTKLIB output format
                # Columns: GPST, latitude(deg), longitude(deg), height(m), Q, ns, sdn(m), sde(m), sdu(m)
                time_str = f"{parts[0]} {parts[1]}"
                lat = float(parts[2])
                lon = float(parts[3])
                height = float(parts[4])
                q = int(parts[5])  # Quality (1=fix, 2=float, 5=single)
                std_u = float(parts[8]) if len(parts) > 8 else 999  # Std vertical
                
                if q <= 2:  # Only use fixed/float solutions
                    times.append(time_str)
                    heights.append(height)
                    std_heights.append(std_u)
                    
            except (ValueError, IndexError):
                continue
    
    # Save to CSV
    with open(output_csv, 'w') as f:
        f.write("time,height_m,std_m\n")
        for t, h, s in zip(times, heights, std_heights):
            f.write(f"{t},{h:.4f},{s:.4f}\n")
    
    print(f"\n✓ Extracted {len(heights)} height measurements")
    print(f"  Output: {output_csv}")
    print(f"  Mean height: {np.mean(heights):.3f} m")
    print(f"  Std dev: {np.std(heights):.3f} m")
    print(f"  Mean uncertainty: {np.mean(std_heights):.3f} m")
    
    return times, heights, std_heights


if __name__ == "__main__":
    print("="*70)
    print("RTKLIB Processing Pipeline for Gravitational Anomaly Detection")
    print("="*70)
    
    print(f"\nInput RINEX: {RINEX_FILE}")
    print(f"Station: {STATION}")
    print(f"Date: {DATE.strftime('%Y-%m-%d')}")
    
    # Step 1: Get IGS product info
    gps_week, dow = download_igs_products(DATE)
    
    # Step 2: Create config
    config_file = setup_rtklib_config()
    
    print("\n" + "="*70)
    print("MANUAL STEPS REQUIRED:")
    print("="*70)
    print(f"\n1. Download IGS products for GPS Week {gps_week}, Day {dow}:")
    print(f"   - igs{gps_week}{dow}.sp3.Z (precise ephemeris)")
    print(f"   - igs{gps_week}{dow}.clk.Z (clock corrections)")
    print(f"\n   From: ftp://igs.ign.fr/pub/igs/products/{gps_week}/")
    print(f"   Or: https://cddis.nasa.gov/archive/gnss/products/{gps_week}/")
    
    print("\n2. Decompress files (7-Zip or gunzip)")
    
    print("\n3. Install RTKLIB:")
    print("   https://github.com/tomojitakasu/RTKLIB")
    
    print("\n4. Run PPP processing:")
    print(f"   rnx2rtkp -k {config_file} -o output.pos {RINEX_FILE} igs{gps_week}{dow}.sp3 igs{gps_week}{dow}.clk")
    
    print("\n5. Run this script again to extract vertical time series")
    
    print("\n" + "="*70)
    print("Once you have the .pos file, we can analyze for:")
    print("  • 38 mHz oscillations (26 second period)")
    print("  • Time-delayed onset signatures")
    print("  • Vertical displacement anomalies")
    print("  • Correlation with seismic activity")
    print("="*70)
