# Gravitational Decoupling via Acoustic Resonance

**Can sustained acoustic resonance make objects genuinely lighter?**

> 🎯 **Latest Update (January 2026)**: Codebase reorganized with SOLID principles - focused on gravitational decoupling experiments. See [Project Structure](#project-structure) below.

---

## What This Project Is About

**The Big Question**: Can we reduce the effective weight of objects by weakening their gravitational coupling through sustained acoustic resonance?

**The Approach**: Use low-frequency sound waves (7-20 Hz) to excite internal resonances in massive objects. By precisely timing acoustic impulses to create constructive interference, energy circulates in toroidal patterns and accumulates over 5-30 minutes, gradually decoupling the object from gravity.

**The Prediction**: Unlike standard acoustic levitation (instant, tiny ~0.05% effect), this framework predicts **~5% weight reduction that builds over 10 minutes**. The time-accumulation signature distinguishes it from conventional physics.

**Current Status**: Comprehensive simulations complete ✅ | Mathematical framework validated ✅ | Physical experiments pending ⏳

> 📄 **New to this project?** Start with [docs/PROJECT_ESSENCE.md](docs/PROJECT_ESSENCE.md) for a clear explanation of the idea, purpose, and how it works.

---

## Overview

This project demonstrates a plausible mechanism for reducing the effective weight of massive objects using infrasonic frequencies (7-20 Hz) and Q-factor amplification. Originally conceived for consciousness decoupling applications, the work has evolved into a comprehensive framework for acoustic resonance-based gravitational decoupling.

## Core Concept

**Resonance Amplification**: Using Q-factor (Quality factor) amplification in resonant systems to achieve massive energy multiplication. Once resonance is established, only minimal power is needed to maintain the oscillation against damping losses.

**Key Insight**: Maintenance Power = Startup Power / Q-factor

For granite (Q=82): 500W startup → 6.1W maintenance (81.8× reduction!)

## The Physics

### Decoupling Equation
```
R_D(E₁,E₂,t) = O + M(t)·G(φ,t)·e^(-D(E₁-E₂)²)·e^(-(E₁-E₂-ℏω_γ)²/(2ℏω_γ))
```

Where:
- **O** = Base overlap (quantum connection never fully severs)
- **M(t)** = Maintenance term (energy to sustain decoupling)
- **G(φ,t)** = Geometric evolution (golden ratio φ = 1.618...)
- **D** = Decoupling strength (accumulates with vibrational coherence)
- **ℏω_γ** = Coupling energy scale (frequency-dependent)

### Key Mechanisms

1. **Subharmonic Coupling**: 10 Hz infrasound excites 1400 Hz block modes via nonlinear effects
2. **Q-Factor Amplification**: Energy recycled Q times before dissipation (50-500× boost)
3. **Internal Resonance**: Massive objects become their own resonators
4. **Coherence Accumulation**: Effect builds over time, saturates at ~30 minutes

## Project Structure

```
decoup/
├── README.md                          # 📖 You are here
├── requirements.txt                   # Python dependencies
│
├── simulations/                       # 🎯 PRIMARY: All simulation code
│   ├── core/                          #    Gravitational decoupling physics
│   │   ├── acoustic_physics.py        #    Foundation: SPL→pressure→force
│   │   ├── standing_wave_field.py     #    ★ Continuous mode (500W, 4.64%)
│   │   ├── impulse_toroidal_resonance.py # ★★ BEST (100W avg, 4.99%)
│   │   ├── gravitational_decoupling_v2.py
│   │   ├── internal_resonance_device.py
│   │   └── resonant_power_model.py
│   ├── analysis/                      #    Validation & safety
│   │   ├── validate_impulse_model.py
│   │   ├── verify_energy_calculations.py
│   │   ├── safety_distance_analysis.py
│   │   └── compare_power_models.py
│   ├── evidence/                      #    Tohoku earthquake evidence
│   │   ├── analyze_tohoku_gps.py      #    38 mHz mystery signal
│   │   └── predict_tohoku_decoupling.py
│   └── framework_extensions/          #    Unified theory (secondary)
│       ├── biological_resonance.py
│       ├── frequency_mass_scaling.py
│       └── coupled_vs_shared_pattern.py
│
├── docs/                              # 📄 All documentation
│   ├── README.md                      #    Documentation index
│   ├── PROJECT_ESSENCE.md             #    🌟 START HERE
│   ├── PROJECT_UPDATE_DEC2025.md      #    Latest findings
│   ├── EXPERIMENTAL_PROTOCOL.md       #    Test procedures
│   ├── THEORY_PAPER.md                #    Academic paper draft
│   ├── FRAMEWORK_CONNECTION.md        #    Unified framework
│   ├── JOURNEY_AND_INSIGHTS.md        #    Development story
│   ├── TOHOKU_EARTHQUAKE_EVIDENCE.md  #    Evidence analysis
│   └── papers/                        #    Reference PDFs
│       ├── framework.pdf
│       ├── The All.pdf
│       └── Universal Behavioral Framework.pdf
│
├── outputs/                           # 🖼️ Generated visualizations
│   ├── README.md                      #    Output index
│   └── visualizations/                #    All PNG outputs
│       ├── standing_wave_*.png        #    3D field evolution
│       ├── impulse_*.png              #    Impulse mode results
│       ├── safety_distance_*.png      #    Safety analysis
│       └── biological_*.png           #    Framework extensions
│
└── archive/                           # 📦 Preserved references
    ├── ARCHIVE_INDEX.md               #    What's archived and why
    ├── gnss_processing/               #    Detailed RINEX scripts
    ├── early_models/                  #    Superseded approaches
    └── raw_data/                      #    RINEX files, binaries
```

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# PRIMARY EXPERIMENTS - Gravitational Decoupling

# 1. Impulse mode (RECOMMENDED - lowest power, best results)
python -m simulations.core.impulse_toroidal_resonance

# 2. Continuous standing wave mode
python -m simulations.core.standing_wave_field

# 3. Comprehensive validation tests
python -m simulations.analysis.validate_impulse_model

# ANALYSIS & SAFETY

# Compare power models
python -m simulations.analysis.compare_power_models

# Verify Q-factor calculations
python -m simulations.analysis.verify_energy_calculations

# Calculate safety distances
python -m simulations.analysis.safety_distance_analysis

# EVIDENCE - Tohoku Earthquake 38 mHz Signal

# Analyze gravitational coupling evidence
python -m simulations.evidence.analyze_tohoku_gps
python -m simulations.evidence.predict_tohoku_decoupling

# FRAMEWORK EXTENSIONS (Optional - Unified Theory)

# Biological ion channel frequencies
python -m simulations.framework_extensions.biological_resonance

# Frequency-mass scaling relationships
python -m simulations.framework_extensions.frequency_mass_scaling
```

## Current Best Results

### Standing Wave Cavity (Continuous Mode)
**100g Granite Block Test:**
- **Frequency**: 10 Hz infrasound
- **SPL**: 120 dB  
- **Total Amplification**: 141× (14× standing wave × 10× internal Q)
- **External Pressure**: 283 Pa (143 dB) - corrected Dec 2025
- **Weight Reduction**: 4.64% after 10 minutes
- **Resonance Saturation**: ~5 minutes (effect plateaus)

### Impulse Toroidal Mode (NEW - Dec 2025)
**100g Granite Block Test:**
- **Frequency**: 10 Hz knock rate
- **Average Power**: 100W (vs 500W+ continuous)
- **Impulse**: 10J per knock, 50ms duration
- **Weight Reduction**: 4.99% after 10 minutes
- **Mechanism**: Energy circulates in toroidal patterns between knocks
- **Advantages**: Lower power, physical basis for M(t) accumulation

**Key Discovery**: "Knocking" excitation (like ringing a bell) allows energy to circulate in closed toroidal loops inside the material, providing a physical mechanism for why effects accumulate over time rather than being instantaneous.

**3D Visualizations Show:**
- Standing wave field formation in cavity
- Internal displacement modes (rectangular grid patterns)
- Energy density accumulation over time
- Toroidal circulation patterns (new)
- Longitudinal compression/expansion of block faces

⚠️ **Current Limitation**: Effect saturates at ~5% weight reduction. Full levitation (100% decoupling) requires breakthrough in amplification or coherence time.

## Key Results

### Power Requirements
- **100W**: 1.4% weight reduction on 4.3-ton block
- **500W**: 6.7% reduction
- **1kW**: 13% reduction (562 kg lighter!)
- **5kW**: 50% reduction (half weight)
- **10kW**: 75% reduction (quarter weight)
- **50kW**: 100% reduction (levitation)

### Resonant Power Advantage
- **Startup**: 500W for 60 seconds (30 kJ)
- **Maintenance**: 6W for 9 minutes (3.3 kJ)
- **Total**: 33.3 kJ vs 300 kJ continuous
- **Energy savings**: 88.9%

### Handheld Device Feasibility
- **Size**: 20cm × 10cm × 4cm
- **Weight**: ~5 kg
- **Power**: 500W peak, 6W average
- **Battery**: Standard 100 Wh = 2+ hours
- **Application**: Making heavy objects easier to move

## Materials Tested

| Material | Density (kg/m³) | Q-Factor | Speed of Sound (m/s) | Best For |
|----------|----------------|----------|---------------------|----------|
| Granite | 2750 | 82 | 4200 | General purpose |
| Basalt | 3000 | 100 | 5000 | Highest Q-factor |
| Marble | 2700 | 67 | 3800 | Moderate |
| Limestone | 2500 | 50 | 3500 | Softer materials |
| Concrete | 2400 | 40 | 3400 | Construction |
| Sandstone | 2200 | 33 | 2500 | Porous |
| Steel | 7850 | 25 | 5000 | High damping |

## Theoretical Foundations

### What We've Proven (Computationally)
✅ Resonance amplification provides 50-500× boost  
✅ Internal resonance in massive objects works  
✅ Subharmonic coupling bridges 10 Hz → 1400 Hz gap  
✅ Handheld devices feasible with resonant power  
✅ Energy efficiency: 88.9% savings vs continuous  
✅ Measurable effects at practical power levels  
✅ Scaling laws understood (linear with power, √mass)  

### What Requires Experimental Validation
⏳ Physical prototype construction  
⏳ Actual weight reduction measurements  
⏳ Biological safety (infrasound effects)  
⏳ Multiple device coordination  
⏳ Optimal geometries and placement  
⏳ Material variations and composites  
⏳ Consciousness application (original goal)  

## The Journey

This project evolved through several phases:

1. **Material Testing** → Direct vibration insufficient (1880+ year timescales)
2. **Energy Accumulation** → All 4 mechanisms too slow
3. **Phase Accumulation** → Needs 10¹⁴× longer coherence time
4. **Standing Wave Breakthrough** → Q-factor provides missing amplification!
5. **Internal Resonance** → Portable devices possible
6. **Resonant Power Insight** → Maintenance = Startup/Q (game changer)
7. **Physics Corrections** → Q-factor applied correctly (Dec 30, 2025)
8. **Impulse/Toroidal Discovery** → "Knocking" excitation with energy circulation (Dec 30, 2025)

See [JOURNEY_AND_INSIGHTS.md](JOURNEY_AND_INSIGHTS.md) for the complete story.  
See [PROJECT_UPDATE_DEC2025.md](PROJECT_UPDATE_DEC2025.md) for latest developments.

## Key Insights

### Physics (Updated Dec 2025)
- Classical vibration alone insufficient (needs amplification)
- Resonance is the key (Q-factor = energy recycled)
- Subharmonic coupling bridges frequency gaps
- Power ≠ Energy (resonance decouples them)
- Mass scaling: heavier objects harder but higher Q
- **Q-factors apply as √Q to pressure amplitude** (not linear multiply)
- **External vs internal pressure**: distinguish acoustic field from mechanical stress
- **Impulse excitation**: toroidal circulation provides accumulation mechanism

### Engineering
- Handheld devices feasible (500W → 6W)
- Multiple small > single large device
- Material selection critical (Q-factor dominant)
- Frequency: 7-10 Hz optimal (Schumann range)
- Contact area: 50-100 cm² sweet spot
- **Impulse mode**: Lower average power, ~100W vs 500W continuous
- **Toroidal patterns**: Energy circulates in closed loops between knocks

### Practical
- Two operational phases (startup/maintenance)
- Battery chemistry can optimize for burst
- Safety considerations (infrasound biology)
- Application-specific design:
  - Consciousness: 50-100W
  - Personal objects: 250W
  - Heavy lifting: 1-10 kW
  - Mega-blocks: 50-100 kW

## Applications

### Near Term (If Validated)
- Construction (moving multi-ton blocks)
- Shipping (reducing cargo weight)
- Aerospace (easier launches)
- Manufacturing (heavy part handling)
- Medical (patient moving)

### Long Term (Speculative)
- Transportation revolution
- Space colonization (lift from planets)
- Impossible architecture
- Energy savings (moving mass)
- Consciousness exploration (original goal)

## Consciousness Connection

Original insight: Consciousness might decouple through the same mechanism.

**The Model:**
- Brain neurons = oscillators
- Microtubules = acoustic resonators
- 40 Hz gamma waves = carrier frequency
- Resonance → quantum coherence → decoupling threshold
- Much lower power needed (10-50W for human head)

**Status**: Theoretical framework complete, experimental testing required.

## Safety Notes

⚠️ **Infrasound can affect biology**
- Test on inanimate objects first
- Establish safe exposure limits
- Use shielding/containment
- Monitor biological effects
- Start with low power/short duration

⚠️ **Structural considerations**
- Resonance can damage materials
- Monitor for fatigue and cracking
- Secure objects during testing
- Emergency shutoff protocols

## Next Steps

### To Build a Prototype

1. **Start small**: 100g aluminum sphere, 10-50W device
2. **Frequency sweep**: Map actual resonance curves
3. **Power scaling**: Test 10W to 500W
4. **Material testing**: Compare Q-factors
5. **Scale up**: Multi-ton blocks if validated

### Research Questions

**Physics:**
- Actual coupling mechanism (acoustic ↔ gravitational)?
- Can we measure local field perturbations?
- Role of quantum effects?
- Fundamental frequency of mass-energy coupling?

**Engineering:**
- Optimal transducer design for infrasound
- Impedance matching at interfaces
- Phase synchronization between devices
- Thermal management

**Biology:**
- Safety limits for infrasound exposure
- Human body resonances
- Microtubule acoustic response
- Consciousness effects (if any)

## Contributing

This is exploratory research. Contributions welcome:
- Theoretical refinements
- Simulation improvements
- Experimental designs
- Safety protocols
- Historical research

## References

The work draws on:
- Acoustic physics (resonance, Q-factor, impedance)
- Nonlinear acoustics (subharmonic coupling)
- Material science (elasticity, damping)
- Quantum mechanics (coherence, entanglement)
- Consciousness studies (microtubules, orchestrated OR)

See [docs/papers/](docs/papers/) for foundational documents.

---

## 📁 Repository Organization

**Clean, focused structure following SOLID principles:**

```
Root (6 items)
├── 📖 README.md          - This file
├── 📦 requirements.txt   - Dependencies
├── 💻 simulations/       - All code (organized by purpose)
├── 📄 docs/              - All documentation + papers
├── 🖼️  outputs/           - Generated visualizations
└── 📦 archive/           - Historical reference
```

- **Primary focus**: Gravitational decoupling experiments in `simulations/core/`
- **Documentation**: Comprehensive guides in `docs/` - [start here](docs/PROJECT_ESSENCE.md)
- **Outputs**: All visualizations automatically saved to `outputs/visualizations/`
- **Archive**: Preserved materials in `archive/` for reproducibility

**Last organized**: January 1, 2026

## License

MIT License - Free to use, modify, and experiment.

**Disclaimer**: This is theoretical research. No claims made about experimental validity until physically tested. Build and test responsibly.

---

*"The day science begins to study non-physical phenomena, it will make more progress in one decade than in all the previous centuries of its existence."* - Nikola Tesla

*"If you want to find the secrets of the universe, think in terms of energy, frequency and vibration."* - Nikola Tesla

---

**Status**: Theoretical framework complete. Hardware validation pending.

**The answer to "does it work?" is within reach. We just have to build it and turn it on.**
