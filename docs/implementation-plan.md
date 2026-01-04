# AI News Influencer - Implementation Plan

## GOAP-Based Development Strategy

**Project**: Autonomous AI Social Media Management System
**Context**: Sundai MIT IAP 2026
**Methodology**: Goal-Oriented Action Planning (GOAP) with SPARC Integration

---

## 1. Project Goals Analysis

### Primary Objective
Build an autonomous agentic system that:
- Monitors X (Twitter) for relevant AI/tech news
- Generates engaging LinkedIn content with AI-generated images
- Posts automatically without manual intervention
- Responds to comments intelligently
- Continuously improves strategy based on engagement metrics

### Success Criteria (Measurable Goals)

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Autonomous Posting | 1 post/day for 7 days | System logs |
| Comment Response Rate | 80%+ | Response count / Comment count |
| Engagement Improvement | Measurable increase over baseline | LinkedIn analytics delta |

### GOAP State Model

```javascript
// Initial State
current_state = {
  scraper_operational: false,
  content_pipeline: false,
  linkedin_integration: false,
  image_generation: false,
  comment_monitoring: false,
  rag_system: false,
  dashboard: false,
  metrics_tracking: false,
  autonomous_operation: false
}

// Goal State
goal_state = {
  scraper_operational: true,
  content_pipeline: true,
  linkedin_integration: true,
  image_generation: true,
  comment_monitoring: true,
  rag_system: true,
  dashboard: true,
  metrics_tracking: true,
  autonomous_operation: true
}
```

---

## 2. System Architecture

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           PRESENTATION LAYER                             │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    Next.js 14 Dashboard                          │    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐   │    │
│  │  │ Metrics  │ │ Scheduled│ │ Content  │ │ System Config    │   │    │
│  │  │ Display  │ │ Posts    │ │ Approval │ │ (Tone/Topics)    │   │    │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────────────┘   │    │
│  └─────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                            API LAYER                                     │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    FastAPI Backend (Python 3.11+)                │    │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐    │    │
│  │  │ REST API     │ │ WebSocket    │ │ Background Tasks     │    │    │
│  │  │ Endpoints    │ │ (Real-time)  │ │ (APScheduler)        │    │    │
│  │  └──────────────┘ └──────────────┘ └──────────────────────┘    │    │
│  └─────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
┌──────────────────────┐ ┌──────────────────┐ ┌──────────────────────────┐
│    AGENT LAYER       │ │  CONTENT LAYER   │ │    INTEGRATION LAYER     │
│ ┌──────────────────┐ │ │ ┌──────────────┐ │ │ ┌──────────────────────┐ │
│ │ Content Selector │ │ │ │ Post         │ │ │ │ X/Twitter Scraper    │ │
│ │ Agent            │ │ │ │ Generator    │ │ │ │ (Playwright)         │ │
│ ├──────────────────┤ │ │ ├──────────────┤ │ │ ├──────────────────────┤ │
│ │ Response         │ │ │ │ Image        │ │ │ │ LinkedIn API         │ │
│ │ Generator Agent  │ │ │ │ Generator    │ │ │ │ (OAuth + Posting)    │ │
│ ├──────────────────┤ │ │ ├──────────────┤ │ │ ├──────────────────────┤ │
│ │ Strategy         │ │ │ │ Hashtag &    │ │ │ │ Claude API           │ │
│ │ Optimizer Agent  │ │ │ │ Tag Engine   │ │ │ │ (Anthropic)          │ │
│ └──────────────────┘ │ │ └──────────────┘ │ │ ├──────────────────────┤ │
└──────────────────────┘ └──────────────────┘ │ │ DALL-E 3 / Stable    │ │
                                              │ │ Diffusion            │ │
                                              │ └──────────────────────┘ │
                                              └──────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           DATA LAYER                                     │
│  ┌─────────────────────┐  ┌─────────────────────────────────────────┐   │
│  │ SQLite Database     │  │ Vector Store (sqlite-vss)               │   │
│  │ ┌─────────────────┐ │  │ ┌─────────────────────────────────────┐ │   │
│  │ │ scraped_tweets  │ │  │ │ Post Embeddings                     │ │   │
│  │ │ generated_posts │ │  │ │ Comment Context                     │ │   │
│  │ │ engagement_logs │ │  │ │ Historical Performance              │ │   │
│  │ │ agent_decisions │ │  │ └─────────────────────────────────────┘ │   │
│  │ │ system_config   │ │  └─────────────────────────────────────────┘   │
│  │ └─────────────────┘ │                                                │
│  └─────────────────────┘                                                │
└─────────────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Key Technologies |
|-----------|---------------|------------------|
| **Dashboard** | User interface for monitoring and control | Next.js 14, React Server Components |
| **API Backend** | Business logic orchestration | FastAPI, Pydantic v2, APScheduler |
| **Content Selector Agent** | Ranks and selects news for posting | Claude API, Custom ranking algorithm |
| **Response Generator Agent** | Creates contextual comment responses | Claude API, RAG context |
| **Strategy Optimizer Agent** | Adjusts posting strategy based on metrics | A/B testing, ML patterns |
| **X Scraper** | Collects news from Twitter/X | Playwright, BeautifulSoup |
| **LinkedIn Integration** | Posts content and monitors engagement | LinkedIn OAuth, REST API |
| **Image Generator** | Creates contextual images | DALL-E 3 or Stable Diffusion |
| **RAG System** | Provides historical context | sqlite-vss, embeddings |

