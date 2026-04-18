import sys

with open('frontend/dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Locate section-simulation stat cards start
stat_cards_idx = html.find('<!-- Stat Cards -->')

# Locate right panel section
rp_start_idx = html.find('<!-- ─── RIGHT PANEL ───────────────────────────────────────────────────── -->')
rp_end_idx = html.find('</aside>', rp_start_idx) + 8

if stat_cards_idx == -1 or rp_start_idx == -1:
    print('Could not find markers')
    sys.exit(1)

rp_content = html[rp_start_idx:rp_end_idx]
# Change aside class to sim-sidebar
rp_content = rp_content.replace('class="right-panel"', 'class="sim-sidebar"')

# Remove rp_content from its original place
new_html = html[:rp_start_idx] + html[rp_end_idx:]

# Locate end of section-simulation
sim_end_idx = new_html.find('</div><!-- /section-simulation -->')
if sim_end_idx == -1:
    print('Could not find end of section-simulation')
    sys.exit(1)

# Everything from '<!-- Stat Cards -->' up to '</div><!-- /section-simulation -->' belongs in .sim-main
stat_start = new_html.find('<!-- Stat Cards -->')
sim_end = new_html.find('</div><!-- /section-simulation -->')

sim_main_content = new_html[stat_start:sim_end]

# Compose the new section simulation interior
replacement = f'''<div class="sim-layout">
  <div class="sim-main">
    {sim_main_content}
  </div>
  {rp_content}
</div>
'''

final_html = new_html[:stat_start] + replacement + new_html[sim_end:]

with open('frontend/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(final_html)

print('Successfully restructured Simulation layout!')
