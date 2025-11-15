from typing import Dict, List, Optional
from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain.tools import Tool
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from langchain_community.callbacks import StreamlitCallbackHandler
from dotenv import load_dotenv
import os
from utils import sqlite_retrieve, execute_sql_query, format_sql_results, clean_sql_query
from langchain.globals import set_verbose

# Set global verbosity for LangChain
set_verbose(True)

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class AUBStudentAgent:
    """LangChain-based AI agent for AUB student assistance"""
    
    def __init__(self, temperature: float = 0.2):
        self.llm = ChatOpenAI(
            api_key=OPENAI_API_KEY,
            model="gpt-4.1",
            temperature=temperature
        )
        
        # Define tools that the agent can use
        self.tools = self._create_tools()
        
        # Create the agent with a comprehensive prompt
        self.agent = self._create_agent()
        
        # Create agent executor
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=3
        )
    
    def _create_tools(self) -> List[Tool]:
        """Create tools that the agent can use"""
        
        def semantic_search_tool(query: str, program: str = "") -> str:
            """Search the AUB FAQ database using semantic similarity"""
            try:
                results = sqlite_retrieve(query, program, top_k=6)
                if results and results[0] != "No relevant information found in the database.":
                    return "\n\n".join(results)
                return "No relevant information found in the database."
            except Exception as e:
                return f"Error searching database: {str(e)}"

        def llm_sql_tool(query: str) -> str:
            """Convert user query to SQL using LLM, then run it and return results."""
            try:
                sql_prompt = f"""
                You are an expert at converting natural language questions into SQL queries for the following SQLite schema:
                Table: faq (id INTEGER PRIMARY KEY, question TEXT, answer TEXT, section TEXT, embedding BLOB, section_is_program BOOLEAN)
                columns description:
                - id: Unique identifier for each FAQ entry
                - question: The FAQ question text
                - answer: The FAQ answer text
                - section: The name of program the FAQ belongs
                - embedding: The vector embedding of the question for semantic search
                - section_is_program: Boolean indicating if the section is a program or not
                User question: {query}
                Only return the SQL query, nothing else.
                """
                sql_response = self.llm.invoke(sql_prompt)
                sql_query = clean_sql_query(sql_response.content.strip())
                results = execute_sql_query(sql_query)
                if not results:
                    return f"Executed SQL: {sql_query}\nNo results found."
                return f"Executed SQL: {sql_query}\n{format_sql_results(results)}"
            except Exception as e:
                return f"Error in LLM SQL tool: {str(e)}"
        
        return [
            Tool(
                name="semantic_search",
                description="Search the AUB FAQ database using semantic similarity. Use this for specific questions about program details, requirements, admissions, courses, fees, prerequisites, career outcomes. Input should be the user's question and optionally a specific program name.",
                func=lambda x: semantic_search_tool(x.split("|")[0], x.split("|")[1] if "|" in x else "")
            ),
            Tool(
                name="llm_sql_tool",
                description="Convert a user question to SQL using the LLM, then run it on the FAQ database. Use for any question that can be answered by a SQL query.",
                func=llm_sql_tool
            )
        ]
    
    def _create_agent(self):
        """Create the LangChain agent with a comprehensive prompt"""
        
        system_prompt = """You are a helpful AUB (American University of Beirut) student assistant. Your ONLY function is to use tools to answer questions about AUB programs. You MUST follow these rules:

1.  **CRITICAL RULE:** For ANY question about AUB programs, admissions, courses, fees, or any related topic, you MUST use either the `semantic_search` tool or the `llm_sql_tool`. DO NOT answer from your own knowledge.
2.  If a tool returns information, base your entire answer on that information.
3.  If a tool returns "No relevant information found", then and only then should you state that you could not find the information and suggest contacting AUB admissions at info@aub.edu.lb.
4.  You are forbidden from answering questions about AUB programs from memory. Your memory is only for conversation history. All factual data must come from a tool.
5.  If the user asks a question that is not about AUB programs, politely decline and state your purpose.
6. When the user question does not require Semantic Retrieval, but can be answered via a direct SQL query, use the llm_sql_tool.
AVAILABLE TOOLS:
- semantic_search: Search FAQ database using semantic similarity
- llm_sql_tool: Convert a user question to SQL using the LLM, then run it on the FAQ database

Remember to maintain conversation context and provide helpful, accurate responses based on the tool outputs."""

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        return create_openai_functions_agent(self.llm, self.tools, prompt)
    
    def _format_chat_history(self, messages: List[Dict]) -> List[BaseMessage]:
        """Convert message history to LangChain format, keeping last 6 user and 6 assistant messages (12 total)"""
        formatted_messages = []
        # Only keep last 6 user and last 6 assistant messages (12 total, alternating)
        user_msgs = [m for m in messages if m["role"] == "user"][-6:]
        assistant_msgs = [m for m in messages if m["role"] == "assistant"][-6:]
        # Interleave them in order as in the original chat
        combined = []
        i = j = 0
        for m in messages:
            if m["role"] == "user" and i < len(user_msgs) and m == user_msgs[i]:
                combined.append(m)
                i += 1
            elif m["role"] == "assistant" and j < len(assistant_msgs) and m == assistant_msgs[j]:
                combined.append(m)
                j += 1
            if len(combined) == 12:
                break
        # If not enough, just take the last 12 in order
        if len(combined) < 12:
            combined = messages[-12:]
        for msg in combined:
            if msg["role"] == "user":
                formatted_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                formatted_messages.append(AIMessage(content=msg["content"]))
        return formatted_messages
    
    def process_query(self, 
                     user_input: str, 
                     chat_history: List[Dict],
                     streamlit_callback: Optional[StreamlitCallbackHandler] = None,
                     verbose: bool = False) -> Dict:
        """Process user query using the agent"""
        
        try:
            # Format chat history
            formatted_history = self._format_chat_history(chat_history)
            
            # Prepare input with program context if selected
            enhanced_input = user_input
            # Set up callbacks
            callbacks = [streamlit_callback] if streamlit_callback else []
            
            # Set verbose mode
            self.agent_executor.verbose = verbose
            
            # Execute the agent
            result = self.agent_executor.invoke({
                "input": enhanced_input,
                "chat_history": formatted_history
            }, callbacks=callbacks)
            
            return {
                "response": result["output"],
                "success": True,
                "tools_used": self._extract_tools_used(result)
            }
            
        except Exception as e:
            return {
                "response": f"I apologize, but I encountered an error: {str(e)}",
                "success": False,
                "tools_used": []
            }
    
    def _extract_tools_used(self, result: Dict) -> List[str]:
        """Extract which tools were used during execution"""
        tools_used = []
        
        # This is a simplified extraction - in practice, you might want to 
        # implement more sophisticated tracking
        if "intermediate_steps" in result:
            for step in result["intermediate_steps"]:
                if hasattr(step[0], 'tool'):
                    tools_used.append(step[0].tool)
        
        return tools_used

# Convenience functions for backward compatibility
def create_aub_agent() -> AUBStudentAgent:
    """Create and return an AUB student agent"""
    return AUBStudentAgent()

def process_user_query(agent: AUBStudentAgent, 
                      user_input: str, 
                      chat_history: List[Dict],
                      verbose: bool = False,
                      streamlit_callback: Optional[StreamlitCallbackHandler] = None) -> Dict:
    """Process user query using the agent"""
    return agent.process_query(user_input, chat_history, streamlit_callback, verbose)
