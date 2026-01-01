# Archive Index

This directory contains files that are **preserved for reference** but not part of the active gravitational decoupling experiments.

## Structure

### `/gnss_processing/` - Detailed GNSS Analysis Scripts
**Archived**: January 1, 2026  
**Reason**: Detailed RINEX processing scripts are not needed for primary gravitational experiments. The key findings (38 mHz Tohoku signal) are preserved in `simulations/evidence/`.

**Contents**:
- `analyze_gnss_full.py` - Full RINEX3 parsing and analysis
- `analyze_gnss_georinex.py` - GeoRINEX-based analysis
- `analyze_gnss_timing.py` - Timing anomaly detection
- `analyze_pseudoranges.py` - Pseudorange analysis
- `parse_rinex_data.py` - Raw RINEX parser
- `process_crinex_data.py` - Compressed RINEX processing
- `process_with_rtklib.py` - RTKLIB integration
- `diagnose_sbf.py` - SBF format diagnostics
- `rinex_timing_analysis.png` - Visualization output

### `/early_models/` - Superseded Simulation Models
**Archived**: January 1, 2026  
**Reason**: Early exploration models that were superseded by more comprehensive approaches.

**Contents**:
- `energy_accumulation.py` - 4 storage mechanisms (proved insufficient alone)
- `phase_accumulation.py` - Information model (needs long coherence)
- `standing_wave_field_backup.py` - Old backup version

**Superseded By**:
- `simulations/core/standing_wave_field.py` (continuous mode)
- `simulations/core/impulse_toroidal_resonance.py` (impulse mode - superior)

### `/raw_data/` - RINEX Files and Binaries
**Archived**: January 1, 2026  
**Reason**: Raw data files preserved for reproducibility but not needed for active development.

**Contents**:
- `ab180050.22d` - RINEX observation file (2011 Tohoku)
- `ab180050.22d.Z` - Compressed version
- `AB180050.22O` - Additional RINEX format
- `crx2rnx.exe` - CRINEX decompression binary (Windows)
- `crx2rnx.zip` - Binary package

**Note**: Source code for crx2rnx maintained in `simulations/crx2rnx-2.6.0/`

## Restoration

If any archived files are needed:
```bash
# Example: Restore GNSS analysis script
cp archive/gnss_processing/analyze_gnss_full.py simulations/
```

## Deletion Policy

**DO NOT DELETE** - All archived materials are kept for:
- Historical reference
- Reproducibility
- Future extensions
- Documentation of development journey

Last Updated: January 1, 2026
