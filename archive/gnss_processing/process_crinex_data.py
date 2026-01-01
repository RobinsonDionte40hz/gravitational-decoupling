"""
Process CRINEX GNSS data: decompress to RINEX, then parse and save analysis results.
Saves output to simulations/ folder, not downloads.
"""
import hatanaka
import numpy as np
from datetime import datetime, timedelta
import json
import os

def decompress_crinex_to_rinex(crinex_path, rinex_path):
    """Decompress CRINEX and write RINEX file to disk"""
    
    print(f"Reading CRINEX file: {crinex_path}")
    with open(crinex_path, 'r', encoding='latin-1') as f:
        compressed = f.read()
    
    print(f"Decompressing {len(compressed):,} bytes...")
    decompressed = hatanaka.decompress(compressed)
    
    print(f"Writing RINEX file: {rinex_path}")
    with open(rinex_path, 'w', encoding='latin-1') as f:
        f.write(decompressed)
    
    size = os.path.getsize(rinex_path)
    print(f"✓ Created RINEX file: {size / 1e6:.1f} MB")
    return rinex_path

def parse_rinex_file(rinex_path, output_json):
    """Parse RINEX file and save analysis to JSON"""
    
    print(f"\nParsing RINEX file: {rinex_path}")
    
    print(f"Parsing RINEX data ({len(decompressed):,} bytes)...")
    lines = decompressed.split('\n')
    
    # Parse header
    header = {}
    data_start = 0
    for i, line in enumerate(lines):
        if 'END OF HEADER' in line:
            data_start = i + 1
            break
        if 'MARKER NAME' in line:
            header['station'] = line[:60].strip()
        if 'APPROX POSITION XYZ' in line:
            coords = line[:60].split()
            header['position'] = [float(x) for x in coords[:3]]
        if 'INTERVAL' in line:
            header['interval'] = float(line.split()[0])
    
    print(f"Station: {header.get('station', 'Unknown')}")
    print(f"Position: {header.get('position', 'Unknown')}")
    print(f"Interval: {header.get('interval', 'Unknown')} sec")
    
    # Parse epochs (time stamps)
    epochs = []
    current_epoch = None
    
    for i in range(data_start, min(data_start + 100000, len(lines))):
        line = lines[i]
        if not line or len(line) < 30:
            continue
            
        # Check if this is an epoch line (starts with > or space followed by date)
        if line.startswith('>') or (line[0] == ' ' and len(line) > 26):
            try:
                # Try to parse epoch line
                if line.startswith('>'):
                    parts = line.split()
                    if len(parts) >= 7:
                        year = int(parts[1])
                        month = int(parts[2])
                        day = int(parts[3])
                        hour = int(parts[4])
                        minute = int(parts[5])
                        second = float(parts[6])
                        
                        dt = datetime(year, month, day, hour, minute, int(second))
                        current_epoch = dt.timestamp()
                        epochs.append(current_epoch)
            except:
                continue
    
    print(f"Found {len(epochs)} epochs")
    
    if len(epochs) > 1:
        time_diffs = np.diff(epochs)
        actual_rate = 1.0 / np.median(time_diffs)
        duration_hours = (epochs[-1] - epochs[0]) / 3600
        
        analysis = {
            'file': crinex_path.split('\\')[-1],
            'station': header.get('station', 'Unknown'),
            'position': header.get('position', None),
            'num_epochs': len(epochs),
            'sampling_rate_hz': round(actual_rate, 2),
            'duration_hours': round(duration_hours, 2),
            'start_time': datetime.fromtimestamp(epochs[0]).isoformat(),
            'end_time': datetime.fromtimestamp(epochs[-1]).isoformat(),
            'median_interval_sec': round(np.median(time_diffs), 3),
        }
        
        print("\n=== ANALYSIS RESULTS ===")
        for key, val in analysis.items():
            print(f"{key}: {val}")
        
        # Save to JSON
        with open(output_json, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        print(f"\n✓ Saved results to: {output_json}")
        return analysis
    else:
        print("ERROR: Could not parse epoch data")
        return None

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        input_path = sys.argv[1]
    else:
        input_path = r'c:\Users\ROB\Downloads\ab180050.22d\ab180050.22d'
    
    output_path = r'c:\Users\ROB\Files\Projects\decoup\simulations\gnss_analysis_ab180050.json'
    
    decompress_and_parse(input_path, output_path)
