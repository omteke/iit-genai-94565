from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain.tools import tool
from langchain.agents.middleware import wrap_model_call 
from dotenv import load_dotenv
import os
import requests
import json
load_dotenv()
@tool
def calculator(expression):
    """
    This calculator function solves all arithmatic expressions containing constant values
    and it also supports all arithmatic operators like +,-,*,/ and parenthesis

    :para expression:str input arithmatic expression
    :return expression result as str
    """
    try:
        result = eval(expression)
        return str(result)
    except:
        "Error: cannot solve the expression"

@tool
def current_weather(city):
    """This current_weather() function get the current weather of given city.
        if weather cannot found,it return 'Error'.
        This fuction cannot return historic and general weather of  city
        
    :param city: str input - city name
    :returns current weather in json format or 'Error'"""

    try:
        api_key = os.getenv("OPENWEATHER_API_KEY")
        url = (
            f"https://api.openweathermap.org/data/2.5/weather"
            f"?q={city}&appid={api_key}&units=metric"
        )
        response = requests.get(url)
        data = response.json()

        if response.status_code != 200:
            return "Weather not found"

        return (
            f"City: {city}\n"
            f"Temperature: {data['main']['temp']} °C\n"
            f"Humidity: {data['main']['humidity']} %\n"
            f"Condition: {data['weather'][0]['description']}"
        )
    except Exception as e:
        return f"Error: {e}"

@tool
def file_reader(filepath):
     """
    Read and return the content of a text file.

    Args:
        filepath (str): Path of the file to read
    """
     with open(filepath, "r") as file:
        text = file.read()
        return text
    
@tool
def knowledge_lookup(topic: str) -> str:
    """Lookup basic knowledge about a topic."""
    knowledge_base = {
        "python": "Python is a high-level programming language.",
        "langchain": "LangChain is a framework for building LLM-powered applications.",
        "llm": "LLM stands for Large Language Model."
    }
    return knowledge_base.get(topic.lower(), "No information found.")
                              
@wrap_model_call
def logging_middleware(request, handler):
    print("\nBEFORE MODEL CALL")
    for msg in request.messages:
        print(msg)

    response = handler(request)

    print("AFTER MODEL CALL")
    print("Model Output:", response.result[0].content)

    return response

llm=init_chat_model(
    model="google/gemma-3-4b",
    model_provider="openai",
    base_url="http://127.0.0.1:1234/v1",
    api_key = "non-neened"

)

agent = create_agent(
    model=llm,
    tools=[
        calculator,
        current_weather,
        file_reader
    ],
    middleware=[logging_middleware],
    system_prompt="You are a helpful assistant.answer in short"
)

user_inputs = input("YOU:")
while True:
    if user_inputs == "exit":
        break

    result = agent.invoke({
        "messages":[{"role":"user","content":user_inputs}]
    })

    llm_output = result["messages"][-1]
    print("AI:",llm_output.content)
    print("\n\n", result["messages"])