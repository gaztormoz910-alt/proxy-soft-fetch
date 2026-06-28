import json
import re

def main():
    with open('good_dialog_sources.json', 'r', encoding='utf-8') as f:
        good_urls = json.load(f)
        
    with open('fetch_proxy.py', 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Extract current urls to avoid duplicates
    existing_urls = set()
    for match in re.finditer(r'\(\s*[\'"](https?://[^\'"]+)[\'"]\s*,', content):
        existing_urls.add(match.group(1))
        
    new_entries = []
    for u in good_urls:
        if u not in existing_urls:
            # guess protocol
            proto = "http"
            lu = u.lower()
            if "socks5" in lu: proto = "socks5"
            elif "socks4" in lu: proto = "socks4"
            elif "vless" in lu or "vmess" in lu or "clash" in lu or "sub" in lu or "v2ray" in lu or "shadowsocks" in lu:
                proto = "vless" # just a catchall for sub links, parser handles it
                
            new_entries.append(f'    ("{u}", "{proto}"),')
            
    if not new_entries:
        print("No new unique URLs to add.")
        return
        
    print(f"Adding {len(new_entries)} new sources...")
    
    # find the end of SOURCES list
    # look for `SOURCES = [\n` and then `]`
    sources_start = content.find("SOURCES = [")
    if sources_start == -1:
        print("Could not find SOURCES = [")
        return
        
    # find the matching closing bracket
    idx = sources_start
    bracket_count = 0
    in_str = False
    str_char = ''
    while idx < len(content):
        c = content[idx]
        if in_str:
            if c == '\\':
                idx += 2
                continue
            if c == str_char:
                in_str = False
        else:
            if c in '"\'':
                in_str = True
                str_char = c
            elif c == '[':
                bracket_count += 1
            elif c == ']':
                bracket_count -= 1
                if bracket_count == 0:
                    # found end!
                    insert_pos = idx
                    break
        idx += 1
        
    if bracket_count != 0:
        print("Could not find end of SOURCES list")
        return
        
    # go back slightly to insert before the closing bracket
    while content[insert_pos-1] in ' \t\n\r,':
        insert_pos -= 1
        
    # Insert a comma if needed, then new entries
    new_text = ",\n" + "\n".join(new_entries) + "\n"
    
    new_content = content[:insert_pos] + new_text + content[insert_pos:]
    
    with open('fetch_proxy.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
        
    print("Successfully updated fetch_proxy.py")

if __name__ == '__main__':
    main()
