#!/usr/bin/env python3
"""
Portfolio Monitor - Main Script
Generates and sends weekly portfolio company digests
"""

import os
import sys
import yaml
import logging
import argparse
from pathlib import Path

from src.news_fetcher import NewsFetcher
from src.funding_tracker import FundingTracker
from src.digest_generator import DigestGenerator
from src.email_sender import EmailSender

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_config(config_path: str = "config/companies.yaml") -> dict:
    """Load configuration from YAML file"""
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        logger.info(f"Loaded configuration from {config_path}")
        return config
    except FileNotFoundError:
        logger.error(f"Configuration file not found: {config_path}")
        logger.error("Please create config/companies.yaml with your portfolio companies")
        sys.exit(1)
    except yaml.YAMLError as e:
        logger.error(f"Error parsing YAML configuration: {e}")
        sys.exit(1)


def get_env_variable(var_name: str, required: bool = True) -> str:
    """Get environment variable with error handling"""
    value = os.environ.get(var_name)
    if required and not value:
        logger.error(f"Required environment variable {var_name} not set")
        logger.error("Please set up your environment variables (see README)")
        sys.exit(1)
    return value


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description='Portfolio Monitor - Weekly Digest Generator')
    parser.add_argument(
        '--test',
        action='store_true',
        help='Send a test email to verify configuration'
    )
    parser.add_argument(
        '--config',
        default='config/companies.yaml',
        help='Path to configuration file (default: config/companies.yaml)'
    )
    parser.add_argument(
        '--skip-funding',
        action='store_true',
        help='Skip funding information lookup (faster)'
    )
    parser.add_argument(
        '--days',
        type=int,
        default=7,
        help='Number of days to look back for news (default: 7)'
    )

    args = parser.parse_args()

    logger.info("=" * 80)
    logger.info("Portfolio Monitor - Starting")
    logger.info("=" * 80)

    # Load configuration
    config = load_config(args.config)
    companies = config.get('companies', [])

    if not companies:
        logger.error("No companies found in configuration file")
        sys.exit(1)

    logger.info(f"Monitoring {len(companies)} companies")

    # Get email configuration from environment variables
    smtp_email = get_env_variable('SMTP_EMAIL')
    smtp_password = get_env_variable('SMTP_PASSWORD')
    recipient_email = get_env_variable('RECIPIENT_EMAIL', required=False) or smtp_email

    # Initialize email sender
    email_sender = EmailSender(smtp_email, smtp_password)

    # Test mode - send test email and exit
    if args.test:
        logger.info("Running in TEST mode")
        success = email_sender.send_test_email(recipient_email)
        if success:
            logger.info("✓ Test email sent successfully!")
            logger.info("Check your inbox to confirm receipt")
        else:
            logger.error("✗ Test email failed")
            sys.exit(1)
        return

    # Regular mode - generate and send digest
    logger.info("Fetching news for portfolio companies...")

    # Fetch news
    news_fetcher = NewsFetcher(days_back=args.days)
    news_data = news_fetcher.fetch_all_companies_news(companies)

    # Fetch funding information (optional)
    funding_data = None
    if not args.skip_funding:
        logger.info("Fetching funding information...")
        funding_tracker = FundingTracker()
        funding_data = funding_tracker.get_all_funding_info(companies)
    else:
        logger.info("Skipping funding information (--skip-funding flag set)")

    # Generate digest
    logger.info("Generating digest...")
    digest_gen = DigestGenerator()
    digest_body = digest_gen.generate_digest(news_data, funding_data)
    subject = digest_gen.generate_subject_line(news_data)

    # Save digest to file (for debugging/logging)
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    from datetime import datetime
    output_file = output_dir / f"digest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

    with open(output_file, 'w') as f:
        f.write(digest_body)
    logger.info(f"Digest saved to: {output_file}")

    # Send email
    logger.info(f"Sending digest to: {recipient_email}")
    success = email_sender.send_digest(
        recipient_email=recipient_email,
        subject=subject,
        body=digest_body
    )

    if success:
        logger.info("=" * 80)
        logger.info("✓ Portfolio digest sent successfully!")
        logger.info("=" * 80)
    else:
        logger.error("=" * 80)
        logger.error("✗ Failed to send portfolio digest")
        logger.error("=" * 80)
        sys.exit(1)


if __name__ == "__main__":
    main()