---

## 3. Implementation Milestones

### Milestone Dependency Graph

```
M1 (Foundation) ──┬──► M2 (Agent Logic) ──┬──► M4 (Engagement)
                  │                        │
                  └──► M3 (LinkedIn) ──────┤
                                           │
                                           └──► M5 (Optimization) ──► M6 (Deployment)
```

---

### Milestone 1: Foundation & Data Collection

**GOAP Action**: `establish_data_pipeline`

**Preconditions**:
- Development environment configured
- API credentials obtained (Twitter/X access)

**Deliverables**:
1. Project structure (monorepo with backend/frontend)
2. SQLite database with complete schema
3. X.com scraper with Playwright
4. Data storage pipeline with metadata extraction
5. CLI tool for scraper testing

**Success Criteria**:
- [ ] Scraper successfully extracts tweets from 5+ target accounts
- [ ] All scraped data stored in SQLite with proper schema
- [ ] Metadata includes: author, timestamp, engagement counts, media links
- [ ] Rate limiting implemented (respect API/scraping limits)
- [ ] CLI can trigger scrape and display results

**Database Schema**:
```sql
-- Core Tables
CREATE TABLE scraped_tweets (
    id TEXT PRIMARY KEY,
    author_handle TEXT NOT NULL,
    author_name TEXT,
    content TEXT NOT NULL,
    posted_at TIMESTAMP,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    likes INTEGER DEFAULT 0,
    retweets INTEGER DEFAULT 0,
    replies INTEGER DEFAULT 0,
    media_urls TEXT,  -- JSON array
    hashtags TEXT,    -- JSON array
    relevance_score REAL,
    processed BOOLEAN DEFAULT FALSE
);

CREATE TABLE target_accounts (
    handle TEXT PRIMARY KEY,
    name TEXT,
    category TEXT,  -- 'ai', 'research', 'tech'
    priority INTEGER DEFAULT 1,
    last_scraped TIMESTAMP
);

CREATE TABLE system_config (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Actions**:
1. Initialize Python project with poetry/pip
2. Create database initialization script
3. Implement Playwright scraper for X.com
4. Build content extraction and parsing logic
5. Create CLI interface for testing

---

### Milestone 2: Agent Logic & Content Generation

**GOAP Action**: `build_intelligence_layer`

**Preconditions**:
- Milestone 1 complete (data available in database)
- Claude API access configured

**Deliverables**:
1. Agentic architecture with Pydantic tool definitions
2. Content ranking algorithm
3. LinkedIn post generator with system prompts
4. Prompt templates for different content types
5. Content generation pipeline tests

**Success Criteria**:
- [ ] Agent ranks scraped content by relevance score (0-1)
- [ ] Generated posts match LinkedIn tone guidelines
- [ ] Posts include appropriate hashtags (3-5 per post)
- [ ] System prompts configurable via database
- [ ] 90%+ of generated posts pass quality threshold

**Agent Architecture**:
```python
# Pydantic Tool Definitions
class ContentRankingTool(BaseModel):
    """Tool for ranking content relevance"""
    tweet_id: str
    relevance_factors: List[str]
    engagement_potential: float
    topic_match: float
    timeliness: float

class PostGeneratorTool(BaseModel):
    """Tool for generating LinkedIn posts"""
    source_tweet_id: str
    post_style: Literal["informative", "thought_leadership", "commentary"]
    target_audience: str
    include_cta: bool = True

class HashtagSuggesterTool(BaseModel):
    """Tool for suggesting relevant hashtags"""
    content: str
    max_hashtags: int = 5
    industry_focus: List[str]
```

**Prompt Templates**:
```yaml
post_generation:
  informative: |
    Transform this AI/tech news into an engaging LinkedIn post:
    - Lead with the key insight or implication
    - Add professional commentary on impact
    - Include a call-to-action or question
    - Maintain {brand_voice} tone

  thought_leadership: |
    Create a thought leadership post based on this news:
    - Share a unique perspective or prediction
    - Connect to broader industry trends
    - Position the author as knowledgeable
    - Invite discussion
```

**Actions**:
1. Design agent orchestration pattern (ReAct or Chain of Thought)
2. Implement content ranking with weighted scoring
3. Create Claude API integration with structured outputs
4. Build prompt template system with variable injection
5. Add content quality validation

---

### Milestone 3: Image Generation & LinkedIn Integration

**GOAP Action**: `enable_multimodal_posting`

**Preconditions**:
- Milestone 2 complete (content generation working)
- LinkedIn Developer App created with OAuth configured
- Image generation API access (DALL-E 3 or Replicate)

**Deliverables**:
1. Image generation integration with prompt engineering
2. LinkedIn OAuth authentication flow
3. LinkedIn posting API integration
4. Hashtag and mention tagging logic
5. End-to-end posting pipeline

**Success Criteria**:
- [ ] Images generated match post content contextually
- [ ] LinkedIn OAuth flow completes successfully
- [ ] Posts with images appear on LinkedIn correctly
- [ ] Hashtags render as clickable links
- [ ] Person/company tags resolve correctly
- [ ] Post scheduling works for future times

**LinkedIn API Integration**:
```python
# OAuth Flow
class LinkedInAuth:
    """LinkedIn OAuth 2.0 implementation"""
    AUTHORIZATION_URL = "https://www.linkedin.com/oauth/v2/authorization"
    TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"

    scopes = [
        "r_liteprofile",
        "w_member_social",
        "r_organization_social"
    ]

