"""Command-line interface for AI News Influencer."""

import argparse
import asyncio
import json
import sys
from datetime import datetime
from typing import Optional

from src.core.config import get_settings
from src.database.models import ScrapedTweet, TargetAccount, init_database
from src.database.session import get_session
from src.integrations.twitter_scraper import TwitterScraper


async def init_db_command() -> None:
    """Initialize the database."""
    settings = get_settings()
    print(f"Initializing database at: {settings.database_url}")

    await init_database(settings.database_url)
    print("Database initialized successfully!")


async def scrape_command(
    accounts: list[str],
    max_tweets: int = 20,
    save: bool = True,
    demo: bool = False,
) -> list[ScrapedTweet]:
    """
    Scrape tweets from specified accounts.

    Args:
        accounts: List of Twitter handles to scrape
        max_tweets: Maximum tweets per account
        save: Whether to save results to database
        demo: Whether to use demo data when scraping fails

    Returns:
        List of scraped tweets
    """
    from src.integrations.twitter_scraper import ScraperConfig

    print(f"Starting scrape for accounts: {', '.join(accounts)}")
    print(f"Max tweets per account: {max_tweets}")
    if demo:
        print("Demo mode: Will use sample data if scraping fails")

    all_tweets: list[ScrapedTweet] = []
    config = ScraperConfig(max_tweets_per_account=max_tweets, demo_mode=demo)

    async with TwitterScraper(config=config) as scraper:
        for account in accounts:
            account = account.lstrip("@")
            print(f"\nScraping @{account}...")

            try:
                tweets = await scraper.scrape_account(account)
                print(f"  Found {len(tweets)} tweets")
                all_tweets.extend(tweets)

                # Display sample tweets
                for tweet in tweets[:3]:
                    print(f"\n  --- Tweet {tweet.id} ---")
                    print(f"  Content: {tweet.content[:100]}...")
                    print(f"  Likes: {tweet.likes}, Retweets: {tweet.retweets}")
                    if tweet.hashtags:
                        print(f"  Hashtags: {', '.join(tweet.hashtags[:5])}")

            except Exception as e:
                print(f"  Error scraping @{account}: {e}")

    if save and all_tweets:
        print(f"\nSaving {len(all_tweets)} tweets to database...")
        await save_tweets_to_db(all_tweets)
        print("Saved successfully!")

    print(f"\nTotal tweets scraped: {len(all_tweets)}")
    return all_tweets


async def save_tweets_to_db(tweets: list[ScrapedTweet]) -> None:
    """Save scraped tweets to the database."""
    from sqlalchemy import text

    async with get_session() as session:
        for tweet in tweets:
            await session.execute(
                text("""
                    INSERT OR REPLACE INTO scraped_tweets
                    (id, author_handle, content, posted_at, likes, retweets, replies, media_urls, hashtags, scraped_at)
                    VALUES (:id, :author_handle, :content, :posted_at, :likes, :retweets, :replies, :media_urls, :hashtags, datetime('now'))
                """),
                {
                    "id": tweet.id,
                    "author_handle": tweet.author_handle,
                    "content": tweet.content,
                    "posted_at": tweet.posted_at.isoformat() if tweet.posted_at else None,
                    "likes": tweet.likes,
                    "retweets": tweet.retweets,
                    "replies": tweet.replies,
                    "media_urls": json.dumps(tweet.media_urls),
                    "hashtags": json.dumps(tweet.hashtags),
                }
            )


async def add_account_command(
    handle: str,
    name: Optional[str] = None,
    category: str = "ai",
    priority: int = 1,
) -> None:
    """Add a target account to monitor."""
    from sqlalchemy import text

    handle = handle.lstrip("@")
    print(f"Adding target account: @{handle}")

    async with get_session() as session:
        await session.execute(
            text("""
                INSERT OR REPLACE INTO target_accounts (handle, name, category, priority, active, created_at)
                VALUES (:handle, :name, :category, :priority, 1, datetime('now'))
            """),
            {"handle": handle, "name": name, "category": category, "priority": priority}
        )

    print(f"Added @{handle} to target accounts")


async def list_accounts_command() -> None:
    """List all target accounts."""
    from sqlalchemy import text

    async with get_session() as session:
        result = await session.execute(
            text("SELECT handle, name, category, priority, active, last_scraped FROM target_accounts ORDER BY priority DESC")
        )
        accounts = result.fetchall()

        if not accounts:
            print("No target accounts configured.")
            return

        print("\nTarget Accounts:")
        print("-" * 60)
        for acc in accounts:
            handle, name, category, priority, active, last_scraped = acc
            status = "Active" if active else "Inactive"
            last_scraped_str = last_scraped if last_scraped else "Never"
            print(f"  @{handle:<20} | {category:<10} | Priority: {priority} | {status}")
            print(f"    Last scraped: {last_scraped_str}")


