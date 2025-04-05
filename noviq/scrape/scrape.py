from abc import ABC, abstractmethod
import requests
from bs4 import BeautifulSoup
import webbrowser
import time


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