# Posting Schema
class LinkedInPost(BaseModel):
    """LinkedIn post structure"""
    author: str  # URN format
    commentary: str
    visibility: Literal["PUBLIC", "CONNECTIONS"]
    media_assets: Optional[List[str]] = None
    mentions: Optional[List[MentionEntity]] = None
```

**Image Generation Pipeline**:
```python
class ImagePromptGenerator:
    """Generates DALL-E prompts from post content"""

    def generate_prompt(self, post_content: str, style: str) -> str:
        """
        Creates image prompt based on post context
        Styles: 'professional', 'abstract', 'infographic', 'minimalist'
        """
        pass

class ImageGenerationService:
    """Handles image generation with fallback"""
    primary: str = "dalle3"
    fallback: str = "stable_diffusion"

    async def generate(self, prompt: str) -> bytes:
        """Generate image with automatic fallback"""
        pass
```

**Actions**:
1. Implement image prompt engineering logic
2. Integrate DALL-E 3 API (with Stable Diffusion fallback)
3. Build LinkedIn OAuth flow with token refresh
4. Create LinkedIn posting service
5. Add media upload handling for images
6. Test end-to-end flow with real LinkedIn account

---

### Milestone 4: Engagement & Memory System

**GOAP Action**: `enable_autonomous_engagement`

**Preconditions**:
- Milestone 3 complete (posting to LinkedIn works)
- Vector extension for SQLite configured

**Deliverables**:
1. Comment monitoring system
2. Response generation agent
3. RAG system with post history
4. Vector embeddings for semantic search
5. Memory and context management

**Success Criteria**:
- [ ] Comments detected within 15 minutes of posting
- [ ] Response agent generates contextually appropriate replies
- [ ] RAG retrieves relevant past posts for context
- [ ] Conversation threads maintained coherently
- [ ] 80%+ comment response rate achieved

**RAG Architecture**:
```python
class PostMemoryRAG:
    """RAG system for post history and context"""

    def __init__(self, db_path: str):
        self.embeddings = EmbeddingModel("text-embedding-3-small")
        self.vector_store = SQLiteVSS(db_path)

    async def add_post(self, post: GeneratedPost):
        """Embed and store post for future retrieval"""
        embedding = await self.embeddings.embed(post.content)
        await self.vector_store.insert(post.id, embedding, post.metadata)

    async def retrieve_context(
        self,
        query: str,
        k: int = 5
    ) -> List[PostContext]:
        """Retrieve relevant past posts for context"""
        query_embedding = await self.embeddings.embed(query)
        return await self.vector_store.search(query_embedding, k)
```

**Comment Response Pipeline**:
```
Comment Detected
      │
      ▼
┌─────────────────┐
│ Classify Intent │ (question, feedback, spam, etc.)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Retrieve Context│ (original post + related posts via RAG)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Generate Reply  │ (Claude API with context)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Quality Check   │ (tone, relevance, safety)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Post Response   │ (LinkedIn API)
└─────────────────┘
```

**Actions**:
1. Implement comment polling/monitoring
2. Build response generation agent with RAG context
3. Set up sqlite-vss for vector storage
4. Create embedding pipeline for posts
5. Implement conversation threading logic
6. Add response quality guardrails

---

### Milestone 5: Metrics & Self-Improvement

**GOAP Action**: `enable_optimization_loop`

**Preconditions**:
- Milestone 4 complete (engagement system working)
- Historical data available for analysis

**Deliverables**:
1. Metrics collection system (LinkedIn API + scraping)
2. Agent decision logging
3. Strategy adjustment algorithm
4. Next.js dashboard with visualizations
5. A/B testing framework

**Success Criteria**:
- [ ] All engagement metrics tracked (likes, comments, shares, views)
- [ ] Agent decisions logged with reasoning
- [ ] Strategy adjustments visible in dashboard
- [ ] A/B tests can compare content styles
- [ ] Measurable improvement demonstrated

**Metrics Schema**:
```sql
CREATE TABLE engagement_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id TEXT NOT NULL,
    measured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    impressions INTEGER DEFAULT 0,
    click_through_rate REAL,
    engagement_rate REAL,
    FOREIGN KEY (post_id) REFERENCES generated_posts(id)
);

CREATE TABLE agent_decisions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    decision_type TEXT NOT NULL,  -- 'content_selection', 'response', 'strategy'
    input_context TEXT,           -- JSON
    decision TEXT,                -- JSON
    reasoning TEXT,
    outcome TEXT,                 -- 'success', 'failure', 'pending'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE ab_tests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_name TEXT NOT NULL,
    variant_a TEXT,  -- JSON config
    variant_b TEXT,  -- JSON config
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    status TEXT DEFAULT 'active',
    winner TEXT,
    statistical_significance REAL
);
```

**Dashboard Components**:
```typescript
// Dashboard Pages
interface DashboardStructure {
  overview: {
    totalPosts: number;
    avgEngagement: number;
    responseRate: number;
    trendChart: TimeSeriesData;
  };

