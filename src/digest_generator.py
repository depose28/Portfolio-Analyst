"""
Digest Generator Module - Formats portfolio data into a readable email digest
"""

from datetime import datetime
from typing import Dict, List, Optional


class DigestGenerator:
    """Generates formatted email digests from portfolio company data"""

    def __init__(self):
        self.digest_date = datetime.now().strftime('%B %d, %Y')

    def generate_digest(
        self,
        news_data: Dict[str, List[Dict]],
        funding_data: Dict[str, Dict] = None,
        ai_summaries: Dict[str, Optional[str]] = None
    ) -> str:
        """
        Generate a complete email digest

        Args:
            news_data: Dictionary mapping company names to news articles
            funding_data: Optional dictionary mapping company names to funding info
            ai_summaries: Optional dictionary mapping company names to AI-generated summaries

        Returns:
            Formatted digest as a string
        """
        lines = []

        # Header
        lines.append("=" * 80)
        lines.append("PORTFOLIO WEEKLY DIGEST")
        lines.append(f"Week of {self.digest_date}")
        lines.append("=" * 80)
        lines.append("")

        # Executive Summary
        lines.append(self._generate_summary(news_data))
        lines.append("")

        # Detailed company reports
        lines.append("=" * 80)
        lines.append("DETAILED COMPANY REPORTS")
        lines.append("=" * 80)
        lines.append("")

        # Sort companies: those with news first, then alphabetically
        companies_with_news = [(name, articles) for name, articles in news_data.items() if articles]
        companies_without_news = [(name, articles) for name, articles in news_data.items() if not articles]

        companies_with_news.sort(key=lambda x: x[0])
        companies_without_news.sort(key=lambda x: x[0])

        # Companies with news
        for company_name, articles in companies_with_news:
            ai_summary = ai_summaries.get(company_name) if ai_summaries else None
            lines.append(self._format_company_section(
                company_name,
                articles,
                funding_data.get(company_name) if funding_data else None,
                ai_summary
            ))
            lines.append("")

        # Companies without news (brief mention)
        if companies_without_news:
            lines.append("-" * 80)
            lines.append("NO NEWS THIS WEEK")
            lines.append("-" * 80)
            lines.append("")

            for company_name, _ in companies_without_news:
                lines.append(f"  • {company_name}")

            lines.append("")

        # Footer
        lines.append("=" * 80)
        lines.append(f"End of digest - Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("=" * 80)

        return "\n".join(lines)

    def _generate_summary(self, news_data: Dict[str, List[Dict]]) -> str:
        """Generate executive summary section"""
        lines = []
        lines.append("-" * 80)
        lines.append("EXECUTIVE SUMMARY")
        lines.append("-" * 80)
        lines.append("")

        total_companies = len(news_data)
        companies_with_news = sum(1 for articles in news_data.values() if articles)
        total_articles = sum(len(articles) for articles in news_data.values())

        lines.append(f"  Portfolio Companies: {total_companies}")
        lines.append(f"  Companies with News: {companies_with_news}")
        lines.append(f"  Total Articles: {total_articles}")
        lines.append("")

        if companies_with_news > 0:
            lines.append("  Companies in the news this week:")
            for company_name, articles in news_data.items():
                if articles:
                    lines.append(f"    • {company_name} ({len(articles)} articles)")
        else:
            lines.append("  No companies had news this week.")

        return "\n".join(lines)

    def _format_company_section(
        self,
        company_name: str,
        articles: List[Dict],
        funding_info: Dict = None,
        ai_summary: Optional[str] = None
    ) -> str:
        """Format a single company's section"""
        lines = []

        lines.append("-" * 80)
        lines.append(f"{company_name.upper()}")
        lines.append("-" * 80)
        lines.append("")

        # Funding information (if available)
        if funding_info:
            from src.funding_tracker import FundingTracker
            funding_summary = FundingTracker.format_funding_summary(funding_info)
            if funding_summary != "No recent public funding data available":
                lines.append(f"Funding: {funding_summary}")
                lines.append("")

        # AI-generated summary (if available)
        if ai_summary:
            lines.append("SUMMARY:")
            lines.append("")
            lines.append(f"  {ai_summary}")
            lines.append("")

        # News article links
        if articles:
            lines.append(f"LINKS ({len(articles)} articles):")
            lines.append("")

            for i, article in enumerate(articles, 1):
                lines.append(f"  [{i}] {article['title']}")
                lines.append(f"      {article['link']}")
                lines.append(f"      {article.get('source', 'Unknown')} | {article['published']}")
                lines.append("")
        else:
            lines.append("No news this week.")
            lines.append("")

        return "\n".join(lines)

    def generate_subject_line(self, news_data: Dict[str, List[Dict]]) -> str:
        """Generate email subject line"""
        companies_with_news = sum(1 for articles in news_data.values() if articles)
        total_articles = sum(len(articles) for articles in news_data.values())

        week_of = datetime.now().strftime('%m/%d/%Y')

        if total_articles == 0:
            return f"Portfolio Digest - Week of {week_of} - Quiet Week"
        elif companies_with_news == 1:
            return f"Portfolio Digest - Week of {week_of} - 1 Company Update"
        else:
            return f"Portfolio Digest - Week of {week_of} - {companies_with_news} Companies with News"
