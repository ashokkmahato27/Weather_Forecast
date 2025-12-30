# Weather Forecast Agent

A small Python agent that uses a Google Gemini LLM to extract a city name from user input and fetch current weather data from the OpenWeather API. The agent is implemented with a simple state graph (via `langgraph`) and demonstrates basic LLM extraction + external API usage.

## Features
- Validate user input.
- Use Gemini (via `langchain_google_genai`) to extract city names from free-text queries.
- Fetch current temperature and description from OpenWeather.
- Simple routing: weather query → weather fetch, otherwise returns current year or an invalid query message.

## Requirements
- Python 3.8+
- Packages used (install via pip):
  - requests
  - python-dotenv
  - langgraph
  - langchain_core
  - langchain_google_genai

You can install the likely dependencies with:
```bash
pip install requests python-dotenv langgraph langchain-core langchain-google-genai
```
(Adjust package names/versions to those compatible with your environment.)

## Environment variables
Create a `.env` file in the project root with the following keys:

```
GOOGLE_API_KEY=your_google_api_key_here
WEATHER_API_KEY=your_openweathermap_api_key_here
```

- GOOGLE_API_KEY: required by the Gemini LLM client.
- WEATHER_API_KEY: required to call OpenWeather current weather API.

## Usage
Run the script and enter a city when prompted:

```bash
python weather.py
```

Example interaction:
<img width="1111" height="255" alt="image" src="https://github.com/user-attachments/assets/2c255c11-5905-4ccd-85ed-3bb0b0bc8ae8" />


Notes:
- The script passes the full user query to the LLM to extract only the city name. If no city is extracted, the code defaults to `Kathmandu`.
- The LLM model used in the script is `gemini-2.5-flash`. Change the model or client configuration as needed.

## Files
- `weather.py` — main script: builds the state graph, queries the LLM to extract the city, calls OpenWeather, and prints the result.

## Error handling & caveats
- If environment variables are missing, the script prints an error message (e.g., missing `GOOGLE_API_KEY`).
- Network/API failures return a friendly message: "Could not fetch weather data for {city}."
- LLM extraction may return unexpected strings; you may want to sanitize or validate the extracted city before calling the weather API.

## Suggested improvements
- Validate and normalize extracted city names before calling OpenWeather.
- Support fallback strategies (e.g., ask user to confirm city if extraction is ambiguous).
- Add unit tests and more robust error logging.
- Use a configuration file or CLI arguments for flexibility.


