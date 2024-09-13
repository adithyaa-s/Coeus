import requests
import subprocess
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os

load_dotenv()

# Function to check for internet connection
def check_internet():
    try:
        requests.get('https://www.google.com/', timeout=5)
        return True
    except requests.ConnectionError:
        return False

# Function to run Llama3 using Ollama
def run_llama3(query):
    try:
        # Call Ollama CLI to run Llama3 model with the query
        result = subprocess.run(['ollama', 'run', 'llama3', query], capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        print(f"Error running Llama3 model: {e}")
        return None

# Function to get search results from Google Custom Search API
def search_google(query):
    api_key = os.getenv('GOOGLE_API_KEY')  # Replace with your Google API Key
    search_engine_id = os.getenv('GOOGLE_SEARCH_ENGINE_KEY')  # Replace with your Custom Search Engine ID
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={api_key}&cx={search_engine_id}"

    response = requests.get(url)
    data = response.json()
    
    if 'items' in data:
        return [item['link'] for item in data['items']]
    else:
        return []

# Function to extract main content from the webpage
def extract_text_from_url(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract text from the page, focusing on main content
        paragraphs = soup.find_all('p')
        content = ' '.join(p.get_text(separator=' ', strip=True) for p in paragraphs)
        
        # Limit text length for brevity
        return content[:2000] if content else "No relevant content found."
    except Exception as e:
        print(f"Error extracting text from {url}: {e}")
        return "Unable to retrieve data."

# Main loop to interact with the assistant
def assistant_loop():
    print("Welcome to your assistant. Type your query or enter '\\?' to quit.")

    while True:
        user_query = input("\nWhat would you like to ask? ")

        if user_query == "\\?":
            print("Exiting assistant. Goodbye!")
            break

        if check_internet():
            print("Internet connection detected. Searching Google for live data...")
            search_results = search_google(user_query)

            if search_results:
                # Extract text from the first relevant link
                print(f"Extracting data from: {search_results[0]}")
                text = extract_text_from_url(search_results[0])
                print("Search result:", text)
            else:
                print("No suitable data found on the web.")
        else:
            print("No internet connection. Querying Llama3 model...")
            llama_answer = run_llama3(user_query)
            if llama_answer:
                print("Llama3 answer:", llama_answer)
            else:
                print("Llama3 could not provide an answer.")

if __name__ == "__main__":
    # Start the assistant loop
    assistant_loop()
