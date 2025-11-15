import json
from pathlib import Path
from datetime import datetime

FILES = [
    Path(r"c:\Users\User\Desktop\Capstone 2\Capstone\Data\knowledge_base.json"),
    Path(r"c:\Users\User\Desktop\Capstone 2\Data\knowledge_base.json"),
]

def reorder_item(item: dict) -> dict:
    # new order: section, question, answer, then any other keys in original order
    new = {}
    # pick section (or program fallback)
    if 'section' in item:
        new['section'] = item['section']
    elif 'program' in item:
        new['section'] = item['program']

    if 'question' in item:
        new['question'] = item['question']
    if 'answer' in item:
        new['answer'] = item['answer']

    # append any other keys preserving original order
    for k, v in item.items():
        if k in ('section', 'program', 'question', 'answer'):
            continue
        new[k] = v

    return new

def process(path: Path):
    if not path.exists():
        print(f"SKIP missing: {path}")
        return 0
    data = json.loads(path.read_text(encoding='utf-8'))
    new_data = [reorder_item(item) for item in data]

    bak = path.with_suffix(path.suffix + f".bak.{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}")
    path.rename(bak)
    path.write_text(json.dumps(new_data, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"Rewrote {path} with reordered keys (backup at {bak})")
    return len(new_data)

def main():
    total = 0
    for p in FILES:
        total += process(p)
    print(f"Processed total items: {total}")

if __name__ == '__main__':
    main()
