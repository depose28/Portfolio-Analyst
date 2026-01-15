# Portfolio Monitor

Automated weekly email digests for your VC portfolio companies. Stay informed about what's happening with your investments without manually checking news sources every day.

## Features

- **Automated News Monitoring**: Fetches recent news articles for all your portfolio companies using Google News RSS (100% free, no API keys required)
- **Weekly Email Digest**: Clean, easy-to-scan plain text reports delivered every Monday morning
- **Funding Information**: Optional lookup of public funding/valuation data where available
- **GitHub Actions Automation**: Runs automatically on a schedule, completely free
- **Manual Testing**: Easy test mode to verify your setup
- **Privacy-First**: Your company list stays in your private config file

## What You'll Receive

Each Monday morning, you'll get an email with:

1. **Executive Summary**: Quick overview of portfolio activity
2. **Company Details**: For each company with news:
   - Recent headlines from the past 7 days
   - Article summaries and links
   - Publication dates and sources
   - Optional funding information
3. **Quiet Companies**: List of companies with no news this week

## Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd Portfolio-Analyst

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Your Portfolio

```bash
# Copy the example configuration
cp config/companies.example.yaml config/companies.yaml

# Edit with your companies
nano config/companies.yaml  # or use your preferred editor
```

Add your portfolio companies to the `companies` list:

```yaml
companies:
  - "Your Company 1"
  - "Your Company 2"
  - "Your Company 3"
  # Add all your portfolio companies...
```

### 3. Set Up Gmail App Password

To send emails, you need a Gmail App Password (not your regular password):

1. Go to your Google Account settings: https://myaccount.google.com/
2. Navigate to **Security** → **2-Step Verification** (enable if not already)
3. Scroll down to **App passwords**
4. Create a new app password:
   - Select app: **Mail**
   - Select device: **Other** (name it "Portfolio Monitor")
