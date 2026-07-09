import ast
import re

def is_cis_source(url):
    url = url.lower()
    # Explicit keywords
    if any(k in url for k in ['russia', 'ukraine', 'belarus', 'kazakhstan', 'moscow', 'kiev', 'minsk', 'astana']):
        return True
    
    # query params or path segments
    if re.search(r'country=(ru|ua|by|kz)\b', url):
        return True
    
    # Path segments or extensions
    if re.search(r'/(ru|ua|by|kz)/', url):
        return True
    
    # Domain TLDs
    if re.search(r'\.(ru|ua|by|kz)/', url):
        return True
    
    # Specific file names like proxy_ru.txt
    if re.search(r'_(ru|ua|by|kz)\.', url):
        return True
        
    return False

def main():
    with open('fetch_proxy.py', 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Find the SOURCES list assignment
    match = re.search(r'SOURCES\s*=\s*\[(.*?)\]\n# === ПАГИНАЦИЯ', content, re.DOTALL)
    if not match:
        print("Could not find SOURCES list.")
        return
        
    sources_str = match.group(1)
    
    # Extract each line/tuple
    new_sources = []
    removed = []
    
    for line in sources_str.split('\n'):
        if not line.strip():
            continue
        if line.strip().startswith('#'):
            new_sources.append(line)
            continue
            
        # Try to parse the URL
        url_match = re.search(r'[\'"]([^\'"]+)[\'"]', line)
        if url_match:
            url = url_match.group(1)
            if is_cis_source(url):
                removed.append(url)
                continue
        new_sources.append(line)
        
    print(f"Removed {len(removed)} CIS sources:")
    for r in removed:
        print("  -", r)
        
    new_content = content[:match.start(1)] + '\n'.join(new_sources) + '\n' + content[match.end(1):]
    
    with open('fetch_proxy.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
        
    print(f"\nSuccessfully updated fetch_proxy.py!")

if __name__ == '__main__':
    main()
