import re
import sys
sys.stdout.reconfigure(encoding='utf-8')
with open('c:/Users/Bog_1/OneDrive/Desktop/Fetch Free Proxy/fetch_proxy.py', 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if re.search(r'[А-Яа-я]', line) and '#' not in line.split('\"')[0].split('\'')[0]:
            print(f'{i+1}: {line.strip()}')
