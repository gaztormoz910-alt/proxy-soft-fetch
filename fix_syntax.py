import re

with open('gui.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('self.clipboard_append("\\n".join(lines))', 'self.clipboard_append("\\\\n".join(lines))')
text = text.replace('f.write(f"{vals[0].lower()}://{vals[1]}:{vals[2]}\\n")', 'f.write(f"{vals[0].lower()}://{vals[1]}:{vals[2]}\\\\n")')
text = text.replace('f.write(f"{vals[1]}:{vals[2]}\\n")', 'f.write(f"{vals[1]}:{vals[2]}\\\\n")')
text = text.replace('f.write(f"{ip}\\n")', 'f.write(f"{ip}\\\\n")')

# Also fix the unterminated string literals caused by the first regex substitution
# Look for: self.clipboard_append("
# ".join(lines))
text = re.sub(r'self\.clipboard_append\("\n"\.join\(lines\)\)', r'self.clipboard_append("\\n".join(lines))', text)
text = re.sub(r'f\.write\(f"\{vals\[0\]\.lower\(\)\}://\{vals\[1\]\}:\{vals\[2\]\}\n"\)', r'f.write(f"{vals[0].lower()}://{vals[1]}:{vals[2]}\\n")', text)
text = re.sub(r'f\.write\(f"\{vals\[1\]\}:\{vals\[2\]\}\n"\)', r'f.write(f"{vals[1]}:{vals[2]}\\n")', text)
text = re.sub(r'f\.write\(f"\{ip\}\n"\)', r'f.write(f"{ip}\\n")', text)

with open('gui.py', 'w', encoding='utf-8') as f:
    f.write(text)
