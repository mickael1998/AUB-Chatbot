import sqlite3
import json
import numpy as np
from typing import List
from openai import OpenAI
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

def cosine_similarity(vec1, vec2):
    """Calculate cosine similarity between two vectors"""
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

def sqlite_retrieve(user_input: str, selected_program: str = "", top_k: int = 6) -> List[str]:
    """Retrieve top-K relevant FAQs from SQLite database"""
    try:
        query_embedding = client.embeddings.create(
            input=user_input,
            model="text-embedding-3-large"
        ).data[0].embedding

        conn = sqlite3.connect("knowledge_base.db")
        c = conn.cursor()
        
        if selected_program:
            c.execute(
                "SELECT question, answer, program, embedding FROM faq WHERE program = ?",
                (selected_program,)
            )
        else:
            c.execute("SELECT question, answer, program, embedding FROM faq")
            
        results = c.fetchall()
        conn.close()

        if not results:
            return ["No relevant information found in the database."]

        sims = []
        for q, a, prog, emb_json in results:
            emb = json.loads(emb_json)
            sim = cosine_similarity(query_embedding, emb)
            sims.append((sim, f"**Program: {prog}**\n**Q:** {q}\n**A:** {a}"))

        sims.sort(key=lambda x: x[0], reverse=True)
        return [x[1] for x in sims[:top_k]]
    
    except Exception as e:
        return [f"Error retrieving from database: {str(e)}"]

def execute_sql_query(sql_query: str) -> List[tuple]:
    """Execute SQL query and return results"""
    conn = sqlite3.connect("knowledge_base.db")
    c = conn.cursor()
    c.execute(sql_query)
    results = c.fetchall()
    conn.close()
    return results

def format_sql_results(results: List[tuple]) -> str:
    """Format SQL query results for LLM processing"""
    if not results:
        return "No results found."
    
    if len(results[0]) == 1:  # Single column
        return "\n".join([str(row[0]) for row in results])
    else:  # Multiple columns
        return "\n".join([" | ".join([str(cell) for cell in row]) for row in results])

def clean_sql_query(sql_query: str) -> str:
    """Clean SQL query from markdown formatting"""
    if sql_query.startswith("```sql"):
        sql_query = sql_query[6:]
    if sql_query.startswith("```"):
        sql_query = sql_query[3:]
    if sql_query.endswith("```"):
        sql_query = sql_query[:-3]
    return sql_query.strip()

def build_conversation_context(chat_history: List[dict], max_messages: int = 3) -> str:
    """Build conversation context from chat history"""
    if not chat_history:
        return ""
    
    recent_history = chat_history[-max_messages:]
    conversation_context = ""
    for msg in recent_history:
        role = "User" if msg["role"] == "user" else "Assistant"
        conversation_context += f"{role}: {msg['content']}\n"
    
    return conversation_context
