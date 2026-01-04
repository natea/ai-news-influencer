# AI News Influencer

Autonomous AI-powered social media management system that curates AI news from Twitter/X and generates engaging LinkedIn content.

## What It Does

- **Scrapes AI news** from Twitter/X using Playwright
- **Ranks and selects** the most relevant stories using AI agents
- **Generates LinkedIn posts** with Claude API
- **Creates images** using DALL-E 3 (with Stable Diffusion fallback)
- **Tracks engagement** metrics and optimizes strategy over time
- **Automates posting** on a configurable schedule

## Quick Start

### 1. Install Dependencies

```bash
pip install -e .
playwright install chromium
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your API keys:
- `ANTHROPIC_API_KEY` - Claude API
- `OPENAI_API_KEY` - DALL-E 3
- LinkedIn OAuth credentials

### 3. Run the Server

```bash
uvicorn src.api.main:app --reload --port 8000
```

Or with Docker:
```bash
docker compose up --build
```

### 4. Use the CLI

```bash
# Scrape AI news
ai-news scrape --accounts "@OpenAI,@AnthropicAI" --limit 50

# Generate a post
ai-news generate --topic "AI News"

# View metrics
ai-news metrics --days 7
```

## Documentation

- **[DEVPOD.md](./DEVPOD.md)** - Devpod/devcontainer setup instructions
- **API Docs** - Available at `http://localhost:8000/docs` when running

## Requirements

- Python 3.11+
- SQLite
- API keys for Anthropic, OpenAI, and LinkedIn

## License

MIT
