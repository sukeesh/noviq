import requests
from bs4 import BeautifulSoup
from urllib.parse import quote



def get_search_queries(search_query) -> list[tuple[str, str]]:
    # DuckDuckGo HTML search
    url = f"https://html.duckduckgo.com/html/?q={quote(search_query)}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
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
    