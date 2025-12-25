from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain.tools import tool
# from dotenv import load_dotenv
from bs4 import BeautifulSoup

import pandasql as ps
import pandas as pd
import requests
import os

# load_dotenv()

llm = init_chat_model(
    model="google/gemma-3-4b",
    model_provider="openai",
    base_url="http://127.0.0.1:1234/v1",
    api_key="not-needed"
)

@tool
def csv_auto_sql_tool(file_path: str, question: str) -> str:
    """
    Automatically generate SQL from user question using LLM
    and execute it on CSV using pandasql.
    """
    file_path = "C:/GenAi_internship/Sunbeam_assignments/iit-genai-94565/Assigment09/emp_hdr.csv"

    df = pd.read_csv(file_path)
    schema = df.dtypes.to_string() #Converts the output into a single formatted string instead of a pandas object

    sql_prompt = f"""
You are an expert SQLite developer.

Table name: csv_df

Schema:
{schema}

Rules:
- Return ONLY SQL
- No explanation
- No markdown
- No semicolon

Question:
{question}
"""

    sql_response = llm.invoke(sql_prompt)
    sql_query = sql_response.content.strip() #Removing extra spaces/newlines

    try:
        result = ps.sqldf(sql_query, {"csv_df": df})
    except Exception as e:
        return f"SQL ERROR:\n{e}\n\nSQL:\n{sql_query}"

    return f"""
Generated SQL:
{sql_query}

Result:
{result}
"""

@tool
def sunbeam_web_tool(question: str) -> str:
    """
    Scrape Sunbeam website and answer user question
    based on scraped content.
    """

    url = "https://www.sunbeaminfo.com"
    response = requests.get(url, timeout=10)

    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = soup.get_text(separator=" ")
    text = " ".join(text.split())

    question_lower = question.lower()

    relevant = [
        s for s in text.split(".")
        if any(w in s.lower() for w in question_lower.split())
    ]

    if not relevant:
        return "No relevant information found on Sunbeam website."

    context = ". ".join(relevant[:8])

    prompt = f"""
Answer the question using ONLY the context below.

Context:
{context}

Question:
{question}

Answer in simple English.
"""

    response = llm.invoke(prompt)
    return response.content


agent = create_agent(
    model=llm,
    tools=[csv_auto_sql_tool, sunbeam_web_tool],
    system_prompt="""
You are an intelligent assistant.
- Use CSV tool for CSV questions
- Use Web tool for Sunbeam questions
- Answer briefly and clearly
"""
)


chat_history = []

print("\n=== Intelligent Agent Started ===")
print("Type 'exit' to quit\n")

while True:
    user_input = input("YOU: ")
    if user_input.lower() == "exit":
        break

    chat_history.append({"role": "user", "content": user_input})

    result = agent.invoke({"messages": chat_history})

    chat_history.extend(result["messages"])

    print("\nAI:", result["messages"][-1].content)
    print("-" * 50)