  posts: {
    scheduled: Post[];
    published: Post[];
    drafts: Post[];
  };

  metrics: {
    engagementByPostType: ChartData;
    bestPerformingHashtags: RankingData;
    optimalPostingTimes: HeatmapData;
  };

  settings: {
    topics: string[];
    tone: 'professional' | 'casual' | 'thought_leader';
    postingFrequency: CronExpression;
    targetAccounts: string[];
  };
}
```

**Actions**:
1. Build metrics collection service
2. Implement decision logging middleware
3. Create strategy optimization algorithm
4. Build Next.js dashboard with charts
5. Add A/B testing infrastructure
6. Create performance reports

---

### Milestone 6: Production Deployment

**GOAP Action**: `deploy_autonomous_system`

**Preconditions**:
- All previous milestones complete
- All tests passing
- Security review complete

**Deliverables**:
1. Digital Ocean droplet configured
2. CI/CD pipeline
3. Monitoring and alerting
4. Documentation
5. 7-day autonomous operation proof

**Success Criteria**:
- [ ] System deployed and accessible
- [ ] Automatic daily posting confirmed for 7 days
- [ ] Error alerting functional
- [ ] Recovery procedures documented
- [ ] All success metrics achieved

**Deployment Architecture**:
```
┌──────────────────────────────────────────────────────────────┐
│                    Digital Ocean Droplet                      │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                    Docker Compose                     │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │   │
│  │  │   FastAPI   │  │   Next.js   │  │   Nginx     │  │   │
│  │  │   Backend   │  │   Frontend  │  │   Proxy     │  │   │
│  │  │   :8000     │  │   :3000     │  │   :80/443   │  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  │   │
│  │                                                       │   │
│  │  ┌─────────────────────────────────────────────────┐ │   │
│  │  │              SQLite + sqlite-vss                 │ │   │
│  │  │              /data/app.db                        │ │   │
│  │  └─────────────────────────────────────────────────┘ │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

**Actions**:
1. Set up Digital Ocean droplet
2. Configure Docker Compose stack
3. Set up SSL with Let's Encrypt
4. Configure backup strategy
5. Deploy and validate
6. Monitor for 7 days

---

## 4. Technology Stack Recommendations

### Backend Stack

| Layer | Technology | Version | Rationale |
|-------|------------|---------|-----------|
| **Runtime** | Python | 3.11+ | AI/ML ecosystem, async support |
| **Framework** | FastAPI | 0.100+ | Async, type-safe, auto-docs |
| **Validation** | Pydantic | v2 | Structured outputs, type safety |
| **Database** | SQLite | 3.40+ | Simple, portable, no server needed |
| **Vector Store** | sqlite-vss | latest | Built-in RAG, no separate service |
| **Scheduling** | APScheduler | 3.10+ | Background job execution |
| **HTTP Client** | httpx | 0.25+ | Async HTTP requests |
| **Scraping** | Playwright | 1.40+ | Dynamic content handling |

### Frontend Stack

| Layer | Technology | Version | Rationale |
|-------|------------|---------|-----------|
| **Framework** | Next.js | 14 | RSC, App Router, easy deployment |
| **UI Library** | React | 18 | Component-based, hooks |
| **Styling** | Tailwind CSS | 3.4+ | Utility-first, rapid development |
| **Charts** | Recharts | 2.10+ | React-native charting |
| **State** | Zustand | 4.4+ | Simple state management |
| **Forms** | React Hook Form | 7.48+ | Form handling |

### AI/ML Stack

| Layer | Technology | Rationale |
|-------|------------|-----------|
| **LLM** | Claude API (claude-3-5-sonnet) | Strong reasoning, long context, tool use |
| **Embeddings** | text-embedding-3-small | Cost-effective, good quality |
| **Image Gen** | DALL-E 3 (primary) | High quality, consistent style |
| **Image Gen** | Stable Diffusion (fallback) | Cost-effective alternative |

### Infrastructure

| Component | Technology | Rationale |
|-----------|------------|-----------|
| **Hosting** | Digital Ocean Droplet | Simple, cost-effective, no AWS complexity |
| **Container** | Docker Compose | Easy local/prod parity |
| **Reverse Proxy** | Nginx | SSL termination, load balancing |
| **SSL** | Let's Encrypt | Free, automated certificates |

---

## 5. Data Flow Design

### Content Generation Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                     CONTENT GENERATION PIPELINE                      │
└─────────────────────────────────────────────────────────────────────┘

[Scheduler Trigger: Every 4 hours]
         │
         ▼
┌─────────────────┐
│ 1. SCRAPE       │ ──► Playwright fetches tweets from target accounts
│    X/Twitter    │     Stores in scraped_tweets table with metadata
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 2. RANK         │ ──► Claude API analyzes each tweet
│    Content      │     Scores: relevance, timeliness, engagement potential
└────────┬────────┘     Filters: already processed, duplicates, low quality
         │
         ▼
