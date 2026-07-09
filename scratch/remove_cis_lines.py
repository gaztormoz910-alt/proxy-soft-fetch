import re
import fetch_proxy

def is_cis_source(url):
    url = url.lower()
    if any(k in url for k in ['russia', 'ukraine', 'belarus', 'kazakhstan', 'moscow', 'kiev', 'minsk', 'astana']):
        return True
    if re.search(r'country=(ru|ua|by|kz)\b', url):
        return True
    if re.search(r'/(ru|ua|by|kz)/', url):
        return True
    if re.search(r'\.(ru|ua|by|kz)/', url):
        return True
    if re.search(r'_(ru|ua|by|kz)\.', url):
        return True
    return False

def main():
    bad_urls = [s[0] for s in fetch_proxy.SOURCES if is_cis_source(s[0])]
    print(f"Found {len(bad_urls)} bad URLs to remove.")
    
    with open('fetch_proxy.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    new_lines = []
    removed_count = 0
    for line in lines:
        if any(bad_url in line for bad_url in bad_urls):
            removed_count += 1
            print(f"Removing line: {line.strip()}")
        else:
            new_lines.append(line)
            
    with open('fetch_proxy.py', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
        
    print(f"\nRemoved {removed_count} lines from fetch_proxy.py.")

if __name__ == '__main__':
    main()
