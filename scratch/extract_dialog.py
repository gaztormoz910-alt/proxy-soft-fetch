import re
import json

def main():
    try:
        with open('Диалог с AI.txt', 'r', encoding='utf-8') as f:
            text = f.read()
            
        urls = re.findall(r'https?://[^\s\"\'\>\]\)]+', text)
        unique_urls = list(set(urls))
        
        proxy_urls = []
        for u in unique_urls:
            # basic filtering for proxy-related URLs or github repos
            if 'github.com' in u or 'raw.githubusercontent.com' in u or 'prox' in u.lower() or '.txt' in u or 'api' in u:
                proxy_urls.append(u)
                
        print(f"Total unique URLs found: {len(unique_urls)}")
        print(f"Potential proxy URLs: {len(proxy_urls)}")
        
        with open('extracted_from_dialog.json', 'w', encoding='utf-8') as f:
            json.dump(proxy_urls, f, indent=4)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
