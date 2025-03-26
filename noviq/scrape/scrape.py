from abc import ABC, abstractmethod
import requests
from bs4 import BeautifulSoup


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
        response = requests.get(self.url)
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
