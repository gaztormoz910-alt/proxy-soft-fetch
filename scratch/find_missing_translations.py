import re

content = open(r'c:\Users\Bog_1\OneDrive\Desktop\Fetch Free Proxy\gui.py', encoding='utf-8').read()

# find all components that are created with `text=self._t("something")`
matches = re.findall(r'self\.([a-zA-Z0-9_]+)\s*=\s*ctk\.CTk[a-zA-Z]+\(.*?text=self\._t\([\'"](.*?)[\'"]\)', content, re.DOTALL)
elements_with_t = set(matches)

print("Elements with _t:")
for k, v in sorted(elements_with_t):
    print(f"{k}: {v}")

# find all elements updated in _apply_language
apply_lang = content[content.find('def _apply_language'):content.find('def _on_tab_change')]
updated_elements = re.findall(r'self\._safe_config\s*\(\s*self\.([a-zA-Z0-9_]+)', apply_lang)
updated_elements = set(updated_elements)

print("\nElements updated in _apply_language:")
for k in sorted(updated_elements):
    print(k)

print("\nMissing in _apply_language:")
for k, v in sorted(elements_with_t):
    if k not in updated_elements:
        print(f"{k}: {v}")
