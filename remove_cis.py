import re

CIS_COUNTRIES = ['RU', 'UA', 'BY', 'KG', 'TJ', 'TM', 'KZ', 'UZ', 'AZ', 'AM', 'MD']

with open('gui.py', 'r', encoding='utf-8') as f:
    gui_code = f.read()

# 1. Remove the entire "🇷🇺 СНГ" block
gui_code = re.sub(r'[ \t]*"🇷🇺 СНГ": \{[^}]+\},\n?', '', gui_code)

# 2. Remove the entire "🇷🇺 CIS" block
gui_code = re.sub(r'[ \t]*"🇷🇺 CIS": \{[^}]+\},\n?', '', gui_code)

# 3. Remove all occurrences of the specific CIS countries from ANY other categories 
for c in CIS_COUNTRIES:
    # Match something like: "KZ": "Казахстан", or "KZ": "Kazakhstan",
    gui_code = re.sub(r'[ \t]*"'+c+r'": "[^"]+",?\n?', '', gui_code)

# 4. Fix trailing commas before closing braces that might have been caused by removal
gui_code = re.sub(r',\s*\}', '\n    }', gui_code)

with open('gui.py', 'w', encoding='utf-8') as f:
    f.write(gui_code)
    
print("Removed CIS countries from gui.py")
