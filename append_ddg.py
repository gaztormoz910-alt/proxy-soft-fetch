queries = [
    'https://html.duckduckgo.com/html/?q=site:pastebin.com+"socks5"+intext:"1080"&df=d',
    'https://html.duckduckgo.com/html/?q=site:pastebin.com+"socks5://"+IP+PORT&df=d',
    'https://html.duckduckgo.com/html/?q=site:pastebin.com+"proxy+list"+"socks5"&df=d',
    'https://html.duckduckgo.com/html/?q=site:rentry.co+"socks5"&df=d',
    'https://html.duckduckgo.com/html/?q=site:ghostbin.com+"socks5"&df=d',
]

with open('fetch_proxy.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

end_idx = -1
for i, line in enumerate(lines):
    if line.startswith(']'):
        end_idx = i
        break

if end_idx != -1:
    new_lines = []
    new_lines.append('    # --- PASTEBIN/RENTRY SEARCH DORKING (DuckDuckGo HTML) ---\n')
    for q in queries:
        new_lines.append(f"    ('{q}', 'socks5'),\n")
    
    lines.insert(end_idx, "".join(new_lines))
    
    with open('fetch_proxy.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print(f'Appended {len(queries)} search queries')
