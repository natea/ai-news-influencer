"""X/Twitter scraper using Playwright for dynamic content."""
import asyncio
import json
import re
from datetime import datetime
from typing import Optional
from urllib.parse import quote

from playwright.async_api import async_playwright, Page, Browser
from pydantic import BaseModel

from src.database.models import ScrapedTweet


class ScraperConfig(BaseModel):
    """Configuration for the Twitter scraper."""
    headless: bool = True
    timeout_ms: int = 30000
    max_tweets_per_account: int = 20
    scroll_pause_ms: int = 2000
    demo_mode: bool = False  # Use demo data when scraping fails
    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )


# Demo tweets for testing when real scraping fails
DEMO_TWEETS = {
    "openai": [
        {"id": "demo_openai_1", "content": "Introducing GPT-5: Our most capable model yet with enhanced reasoning, creativity, and safety features. Available now for ChatGPT Plus subscribers. #AI #GPT5", "likes": 45000, "retweets": 12000},
        {"id": "demo_openai_2", "content": "New research: We've developed a novel approach to AI alignment that shows promising results in reducing hallucinations by 40%. Paper: arxiv.org/abs/... #AIResearch #MachineLearning", "likes": 28000, "retweets": 8500},
        {"id": "demo_openai_3", "content": "ChatGPT can now browse the web, analyze images, and execute code - all in a single conversation. The future of AI assistants is here. #ChatGPT #Innovation", "likes": 52000, "retweets": 15000},
    ],
    "anthropicai": [
        {"id": "demo_anthropic_1", "content": "Announcing Claude 4: Our safest and most helpful AI assistant yet. Now with 200K context window and improved coding capabilities. #Claude #AI #Safety", "likes": 32000, "retweets": 9800},
        {"id": "demo_anthropic_2", "content": "New constitutional AI research: How we're training models to be helpful, harmless, and honest through iterative feedback. Read our latest paper: anthropic.com/research/... #AIAlignment", "likes": 18000, "retweets": 5200},
        {"id": "demo_anthropic_3", "content": "Claude can now analyze PDFs, spreadsheets, and code repositories in a single prompt. Enterprise features rolling out this week. #Enterprise #AI #Productivity", "likes": 24000, "retweets": 7100},
    ],
    "default": [
        {"id": "demo_default_1", "content": "Exciting developments in AI this week! The pace of innovation continues to accelerate. #AI #Tech #Innovation", "likes": 5000, "retweets": 1200},
        {"id": "demo_default_2", "content": "Machine learning is transforming every industry. Here's what you need to know about the latest trends. #MachineLearning #DataScience", "likes": 3500, "retweets": 890},
    ]
}


