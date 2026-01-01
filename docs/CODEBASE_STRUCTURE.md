# Codebase Structure and Organization

**Last Updated**: January 1, 2026  
**Reorganization**: Applied SOLID principles with gravitational decoupling as primary focus

---

## Design Philosophy (SOLID Principles)

### Single Responsibility Principle
Each module has one clear purpose:
- `core/acoustic_physics.py` - ONLY handles acoustic calculations
- `core/impulse_toroidal_resonance.py` - ONLY models impulse-driven resonance
- `analysis/validate_impulse_model.py` - ONLY validates model predictions

### Open/Closed Principle
Core physics foundation (`acoustic_physics.py`) is stable and extended by:
- Different resonance models (standing wave, impulse, internal device)
- Analysis tools that import and build upon core functions

### Liskov Substitution Principle
All resonance models (`standing_wave_field.py`, `impulse_toroidal_resonance.py`) can be used interchangeably for weight reduction calculations.

### Interface Segregation Principle
Modules expose focused interfaces:
- Physics calculations separate from visualization
- Analysis separate from modeling
- Evidence separate from predictions

### Dependency Inversion Principle
High-level modules (analysis, validation) depend on abstractions (acoustic physics) not concrete implementations.

---

## Directory Structure

```
decoup/
│
├── simulations/                    # Main package - all executable code
│   ├── __init__.py                # Package metadata and version
│   │
│   ├── core/                      # 🎯 PRIMARY: Gravitational physics
│   │   ├── __init__.py           # Core module documentation
│   │   ├── acoustic_physics.py   # Foundation: SPL, pressure, forces, materials
│   │   ├── standing_wave_field.py      # Continuous mode: 3D cavity resonance
│   │   ├── impulse_toroidal_resonance.py # ⭐ BEST: Impulse mode with circulation
│   │   ├── gravitational_decoupling_v2.py # Physics-grounded decoupling model
│   │   ├── internal_resonance_device.py   # Portable device design
│   │   └── resonant_power_model.py        # Power dynamics (startup/maintenance)
│   │
│   ├── analysis/                  # 📊 Validation and safety
│   │   ├── __init__.py           # Analysis module documentation
│   │   ├── validate_impulse_model.py    # Comprehensive validation suite
│   │   ├── verify_energy_calculations.py # Q-factor correction tests
│   │   ├── safety_distance_analysis.py   # Acoustic exposure danger zones
│   │   └── compare_power_models.py       # Model comparison studies
│   │
│   ├── evidence/                  # 🌍 Experimental evidence
│   │   ├── __init__.py           # Evidence module documentation
│   │   ├── analyze_tohoku_gps.py        # 38 mHz mystery signal analysis
│   │   ├── predict_tohoku_decoupling.py # Framework predictions
│   │   ├── ggv147.pdf                   # Mitsui & Heki (2015) paper
│   │   └── Wang_etal_Tohoku_BSSA2013.pdf
│   │
│   ├── framework_extensions/      # 🧬 Unified theory extensions
│   │   ├── __init__.py           # Framework module documentation
│   │   ├── biological_resonance.py      # Ion channels, consciousness
│   │   ├── frequency_mass_scaling.py    # Frequency-energy correspondence
│   │   └── coupled_vs_shared_pattern.py # Channel manifestation patterns
│   │
│   └── crx2rnx-2.6.0/            # External tool (Rust RINEX decompressor)
│
├── archive/                       # 📦 Preserved reference materials
│   ├── ARCHIVE_INDEX.md          # Comprehensive archive documentation
│   ├── gnss_processing/          # Detailed RINEX analysis (not needed for experiments)
│   ├── early_models/             # Superseded approaches (energy/phase accumulation)
│   └── raw_data/                 # RINEX files, binaries
│
├── docs/                          # 📄 Documentation (all kept)
│   ├── README.md                 # Main entry point (project root)
│   ├── PROJECT_ESSENCE.md        # 🌟 START HERE - clear explanation
│   ├── PROJECT_UPDATE_DEC2025.md # Latest findings and breakthrough
│   ├── EXPERIMENTAL_PROTOCOL.md  # Detailed test procedures
│   ├── JOURNEY_AND_INSIGHTS.md   # Complete development history
│   ├── FRAMEWORK_CONNECTION.md   # Unified framework (3 domains)
│   ├── THEORY_PAPER.md          # Academic paper draft
│   ├── TOHOKU_EARTHQUAKE_EVIDENCE.md # Gravitational coupling evidence
│   ├── CHANNEL_MANIFESTATION_QUESTION.md
│   ├── element_frequency_mapping.md
│   └── frequency_medium_analysis.md
│
├── requirements.txt              # Python dependencies
└── CODEBASE_STRUCTURE.md        # This file

```

