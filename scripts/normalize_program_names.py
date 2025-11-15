import json
from pathlib import Path
from datetime import datetime

REPLACEMENTS = {
    "ITC": "ITC Diploma",
    "AI Starter Kit": "AI Starter Kit Diploma",
}

FILES = [
    Path(r"c:\Users\User\Desktop\Capstone 2\Capstone\Data\knowledge_base.json"),
    Path(r"c:\Users\User\Desktop\Capstone 2\Data\knowledge_base.json"),
]


def normalize_file(path: Path):
    if not path.exists():
        print(f"SKIP: {path} does not exist")
        return 0
    try:
        text = path.read_text(encoding="utf-8")
        data = json.loads(text)
    except Exception as e:
        print(f"ERROR reading {path}: {e}")
        return 0

    changed = 0
    for item in data:
        prog = item.get("program")
        if prog in REPLACEMENTS:
            item["program"] = REPLACEMENTS[prog]
            changed += 1

    if changed == 0:
        print(f"No changes needed for {path}")
        return 0

    # backup
    bak = path.with_suffix(path.suffix + f".bak.{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}")
    path.rename(bak)
    # write updated file
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Updated {path}: {changed} replacements (backup at {bak})")
    return changed


def main():
    total = 0
    for f in FILES:
        total += normalize_file(f)
    print(f"Total replacements: {total}")


if __name__ == "__main__":
    main()
