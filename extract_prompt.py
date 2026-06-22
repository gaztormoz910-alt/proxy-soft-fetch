import json

with open(r"c:\Users\Bog_1\.gemini\antigravity\brain\39f57b39-3a6d-498d-88a5-e57d62d9c823\.system_generated\logs\transcript_full.jsonl", 'r', encoding='utf-8') as f:
    for line in f:
        try:
            data = json.loads(line)
            if data.get('type') == 'USER_INPUT' and 'FINAL_BOSS_SOURCES' in data.get('content', ''):
                with open('extracted_prompt.py', 'w', encoding='utf-8') as out:
                    out.write(data['content'])
                print("Found and extracted!")
                break
        except Exception as e:
            print(e)