---

## Module Dependencies

### Core Dependencies Flow
```
acoustic_physics.py (foundation)
    ↓
    ├─→ standing_wave_field.py
    ├─→ impulse_toroidal_resonance.py
    ├─→ gravitational_decoupling_v2.py
    ├─→ internal_resonance_device.py
    └─→ resonant_power_model.py
         ↓
         └─→ analysis/* (validation, comparison, safety)
```

### External Dependencies
- `numpy` - Numerical computations
- `scipy` - Scientific functions (FFT, integration)
- `matplotlib` - Visualizations
- `pandas` - Data handling (optional for evidence analysis)

---

## How to Navigate the Codebase

### For Experimentalists (Building the Device)
1. **Start**: [PROJECT_ESSENCE.md](PROJECT_ESSENCE.md) - Understand the concept
2. **Physics**: `simulations/core/acoustic_physics.py` - Material properties, calculations
3. **Best Model**: `simulations/core/impulse_toroidal_resonance.py` - Implement this
4. **Protocol**: [EXPERIMENTAL_PROTOCOL.md](EXPERIMENTAL_PROTOCOL.md) - Step-by-step test procedure
5. **Safety**: `simulations/analysis/safety_distance_analysis.py` - Know the danger zones

### For Theorists (Understanding the Framework)
1. **Start**: [THEORY_PAPER.md](THEORY_PAPER.md) - Full mathematical framework
2. **Evidence**: `simulations/evidence/` - Tohoku earthquake 38 mHz signal
3. **Extensions**: `simulations/framework_extensions/` - Biological, consciousness applications
4. **Journey**: [JOURNEY_AND_INSIGHTS.md](JOURNEY_AND_INSIGHTS.md) - How we got here

### For Developers (Extending the Code)
1. **Start**: `simulations/__init__.py` - Package structure
2. **Foundation**: `simulations/core/acoustic_physics.py` - Core abstractions
3. **Example**: `simulations/core/impulse_toroidal_resonance.py` - Well-structured model
4. **Validation**: `simulations/analysis/validate_impulse_model.py` - Testing patterns
5. **This File**: SOLID principles guide

### For Reviewers (Validating Claims)
1. **Start**: [PROJECT_UPDATE_DEC2025.md](PROJECT_UPDATE_DEC2025.md) - Latest status
2. **Primary Evidence**: `simulations/evidence/analyze_tohoku_gps.py` + papers in evidence/
3. **Validation Suite**: `simulations/analysis/validate_impulse_model.py`
4. **Comparison**: `simulations/analysis/compare_power_models.py`
5. **Safety Check**: `simulations/analysis/verify_energy_calculations.py`

---

## Key Files by Purpose

### Primary Experiments (Gravitational Decoupling)
| File | Purpose | Status |
|------|---------|--------|
| `core/impulse_toroidal_resonance.py` | ⭐ Best approach - 100W avg, 4.99% reduction | **RECOMMENDED** |
| `core/standing_wave_field.py` | Alternative - 500W continuous, 4.64% reduction | Validated |
| `core/acoustic_physics.py` | Foundation for all models | Stable |
| `analysis/validate_impulse_model.py` | Comprehensive test suite | Essential |

### Supporting Analysis
| File | Purpose | When to Use |
|------|---------|-------------|
| `analysis/verify_energy_calculations.py` | Q-factor corrections | Before experiments |
| `analysis/safety_distance_analysis.py` | Danger zones | **CRITICAL** for safety |
| `analysis/compare_power_models.py` | Model comparison | Understanding tradeoffs |

### Evidence & Validation
| File | Purpose | Significance |
|------|---------|--------------|
| `evidence/analyze_tohoku_gps.py` | 38 mHz signal analysis | Planetary-scale validation |
| `evidence/ggv147.pdf` | Mitsui & Heki (2015) | Peer-reviewed source |
| `evidence/predict_tohoku_decoupling.py` | Framework predictions | Testable claims |

