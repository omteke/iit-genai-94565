from langchain.chat_models import init_chat_model
import os
import pandas as pd
from dotenv import load_dotenv
import pandas as pd
import pandasql as ps

load_dotenv()

llm = init_chat_model(
    model = "llama-3.3-70b-versatile",
    model_provider = "openai",
    base_url = "https://api.groq.com/openai/v1",
    api_key = os.getenv("GROQ_API_KEY")
)
conversation = [
    {"role": "system", "content": "You are SQLite expert developer with 10 years of experience."}
]

csv_file = input("Enter path of a CSV file: ")
df = pd.read_csv(csv_file)
print("CSV schema: ")
print(df.dtypes)

while True:
    user_input = input("Ask anything about this CSV? ")
    if user_input == "exit":
        break
    llm_input = f"""
        Table Name: data
        Table Schema: {df.dtypes}
        Question: {user_input}
        Instruction:
            Write a SQL query for the above question. 
            Generate SQL query only in plain text format and nothing else.
            If you cannot generate the query, then output 'Error'.
    """
    result = llm.invoke(llm_input)
    print(result.content)

    final_result = ps.sqldf(result.content,{"data": df})
    print(final_result)
    # Invoke query -- SQL on Panda
    # Give result to LLM and ask to explain result in English.