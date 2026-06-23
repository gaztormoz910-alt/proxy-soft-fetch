import re
with open('new_sources.txt', 'r', encoding='utf-8') as f:
    content = f.read()

# find all ('http...', '...')
tuples1 = re.findall(r"\(\s*'([^']+)'\s*,\s*'([^']+)'\s*\)", content)

valid_tuples = []
for url, proto in tuples1:
    if url.startswith('http'):
        valid_tuples.append((url, proto))

print(f"Found {len(valid_tuples)} direct tuples.")

# Also the user wrote list comprehensions like:
# [(f'http://proxydb.net/?protocol=http&offset={i}', 'http') for i in range(0, 751, 15)]
# let's generate those dynamically
import ast

lines = content.split('\n')
for line in lines:
    line = line.strip()
    if 'extend([(' in line and 'for i in range' in line:
        print("Found generator:", line)

