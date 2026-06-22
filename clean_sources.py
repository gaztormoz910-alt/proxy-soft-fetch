import json
import re

# Load the check report
with open('source_check_report.json', 'r', encoding='utf-8') as f:
    report = json.load(f)

# Extract alive sources that actually yielded proxies
alive_sources = set(item['url'] for item in report['alive_sources'])

# Also, we should keep sources that might be dynamic APIs which happened to be empty but are valid endpoints?
# Actually, the user wants ONLY alive and dynamic sources.
# Let's read fetch_proxy.py and keep only the alive sources.
with open('fetch_proxy.py', 'r', encoding='utf-8') as f:
    content = f.read()

# We need to extract the SOURCES block and rewrite it.
# Wait, fetch_proxy.py has SOURCES.extend(...) dynamically now.
# Let's extract the actual code block, execute it to get the list, filter it, and then rewrite it as a static list?
# No, fetch_proxy has some static definitions, and we appended `SOURCES.extend(...)`
# The easiest way is to dynamically load SOURCES, filter it against `alive_sources`, and completely replace the SOURCES definition in fetch_proxy.py with a clean, static list.

import fetch_proxy
all_sources = fetch_proxy.SOURCES

clean_sources = []
for url, proto in all_sources:
    if url in alive_sources:
        clean_sources.append((url, proto))

# Now we need to replace EVERYTHING related to SOURCES in fetch_proxy.py with just one big SOURCES = [...] list.
# We will look for `SOURCES = [` and replace everything up to `class ProxyUtils:`

start_idx = content.find('SOURCES = [')
end_idx = content.find('class ProxyUtils:')

if start_idx != -1 and end_idx != -1:
    # Build the new SOURCES string
    new_sources_str = "SOURCES = [\n"
    for url, proto in clean_sources:
        new_sources_str += f"    ('{url}', '{proto}'),\n"
    new_sources_str += "]\n\n"
    
    new_content = content[:start_idx] + new_sources_str + content[end_idx:]
    
    with open('fetch_proxy.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"Successfully cleaned sources! Reduced from {len(all_sources)} to {len(clean_sources)} elite sources.")
else:
    print("Could not find SOURCES block!")
