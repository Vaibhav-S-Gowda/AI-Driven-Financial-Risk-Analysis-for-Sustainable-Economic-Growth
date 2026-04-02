import os

app_path = r'c:\Users\vaibh\Desktop\AIML project\app.py'
html_path = r'c:\Users\vaibh\Desktop\AIML project\landing.html'

with open(html_path, 'r', encoding='utf-8') as f:
    html_content = f.read()

# Wire up the CTA buttons to trigger Streamlit's routing via URL parameters
html_content = html_content.replace('href="#"', 'href="#" onclick="try { window.parent.location.href=\'?nav=login\'; } catch(e) {} return false;"')

with open(app_path, 'r', encoding='utf-8') as f:
    app_lines = f.readlines()

start_idx = -1
end_idx = -1
for i, line in enumerate(app_lines):
    if 'landing_html = r"""' in line:
        start_idx = i
    if '    """' in line and start_idx != -1 and i > start_idx and i < start_idx + 400: # Ensure we don't grab something way at the end
        end_idx = i
        break

if start_idx != -1 and end_idx != -1:
    # Notice we append the raw html content between the triple quotes
    new_app = "".join(app_lines[:start_idx+1]) + html_content + "\n" + "".join(app_lines[end_idx:])
    with open(app_path, 'w', encoding='utf-8') as f:
        f.write(new_app)
    print(f"Injected successfully! Lines found: start {start_idx}, end {end_idx}")
else:
    print("Could not find landing_html block.")