async def generate_command(tweet_id: str, style: str = "informative") -> None:
    """Generate a LinkedIn post from a tweet."""
    from sqlalchemy import text

    from src.integrations.claude import ClaudeClient

    async with get_session() as session:
        result = await session.execute(
            text("SELECT id, author_handle, content FROM scraped_tweets WHERE id = :tweet_id"),
            {"tweet_id": tweet_id}
        )
        tweet = result.fetchone()

        if not tweet:
            print(f"Tweet {tweet_id} not found in database.")
            return

        tweet_id, author_handle, content = tweet
        print(f"\nSource Tweet from @{author_handle}:")
        print(f"  {content}")
        print(f"\nGenerating LinkedIn post in '{style}' style...")

        client = ClaudeClient()
        gen_result = await client.generate_linkedin_post(
            source_content=content,
            style=style,
        )

        print("\n" + "=" * 60)
        print("GENERATED POST:")
        print("=" * 60)
        print(gen_result.get("content", ""))
        print("\nHashtags:", ", ".join(f"#{h}" for h in gen_result.get("hashtags", [])))


async def stats_command() -> None:
    """Display database statistics."""
    from sqlalchemy import text

    async with get_session() as session:
        # Count tweets
        tweet_count = await session.execute(text("SELECT COUNT(*) FROM scraped_tweets"))
        tweets = tweet_count.scalar() or 0

        # Count processed tweets (check if column exists, default to 0)
        try:
            processed_count = await session.execute(
                text("SELECT COUNT(*) FROM scraped_tweets WHERE processed = 1")
            )
            processed = processed_count.scalar() or 0
        except Exception:
            processed = 0

        # Count posts
        post_count = await session.execute(text("SELECT COUNT(*) FROM generated_posts"))
        posts = post_count.scalar() or 0

        # Count accounts
        account_count = await session.execute(text("SELECT COUNT(*) FROM target_accounts"))
        accounts = account_count.scalar() or 0

        print("\nDatabase Statistics:")
        print("-" * 40)
        print(f"  Target Accounts:    {accounts}")
        print(f"  Scraped Tweets:     {tweets}")
        print(f"  Processed Tweets:   {processed}")
        print(f"  Generated Posts:    {posts}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="AI News Influencer - CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # init command
    subparsers.add_parser("init", help="Initialize the database")

    # scrape command
    scrape_parser = subparsers.add_parser("scrape", help="Scrape tweets from accounts")
    scrape_parser.add_argument(
        "--accounts", "-a",
        type=str,
        required=True,
        help="Comma-separated list of Twitter handles",
    )
    scrape_parser.add_argument(
        "--max-tweets", "-m",
        type=int,
        default=20,
        help="Maximum tweets per account",
    )
    scrape_parser.add_argument(
        "--no-save",
        action="store_true",
        help="Don't save to database",
    )
    scrape_parser.add_argument(
        "--demo",
        action="store_true",
        help="Use demo data (for testing when Twitter scraping fails)",
    )

    # add-account command
    add_parser = subparsers.add_parser("add-account", help="Add a target account")
    add_parser.add_argument("handle", help="Twitter handle")
    add_parser.add_argument("--name", "-n", help="Display name")
    add_parser.add_argument(
        "--category", "-c",
        default="ai",
        choices=["ai", "research", "tech", "news"],
        help="Account category",
    )
    add_parser.add_argument(
        "--priority", "-p",
        type=int,
        default=1,
        help="Priority (higher = more important)",
    )

    # list-accounts command
    subparsers.add_parser("list-accounts", help="List target accounts")

    # generate command
    gen_parser = subparsers.add_parser("generate", help="Generate post from tweet")
    gen_parser.add_argument("tweet_id", help="Tweet ID")
    gen_parser.add_argument(
        "--style", "-s",
        default="informative",
        choices=["informative", "thought_leadership", "commentary"],
        help="Post style",
    )

    # stats command
    subparsers.add_parser("stats", help="Show database statistics")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Run the appropriate command
    if args.command == "init":
        asyncio.run(init_db_command())
    elif args.command == "scrape":
        accounts = [a.strip() for a in args.accounts.split(",")]
        asyncio.run(scrape_command(accounts, args.max_tweets, not args.no_save, args.demo))
    elif args.command == "add-account":
        asyncio.run(add_account_command(args.handle, args.name, args.category, args.priority))
    elif args.command == "list-accounts":
        asyncio.run(list_accounts_command())
    elif args.command == "generate":
        asyncio.run(generate_command(args.tweet_id, args.style))
    elif args.command == "stats":
        asyncio.run(stats_command())


if __name__ == "__main__":
    main()
