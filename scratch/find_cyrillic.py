import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

content = open(r'c:\Users\Bog_1\OneDrive\Desktop\Fetch Free Proxy\gui.py', encoding='utf-8').read()
matches = re.finditer(r'text=[\'"]([^\'"]*?[А-Яа-яЁё][^\'"]*?)[\'"]', content)
print("TEXT=")
for m in matches:
    print(m.group(0))

print("---")
print("ADD=")
matches = re.finditer(r'\.add\([\'"]([^\'"]*?[А-Яа-яЁё][^\'"]*?)[\'"]\)', content)
for m in matches:
    print(m.group(0))