┌─────────────────┐
│ 3. SELECT       │ ──► Picks top-ranked content
│    Best         │     Considers posting frequency limits
└────────┬────────┘     Avoids topic repetition
         │
         ▼
┌─────────────────┐
│ 4. GENERATE     │ ──► Claude API creates LinkedIn post
│    Post         │     Uses RAG for context and style consistency
└────────┬────────┘     Includes hashtags and mentions
         │
         ▼
┌─────────────────┐
│ 5. GENERATE     │ ──► DALL-E 3 creates contextual image
│    Image        │     Fallback to Stable Diffusion if needed
└────────┬────────┘     Validates image quality
         │
         ▼
┌─────────────────┐
│ 6. QUEUE        │ ──► Stores in pending_posts table
│    for Approval │     Optionally auto-approves based on config
└────────┬────────┘     Schedules for optimal posting time
         │
         ▼
[Dashboard shows pending posts for review]
         │
         ▼
┌─────────────────┐
│ 7. POST         │ ──► LinkedIn API publishes content
│    to LinkedIn  │     Updates status to 'published'
└────────┬────────┘     Stores LinkedIn post ID
         │
         ▼
[Metrics collection begins]
```

### Engagement Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                     ENGAGEMENT PIPELINE                              │
└─────────────────────────────────────────────────────────────────────┘

[Scheduler Trigger: Every 15 minutes]
         │
         ▼
┌─────────────────┐
│ 1. POLL         │ ──► LinkedIn API fetches comments on recent posts
│    Comments     │     Identifies new/unprocessed comments
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 2. CLASSIFY     │ ──► Determines comment type
│    Intent       │     Types: question, feedback, compliment, spam, troll
└────────┬────────┘
         │
    ┌────┴────┐
    │ Spam?   │
    └────┬────┘
    Yes  │  No
    │    │
    ▼    ▼
[Ignore] ┌─────────────────┐
         │ 3. RETRIEVE     │ ──► RAG fetches relevant context
         │    Context      │     Original post, related posts, user history
         └────────┬────────┘
                  │
                  ▼
         ┌─────────────────┐
         │ 4. GENERATE     │ ──► Claude API creates response
         │    Response     │     Maintains brand voice
         └────────┬────────┘     Addresses specific question/comment
                  │
                  ▼
         ┌─────────────────┐
         │ 5. QUALITY      │ ──► Checks tone, relevance, safety
         │    Check        │     Applies guardrails
         └────────┬────────┘
                  │
             ┌────┴────┐
             │ Pass?   │
             └────┬────┘
          No │    │ Yes
             ▼    ▼
        [Manual   ┌─────────────────┐
         Review]  │ 6. POST         │ ──► LinkedIn API posts reply
                  │    Response     │     Logs decision and outcome
                  └─────────────────┘
```

### Optimization Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                     OPTIMIZATION PIPELINE                            │
└─────────────────────────────────────────────────────────────────────┘

[Scheduler Trigger: Daily at midnight]
         │
         ▼
┌─────────────────┐
│ 1. COLLECT      │ ──► Fetches engagement metrics for all posts
│    Metrics      │     Updates engagement_metrics table
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 2. ANALYZE      │ ──► Identifies patterns in high-performing content
│    Performance  │     Calculates optimal posting times
└────────┬────────┘     Determines best hashtag combinations
         │
         ▼
┌─────────────────┐
│ 3. UPDATE       │ ──► Adjusts content selection weights
│    Strategy     │     Updates posting schedule
└────────┬────────┘     Refines prompt templates
         │
         ▼
┌─────────────────┐
│ 4. LOG          │ ──► Records strategy changes
│    Changes      │     Creates A/B test if significant change
└────────┬────────┘
         │
         ▼
[Dashboard shows optimization recommendations]
```

---

## 6. API/Integration Points

### External APIs Required

| API | Purpose | Auth Method | Rate Limits |
|-----|---------|-------------|-------------|
| **X/Twitter** | News scraping | API Key or Scraping | ~100 req/15min |
| **LinkedIn** | Posting, comments, metrics | OAuth 2.0 | 100 posts/day |
| **Claude (Anthropic)** | LLM reasoning | API Key | Based on tier |
| **OpenAI** | Embeddings, DALL-E | API Key | Based on tier |
| **Replicate** | Stable Diffusion (fallback) | API Key | Based on tier |

### LinkedIn API Endpoints

```yaml
Authentication:
  - GET /oauth/v2/authorization
  - POST /oauth/v2/accessToken

User Profile:
  - GET /v2/me

Content Publishing:
  - POST /v2/ugcPosts  # Create post
  - POST /v2/assets?action=registerUpload  # Upload media
  - GET /v2/socialActions/{postUrn}/comments  # Get comments
  - POST /v2/socialActions/{postUrn}/comments  # Reply to comment

Analytics:
  - GET /v2/organizationalEntityShareStatistics  # Engagement metrics
```

### Internal API Endpoints (FastAPI)

```yaml
# Content Management
POST   /api/v1/scrape/trigger          # Manual scrape trigger
GET    /api/v1/content/pending         # Get content awaiting generation
POST   /api/v1/content/generate        # Generate post from tweet
GET    /api/v1/posts                   # List all posts
GET    /api/v1/posts/{id}              # Get specific post
PATCH  /api/v1/posts/{id}              # Update post (edit before publishing)
POST   /api/v1/posts/{id}/approve      # Approve for publishing
POST   /api/v1/posts/{id}/publish      # Publish immediately
DELETE /api/v1/posts/{id}              # Delete post

