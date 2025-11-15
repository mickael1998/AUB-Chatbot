import json
from pathlib import Path

p = Path(r"c:\Users\User\Desktop\Capstone 2\Data\knowledge_base.json")

def short(x, n=120):
    s = repr(x)
    return s if len(s) <= n else s[:n-1] + '…'

data = json.loads(p.read_text(encoding='utf-8'))
print(f"Loaded {p} -> {len(data)} items")

missing_program = []
missing_question = []
missing_answer = []
empty_objects = []
nonstring_program = []
nonstring_question = []
nonstring_answer = []

for i, item in enumerate(data):
    if not item:
        empty_objects.append(i)
        continue
    # accept either 'section' (new) or 'program' (legacy)
    if 'section' not in item and 'program' not in item:
        missing_program.append((i, item))
    else:
        val = item.get('section') if 'section' in item else item.get('program')
        if not isinstance(val, str):
            nonstring_program.append((i, val))
    if 'question' not in item:
        missing_question.append((i, item))
    else:
        if not isinstance(item['question'], str):
            nonstring_question.append((i, item['question']))
    if 'answer' not in item:
        missing_answer.append((i, item))
    else:
        if not isinstance(item['answer'], (str, dict, list)):
            nonstring_answer.append((i, item['answer']))

print('\nSummary:')
print(f"  empty objects: {len(empty_objects)}")
print(f"  missing 'section' or 'program': {len(missing_program)}")
print(f"  missing 'question': {len(missing_question)}")
print(f"  missing 'answer': {len(missing_answer)}")
print(f"  non-string 'program' values: {len(nonstring_program)}")
print(f"  non-string 'question' values: {len(nonstring_question)}")
print(f"  non-string 'answer' values (neither str/dict/list): {len(nonstring_answer)}")

def show_samples(lst, title, limit=5):
    if not lst:
        return
    print(f"\n{title} (showing up to {limit}):")
    for idx, sample in lst[:limit]:
        print(f" - index {idx}: {short(sample)}")

show_samples([(i, data[i]) for i in empty_objects], 'Empty objects')
show_samples(missing_program, "Missing 'section'/'program' entries")
show_samples(missing_question, "Missing 'question' entries")
show_samples(missing_answer, "Missing 'answer' entries")
show_samples(nonstring_program, "Non-string section/program values")
show_samples(nonstring_question, "Non-string question values")
show_samples(nonstring_answer, "Non-string answer values")

if __name__ == '__main__':
    pass
