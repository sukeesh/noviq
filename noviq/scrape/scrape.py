from abc import ABC, abstractmethod
import requests
from bs4 import BeautifulSoup
import webbrowser
import time
import os
import json


class Scrape(ABC):
    def __init__(self, url: str):
        self.url = url

    @abstractmethod
    def scrape(self):
        """Abstract method that must be implemented by child classes"""
        pass


class HTTPScrape(Scrape):
    def scrape(self) -> str:
        """Returns raw HTML content as string"""
        response = requests.get(self.url)
        return response.text


class BeautifulSoupScrape(Scrape):
    def scrape(self) -> str:
        """Returns cleaned HTML content as string"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        try:
            response = requests.get(self.url, headers=headers, timeout=10)
            
            # For non-DuckDuckGo websites, if we get a 403 or CAPTCHA, just skip
            if response.status_code == 403 or "Please solve this CAPTCHA" in response.text or "captcha" in response.text.lower():
                print(f"\n⚠️  Website at {self.url} has access restrictions. Skipping this webpage.")
                return "Skipped due to website access restrictions"
                
            soup = BeautifulSoup(response.text, 'html.parser')
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            # Get text and clean it up
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            return text
        except Exception as e:
            print(f"Error scraping webpage {self.url}: {e}")
            return f"Skipped due to error: {e}"


class GoogleSearchScrape:
    def __init__(self, api_key=None, cx=None):
        """
        Initialize Google Custom Search API client
        
        Args:
            api_key (str): Google API key
            cx (str): Google Custom Search Engine ID
        """
        self.api_key = api_key or os.environ.get('GOOGLE_API_KEY')
        self.cx = cx or os.environ.get('GOOGLE_CSE_ID')
        
        if not self.api_key:
            raise ValueError("Google API key is required. Set GOOGLE_API_KEY environment variable or pass api_key.")
        if not self.cx:
            raise ValueError("Google Custom Search Engine ID is required. Set GOOGLE_CSE_ID environment variable or pass cx.")
    
    def search(self, query, num_results=10):
        """
        Perform a Google search and return results
        
        Args:
            query (str): Search query
            num_results (int): Number of results to return (max 10 per request)
            
        Returns:
            list: List of tuples containing (title, url)
        """
        base_url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'key': self.api_key,
            'cx': self.cx,
            'q': query,
            'num': min(num_results, 10)  # API limits to 10 per request
        }
        
        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            
            search_results = []
            data = response.json()
            
            if 'items' in data:
                for item in data['items']:
                    title = item.get('title', '')
                    url = item.get('link', '')
                    search_results.append((title, url))
            
            return search_results
        except Exception as e:
            print(f"Error performing Google search: {e}")
            return []


def get_search_engine():
    """
    Returns the appropriate search engine based on environment variables
    
    Returns:
        str: 'google' or 'duckduckgo'
    """
    return os.environ.get('SEARCH_ENGINE', 'duckduckgo').lower()