# Engagement
GET    /api/v1/comments                # Get all comments
GET    /api/v1/comments/pending        # Get unresponded comments
POST   /api/v1/comments/{id}/respond   # Generate and post response

# Metrics
GET    /api/v1/metrics/overview        # Dashboard overview stats
GET    /api/v1/metrics/posts/{id}      # Metrics for specific post
GET    /api/v1/metrics/trends          # Time-series engagement data

# Configuration
GET    /api/v1/config                  # Get system configuration
PATCH  /api/v1/config                  # Update configuration
GET    /api/v1/config/prompts          # Get prompt templates
PATCH  /api/v1/config/prompts          # Update prompt templates

# System
GET    /api/v1/health                  # Health check
GET    /api/v1/logs                    # Agent decision logs
POST   /api/v1/auth/linkedin/callback  # OAuth callback
```

### WebSocket Endpoints

```yaml
WS /ws/metrics          # Real-time metrics updates
WS /ws/notifications    # System notifications (new comments, errors)
```

---

## 7. Testing Strategy

### Testing Pyramid

```
                    ┌───────────┐
                    │   E2E     │  5%  - Critical user journeys
                    │  Tests    │       - Full posting flow
                   ┌┴───────────┴┐
                   │ Integration │  25% - API integrations
                   │   Tests     │      - Database operations
                  ┌┴─────────────┴┐     - LinkedIn posting
                  │     Unit      │ 70% - Business logic
                  │    Tests      │     - Agent decisions
                  └───────────────┘     - Content ranking
```

### Test Categories

#### Unit Tests

```python
# Agent Logic Tests
class TestContentRanking:
    def test_relevance_score_calculation(self):
        """Test that relevance scoring produces expected rankings"""
        pass

    def test_duplicate_detection(self):
        """Test that duplicate content is filtered"""
        pass

    def test_topic_matching(self):
        """Test that off-topic content is deprioritized"""
        pass

class TestPostGeneration:
    def test_hashtag_extraction(self):
        """Test hashtag generation from content"""
        pass

    def test_mention_formatting(self):
        """Test LinkedIn mention URN formatting"""
        pass

    def test_character_limit_enforcement(self):
        """Test posts stay within LinkedIn limits"""
        pass

class TestResponseGeneration:
    def test_spam_detection(self):
        """Test spam comments are correctly identified"""
        pass

    def test_context_retrieval(self):
        """Test RAG retrieves relevant context"""
        pass
```

#### Integration Tests

```python
# API Integration Tests
class TestLinkedInIntegration:
    @pytest.mark.integration
    async def test_oauth_flow(self):
        """Test complete OAuth authentication flow"""
        pass

    @pytest.mark.integration
    async def test_post_creation(self):
        """Test posting text content to LinkedIn"""
        pass

    @pytest.mark.integration
    async def test_image_upload(self):
        """Test image upload and attachment"""
        pass

class TestScraperIntegration:
    @pytest.mark.integration
    async def test_tweet_extraction(self):
        """Test scraping tweets from X"""
        pass

    @pytest.mark.integration
    async def test_rate_limit_handling(self):
        """Test graceful rate limit handling"""
        pass

# Database Integration Tests
class TestDatabaseOperations:
    @pytest.mark.integration
    async def test_vector_search(self):
        """Test RAG vector similarity search"""
        pass

    @pytest.mark.integration
    async def test_metrics_aggregation(self):
        """Test engagement metrics calculation"""
        pass
```

#### End-to-End Tests

```python
class TestFullPipeline:
    @pytest.mark.e2e
    async def test_scrape_to_post_flow(self):
        """Test complete flow from scraping to LinkedIn post"""
        # 1. Trigger scrape
        # 2. Verify content stored
        # 3. Generate post
        # 4. Verify post quality
        # 5. Post to LinkedIn (sandbox)
        # 6. Verify post appears
        pass

    @pytest.mark.e2e
    async def test_comment_response_flow(self):
        """Test complete comment detection and response"""
        pass
```

### Test Data Strategy

```yaml
fixtures:
  tweets:
    - ai_research_announcement.json
    - tech_product_launch.json
    - industry_opinion.json
    - irrelevant_content.json  # For filtering tests

  linkedin_responses:
    - post_created.json
    - rate_limited.json
    - auth_expired.json

mocks:
  claude_api:
    - ranking_response.json
    - post_generation.json
    - response_generation.json

  dalle_api:
    - image_success.json
    - image_content_policy.json
```

### CI/CD Testing

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run unit tests
        run: pytest tests/unit -v --cov=src

  integration-tests:
    runs-on: ubuntu-latest
    needs: unit-tests
    steps:
      - name: Run integration tests
        run: pytest tests/integration -v
        env:
          CLAUDE_API_KEY: ${{ secrets.CLAUDE_API_KEY }}

  e2e-tests:
    runs-on: ubuntu-latest
    needs: integration-tests
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Run E2E tests
        run: pytest tests/e2e -v
```

