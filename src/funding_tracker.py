"""
Funding Tracker Module - Attempts to find public funding information for companies
"""

import logging
import requests
from typing import Dict, Optional
from bs4 import BeautifulSoup
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FundingTracker:
    """
    Attempts to find publicly available funding information for companies.
    Note: For private companies, this information is often limited or unavailable.
    """

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def get_funding_info(self, company_name: str) -> Dict[str, Optional[str]]:
        """
        Attempt to find funding information for a company

        Args:
            company_name: Name of the company

        Returns:
            Dictionary with funding info (may be empty if not found)
        """
        funding_info = {
            'company': company_name,
            'status': 'No public funding data available',
            'last_funding_round': None,
            'total_raised': None,
            'valuation': None,
            'source': None
        }

        try:
            # Try to get basic info from search results
            # This is a best-effort approach since most private companies don't publish this data
            search_url = f"https://www.google.com/search?q={company_name}+funding+round+valuation"

            response = requests.get(search_url, headers=self.headers, timeout=10)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # Look for funding-related snippets in search results
                # Note: This is intentionally simple and best-effort
                text = soup.get_text()

                # Check if there are mentions of funding
                funding_keywords = ['raised', 'funding', 'valuation', 'Series', 'million', 'billion']
                if any(keyword in text for keyword in funding_keywords):
                    funding_info['status'] = 'Some funding information may be available in search results'

            # Add a small delay to be respectful
            time.sleep(1)

        except Exception as e:
            logger.warning(f"Could not fetch funding info for {company_name}: {e}")

        return funding_info

    def get_all_funding_info(self, companies: list) -> Dict[str, Dict]:
        """
        Get funding information for multiple companies

        Args:
            companies: List of company names (strings) or dicts with 'name' and 'search' keys

        Returns:
            Dictionary mapping company names to their funding info
        """
        results = {}

        for company in companies:
            # Handle both string and dict formats
            if isinstance(company, dict):
                display_name = company.get('name', '')
                search_query = display_name  # Use display name for funding search
            else:
                display_name = company
                search_query = company

            if not display_name:
                continue

            logger.info(f"Checking funding info for: {display_name}")
            results[display_name] = self.get_funding_info(search_query)
            # Be respectful with rate limiting
            time.sleep(2)

        return results

    @staticmethod
    def format_funding_summary(funding_info: Dict) -> str:
        """
        Format funding information into a readable summary

        Args:
            funding_info: Dictionary with funding information

        Returns:
            Formatted string summary
        """
        if funding_info['status'] == 'No public funding data available':
            return "No recent public funding data available"

        parts = []

        if funding_info['last_funding_round']:
            parts.append(f"Last Round: {funding_info['last_funding_round']}")

        if funding_info['total_raised']:
            parts.append(f"Total Raised: {funding_info['total_raised']}")

        if funding_info['valuation']:
            parts.append(f"Valuation: {funding_info['valuation']}")

        if parts:
            return " | ".join(parts)
        else:
            return funding_info['status']
