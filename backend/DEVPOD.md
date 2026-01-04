# AI News Influencer - Backend

Autonomous AI Social Media Management System for curating AI news from Twitter/X and posting engaging content to LinkedIn.

## Features

- **Twitter/X Scraping**: Playwright-based scraper for collecting AI news content
- **Content Pipeline**: Extraction, parsing, and intelligent content ranking
- **AI Agents**:
  - Content Selector: Ranks and selects top AI news stories
  - Post Generator: Creates engaging LinkedIn posts using Claude API
  - Response Generator: Generates contextual replies using RAG
  - Strategy Optimizer: Learns from engagement metrics
- **RAG System**: Vector storage with embeddings for contextual responses
- **LinkedIn Integration**: OAuth 2.0 authentication and posting
- **Image Generation**: DALL-E 3 with Stable Diffusion fallback
- **Metrics & Analytics**: Engagement tracking and A/B testing
- **Scheduled Jobs**: APScheduler for automated operations

## Requirements

- Python 3.11+
- SQLite
- API Keys:
  - `ANTHROPIC_API_KEY` - Claude API for content generation
  - `OPENAI_API_KEY` - DALL-E 3 for image generation
  - LinkedIn OAuth credentials

## Installation

```bash
# Install dependencies
pip install -e .

# Install Playwright browsers
playwright install chromium

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

## Configuration

Create a `.env` file with:

```env
ANTHROPIC_API_KEY=your_anthropic_key
OPENAI_API_KEY=your_openai_key
LINKEDIN_CLIENT_ID=your_linkedin_client_id
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret
LINKEDIN_REDIRECT_URI=http://localhost:8000/auth/linkedin/callback
DATABASE_URL=sqlite:///./data/app.db
```

## Running

### Development

```bash
# Run the API server
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker

```bash
# From project root
docker compose up --build
```

### CLI Tool

```bash
# Scrape Twitter for AI news
ai-news scrape --accounts "@OpenAI,@AnthropicAI" --limit 50

# Generate a LinkedIn post
ai-news generate --topic "AI News"

# Check metrics
ai-news metrics --days 7
```

## API Endpoints

- `GET /health` - Health check
- `GET /api/content/trending` - Get trending AI content
- `POST /api/content/generate` - Generate a LinkedIn post
- `GET /api/metrics/engagement` - Get engagement metrics
- `GET /api/config` - Get current configuration
- `POST /auth/linkedin/authorize` - Start LinkedIn OAuth flow

## Project Structure

```
backend/
├── src/
│   ├── agents/          # AI agents (selector, generator, optimizer)
│   ├── api/             # FastAPI routes
│   ├── core/            # Config, prompts, scheduler
│   ├── database/        # SQLite models, vector store
│   ├── integrations/    # Twitter, Claude, LinkedIn, image gen
│   └── services/        # Metrics, comments, threading, A/B testing
├── tests/               # Unit and integration tests
├── pyproject.toml       # Project configuration
└── Dockerfile           # Container build
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test suite
pytest tests/unit -v
pytest tests/integration -v
```

## License

MIT
