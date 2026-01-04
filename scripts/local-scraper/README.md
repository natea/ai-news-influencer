# Local Twitter/X Scraper

Run this on your **local machine** (not in DevPod) for reliable browser-based Twitter scraping.

## Why Local?

- **Visible browser** = better bot detection evasion
- **No Docker complexity** = browsers work properly
- **Manual CAPTCHA solving** = if needed, you can intervene
- **Debugging** = see exactly what's happening

## Quick Setup

```bash
# 1. Clone or copy this folder to your local machine

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install Firefox browser for Playwright
playwright install firefox
```

## Usage

```bash
# Single account (browser visible - recommended)
python twitter_scraper_local.py @elikiiii

# Multiple accounts
python twitter_scraper_local.py @elikiiii @OpenAI @AnthropicAI

# Save to JSON
python twitter_scraper_local.py @elikiiii --output tweets.json

# More tweets per account
python twitter_scraper_local.py @elikiiii --max-tweets 50

# Headless mode (less reliable, but no GUI needed)
python twitter_scraper_local.py @elikiiii --headless
```

## Tips for Best Results

1. **Use headed mode** (default) - Twitter detects headless browsers
2. **Don't interact with the browser** while it's scraping
3. **If CAPTCHA appears** - solve it manually, the script will continue
4. **Space out scraping sessions** - don't run too frequently
5. **Use residential IP** - VPN/datacenter IPs get flagged faster

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Timeout loading account" | Account may not exist or rate limited. Wait 30 min. |
| Login wall appears | Twitter is blocking. Try again later or use residential proxy. |
| No tweets collected | Scroll detection failed. Try headed mode. |
| CAPTCHA loop | Solve manually or wait 1+ hour before retrying. |

## Integration with DevPod Backend

Once you validate scraping works locally, the production backend should use **Apify**
for reliable scraping without browser complexity. This local script is for:

- Testing and development
- Validating which accounts can be scraped
- Understanding Twitter's current detection patterns
