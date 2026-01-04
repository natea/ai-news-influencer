"""Content pipeline orchestrating scraping, ranking, and post generation."""

import json
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.agents.content_selector import ContentSelectorAgent
from src.agents.post_generator import PostGeneratorAgent
from src.agents.tools import (
    ContentRankingOutput,
    ContentSelectionInput,
    PostGenerationInput,
    PostStyle,
)
from src.database.models import GeneratedPost, PostStatus, ScrapedTweet, TargetAccount
from src.integrations.twitter_scraper import TwitterScraper


class ContentPipeline:
    """Orchestrates the content generation pipeline."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self._content_selector = ContentSelectorAgent()
        self._post_generator = PostGeneratorAgent()

    async def scrape_all_accounts(self) -> list[ScrapedTweet]:
        """Scrape tweets from all active target accounts."""
        # Get active accounts
        result = await self.session.execute(
            select(TargetAccount).where(TargetAccount.active == True)
        )
        accounts = result.scalars().all()

        if not accounts:
            return []

        handles = [acc.handle for acc in accounts]
        all_tweets = []

        async with TwitterScraper() as scraper:
            for handle in handles:
                tweets = await scraper.scrape_account(handle)
                for tweet in tweets:
                    # Check if tweet already exists
                    existing = await self.session.get(ScrapedTweet, tweet.id)
                    if not existing:
                        scraped_tweet = ScrapedTweet(
                            id=tweet.id,
                            author_handle=tweet.author_handle,
                            content=tweet.content,
                            posted_at=tweet.posted_at,
                            scraped_at=datetime.utcnow(),
                            likes=tweet.likes,
                            retweets=tweet.retweets,
                            replies=tweet.replies,
                            media_urls=json.dumps(tweet.media_urls),
                            hashtags=json.dumps(tweet.hashtags),
                            processed=False,
                        )
                        self.session.add(scraped_tweet)
                        all_tweets.append(scraped_tweet)

                # Update last scraped timestamp
                account = await self.session.get(TargetAccount, handle)
                if account:
                    account.last_scraped = datetime.utcnow()

        await self.session.commit()
        return all_tweets

    async def rank_unprocessed_tweets(self) -> list[ContentRankingOutput]:
        """Rank all unprocessed tweets."""
        result = await self.session.execute(
            select(ScrapedTweet).where(ScrapedTweet.processed == False)
        )
        tweets = result.scalars().all()

        rankings = []
        for tweet in tweets:
            ranking = await self._content_selector.rank_tweet(tweet)
            rankings.append(ranking)

            # Update relevance score in database
            tweet.relevance_score = ranking.relevance_score

        await self.session.commit()
        return rankings

    async def select_best_content(
        self,
        rankings: list[ContentRankingOutput],
        max_selections: int = 1,
    ) -> list[str]:
        """Select the best content for posting."""
        selection_input = ContentSelectionInput(
            candidates=rankings,
            max_selections=max_selections,
        )

        result = await self._content_selector.run(selection_input)

        if result.success and result.output:
            return result.output.selected_ids
        return []

    async def generate_post(
        self,
        tweet_id: str,
        style: PostStyle = PostStyle.INFORMATIVE,
        target_audience: str = "AI/tech professionals",
        brand_voice: str = "professional yet approachable",
    ) -> Optional[GeneratedPost]:
        """Generate a LinkedIn post from a tweet."""
        # Get the tweet
        tweet = await self.session.get(ScrapedTweet, tweet_id)
        if not tweet:
            return None

        # Generate the post
        generation_input = PostGenerationInput(
            source_tweet_id=tweet_id,
            source_content=tweet.content,
            source_author=tweet.author_handle,
            post_style=style,
            target_audience=target_audience,
            brand_voice=brand_voice,
            include_cta=True,
        )

        result = await self._post_generator.run(generation_input)

        if not result.success or not result.output:
            return None

        # Create the post record
        post = GeneratedPost(
            id=str(uuid.uuid4()),
            source_tweet_id=tweet_id,
            content=result.output.content,
            style=style.value,
            hashtags=json.dumps(result.output.hashtags),
            status=PostStatus.DRAFT.value,
            created_at=datetime.utcnow(),
        )

        # Mark tweet as processed
        tweet.processed = True

        self.session.add(post)
        await self.session.commit()

        return post

    async def run_full_pipeline(
        self,
        style: PostStyle = PostStyle.INFORMATIVE,
    ) -> list[GeneratedPost]:
        """Run the complete content generation pipeline."""
        # Step 1: Scrape new content
        await self.scrape_all_accounts()

        # Step 2: Rank unprocessed tweets
        rankings = await self.rank_unprocessed_tweets()

        if not rankings:
            return []

        # Step 3: Select best content
        selected_ids = await self.select_best_content(rankings, max_selections=1)

        if not selected_ids:
            return []

        # Step 4: Generate posts
        posts = []
        for tweet_id in selected_ids:
            post = await self.generate_post(tweet_id, style=style)
            if post:
                posts.append(post)

        return posts
