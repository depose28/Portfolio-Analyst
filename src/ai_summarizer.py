"""
AI Summarizer Module - Uses Claude API to generate intelligent summaries
"""

import logging
from typing import List, Dict, Optional
import anthropic

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AISummarizer:
    """Uses Claude API to generate intelligent summaries of company news"""

    def __init__(self, api_key: str):
        """
        Initialize the AI summarizer

        Args:
            api_key: Anthropic API key
        """
        self.client = anthropic.Anthropic(api_key=api_key)

    def summarize_company_news(
        self,
        company_name: str,
        articles: List[Dict]
    ) -> Optional[str]:
        """
        Generate an intelligent summary of news articles for a company

        Args:
            company_name: Name of the company
            articles: List of news articles

        Returns:
            A synthesized paragraph summarizing the news, or None if no articles
        """
        if not articles:
            return None

        try:
            # Prepare article data for the prompt
            article_text = []
            for i, article in enumerate(articles[:3], 1):  # Limit to top 3 articles
                article_text.append(
                    f"{i}. {article['title']}\n"
                    f"   Date: {article['published']}\n"
                    f"   Summary: {article.get('summary', 'No summary available')}\n"
                )

            articles_str = "\n".join(article_text)

            # Create prompt for Claude
            prompt = f"""Analyze these news headlines about {company_name} and create a brief 2-3 sentence summary for an investor.

IMPORTANT INSTRUCTIONS:
- Work with whatever information is available, even if limited to just headlines
- Be concise and direct - NO apologies or meta-commentary about limited information
- Focus on what IS mentioned, not what's missing
- If only headlines are available, synthesize what you can infer
- Use confident, factual language

Headlines/Articles:
{articles_str}

Write a concise 2-3 sentence investor summary:"""

            # Call Claude API
            message = self.client.messages.create(
                model="claude-3-5-haiku-20241022",  # Using Haiku for cost-efficiency
                max_tokens=300,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            summary = message.content[0].text.strip()
            logger.info(f"Generated AI summary for {company_name}")
            return summary

        except Exception as e:
            logger.error(f"Error generating AI summary for {company_name}: {e}")
            # Fallback to simple concatenation
            return self._fallback_summary(company_name, articles)

    def _fallback_summary(self, company_name: str, articles: List[Dict]) -> str:
        """
        Fallback summary method if AI fails

        Args:
            company_name: Name of the company
            articles: List of articles

        Returns:
            Simple concatenated summary
        """
        if not articles:
            return f"{company_name} had no news this week."

        headlines = [article['title'] for article in articles[:3]]

        if len(articles) == 1:
            return f"{company_name} made headlines with: {headlines[0]}"
        elif len(articles) == 2:
            return f"{company_name} had {len(articles)} news items: {headlines[0]} and {headlines[1]}"
        else:
            summary = f"{company_name} had {len(articles)} news items this week, including: "
            summary += ", ".join(headlines[:3])
            if len(articles) > 3:
                summary += f", and {len(articles) - 3} more."
            return summary

    def summarize_all_companies(
        self,
        news_data: Dict[str, List[Dict]]
    ) -> Dict[str, Optional[str]]:
        """
        Generate summaries for all companies

        Args:
            news_data: Dictionary mapping company names to article lists

        Returns:
            Dictionary mapping company names to their AI-generated summaries
        """
        summaries = {}

        for company_name, articles in news_data.items():
            if articles:  # Only generate summary if there are articles
                logger.info(f"Generating summary for {company_name}...")
                summary = self.summarize_company_news(company_name, articles)
                summaries[company_name] = summary
            else:
                summaries[company_name] = None

        return summaries
