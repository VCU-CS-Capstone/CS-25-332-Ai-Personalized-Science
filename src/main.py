import os
import re
import requests
import urllib.request
from dotenv import load_dotenv

# Load your Claude API key
load_dotenv()
API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Claude Opus API URL and version
CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"
CLAUDE_MODEL = "claude-3-opus-20240229"

# Step 1: User interests
interests = "algebra and science"

# Step 2: Fetch 50 articles from arXiv
def get_arxiv_articles():
    url = 'http://export.arxiv.org/api/query?search_query=all&start=0&max_results=50'
    data = urllib.request.urlopen(url).read().decode('utf-8')
    entries = re.findall(r'<entry.*?>.*?<title.*?>(.*?)</title>.*?<summary.*?>(.*?)</summary>', data, re.DOTALL)
    return [(title.strip(), summary.strip()) for title, summary in entries]

# Step 3: Build prompt for Claude
def build_prompt(interests, articles):
    prompt = f"""
You are a highly capable research assistant. A user has specified their interests as: {interests}.

Below is a list of article titles and summaries. Analyze each and determine how closely they match the user's interests. 
Rank the **top 10 most relevant articles** from 1 to 10. For each, provide:
- The article title
- A brief justification
- A relevance score from 0 (not relevant) to 100 (extremely relevant)

Articles:
"""
    for i, (title, summary) in enumerate(articles, 1):
        trimmed_summary = summary[:300].strip() + ("..." if len(summary) > 300 else "")
        prompt += f"\nArticle {i} Title: {title}\nArticle {i} Summary: {trimmed_summary}\n"
    return prompt

# Step 4: Send request to Claude for a chat
def query_claude(messages):
    headers = {
        "x-api-key": API_KEY,
        "Content-Type": "application/json",
        "anthropic-version": "2023-06-01"
    }

    body = {
        "model": CLAUDE_MODEL,
        "max_tokens": 1024,
        "messages": messages
    }

    response = requests.post(CLAUDE_API_URL, headers=headers, json=body)

    # Check for any error
    if response.status_code != 200:
        print("Claude API Error:")
        print("Status Code:", response.status_code)
        print("Response:", response.text)
        response.raise_for_status()

    return response.json()

# Step 5: Main logic
def main():
    print("Fetching articles from arXiv...")
    articles = get_arxiv_articles()

    # Initialize message history for the chat session
    messages = [{"role": "user", "content": f"My interests are in {interests}. Can you recommend articles based on these?"}]
    
    # Build prompt and send to Claude
    print("\nBuilding prompt and querying Claude Opus...")
    prompt = build_prompt(interests, articles)
    
    # Add the generated prompt to the messages for the chat
    messages.append({"role": "user", "content": prompt})

    # Get response from Claude (first round)
    result = query_claude(messages)

    # Extract and print Claude's response
    print("\nClaude's Top 10 Article Recommendations:\n")
    print(result['content'][0]['text'])

    # Optionally: Ask for feedback or further questions from the user and repeat the loop
    while True:
        user_input = input("\nDo you want to ask anything else or refine the recommendations? Type 'exit' to quit: ")
        if user_input.lower() == 'exit':
            print("Ending chat session.")
            break
        
        # Add user's question to the messages
        messages.append({"role": "user", "content": user_input})

        # Send the updated messages to Claude for a new response
        result = query_claude(messages)
        print("\nClaude's Response:\n", result['content'][0]['text'])

if __name__ == "__main__":
    main()
