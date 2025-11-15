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

def escape_markdown(text):
    """Escape $ signs so Streamlit Markdown doesn't break"""
    return text.replace("$", "\\$")


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
                "SELECT question, answer, section, embedding FROM faq WHERE section = ?",
                (selected_program,)
            )
        else:
            c.execute("SELECT question, answer, section, embedding FROM faq")
            
        results = c.fetchall()
        conn.close()

        if not results:
            return ["No relevant information found in the database."]

        sims = []
        for q, a, prog, emb_json in results:
            emb = json.loads(emb_json)
            sim = cosine_similarity(query_embedding, emb)
            # Try to parse answer as JSON/dict for formatting
            formatted_answer = a
            try:
                answer_obj = json.loads(a)
                if isinstance(answer_obj, dict):
                    # Special formatting for Project Management Diploma curriculum
                    if prog == "Project Management Diploma" and q.strip().lower() == "what is the program curriculum and structure?":
                        overview = answer_obj.get("overview", "")
                        track_1 = answer_obj.get("track_1", {})
                        track_2 = answer_obj.get("track_2", {})
                        electives = answer_obj.get("electives", {})
                        all_electives = electives.get('list', [])
                        formatted_answer = (
                            f"{overview}\n\n"
                            f"**Option 1: Construction Management Track (4 core + 2 electives)**\n"
                            f"Core Courses:\n- " + "\n- ".join(track_1.get('core_courses', [])) + "\n\n"
                            f"**Elective Courses (choose 2):**\n\n" + "\n- ".join([""].__add__(all_electives)) + "\n\n"
                            f"**Option 2: Adaptive and Strategic Project Management Track (2 core + 4 electives)**\n"
                            f"Core Courses:\n- " + "\n- ".join(track_2.get('core_courses', [])) + "\n\n"
                            f"**Elective Courses (choose 4):**\n\n" + "\n- ".join([""].__add__(all_electives))
                        )
                    else:
                        # Generic dict formatting
                        formatted_answer = json.dumps(answer_obj, indent=2)
                elif isinstance(answer_obj, list):
                    formatted_answer = "\n".join([str(item) for item in answer_obj])
            except Exception:
                pass
            sims.append((sim, f"**Program: {prog}**\n**Q:** {q}\n**A:** {formatted_answer}"))

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
