import ast
with open('fetch_proxy.py', encoding='utf-8') as f:
    tree = ast.parse(f.read())
for n in ast.walk(tree):
    if isinstance(n, ast.Assign) and getattr(n.targets[0], 'id', '') == 'user_agents':
        print(f"Starts at {n.lineno}, ends at {n.end_lineno}")
