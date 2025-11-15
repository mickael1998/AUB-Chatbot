import json
from pathlib import Path
from datetime import datetime

FILES = [
    Path(r"c:\Users\User\Desktop\Capstone 2\Capstone\Data\knowledge_base.json"),
    Path(r"c:\Users\User\Desktop\Capstone 2\Data\knowledge_base.json"),
]

def convert(path: Path):
    if not path.exists():
        print(f"SKIP missing: {path}")
        return 0
    text = path.read_text(encoding='utf-8')
    data = json.loads(text)
    changed = 0
    for item in data:
        if 'program' in item:
            # move value to 'section'
            item['section'] = item.pop('program')
            changed += 1

    if changed == 0:
        print(f"No 'program' keys found in {path}; nothing changed.")
        return 0

    # backup
    bak = path.with_suffix(path.suffix + f".bak.{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}")
    path.rename(bak)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"Converted {path}: {changed} 'program' -> 'section' (backup at {bak})")
    return changed

def main():
    total = 0
    for p in FILES:
        total += convert(p)
    print(f"Total converted entries: {total}")

if __name__ == '__main__':
    main()
