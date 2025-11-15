import json

filepath = 'Data/knowledge_base.json'

with open(filepath, 'r', encoding='utf-8') as f:
    kb = json.load(f)

count = 0
for item in kb:
    if 'program' in item:
        item['section'] = item.pop('program')
        count += 1

with open(filepath, 'w', encoding='utf-8') as f:
    json.dump(kb, f, indent=2, ensure_ascii=False)

print(f'✅ {filepath}: Replaced {count} "program" keys with "section"')
print(f'Total items: {len(kb)}')
