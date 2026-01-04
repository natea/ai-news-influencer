#!/usr/bin/env python3
"""
Local Twitter/X Scraper with Playwright Stealth
Run this on your LOCAL machine (not in DevPod) for best results.

Usage:
    python twitter_scraper_local.py @elikiiii
    python twitter_scraper_local.py @elikiiii @OpenAI --headless
    python twitter_scraper_local.py @elikiiii --output tweets.json
"""

import argparse
import json
import random
import time
from datetime import datetime
from pathlib import Path

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from playwright_stealth import stealth_sync
from fake_useragent import UserAgent
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

# Stealth configuration
VIEWPORT_OPTIONS = [
    {"width": 1920, "height": 1080},
    {"width": 1366, "height": 768},
    {"width": 1536, "height": 864},
    {"width": 1440, "height": 900},
]

LANGUAGES = ["en-US", "en-GB", "en"]


def random_delay(min_sec: float = 1.0, max_sec: float = 3.0):
    """Human-like random delay"""
    time.sleep(random.uniform(min_sec, max_sec))


def create_stealth_context(playwright, headless: bool = False):
    """Create a browser context with stealth settings"""
    ua = UserAgent()
    viewport = random.choice(VIEWPORT_OPTIONS)

    # Firefox is recommended for Twitter - less detection
    browser = playwright.firefox.launch(
        headless=headless,
        slow_mo=50,  # Slight slowdown for more human-like behavior
    )

    context = browser.new_context(
        viewport=viewport,
        user_agent=ua.firefox,
        locale=random.choice(LANGUAGES),
        timezone_id="America/New_York",
        color_scheme="light",
    )

    return browser, context


def scrape_twitter_account(page, username: str, max_tweets: int = 20) -> list[dict]:
    """Scrape tweets from a Twitter/X account"""
    tweets = []
    url = f"https://x.com/{username.lstrip('@')}"

    console.print(f"[cyan]Navigating to {url}...[/cyan]")

    try:
        page.goto(url, wait_until="networkidle", timeout=30000)
        random_delay(2, 4)

        # Check for login wall or error
        if "login" in page.url.lower():
            console.print("[yellow]Warning: Hit login wall. Trying to continue...[/yellow]")

        # Wait for tweets to load
        page.wait_for_selector('article[data-testid="tweet"]', timeout=15000)

        # Scroll and collect tweets
        collected = 0
        scroll_attempts = 0
        max_scrolls = 10

        while collected < max_tweets and scroll_attempts < max_scrolls:
            # Find all tweet articles
            tweet_elements = page.query_selector_all('article[data-testid="tweet"]')

            for tweet_el in tweet_elements:
                if collected >= max_tweets:
                    break

                try:
                    # Extract tweet text
                    text_el = tweet_el.query_selector('[data-testid="tweetText"]')
                    text = text_el.inner_text() if text_el else ""

                    # Extract timestamp
                    time_el = tweet_el.query_selector("time")
                    timestamp = time_el.get_attribute("datetime") if time_el else None

                    # Extract metrics (likes, retweets, etc.)
                    metrics = {}
                    for metric in ["reply", "retweet", "like"]:
                        metric_el = tweet_el.query_selector(f'[data-testid="{metric}"]')
                        if metric_el:
                            metric_text = metric_el.inner_text()
                            metrics[metric] = metric_text if metric_text else "0"

                    # Extract tweet URL
                    link_el = tweet_el.query_selector('a[href*="/status/"]')
                    tweet_url = f"https://x.com{link_el.get_attribute('href')}" if link_el else None

                    tweet_data = {
                        "username": username,
                        "text": text,
                        "timestamp": timestamp,
                        "url": tweet_url,
                        "metrics": metrics,
                        "scraped_at": datetime.utcnow().isoformat(),
                    }

                    # Avoid duplicates
                    if tweet_url and not any(t.get("url") == tweet_url for t in tweets):
                        tweets.append(tweet_data)
                        collected += 1

                except Exception as e:
                    console.print(f"[dim]Error parsing tweet: {e}[/dim]")
                    continue

            # Scroll down for more tweets
            page.evaluate("window.scrollBy(0, 800)")
            random_delay(1.5, 3)
            scroll_attempts += 1

        console.print(f"[green]Collected {len(tweets)} tweets from {username}[/green]")

    except PlaywrightTimeout:
        console.print(f"[red]Timeout loading {username} - may be rate limited or account doesn't exist[/red]")
    except Exception as e:
        console.print(f"[red]Error scraping {username}: {e}[/red]")

    return tweets


def display_results(all_tweets: list[dict]):
    """Display scraped tweets in a nice table"""
    if not all_tweets:
        console.print("[yellow]No tweets collected[/yellow]")
        return

    table = Table(title="Scraped Tweets", show_lines=True)
    table.add_column("Account", style="cyan", width=15)
    table.add_column("Tweet", style="white", width=60)
    table.add_column("Time", style="dim", width=20)
    table.add_column("Likes", style="red", width=8)

    for tweet in all_tweets[:20]:  # Show first 20
        text = tweet.get("text", "")[:100] + "..." if len(tweet.get("text", "")) > 100 else tweet.get("text", "")
        likes = tweet.get("metrics", {}).get("like", "0")
        timestamp = tweet.get("timestamp", "")[:10] if tweet.get("timestamp") else "N/A"

        table.add_row(
            tweet.get("username", ""),
            text,
            timestamp,
            str(likes)
        )

    console.print(table)


def main():
    parser = argparse.ArgumentParser(description="Local Twitter/X Scraper with Stealth")
    parser.add_argument("accounts", nargs="+", help="Twitter accounts to scrape (e.g., @elikiiii)")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode (less reliable)")
    parser.add_argument("--max-tweets", type=int, default=20, help="Max tweets per account")
    parser.add_argument("--output", "-o", type=str, help="Output JSON file path")

    args = parser.parse_args()

    console.print("[bold blue]Twitter/X Local Scraper with Playwright Stealth[/bold blue]")
    console.print(f"[dim]Mode: {'Headless' if args.headless else 'Headed (visible browser)'}[/dim]")
    console.print(f"[dim]Accounts: {', '.join(args.accounts)}[/dim]")
    console.print()

    if not args.headless:
        console.print("[yellow]A browser window will open. Don't interact with it.[/yellow]")
        console.print("[yellow]If you see a CAPTCHA, solve it manually.[/yellow]")
        console.print()

    all_tweets = []

    with sync_playwright() as p:
        browser, context = create_stealth_context(p, headless=args.headless)
        page = context.new_page()

        # Apply stealth
        stealth_sync(page)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            for account in args.accounts:
                task = progress.add_task(f"Scraping {account}...", total=None)

                tweets = scrape_twitter_account(page, account, args.max_tweets)
                all_tweets.extend(tweets)

                progress.remove_task(task)

                # Delay between accounts
                if account != args.accounts[-1]:
                    console.print("[dim]Waiting before next account...[/dim]")
                    random_delay(3, 6)

        browser.close()

    # Display results
    display_results(all_tweets)

    # Save to file if requested
    if args.output:
        output_path = Path(args.output)
        with open(output_path, "w") as f:
            json.dump(all_tweets, f, indent=2)
        console.print(f"\n[green]Saved {len(all_tweets)} tweets to {output_path}[/green]")

    console.print(f"\n[bold]Total: {len(all_tweets)} tweets scraped[/bold]")


if __name__ == "__main__":
    main()
