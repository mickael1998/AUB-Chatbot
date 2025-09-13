import os
import json
import sqlite3
from openai import OpenAI

client = OpenAI(api_key="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")

def get_openai_embedding(text, model="text-embedding-3-large"):
    response = client.embeddings.create(
        input=text,
        model=model
    )
    return response.data[0].embedding

def main():
    # Load knowledge base
    with open("Data/knowledge_base.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    # Connect to SQLite
    conn = sqlite3.connect("knowledge_base.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS faq (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT,
            answer TEXT,
            embedding BLOB,
            program TEXT
        )
    """)

    # Insert data
    for entry in data:
        question = entry["question"]
        answer = entry["answer"]
        program = entry["program"]
        embedding = get_openai_embedding(question)
        # Store embedding as JSON string
        c.execute(
            "INSERT INTO faq (question, answer, program, embedding) VALUES (?, ?, ?, ?)",
            (question, answer, program, json.dumps(embedding))
        )
        print(f"Inserted: {question}")

    conn.commit()
    conn.close()
    print("All questions embedded and stored in SQLite database.")

if __name__ == "__main__":
    main()
