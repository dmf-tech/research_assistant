import requests
from bs4 import BeautifulSoup
from newspaper import Article
from duckduckgo_search import DDGS
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from waybackpy import Url
import whois
import tldextract
import feedparser
import time
from urllib.parse import quote_plus

class ResearchScraper:
    def __init__(self):
        self.session = requests.Session()
        self.setup_selenium()
        self.max_retries = 3
        self.retry_delay = 2  # seconds

    def setup_selenium(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(options=chrome_options)

    def search_web(self, query, max_results=10):
        for attempt in range(self.max_retries):
            try:
                return self._search_with_ddg(query, max_results)
            except Exception as e:
                if attempt == self.max_retries - 1:
                    return self._fallback_search(query, max_results)
                time.sleep(self.retry_delay)

    def _search_with_ddg(self, query, max_results):
        results = []
        with DDGS() as ddgs:
            ddgs_results = ddgs.text(query, max_results=max_results)
            for r in ddgs_results:
                results.append({
                    'title': r['title'],
                    'link': r['link'],
                    'snippet': r['body']
                })
        return results

    def _fallback_search(self, query, max_results):
        # Fallback to direct HTML scraping of search results
        try:
            encoded_query = quote_plus(query)
            url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
            response = self.session.get(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })
            soup = BeautifulSoup(response.text, 'lxml')
            results = []
            
            for result in soup.select('.result')[:max_results]:
                title_elem = result.select_one('.result__title')
                snippet_elem = result.select_one('.result__snippet')
                link_elem = result.select_one('.result__url')
                
                if title_elem and link_elem:
                    results.append({
                        'title': title_elem.get_text(strip=True),
                        'link': link_elem.get('href', ''),
                        'snippet': snippet_elem.get_text(strip=True) if snippet_elem else ''
                    })
            
            return results
        except Exception as e:
            return [{'error': f'Search failed: {str(e)}'}]

    def fetch_article(self, url):
        article = Article(url)
        try:
            article.download()
            article.parse()
            return {
                'title': article.title,
                'text': article.text,
                'authors': article.authors,
                'publish_date': article.publish_date,
                'top_image': article.top_image,
                'url': url
            }
        except Exception as e:
            return {'error': str(e)}

    def get_domain_info(self, url):
        extracted = tldextract.extract(url)
        domain = f"{extracted.domain}.{extracted.suffix}"
        try:
            domain_info = whois.whois(domain)
            return domain_info
        except Exception:
            return None

    def get_historical_versions(self, url):
        try:
            wayback = Url(url, 'Research Assistant')
            snapshots = wayback.snapshots()
            return [{
                'timestamp': snapshot.timestamp,
                'url': snapshot.archive_url
            } for snapshot in snapshots]
        except Exception as e:
            return {'error': str(e)}

    def __del__(self):
        if hasattr(self, 'driver'):
            self.driver.quit() 