import sys
import re

with open('fetch_proxy.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: task_done in worker
old_worker = '''    def _worker(self, q, pbar):
        while not self._cancel_event.is_set():
            if self._wait_if_paused(): break
            try:
                item = q.get(timeout=2)
                self._check_url(item)
                q.task_done()
                if pbar: pbar.update(1)
            except Exception:
                break'''
new_worker = '''    def _worker(self, q, pbar):
        while not self._cancel_event.is_set():
            if self._wait_if_paused(): break
            try:
                item = q.get(timeout=2)
                try:
                    self._check_url(item)
                finally:
                    q.task_done()
                    if pbar: pbar.update(1)
            except Exception:
                break'''
content = content.replace(old_worker, new_worker)

# Fix 2: Base64 string memory duplicate
old_base64 = '''        stripped = content.replace('\\n', '').replace('\\r', '').strip()
        if len(stripped) > 20 and re.match(r'^[A-Za-z0-9+/]+={0,2}$', stripped):
            import base64
            try:
                decoded = base64.b64decode(stripped).decode('utf-8')
                content = content + "\\n" + decoded
            except Exception:
                pass'''
new_base64 = '''        stripped = content.replace('\\n', '').replace('\\r', '').strip()
        if len(stripped) > 20 and re.match(r'^[A-Za-z0-9+/]+={0,2}$', stripped):
            import base64
            try:
                # [AUDIT FIX] Override content instead of concatenating to avoid memory duplication
                decoded = base64.b64decode(stripped).decode('utf-8')
                content = decoded
            except Exception:
                pass'''
content = content.replace(old_base64, new_base64)

with open('fetch_proxy.py', 'w', encoding='utf-8') as f:
    f.write(content)