5. Copy the 16-character password (you'll use this below)

**Important**: Never use your regular Gmail password. Always use an App Password.

### 4. Configure Environment Variables

Create a `.env` file for local testing (or set GitHub Secrets for automation):

```bash
# For local testing, create .env file:
SMTP_EMAIL=your-email@gmail.com
SMTP_PASSWORD=your-16-char-app-password
RECIPIENT_EMAIL=your-email@gmail.com  # Optional, defaults to SMTP_EMAIL
```

**For GitHub Actions**, add these as repository secrets:

1. Go to your repository on GitHub
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret** and add:
   - `SMTP_EMAIL`: Your Gmail address
   - `SMTP_PASSWORD`: Your Gmail App Password
   - `RECIPIENT_EMAIL`: Email to receive digests (optional)

### 5. Test Your Setup

```bash
# Run a test to verify email configuration
python main.py --test

# Run a full digest (without sending email, saves to output/ folder)
python main.py --skip-funding  # Faster, skips funding lookup

# Run a full digest and send email
python main.py
```

## Usage

### Local Execution

```bash
# Full digest with all features
python main.py

# Skip funding information (faster)
python main.py --skip-funding

# Look back 14 days instead of 7
python main.py --days 14

# Send test email
python main.py --test

# Use custom config file
python main.py --config path/to/companies.yaml
```

### Automated Weekly Delivery

The repository includes a GitHub Actions workflow (`.github/workflows/weekly-digest.yml`) that:

- Runs every **Monday at 8:00 AM UTC** (adjust timezone in workflow file)
- Can be **manually triggered** from the GitHub Actions tab
- Automatically sends your digest email
- Saves a copy of each digest as an artifact

**To enable automated delivery:**

1. Add your companies to `config/companies.yaml`
2. Commit and push the file to your repository
3. Set up GitHub Secrets (see step 4 above)
4. The workflow will run automatically every Monday

**To manually trigger:**

1. Go to your repository on GitHub
2. Click **Actions** tab
3. Select **Weekly Portfolio Digest** workflow
4. Click **Run workflow** → **Run workflow**

## Project Structure

```
Portfolio-Analyst/
├── .github/
│   └── workflows/
│       └── weekly-digest.yml    # GitHub Actions automation
├── config/
│   ├── companies.example.yaml   # Example configuration
│   └── companies.yaml           # Your companies (create this)
├── src/
│   ├── __init__.py
│   ├── news_fetcher.py          # Google News RSS fetching
│   ├── funding_tracker.py       # Funding information lookup
│   ├── digest_generator.py      # Email digest formatting
│   └── email_sender.py          # Gmail SMTP sending
├── output/                      # Generated digests (auto-created)
├── main.py                      # Main orchestration script
├── requirements.txt             # Python dependencies
├── .gitignore
└── README.md
```

## Configuration Options

Edit `config/companies.yaml` to customize:

```yaml
companies:
  - "Company 1"
  - "Company 2"

settings:
  # Number of days to look back for news
  days_back: 7

  # Include funding information
  include_funding: true
```

## Customization

### Change Email Schedule

Edit `.github/workflows/weekly-digest.yml`:

```yaml
schedule:
  # Run every Monday at 8:00 AM UTC
  - cron: '0 8 * * 1'

  # Examples:
  # Every Sunday at 9:00 AM UTC: '0 9 * * 0'
  # Every Friday at 5:00 PM UTC: '0 17 * * 5'
  # Twice a week (Mon & Thu): '0 8 * * 1,4'
```

Use [crontab.guru](https://crontab.guru/) to create custom schedules.

### Adjust News Lookback Period

```bash
# Look back 14 days
python main.py --days 14

# Or edit config/companies.yaml:
settings:
  days_back: 14
```

## Troubleshooting

### Email Not Sending

**Problem**: `SMTP Authentication failed`

**Solution**:
- Ensure you're using a Gmail **App Password**, not your regular password
- Verify 2-Step Verification is enabled on your Google account
- Check that environment variables are set correctly
- Try running `python main.py --test` to isolate the issue

### No News Found

**Problem**: Companies show "No news this week"

**Solutions**:
- Verify company names match how they appear in news articles
- Try adding the company's full legal name or common variations
- Increase lookback period: `python main.py --days 14`
- Check if the company has been in the news recently (Google search)

### GitHub Actions Failing

**Problem**: Workflow runs but fails

**Solutions**:
- Check that GitHub Secrets are set correctly (Settings → Secrets)
- Verify `config/companies.yaml` is committed and pushed
- Look at workflow logs in the Actions tab for specific errors
- Test locally first: `python main.py --test`

### Rate Limiting

**Problem**: Getting blocked by news sources

**Solution**:
- The tool is designed to be respectful with rate limiting
- Google News RSS is free and has no strict rate limits
- If issues persist, reduce portfolio size or increase --days parameter

## Privacy & Security

- **Company List**: Your `config/companies.yaml` file is private to your repository
- **Email Credentials**: Stored as GitHub Secrets (encrypted) or local `.env` (not committed)
- **No External Services**: All data fetching uses free, public sources
- **No Data Storage**: News data is only stored temporarily in memory
- **Digest Archives**: Saved locally in `output/` folder (optional)

## Cost

**100% Free** - This project uses:
- Google News RSS (free, no API key)
- GitHub Actions free tier (2,000 minutes/month for private repos)
- Gmail SMTP (free)
- All open-source Python libraries

## Technical Details

- **Python**: 3.11+ (but works with 3.9+)
- **News Source**: Google News RSS feeds (no rate limits)
- **Email**: Gmail SMTP with TLS encryption
- **Scheduling**: GitHub Actions cron
- **Dependencies**: feedparser, requests, beautifulsoup4, pyyaml

## Contributing

Feel free to fork and customize for your needs. This is a personal tool designed to be simple and maintainable.

## License

MIT License - Use freely for personal or commercial purposes.

## Support

For issues or questions:
1. Check the Troubleshooting section above
2. Review GitHub Actions logs for specific errors
3. Test locally with `python main.py --test`
4. Open an issue on GitHub

---

**Built for investors who want to stay informed without the manual work.**

Enjoy your Monday morning coffee with a fresh portfolio digest!
