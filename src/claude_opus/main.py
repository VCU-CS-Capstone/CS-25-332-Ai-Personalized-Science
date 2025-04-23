import os
import re
import requests
import urllib.request
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("ANTHROPIC_API_KEY")


CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"
CLAUDE_MODEL = "claude-3-opus-20240229"


interests = "algebra and science"


def get_arxiv_articles():
    url = 'http://export.arxiv.org/api/query?search_query=all&start=0&max_results=50'
    data = urllib.request.urlopen(url).read().decode('utf-8')
    entries = re.findall(r'<entry.*?>.*?<title.*?>(.*?)</title>.*?<summary.*?>(.*?)</summary>', data, re.DOTALL)
    return [(title.strip(), summary.strip()) for title, summary in entries]


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

    
    if response.status_code != 200:
        print("Claude API Error:")
        print("Status Code:", response.status_code)
        print("Response:", response.text)
        response.raise_for_status()

    return response.json()


def main():
    print("Fetching articles from arXiv...")
    articles = get_arxiv_articles()

    
    messages = [{"role": "user", "content": f"My interests are in {interests}. Can you recommend articles based on these?"}]
    
    
    print("\nBuilding prompt and querying Claude Opus...")
    prompt = build_prompt(interests, articles)
    
    
    messages.append({"role": "user", "content": prompt})

    
    result = query_claude(messages)

  
    print("\nClaude's Top 10 Article Recommendations:\n")
    print(result['content'][0]['text'])

    
    while True:
        user_input = input("\nDo you want to ask anything else or refine the recommendations? Type 'exit' to quit: ")
        if user_input.lower() == 'exit':
            print("Ending chat session.")
            break
        
  
        messages.append({"role": "user", "content": user_input})

        
        result = query_claude(messages)
        print("\nClaude's Response:\n", result['content'][0]['text'])

if __name__ == "__main__":
    main()
