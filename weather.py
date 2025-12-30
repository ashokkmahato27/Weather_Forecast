import os
import requests
from typing import TypedDict
from langgraph.graph import StateGraph, MessagesState, START, END
from langchain_core.messages import AIMessage
from datetime import datetime
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

# Loading environment variables (API keys)
load_dotenv()

# Ensure Google API key exists
if not os.getenv("GOOGLE_API_KEY"):
    print("Error: GOOGLE_API_KEY not found! Check your .env file.")

# Initialize Gemini LLM
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

# Extends MessagesState to store routing flags
class AgentState(MessagesState):
    is_valid: bool        
    needs_weather: bool   


# ----Node Functions ----
def validate_query(state: AgentState):
    """
    Checks whether the user query is non-empty and meaningful.
    """
    user_message = state["messages"][-1].content
    state["is_valid"] = bool(user_message and len(user_message.strip()) >= 2)
    return state


def check_weather_needed(state: AgentState):
    """
    Determines whether the query is related to weather.
    """
    state["needs_weather"] = "weather" in state["messages"][-1].content.lower()
    return state


def weather_node(state: AgentState):
    """
    Extracts city name using LLM and fetches weather data
    from OpenWeather API.
    """
    user_message = state["messages"][-1].content.lower()

    if "weather" in user_message:
        print("Your Query is in Progress ...")

        # Extract city name using LLM
        extraction_prompt = f"Extract only the city name from: '{user_message}'. If none, say Kathmandu."
        city = llm.invoke(extraction_prompt).content.strip()

        WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"

        try:
            data = requests.get(url).json()
            temp = data['main']['temp']
            desc = data['weather'][0]['description']
            response = f"The weather in {city} is {temp}°C with {desc}."
        except:
            response = f"Could not fetch weather data for {city}."

        return {"needs_weather": True, "messages": [AIMessage(content=response)]}

    return {"needs_weather": False}


def current_year(state: AgentState):
    """
    Returns the current system year if weather is not requested.
    """
    year = datetime.now().year
    return {"messages": [AIMessage(content=f"The current running year is {year}.")]}


def invalid_query(state: AgentState):
    """
    Handles invalid or empty user input.
    """
    return {"messages": [AIMessage(content="The query you provided is invalid.")]}


# ---------- Routing Logic ----------
def route_validation(state: AgentState):
    """Routes based on query validity."""
    return "valid" if state["is_valid"] else "invalid"


def route_weather(state: AgentState):
    """Routes based on whether weather data is required."""
    return "weather" if state["needs_weather"] else "year"


# ---------- Graph Construction ----------
graph = StateGraph(AgentState)

# Register nodes
graph.add_node("validate_query", validate_query)
graph.add_node("check_weather", check_weather_needed)
graph.add_node("weather", weather_node)
graph.add_node("current_year", current_year)
graph.add_node("invalid_query", invalid_query)

# Define flow
graph.add_edge(START, "validate_query")

graph.add_conditional_edges(
    "validate_query",
    route_validation,
    {"valid": "check_weather", "invalid": "invalid_query"}
)

graph.add_conditional_edges(
    "check_weather",
    route_weather,
    {"weather": "weather", "year": "current_year"}
)

# Termination points
graph.add_edge("weather", END)
graph.add_edge("current_year", END)
graph.add_edge("invalid_query", END)

# Compile agent
agent = graph.compile()

# ---------- User Input ----------
city = input("Enter city name: ")
query = f"What is the weather of {city}?"

# Execute agent
result = agent.invoke({
    "messages": [{"role": "user", "content": query}]
})

print("\nOutput:")
print(result["messages"][-1].content)
