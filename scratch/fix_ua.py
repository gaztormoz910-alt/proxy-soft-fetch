import ast

def main():
    with open('fetch_proxy.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    start_idx = 930 - 1
    end_idx = 1921 - 1
    
    new_ua = [
        '        user_agents = [\n',
        '            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",\n',
        '            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",\n',
        '            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",\n',
        '            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36",\n',
        '            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"\n',
        '        ]\n'
    ]
    
    new_lines = lines[:start_idx] + new_ua + lines[end_idx+1:]
    
    with open('fetch_proxy.py', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
        
    print("Replaced user agents!")

if __name__ == '__main__':
    main()
