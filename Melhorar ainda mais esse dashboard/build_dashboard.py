#!/usr/bin/env python3
"""Build the v5.0 dashboard by combining the HTML structure with the full data."""

with open('upload/pasted_file_nudVmu_DASHBOARD_PRODAM_v4.1_BRANDAO_OZORES.html', 'r') as f:
    content = f.read()

# Extract DEVS array
start = content.find('const DEVS=[')
end = content.find('];', start) + 2
devs_full = content[start:end]

with open('DASHBOARD_PRODAM_v5.0_BRANDAO_OZORES.html', 'r') as f:
    dashboard = f.read()

# Find the script section
script_start = dashboard.find('<script>')
# Everything before the script
before_script = dashboard[:script_start]

# Build complete script
script_content = '<script>\n'
script_content += '/* DASHBOARD PRODAM v5.0 */\n\n'
script_content += devs_full + '\n'
script_content += 'const FASES={"F0": {"c": 49, "v": 64951839.18196166}, "F5": {"c": 5, "v": 37192941.68879605}, "F3": {"c": 9, "v": 19367716.391583465}, "F0_DIAGNOSTICO": {"c": 8, "v": 0.0}};\n'
script_content += 'const CENARIOS={"conservador":{"pct":20,"rec":24302499.45,"fee":4860499.89},"base":{"pct":40,"rec":48604998.90,"fee":9720999.78},"otimista":{"pct":70,"rec":85058748.08,"fee":17011749.62}};\n'

# Read the script logic from a separate file
with open('dashboard_script.js', 'r') as f:
    js_logic = f.read()

script_content += js_logic
script_content += '\n</script>\n</body>\n</html>'

final = before_script + script_content

with open('DASHBOARD_PRODAM_v5.0_BRANDAO_OZORES.html', 'w') as f:
    f.write(final)

print(f'Dashboard saved: {len(final)} chars')
print(f'DEVS data: {len(devs_full)} chars')