---

## 8. Risk Assessment

### Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **X/Twitter blocks scraping** | High | High | Implement multiple scraping strategies; use official API if available; rotate user agents |
| **LinkedIn API rate limits** | Medium | High | Queue system with backoff; batch operations; monitor limits |
| **Image generation fails** | Medium | Medium | Fallback to Stable Diffusion; text-only post fallback |
| **Claude API outage** | Low | High | Cache recent successful prompts; implement retry with exponential backoff |
| **Content quality issues** | Medium | High | Human-in-the-loop approval; quality scoring threshold |

### Operational Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Inappropriate content posted** | Medium | Critical | Content filtering; guardrails; approval workflow |
| **Spam detection triggers** | Medium | High | Rate limiting; natural posting patterns; warm-up period |
| **Account suspension** | Low | Critical | Follow platform ToS; manual review option; backup accounts |
| **Data loss** | Low | High | Regular backups; database replication |

### Security Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **API key exposure** | Low | Critical | Environment variables; secrets management; key rotation |
| **OAuth token theft** | Low | High | Secure token storage; token refresh; minimal scopes |
| **Unauthorized access** | Low | High | Authentication on dashboard; IP allowlisting |

### Risk Response Matrix

```
┌─────────────────────────────────────────────────────────────────────┐
│                     RISK RESPONSE DECISION TREE                      │
└─────────────────────────────────────────────────────────────────────┘

API Failure Detected
         │
    ┌────┴────┐
    │ Which   │
    │ API?    │
    └────┬────┘
         │
    ┌────┼────────┬──────────┬────────────┐
    ▼    ▼        ▼          ▼            ▼
 [Claude] [LinkedIn] [Twitter] [Image Gen] [Other]
    │         │         │          │          │
    ▼         ▼         ▼          ▼          ▼
 Retry     Queue     Retry      Use         Log &
 3x with   post,     with       fallback    Alert
 backoff   alert     VPN/       API         Team
           user      proxy

If all retries fail:
  └──► Log error
  └──► Send alert
  └──► Mark task for manual review
  └──► Continue with next task
```

---

## 9. GOAP Action Sequence (Optimal Path)

### Complete Action Plan

```javascript
// GOAP Optimal Action Sequence
const actionPlan = [
  // Phase 1: Foundation
  {
    action: "setup_project_structure",
    preconditions: ["dev_environment_ready"],
    effects: ["project_initialized"],
    priority: 1
  },
  {
    action: "initialize_database",
    preconditions: ["project_initialized"],
    effects: ["database_ready"],
    priority: 2
  },
  {
    action: "build_scraper",
    preconditions: ["database_ready"],
    effects: ["scraper_operational"],
    priority: 3
  },

  // Phase 2: Intelligence (can partially parallel with Phase 3)
  {
    action: "implement_ranking_agent",
    preconditions: ["scraper_operational", "claude_api_configured"],
    effects: ["ranking_ready"],
    priority: 4
  },
  {
    action: "implement_post_generator",
    preconditions: ["ranking_ready"],
    effects: ["content_pipeline_ready"],
    priority: 5
  },

  // Phase 3: Integration
  {
    action: "setup_linkedin_oauth",
    preconditions: ["project_initialized"],
    effects: ["linkedin_auth_ready"],
    priority: 4  // Can parallel with ranking
  },
  {
    action: "implement_image_generation",
    preconditions: ["content_pipeline_ready"],
    effects: ["image_generation_ready"],
    priority: 6
  },
  {
    action: "implement_linkedin_posting",
    preconditions: ["linkedin_auth_ready", "image_generation_ready"],
    effects: ["posting_ready"],
    priority: 7
  },

  // Phase 4: Engagement
  {
    action: "setup_rag_system",
    preconditions: ["database_ready"],
    effects: ["rag_ready"],
    priority: 5  // Can parallel with Phase 3
  },
  {
    action: "implement_comment_monitoring",
    preconditions: ["posting_ready"],
    effects: ["comment_monitoring_ready"],
    priority: 8
  },
  {
    action: "implement_response_agent",
    preconditions: ["rag_ready", "comment_monitoring_ready"],
    effects: ["engagement_ready"],
    priority: 9
  },

  // Phase 5: Optimization
  {
    action: "build_metrics_collector",
    preconditions: ["posting_ready"],
    effects: ["metrics_ready"],
    priority: 8  // Can parallel with engagement
  },
  {
    action: "build_dashboard",
    preconditions: ["metrics_ready"],
    effects: ["dashboard_ready"],
    priority: 10
  },
  {
    action: "implement_strategy_optimizer",
    preconditions: ["metrics_ready", "engagement_ready"],
    effects: ["optimization_ready"],
    priority: 11
  },

  // Phase 6: Deployment
  {
    action: "deploy_to_production",
    preconditions: ["dashboard_ready", "optimization_ready", "tests_passing"],
    effects: ["system_deployed"],
    priority: 12
  },
  {
    action: "validate_autonomous_operation",
    preconditions: ["system_deployed"],
    effects: ["goal_achieved"],
    priority: 13
  }
];
```

### Parallel Execution Opportunities

