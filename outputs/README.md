# Simulation Outputs

This directory contains all outputs generated from the gravitational decoupling simulations.

## 📊 Visualizations

Located in [visualizations/](visualizations/):

### Gravitational Decoupling Results

**Standing Wave Field:**
- `standing_wave_3d_early.png` - Early time evolution (0-3 min)
- `standing_wave_3d_mid.png` - Mid evolution (3-7 min)
- `standing_wave_3d_final.png` - Final saturation (7-10 min)
- `standing_wave_decoupling.png` - Weight reduction time series

**Impulse Toroidal Mode:**
- `impulse_toroidal_resonance.png` - Energy circulation patterns
- `impulse_validation_tests.png` - Comprehensive validation results
- `timing_comparison.png` - Impulse vs continuous comparison

**Analysis:**
- `safety_distance_analysis.png` - Acoustic danger zones
- `frequency_mass_scaling.png` - Scaling relationships

### Framework Extensions

**Biological Systems:**
- `biological_enhancement_10hz.png` - Living vs non-living tissue at 10 Hz
- `biological_frequency_sweep.png` - Ion channel frequency responses

## 🔄 Regenerating Outputs

To regenerate any visualization:

```bash
# Primary simulations
python -m simulations.core.standing_wave_field
python -m simulations.core.impulse_toroidal_resonance

# Validation and analysis
python -m simulations.analysis.validate_impulse_model
python -m simulations.analysis.safety_distance_analysis

# Framework extensions
python -m simulations.framework_extensions.biological_resonance
python -m simulations.framework_extensions.frequency_mass_scaling
```

All outputs will be saved to this directory automatically.

---

**Last Updated**: January 1, 2026
