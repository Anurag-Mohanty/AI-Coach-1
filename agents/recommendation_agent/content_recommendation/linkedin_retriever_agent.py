from bs4 import BeautifulSoup
import requests
import time
import random
from openai import OpenAI
import os
from functools import wraps

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_search_queries(focused_subtask, context):
    prompt = f"""
Generate 3 LinkedIn-style search queries to find influencer posts or practical insights for:
Task: {focused_subtask}
Tools: {context['tool_familiarity']}
Missing skills: {context['missing_skills']}

Output only search queries.
"""
    try:
        res = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )
        return [q.strip() for q in res.choices[0].message.content.split("\n") if q.strip()]
    except Exception as e:
        print("Search query LLM failed:", e)
        return [focused_subtask]

def search_linkedin(query):
    try:
        search_url = f"https://www.linkedin.com/search/results/content/?keywords={query}"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'DNT': '1'
        }

        response = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        results = []
        posts = soup.find_all('div', {'class': 'search-results__list-item'})

        for post in posts[:5]:
            try:
                title_elem = post.find('span', {'class': 'actor-name'})
                link_elem = post.find('a', {'class': 'app-aware-link'}) 
                snippet_elem = post.find('p', {'class': 'search-result__snippet'})

                title = title_elem.text.strip() if title_elem else "LinkedIn Post"
                link = link_elem['href'] if link_elem else None
                snippet = snippet_elem.text.strip() if snippet_elem else "No preview available"

                if link:
                    results.append({
                        "title": title,
                        "link": link,
                        "source": "LinkedIn (Public)",
                        "format": "Post",
                        "snippet": snippet
                    })
            except Exception as e:
                print(f"Error processing result: {str(e)}")
                continue

        return results
    except Exception as e:
        print(f"Search error: {str(e)}")
        return []

def timed_function(name):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"{name}: Execution time = {elapsed_time:.4f} seconds")
            return result
        return wrapper
    return decorator

@timed_function("LinkedIn Retrieval")
def run_linkedin_retriever(focused_subtask, context, token=None):
    all_results = []
    queries = generate_search_queries(focused_subtask, context)

    print(f"Generated queries: {queries}")

    for query in queries:
        print(f"Searching LinkedIn with query: {query}")
        time.sleep(random.uniform(1, 2))  # Be nice to LinkedIn
        results = search_linkedin(query)
        print(f"Found {len(results)} results for query")
        all_results.extend(results)

    # Deduplicate results
    seen_links = set()
    unique_results = []
    for result in all_results:
        if result['link'] not in seen_links:
            seen_links.add(result['link'])
            unique_results.append(result)

    print(f"LinkedIn: Retrieved {len(unique_results)} unique results")
    return unique_results, [f"Found {len(unique_results)} LinkedIn results"]