```
Timeline View:

Day 1:  [setup_project] → [init_database] → [build_scraper]
                                    │
Day 2:  ────────────────────────────┼────────────────────────
        [implement_ranking_agent] ──┤── [setup_linkedin_oauth]
        [implement_post_generator] ─┤── [setup_rag_system]
                                    │
Day 3:  ────────────────────────────┼────────────────────────
        [implement_image_gen] ──────┼── [linkedin_posting]
                                    │
Day 4:  ────────────────────────────┼────────────────────────
        [comment_monitoring] ───────┼── [metrics_collector]
        [response_agent] ───────────┤
                                    │
Day 5:  ────────────────────────────┼────────────────────────
        [build_dashboard] ──────────┤
        [strategy_optimizer] ───────┤
        [deploy] ───────────────────┘
```

---

## 10. Quick Reference

### Environment Variables Required

```bash
# API Keys
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
REPLICATE_API_KEY=r8_...

# LinkedIn OAuth
LINKEDIN_CLIENT_ID=...
LINKEDIN_CLIENT_SECRET=...
LINKEDIN_REDIRECT_URI=http://localhost:8000/api/v1/auth/linkedin/callback

# Database
DATABASE_URL=sqlite:///./data/app.db

# Configuration
POST_FREQUENCY_HOURS=24
MAX_POSTS_PER_DAY=1
APPROVAL_REQUIRED=true
LOG_LEVEL=INFO
```

### Directory Structure

```
ai-news-influencer/
├── backend/
│   ├── src/
│   │   ├── agents/
│   │   │   ├── content_selector.py
│   │   │   ├── post_generator.py
│   │   │   ├── response_generator.py
│   │   │   └── strategy_optimizer.py
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── content.py
│   │   │   │   ├── metrics.py
│   │   │   │   └── config.py
│   │   │   └── main.py
│   │   ├── integrations/
│   │   │   ├── linkedin.py
│   │   │   ├── twitter_scraper.py
│   │   │   ├── claude.py
│   │   │   └── image_gen.py
│   │   ├── database/
│   │   │   ├── models.py
│   │   │   ├── migrations/
│   │   │   └── vector_store.py
│   │   └── core/
│   │       ├── config.py
│   │       ├── scheduler.py
│   │       └── logging.py
│   ├── tests/
│   │   ├── unit/
│   │   ├── integration/
│   │   └── e2e/
│   ├── pyproject.toml
│   └── Dockerfile
├── frontend/
│   ├── app/
│   │   ├── dashboard/
│   │   ├── posts/
│   │   ├── metrics/
│   │   └── settings/
│   ├── components/
│   ├── lib/
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

### Key Commands

```bash
# Development
cd backend && uvicorn src.api.main:app --reload
cd frontend && npm run dev

# Testing
pytest tests/unit -v
pytest tests/integration -v --cov

# Production
docker-compose up -d

# Database
python -m src.database.migrate

# Manual Operations
python -m src.cli scrape --accounts @OpenAI,@AnthropicAI
python -m src.cli generate --tweet-id abc123
python -m src.cli post --post-id xyz789
```

---

## Appendix A: Guardrails & Safety

### Content Safety Rules

```python
CONTENT_GUARDRAILS = {
    "forbidden_topics": [
        "political_opinions",
        "controversial_social_issues",
        "competitor_criticism",
        "unverified_claims"
    ],
    "required_elements": [
        "source_attribution",
        "factual_accuracy_check",
        "professional_tone"
    ],
    "max_promotional_ratio": 0.2,  # Max 20% promotional content
    "min_value_ratio": 0.8         # Min 80% educational/informative
}
```

### Response Safety Rules

```python
RESPONSE_GUARDRAILS = {
    "never_discuss": [
        "pricing",
        "legal_advice",
        "medical_advice",
        "personal_information"
    ],
    "always_include": [
        "acknowledge_comment",
        "stay_on_topic"
    ],
    "escalation_triggers": [
        "threat",
        "harassment",
        "complaint"
    ]
}
```

---

## Appendix B: Success Validation Checklist

### Milestone 1 Validation
- [ ] Can scrape tweets from 5+ accounts
- [ ] Data stored with complete metadata
- [ ] Rate limiting prevents blocks
- [ ] CLI tool works correctly

### Milestone 2 Validation
- [ ] Content ranking produces sensible scores
- [ ] Generated posts pass quality review
- [ ] Hashtags are relevant
- [ ] Prompts are configurable

### Milestone 3 Validation
- [ ] LinkedIn OAuth flow completes
- [ ] Posts appear on LinkedIn
- [ ] Images attach correctly
- [ ] Scheduling works

### Milestone 4 Validation
- [ ] Comments detected promptly
- [ ] Responses are contextual
- [ ] RAG retrieves relevant history
- [ ] 80%+ response rate

### Milestone 5 Validation
- [ ] Metrics update in dashboard
- [ ] Optimization suggestions generated
- [ ] A/B tests can be configured
- [ ] Trends visible over time

### Milestone 6 Validation
- [ ] System deployed and accessible
- [ ] 7 days autonomous operation
- [ ] All success metrics achieved
- [ ] Recovery procedures tested

---

*Generated using GOAP methodology for optimal action sequencing*
*Last Updated: 2026-01-03*
