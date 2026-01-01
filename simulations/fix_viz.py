#!/usr/bin/env python
"""Fix visualization sections for rectangular block"""

with open('simulations/standing_wave_field.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find and replace the cross-section visualization
new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    
    # Fix cross-section (YZ plane) visualization
    if '# Distance from object center' in line and 'R_yz' in lines[i+1]:
        # Replace sphere-based cross-section with rectangle
        new_lines.append(line)  # Keep comment
        new_lines.append('    # Check if point is inside rectangular block\n')
        new_lines.append('    inside_block = (np.abs(Y_yz) < params.object_width/2) & (np.abs(Z_yz) < params.object_height/2)\n')
        new_lines.append('    \n')
        new_lines.append('    # Distance from edges (normalized)\n')
        new_lines.append('    dist_y = np.abs(Y_yz) / (params.object_width/2)\n')
        new_lines.append('    dist_z = np.abs(Z_yz) / (params.object_height/2)\n')
        new_lines.append('    max_dist = np.maximum(dist_y, dist_z)\n')
        new_lines.append('    \n')
        # Skip old R_yz lines
        i += 2
        continue
    
    # Fix internal displacement field calculation
    if 'internal_displacement = np.where(' in line:
        new_lines.append(line)
        new_lines.append('        inside_block,\n')
        new_lines.append('        # Inside: standing wave pattern\n')
        new_lines.append('        pressure_amplitude * results[\'internal_q\'] * np.sin(np.pi * dist_y) * np.sin(np.pi * dist_z) * \n')
        new_lines.append('        results[\'accumulated_effect\'][time_index] * 1e6,  # Scale to microns\n')
        new_lines.append('        # Outside: exponential decay\n')
        new_lines.append('        pressure_amplitude * np.exp(-2*np.maximum(0, max_dist - 1.0)) * 1e6\n')
        new_lines.append('    )\n')
        # Skip old lines
        while i < len(lines) and ')' not in lines[i]:
            i += 1
        i += 1
        continue
        
    # Fix object boundary from circle to rectangle
    if '# Object boundary circle' in line:
        new_lines.append('    # Object boundary rectangle\n')
        new_lines.append('    obj_y = [-params.object_width/2, params.object_width/2, params.object_width/2, \n')
        new_lines.append('             -params.object_width/2, -params.object_width/2]\n')
        new_lines.append('    obj_z = [-params.object_height/2, -params.object_height/2, params.object_height/2,\n')
        new_lines.append('             params.object_height/2, -params.object_height/2]\n')
        new_lines.append('    ax2.plot(obj_y, obj_z, np.zeros_like(obj_y), \'r-\', linewidth=3, label=\'Object boundary\')\n')
        # Skip old circle lines
        i += 1
        while i < len(lines) and 'ax2.plot' not in lines[i]:
            i += 1
        i += 1
        continue
    
    # Fix energy density calculation
    if '# Create 2D energy density map' in line and i+1 < len(lines) and 'R_yz < params.object_radius' in lines[i+2]:
        new_lines.append(line)
        new_lines.append('    energy_density = np.where(\n')
        new_lines.append('        inside_block,\n')
        new_lines.append('        # Inside: vibrational energy density (higher at center)\n')
        new_lines.append('        (results[\'internal_q\'] * results[\'accumulated_effect\'][time_index])**2 * \n')
        new_lines.append('        (1 - max_dist**2),  # Higher at center\n')
        new_lines.append('        # Outside: acoustic energy density\n')
        new_lines.append('        np.exp(-2*np.maximum(0, max_dist - 1.0)) * 0.1\n')
        new_lines.append('    )\n')
        # Skip old lines
        i += 1
        while i < len(lines) and ')' not in lines[i]:
            i += 1
        i += 1
        continue
        
    new_lines.append(line)
    i += 1

with open('simulations/standing_wave_field.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Visualization fixes applied")
