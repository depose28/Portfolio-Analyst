"""
News Fetcher Module - Fetches recent news for portfolio companies using Google News RSS
"""

import logging
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import List, Dict
from dateutil import parser as date_parser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NewsFetcher:
    """Fetches news articles for companies using Google News RSS feeds"""

    def __init__(self, days_back: int = 7):
        """
        Initialize the news fetcher

        Args:
            days_back: Number of days to look back for news (default: 7)
        """
        self.days_back = days_back
        self.base_url = "https://news.google.com/rss/search"

    def fetch_company_news(self, company_name: str) -> List[Dict]:
        """
        Fetch recent news for a specific company

        Args:
            company_name: Name of the company to search for

        Returns:
            List of news articles with title, link, published date, and summary
        """
        try:
            # Construct Google News RSS URL
            query = f'"{company_name}"'
            url = f"{self.base_url}?q={query}&hl=en-US&gl=US&ceid=US:en"

            logger.info(f"Fetching news for: {company_name}")

            # Fetch RSS feed
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            # Parse XML
            root = ET.fromstring(response.content)

            # Find all items in the RSS feed
            items = root.findall('.//item')

            if not items:
                logger.info(f"No news found for {company_name}")
                return []

            # Filter and format articles from the last N days
            cutoff_date = datetime.now() - timedelta(days=self.days_back)
            articles = []

            for item in items[:10]:  # Limit to top 10 results
                try:
                    title_elem = item.find('title')
                    link_elem = item.find('link')
                    pub_date_elem = item.find('pubDate')

                    if title_elem is None or link_elem is None:
                        continue

                    title = title_elem.text
                    link = link_elem.text

                    # Parse publication date
                    if pub_date_elem is not None and pub_date_elem.text:
                        pub_date = date_parser.parse(pub_date_elem.text)

                        # Only include articles from the past N days
                        if pub_date.replace(tzinfo=None) < cutoff_date:
                            continue

                        published_str = pub_date.strftime('%Y-%m-%d %H:%M')
                    else:
                        published_str = 'Unknown date'

                    # Try to get source from description
                    source = 'Unknown'
                    desc_elem = item.find('description')
                    if desc_elem is not None and desc_elem.text:
                        # Google News RSS often includes source in description
                        desc_text = desc_elem.text
                        summary = self._clean_summary(desc_text)
                    else:
                        summary = ''

                    article = {
                        'title': title,
                        'link': link,
                        'published': published_str,
                        'source': source,
                        'summary': summary
                    }
                    articles.append(article)

                except Exception as e:
                    logger.warning(f"Error parsing article for {company_name}: {e}")
                    continue

            logger.info(f"Found {len(articles)} recent articles for {company_name}")
            return articles

        except Exception as e:
            logger.error(f"Error fetching news for {company_name}: {e}")
            return []

    def fetch_all_companies_news(self, companies: List) -> Dict[str, List[Dict]]:
        """
        Fetch news for multiple companies

        Args:
            companies: List of company names (strings) or dicts with 'name' and 'search' keys

        Returns:
            Dictionary mapping company names to their news articles
        """
        results = {}

        for company in companies:
            # Handle both string and dict formats
            if isinstance(company, dict):
                display_name = company.get('name', '')
                search_query = company.get('search', display_name)
            else:
                display_name = company
                search_query = company

            if not display_name:
                continue

            logger.info(f"Searching for: {display_name} (query: {search_query})")
            articles = self.fetch_company_news(search_query)
            results[display_name] = articles

        return results

    @staticmethod
    def _clean_summary(summary: str) -> str:
        """Clean HTML tags from summary text"""
        from bs4 import BeautifulSoup

        try:
            # Remove HTML tags
            clean_text = BeautifulSoup(summary, 'html.parser').get_text()
            # Limit length
            if len(clean_text) > 200:
                clean_text = clean_text[:200] + '...'
            return clean_text.strip()
        except:
            return summary[:200] if len(summary) > 200 else summary
