import json
import re

filepath = 'Data/knowledge_base.json'

# Read the raw JSON
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace "program": with "section": using regex
# This handles both single and double quotes
content = re.sub(r'"program"\s*:', '"section":', content)

# Write back
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

# Verify
with open(filepath, 'r', encoding='utf-8') as f:
    kb = json.load(f)

program_count = sum(1 for i in kb if 'program' in i)
section_count = sum(1 for i in kb if 'section' in i)

print(f'✅ Replaced all "program" keys with "section"')
print(f'Total items: {len(kb)}')
print(f'Items with program: {program_count}')
print(f'Items with section: {section_count}')
