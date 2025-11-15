import json
import hashlib
from pathlib import Path

paths = [
    Path(r"c:\Users\User\Desktop\Capstone 2\Capstone\Data\knowledge_base.json"),
    Path(r"c:\Users\User\Desktop\Capstone 2\Data\knowledge_base.json"),
]

def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def load_json(p: Path):
    text = p.read_text(encoding='utf-8')
    data = json.loads(text)
    return text, data

def summarize():
    t0, d0 = load_json(paths[0])
    t1, d1 = load_json(paths[1])

    print(f"File A: {paths[0]}\n  items: {len(d0)}\n  sha256: {sha256_text(t0)}\n")
    print(f"File B: {paths[1]}\n  items: {len(d1)}\n  sha256: {sha256_text(t1)}\n")

    identical = (sha256_text(t0) == sha256_text(t1))
    print(f"Identical files (byte/char-level): {identical}\n")

    # Program name sets
    progs_a = set((item.get('program') for item in d0 if 'program' in item))
    progs_b = set((item.get('program') for item in d1 if 'program' in item))
    print(f"Programs in A ({len(progs_a)}): {sorted(progs_a)[:10]}")
    print(f"Programs in B ({len(progs_b)}): {sorted(progs_b)[:10]}\n")
    if progs_a != progs_b:
        print("Program name differences:")
        print("  In A not in B:", sorted(progs_a - progs_b))
        print("  In B not in A:", sorted(progs_b - progs_a))
    else:
        print("Program name sets are identical.\n")

    # Compare entries one-by-one (by position). Report counts of mismatches.
    min_len = min(len(d0), len(d1))
    diffs = []
    for i in range(min_len):
        if d0[i] != d1[i]:
            diffs.append((i, d0[i], d1[i]))
            if len(diffs) >= 5:
                break

    if len(d0) != len(d1):
        print(f"Different number of items: A={len(d0)} B={len(d1)}")
    print(f"First {len(diffs)} differing entries (by index):")
    for idx, a, b in diffs:
        print(f"- index {idx}:\n  A program: {a.get('program')} | question: {a.get('question')[:80]!s}\n  B program: {b.get('program')} | question: {b.get('question')[:80]!s}\n")

    # If no differences found at same positions, try to detect unmatched items by question text
    if not diffs:
        qa_map_a = {item.get('question'): item for item in d0}
        qa_map_b = {item.get('question'): item for item in d1}
        only_a = set(qa_map_a) - set(qa_map_b)
        only_b = set(qa_map_b) - set(qa_map_a)
        print(f"Questions only in A: {len(only_a)}; only in B: {len(only_b)}")
        if only_a:
            print("  sample only-in-A:", list(only_a)[:3])
        if only_b:
            print("  sample only-in-B:", list(only_b)[:3])

if __name__ == '__main__':
    try:
        summarize()
    except Exception as e:
        print('ERROR during compare:', e)