### Framework Extensions (Unified Theory)
| File | Purpose | Relation to Gravity |
|------|---------|---------------------|
| `framework_extensions/biological_resonance.py` | Ion channels, consciousness | Demonstrates multi-scale coupling |
| `framework_extensions/frequency_mass_scaling.py` | Frequency-energy correspondence | Universal scaling laws |
| `framework_extensions/coupled_vs_shared_pattern.py` | Channel manifestation | Fundamental mechanism |

---

## Import Patterns

### Correct Imports (After Reorganization)
```python
# Core physics
from simulations.core.acoustic_physics import AcousticProperties, MaterialVibration

# Models
from simulations.core.impulse_toroidal_resonance import simulate_impulse_resonance

# Analysis
from simulations.analysis.validate_impulse_model import run_validation_suite

# Evidence
from simulations.evidence.analyze_tohoku_gps import analyze_38mhz_signal

# Framework extensions
from simulations.framework_extensions.biological_resonance import ion_channel_frequencies
```

### Avoid
```python
# ❌ Old flat imports (pre-reorganization)
from simulations.core.impulse_toroidal_resonance import ...

# ✅ Use categorized imports instead
from simulations.core.impulse_toroidal_resonance import ...
```

---

## Development Workflow

### Adding a New Model
1. Create in `simulations/core/new_model.py`
2. Import from `acoustic_physics.py` for foundation
3. Add validation in `simulations/analysis/validate_new_model.py`
4. Update `simulations/core/__init__.py` documentation
5. Add usage example to README.md

### Adding Analysis
1. Create in `simulations/analysis/new_analysis.py`
2. Import models from `simulations.core.*`
3. Document in `simulations/analysis/__init__.py`
4. Add to Quick Start in README.md

### Adding Evidence
1. Place data/papers in `simulations/evidence/`
2. Create analysis script with clear documentation
3. Update `simulations/evidence/__init__.py`
4. Reference in main documentation

---

## Archive Policy

### What Gets Archived
- ✅ Superseded models (early_models/)
- ✅ Detailed processing scripts not needed for experiments (gnss_processing/)
- ✅ Raw data files (raw_data/)
- ✅ Backup versions of active files

### What Stays Active
- ✅ All documentation
- ✅ Latest working models
- ✅ Validation and analysis tools
- ✅ Evidence with final analysis
- ✅ Framework extensions (unified theory)

### Archive Process
```bash
# Move to archive
mv simulations/old_model.py archive/early_models/

# Document in ARCHIVE_INDEX.md
# Update imports if needed
# Test that nothing breaks
```

---

## Testing & Validation

### Run All Tests
```bash
# Core model validation
python -m simulations.analysis.validate_impulse_model

# Energy calculation verification
python -m simulations.analysis.verify_energy_calculations

# Model comparison
python -m simulations.analysis.compare_power_models
```

### Expected Outputs
- Weight reduction ~5% (both models)
- Q-factor amplification validated
- Safety distances calculated
- Power requirements confirmed

---

## Version History

### v2.0.0 (January 1, 2026)
- ✅ Reorganized with SOLID principles
- ✅ Separated core/analysis/evidence/framework_extensions
- ✅ Archived non-essential files
- ✅ Created proper Python package structure
- ✅ Updated all documentation

### v1.0.0 (December 2025)
- ✅ Impulse toroidal resonance breakthrough
- ✅ Comprehensive validation suite
- ✅ Safety analysis corrections
- ✅ Tohoku earthquake evidence analysis

---

## Future Directions

### Potential Additions (Maintain SOLID)
- `simulations/core/multi_frequency_coupling.py` - Combined frequency approach
- `simulations/analysis/material_comparison.py` - Systematic material testing
- `simulations/evidence/other_earthquakes.py` - Additional planetary evidence
- `simulations/experiments/` - New top-level for experimental data

### Keep Primary Focus
All additions should support the main goal: **demonstrating gravitational decoupling via acoustic resonance**

Framework extensions (biological, consciousness) remain secondary supporting evidence for unified theory.

---

## Contact & Contribution

**Author**: Dionte Robinson  
**Focus**: Gravitational decoupling experiments  
**Status**: Active development - experimental validation phase

For questions about code organization, see this file.  
For physics questions, see [THEORY_PAPER.md](THEORY_PAPER.md).  
For experimental procedures, see [EXPERIMENTAL_PROTOCOL.md](EXPERIMENTAL_PROTOCOL.md).

---

**Last Updated**: January 1, 2026
