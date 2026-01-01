"""
Diagnostic tool to identify block types in SBF file
"""

import struct
import sys
from collections import Counter

def diagnose_sbf(filepath):
    """Identify all block types in the SBF file"""
    
    print(f"Diagnosing: {filepath}\n")
    
    SYNC1 = 0x24
    SYNC2 = 0x40
    
    block_ids = Counter()
    block_names = {
        4007: 'PVTGeodetic',
        4006: 'PVTCartesian',
        5891: 'PVTSatCartesian',
        5912: 'PosCart',
        5913: 'PosLocal',
        5914: 'PosProjected',
        4027: 'BaseVectorGeod',
        5905: 'EndOfPVT',
        4013: 'PosCovGeodetic',
        4001: 'MeasEpoch',
        4000: 'GenMeasEpoch',
    }
    
    with open(filepath, 'rb') as f:
        position = 0
        blocks_found = 0
        
        while position < 1000000:  # Check first 1 MB
            f.seek(position)
            sync_test = f.read(2)
            
            if len(sync_test) < 2:
                break
            
            if sync_test[0] == SYNC1 and sync_test[1] == SYNC2:
                try:
                    header_rest = f.read(6)
                    if len(header_rest) < 6:
                        break
                    
                    crc = struct.unpack('<H', header_rest[0:2])[0]
                    id_length = struct.unpack('<H', header_rest[2:4])[0]
                    
                    block_id = id_length & 0x1FFF
                    block_length = ((id_length >> 13) & 0x7) * 4
                    
                    if block_length == 0:
                        length_bytes = f.read(8)
                        if len(length_bytes) >= 2:
                            block_length = struct.unpack('<H', length_bytes[4:6])[0]
                    
                    block_ids[block_id] += 1
                    blocks_found += 1
                    
                    if block_length > 0:
                        position += block_length
                    else:
                        position += 8
                
                except:
                    position += 1
            else:
                position += 1
        
        print(f"Scanned first {position/1e6:.1f} MB")
        print(f"Found {blocks_found} valid SBF blocks\n")
        print("Block Type Distribution:")
        print("-" * 60)
        print(f"{'Block ID':<12} {'Count':<10} {'Name':<30}")
        print("-" * 60)
        
        for block_id, count in block_ids.most_common():
            name = block_names.get(block_id, f"Unknown (0x{block_id:04X})")
            print(f"{block_id:<12} {count:<10} {name:<30}")
        
        print("-" * 60)
        print(f"\nNote: PVTGeodetic (4007) or PVTCartesian (4006) blocks needed for position data")
        
        if 4007 not in block_ids and 4006 not in block_ids:
            print("\n⚠️  WARNING: No position blocks found!")
            print("This file may contain only:")
            print("  - Raw measurements (MeasEpoch)")
            print("  - Base station data")
            print("  - Other auxiliary data")
            print("\nYou may need to process this file with SBF converter or")
            print("RTKLib to extract position solutions.")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        diagnose_sbf(sys.argv[1])
    else:
        print("Usage: python diagnose_sbf.py <sbf_file>")
