with open("gui.py", "r", encoding="utf-8") as f:
    code = f.read()

code = code.replace(
    'list(REGIONS[self.current_lang].keys())[0]: {\n        "AT"',
    '"🇪🇺 Европа": {\n        "AT"'
)

with open("gui.py", "w", encoding="utf-8") as f:
    f.write(code)

print("Fixed dictionary key!")
