import sqlite3
from pathlib import Path

DB = Path(r"c:\Users\User\Desktop\Capstone 2\knowledge_base.db")

def main():
    if not DB.exists():
        print(f"DB not found: {DB}")
        return
    conn = sqlite3.connect(str(DB))
    c = conn.cursor()
    cols = [r[1] for r in c.execute("PRAGMA table_info(faq)").fetchall()]
    print("Existing columns:", cols)
    if 'section' in cols:
        print("No action needed: 'section' column already present.")
        conn.close()
        return
    if 'program' not in cols:
        print("Neither 'program' nor 'section' columns found; nothing to rename.")
        conn.close()
        return

    print("Attempting to rename column 'program' -> 'section' using ALTER TABLE...")
    try:
        c.execute("ALTER TABLE faq RENAME COLUMN program TO section")
        conn.commit()
        print("ALTER TABLE succeeded.")
    except sqlite3.OperationalError as e:
        print("ALTER TABLE failed (perhaps older SQLite). Falling back to create/copy method.", e)
        # recreate table with desired schema
        c.execute("PRAGMA foreign_keys=off")
        conn.commit()
        c.execute("CREATE TABLE IF NOT EXISTS faq_new (id INTEGER PRIMARY KEY AUTOINCREMENT, question TEXT, answer TEXT, embedding BLOB, section TEXT)")
        conn.commit()
        # copy data
        c.execute("INSERT INTO faq_new (id, question, answer, embedding, section) SELECT id, question, answer, embedding, program FROM faq")
        conn.commit()
        c.execute("DROP TABLE faq")
        conn.commit()
        c.execute("ALTER TABLE faq_new RENAME TO faq")
        conn.commit()
        c.execute("PRAGMA foreign_keys=on")
        conn.commit()
        print("Recreated table and copied data.")

    # final schema
    cols2 = [r[1] for r in c.execute("PRAGMA table_info(faq)").fetchall()]
    print("Final columns:", cols2)
    conn.close()

if __name__ == '__main__':
    main()
