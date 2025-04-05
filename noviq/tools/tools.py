import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
import webbrowser
import time



def get_search_queries(search_query) -> list[tuple[str, str]]:
    """
    Get search results for a query using DuckDuckGo
    Returns a list of (title, URL) tuples
    """
    # DuckDuckGo HTML search
    url = f"https://html.duckduckgo.com/html/?q={quote(search_query)}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        
        # Check if we got a 403 Forbidden error (CAPTCHA puzzle)
        if response.status_code == 403 or "Please solve this CAPTCHA" in response.text:
            print(f"\n⚠️  DuckDuckGo is showing a CAPTCHA puzzle. Trying once to solve it manually.")
            
            # Open the URL in the default browser for user to solve
            print(f"Opening {url} in your browser. Please solve the puzzle and press Enter when done.")
            webbrowser.open(url)
            
            # Wait for user to solve the CAPTCHA or skip
            user_input = input("Press Enter after solving the CAPTCHA puzzle or type 'skip' to skip: ")
            
            if user_input.lower() == 'skip':
                print("Skipping this search query.")
                return []
            
            # Try the request again
            print("Retrying search...")
            time.sleep(2)  # Short delay before retry
            response = requests.get(url, headers=headers)
            
            # If still getting CAPTCHA, skip
            if response.status_code == 403 or "Please solve this CAPTCHA" in response.text:
                print("Still getting CAPTCHA. Skipping this search query.")
                return []
        
        # Continue with the regular flow
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        results = []
        for result in soup.select('.result')[:5]:  # Get top 5 results
            title_elem = result.select_one('.result__title')
            link_elem = result.select_one('.result__url')
            if title_elem and link_elem:
                title = title_elem.get_text(strip=True)
                link = link_elem.get('href')
                if link:
                    results.append((title, link))
        
        return results
    except Exception as e:
        print(f"Error fetching search results: {e}")
        return []
    