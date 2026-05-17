"""Fetch DeepSeek via Selenium/Playwright-like approach using requests_html"""
import subprocess
import sys

# Try with curl and cookies
import os

# Use PowerShell to invoke the browser's fetch
# Since the user has the page open, let's try a different approach
# Let's use playwright if available
try:
    from playwright.sync_api import sync_playwright
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('https://chat.deepseek.com/share/aodwo1lrwms8l7mv35', wait_until='networkidle', timeout=30000)
        page.wait_for_timeout(5000)
        
        # Scroll to bottom
        prev_height = 0
        while True:
            page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            page.wait_for_timeout(2000)
            curr_height = page.evaluate('document.body.scrollHeight')
            if curr_height == prev_height:
                break
            prev_height = curr_height
        
        text = page.inner_text('body')
        with open('deepseek_text.txt', 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"Saved {len(text)} chars")
        browser.close()
        
except ImportError:
    print("playwright not installed, trying requests-html...")
    try:
        from requests_html import HTMLSession
        session = HTMLSession()
        r = session.get('https://chat.deepseek.com/share/aodwo1lrwms8l7mv35')
        r.html.render(sleep=5, timeout=30)
        text = r.html.text
        with open('deepseek_text.txt', 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"Saved {len(text)} chars")
    except ImportError:
        print("Neither playwright nor requests-html available.")
        print("Please copy-paste the chat content manually.")
        print("Or install: pip install playwright && playwright install chromium")
