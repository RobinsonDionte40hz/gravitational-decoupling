"""
Compare continuous power model vs resonant power model
Shows that 500W startup + 6W maintenance ≈ 100W continuous (in terms of effect)
"""

from simulations.internal_resonance_device import (
    BlockParams, DeviceParams, simulate_internal_resonance_decoupling
)
from simulations.resonant_power_model import (
    ResonantDeviceParams, simulate_resonant_power_profile
)
import matplotlib.pyplot as plt
import numpy as np

print("="*80)
print("CONTINUOUS vs RESONANT POWER MODELS")
print("="*80)

# Same 4.3 ton granite block
block = BlockParams(
    material='granite',
    length=1.5,
    width=1.5,
    height=0.7
)

print(f"\nBlock: {block.mass()/1000:.2f} ton granite")
print(f"\n{'Model':<30} {'Power Profile':<30} {'Energy (kJ)':<15} {'Weight Reduction':<20}")
print("-"*100)

# Test 1: Continuous 100W
device_100w = DeviceParams(
    frequency=10.0,
    power=100,
    contact_area=0.01,
    num_devices=1
)
results_100w = simulate_internal_resonance_decoupling(block, device_100w, duration=600.0)
energy_100w = device_100w.power * 600 / 1000  # kJ
reduction_100w = results_100w['weight_reduction_pct'][-1]

print(f"{'Continuous 100W':<30} {'100W × 10 min':<30} {energy_100w:<15.1f} {reduction_100w:<20.2f}%")

# Test 2: Continuous 500W  
device_500w = DeviceParams(
    frequency=10.0,
    power=500,
    contact_area=0.01,
    num_devices=1
)
results_500w = simulate_internal_resonance_decoupling(block, device_500w, duration=600.0)
energy_500w = device_500w.power * 600 / 1000
reduction_500w = results_500w['weight_reduction_pct'][-1]

print(f"{'Continuous 500W':<30} {'500W × 10 min':<30} {energy_500w:<15.1f} {reduction_500w:<20.2f}%")

# Test 3: Continuous 1kW
device_1kw = DeviceParams(
    frequency=10.0,
    power=1000,
    contact_area=0.01,
    num_devices=1
)
results_1kw = simulate_internal_resonance_decoupling(block, device_1kw, duration=600.0)
energy_1kw = device_1kw.power * 600 / 1000
reduction_1kw = results_1kw['weight_reduction_pct'][-1]

print(f"{'Continuous 1kW':<30} {'1000W × 10 min':<30} {energy_1kw:<15.1f} {reduction_1kw:<20.2f}%")

# Test 4: Resonant 500W startup + 6W maintenance
resonant_device = ResonantDeviceParams(
    startup_power=500,
    startup_duration=60,
    frequency=10.0,
    contact_area=0.01
)
results_resonant = simulate_resonant_power_profile(block, resonant_device, duration=600.0)
energy_resonant = results_resonant['energy_consumed'][-1] / 1000
reduction_resonant = results_resonant['weight_reduction_pct'][-1]

startup_energy = resonant_device.startup_power * resonant_device.startup_duration / 1000
maint_energy = results_resonant['maintenance_power'] * (600 - resonant_device.startup_duration) / 1000

print(f"{'Resonant (500W → 6W)':<30} {'500W×1min + 6W×9min':<30} {energy_resonant:<15.1f} {reduction_resonant:<20.2f}%")

print("\n" + "="*80)
print("KEY INSIGHT:")
print("="*80)
print(f"""
The resonant model with 500W startup uses only {energy_resonant:.1f} kJ total energy,
compared to {energy_500w:.1f} kJ for continuous 500W.

Energy savings: {(1 - energy_resonant/energy_500w)*100:.1f}%

This is because resonance stores energy in the block itself.
Once vibration is established, only need to replace damping losses.

For portable devices, this makes ALL the difference:
- Battery life increases from {energy_500w*1000/3600:.1f} Wh to {energy_resonant*1000/3600:.1f} Wh
- Device can run {energy_500w/energy_resonant:.1f}x longer on same battery
- Peak power only needed for {resonant_device.startup_duration}s startup burst
""")

# Visualization
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('Continuous vs Resonant Power Models', fontsize=16, fontweight='bold')

# Plot 1: Power profiles
ax1 = axes[0, 0]
t_cont = results_500w['time']
t_res = results_resonant['time']
ax1.plot(t_cont/60, np.ones(len(t_cont))*500, 'r-', linewidth=2, label='Continuous 500W')
ax1.plot(t_res/60, results_resonant['power_profile'], 'b-', linewidth=2, label='Resonant (500W→6W)')
ax1.set_xlabel('Time (minutes)')
ax1.set_ylabel('Power (W)')
ax1.set_title('Power Over Time')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Plot 2: Cumulative energy
ax2 = axes[0, 1]
energy_cont = np.linspace(0, energy_500w, len(t_cont))
ax2.plot(t_cont/60, energy_cont, 'r-', linewidth=2, label='Continuous 500W')
ax2.plot(t_res/60, results_resonant['energy_consumed']/1000, 'b-', linewidth=2, label='Resonant')
ax2.set_xlabel('Time (minutes)')
ax2.set_ylabel('Energy Consumed (kJ)')
ax2.set_title('Cumulative Energy Use')
ax2.legend()
ax2.grid(True, alpha=0.3)

# Plot 3: Weight reduction comparison
ax3 = axes[1, 0]
ax3.plot(t_cont/60, results_100w['weight_reduction_pct'], 'g-', linewidth=2, label='100W continuous')
ax3.plot(t_cont/60, results_500w['weight_reduction_pct'], 'r-', linewidth=2, label='500W continuous')
ax3.plot(t_cont/60, results_1kw['weight_reduction_pct'], 'orange', linewidth=2, label='1kW continuous')
ax3.plot(t_res/60, results_resonant['weight_reduction_pct'], 'b--', linewidth=3, label='Resonant (500W→6W)')
ax3.set_xlabel('Time (minutes)')
ax3.set_ylabel('Weight Reduction (%)')
ax3.set_title('Weight Reduction Over Time')
ax3.legend()
ax3.grid(True, alpha=0.3)

# Plot 4: Efficiency comparison (effect per kJ)
ax4 = axes[1, 1]
powers = [100, 500, 1000]
energies = [energy_100w, energy_500w, energy_1kw]
reductions = [reduction_100w, reduction_500w, reduction_1kw]
efficiencies = [r/e for r, e in zip(reductions, energies)]

ax4.bar(['100W\ncont.', '500W\ncont.', '1kW\ncont.', '500W→6W\nresonant'], 
        efficiencies + [reduction_resonant/energy_resonant],
        color=['green', 'red', 'orange', 'blue'],
        alpha=0.7,
        edgecolor='black',
        linewidth=2)
ax4.set_ylabel('Efficiency (% reduction per kJ)')
ax4.set_title('Energy Efficiency Comparison')
ax4.grid(True, alpha=0.3, axis='y')

for i, eff in enumerate(efficiencies + [reduction_resonant/energy_resonant]):
    ax4.text(i, eff + max(efficiencies)*0.05, f'{eff:.3f}', 
            ha='center', fontweight='bold')

plt.tight_layout()
plt.savefig('continuous_vs_resonant.png', dpi=300, bbox_inches='tight')
print(f"\nVisualization saved to continuous_vs_resonant.png")