class TwitterScraper:
    """Scraper for X/Twitter using Playwright."""

    def __init__(self, config: Optional[ScraperConfig] = None):
        self.config = config or ScraperConfig()
        self._browser: Optional[Browser] = None
        self._page: Optional[Page] = None

    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def start(self) -> None:
        """Start the browser."""
        playwright = await async_playwright().start()
        self._browser = await playwright.chromium.launch(
            headless=self.config.headless
        )
        context = await self._browser.new_context(
            user_agent=self.config.user_agent,
            viewport={"width": 1920, "height": 1080}
        )
        self._page = await context.new_page()

    async def close(self) -> None:
        """Close the browser."""
        if self._browser:
            await self._browser.close()
            self._browser = None
            self._page = None

    async def scrape_account(self, handle: str) -> list[ScrapedTweet]:
        """
        Scrape tweets from a specific account.

        Args:
            handle: Twitter handle (with or without @)

        Returns:
            List of scraped tweets
        """
        if not self._page:
            raise RuntimeError("Scraper not started. Use async with or call start().")

        # Clean handle
        handle = handle.lstrip("@")
        url = f"https://x.com/{handle}"

        try:
            await self._page.goto(url, timeout=self.config.timeout_ms)
            await self._page.wait_for_load_state("networkidle", timeout=self.config.timeout_ms)

            tweets = []
            seen_ids = set()
            scroll_count = 0
            max_scrolls = 10

            while len(tweets) < self.config.max_tweets_per_account and scroll_count < max_scrolls:
                # Extract tweets from current view
                tweet_elements = await self._page.query_selector_all('article[data-testid="tweet"]')

                for element in tweet_elements:
                    try:
                        tweet = await self._extract_tweet(element, handle)
                        if tweet and tweet.id not in seen_ids:
                            seen_ids.add(tweet.id)
                            tweets.append(tweet)
                    except Exception as e:
                        # Skip malformed tweets
                        continue

                # Scroll to load more
                await self._page.evaluate("window.scrollBy(0, window.innerHeight)")
                await asyncio.sleep(self.config.scroll_pause_ms / 1000)
                scroll_count += 1

            if tweets:
                return tweets[:self.config.max_tweets_per_account]

            # Fall back to demo data if no real tweets found
            if self.config.demo_mode:
                return self._get_demo_tweets(handle)
            return []

        except Exception as e:
            print(f"Error scraping {handle}: {e}")
            # Fall back to demo data on error
            if self.config.demo_mode:
                print(f"  Using demo data for @{handle}")
                return self._get_demo_tweets(handle)
            return []

    def _get_demo_tweets(self, handle: str) -> list[ScrapedTweet]:
        """Get demo tweets for testing."""
        handle_lower = handle.lower()
        demo_data = DEMO_TWEETS.get(handle_lower, DEMO_TWEETS["default"])

        tweets = []
        for data in demo_data[:self.config.max_tweets_per_account]:
            hashtags = re.findall(r"#(\w+)", data["content"])
            tweets.append(ScrapedTweet(
                id=data["id"],
                author_handle=f"@{handle}",
                content=data["content"],
                posted_at=datetime.utcnow(),
                likes=data["likes"],
                retweets=data["retweets"],
                replies=data.get("replies", 0),
                media_urls=[],
                hashtags=hashtags
            ))
        return tweets

    async def _extract_tweet(self, element, author_handle: str) -> Optional[ScrapedTweet]:
        """Extract tweet data from a tweet element."""
        try:
            # Get tweet text
            text_element = await element.query_selector('[data-testid="tweetText"]')
            content = await text_element.inner_text() if text_element else ""

            if not content:
                return None

            # Get tweet ID from link
            link_element = await element.query_selector('a[href*="/status/"]')
            if link_element:
                href = await link_element.get_attribute("href")
                tweet_id = href.split("/status/")[-1].split("?")[0] if href else None
            else:
                return None

            # Get engagement metrics
            likes = await self._get_metric(element, "like")
            retweets = await self._get_metric(element, "retweet")
            replies = await self._get_metric(element, "reply")

            # Get timestamp
            time_element = await element.query_selector("time")
            posted_at = None
            if time_element:
                datetime_str = await time_element.get_attribute("datetime")
                if datetime_str:
                    posted_at = datetime.fromisoformat(datetime_str.replace("Z", "+00:00"))

            # Extract hashtags
            hashtags = re.findall(r"#(\w+)", content)

            # Get media URLs
            media_urls = []
            img_elements = await element.query_selector_all('img[src*="pbs.twimg.com"]')
            for img in img_elements:
                src = await img.get_attribute("src")
                if src and "profile" not in src:
                    media_urls.append(src)

            return ScrapedTweet(
                id=tweet_id,
                author_handle=f"@{author_handle}",
                content=content,
                posted_at=posted_at,
                likes=likes,
                retweets=retweets,
                replies=replies,
                media_urls=media_urls,
                hashtags=hashtags
            )

        except Exception as e:
            return None

    async def _get_metric(self, element, metric_type: str) -> int:
        """Get engagement metric from tweet element."""
        try:
            selector = f'[data-testid="{metric_type}"] span'
            metric_element = await element.query_selector(selector)
            if metric_element:
                text = await metric_element.inner_text()
                return self._parse_count(text)
        except:
            pass
        return 0

    @staticmethod
    def _parse_count(text: str) -> int:
        """Parse count string (e.g., '1.5K', '2M') to integer."""
        if not text:
            return 0

        text = text.strip().upper()
        multipliers = {"K": 1000, "M": 1000000, "B": 1000000000}

        for suffix, multiplier in multipliers.items():
            if text.endswith(suffix):
                try:
                    return int(float(text[:-1]) * multiplier)
                except ValueError:
                    return 0

        try:
            return int(text.replace(",", ""))
        except ValueError:
            return 0

    async def search_topic(self, query: str, max_results: int = 20) -> list[ScrapedTweet]:
        """
        Search for tweets by topic/keyword.

        Args:
            query: Search query
            max_results: Maximum tweets to return

        Returns:
            List of matching tweets
        """
        if not self._page:
            raise RuntimeError("Scraper not started.")

        encoded_query = quote(query)
        url = f"https://x.com/search?q={encoded_query}&src=typed_query&f=live"

        try:
            await self._page.goto(url, timeout=self.config.timeout_ms)
            await self._page.wait_for_load_state("networkidle", timeout=self.config.timeout_ms)

            tweets = []
            seen_ids = set()

            tweet_elements = await self._page.query_selector_all('article[data-testid="tweet"]')

            for element in tweet_elements[:max_results]:
                try:
                    # Get author from tweet
                    author_element = await element.query_selector('[data-testid="User-Name"] a')
                    author = ""
                    if author_element:
                        href = await author_element.get_attribute("href")
                        author = href.split("/")[-1] if href else ""

                    tweet = await self._extract_tweet(element, author)
                    if tweet and tweet.id not in seen_ids:
                        seen_ids.add(tweet.id)
                        tweets.append(tweet)
                except:
                    continue

            return tweets

        except Exception as e:
            print(f"Error searching '{query}': {e}")
            return []


async def scrape_all_accounts(accounts: list[str]) -> list[ScrapedTweet]:
    """
    Scrape tweets from multiple accounts.

    Args:
        accounts: List of Twitter handles

    Returns:
        Combined list of scraped tweets
    """
    all_tweets = []

    async with TwitterScraper() as scraper:
        for account in accounts:
            tweets = await scraper.scrape_account(account)
            all_tweets.extend(tweets)
            # Rate limiting pause between accounts
            await asyncio.sleep(2)

    return all_tweets
