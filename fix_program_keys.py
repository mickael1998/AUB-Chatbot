import json

files = [
    "Data/knowledge_base.json",
    "Capstone/Data/knowledge_base.json"
]

for filepath in files:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            kb = json.load(f)
        
        count = 0
        for item in kb:
            if "program" in item:
                item["section"] = item.pop("program")
                count += 1
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(kb, f, indent=2, ensure_ascii=False)
        
        print(f"✅ {filepath}: Replaced {count} 'program' keys with 'section'")
    except Exception as e:
        print(f"❌ {filepath}: {e}")
