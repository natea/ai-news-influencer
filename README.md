# AI News Influencer

Autonomous AI-powered social media management system that curates AI news from Twitter/X and generates engaging LinkedIn content.

## Overview

This system automatically:
- **Scrapes AI news** from Twitter/X using Playwright
- **Ranks and selects** the most relevant stories using AI agents
- **Generates LinkedIn posts** with Claude API
- **Creates images** using DALL-E 3 (with Stable Diffusion fallback)
- **Tracks engagement** metrics and optimizes strategy over time
- **Automates posting** on a configurable schedule

## Project Structure

```
├── backend/          # Python FastAPI backend
│   ├── src/
│   │   ├── agents/       # AI agents (selector, generator, optimizer)
│   │   ├── api/          # REST API endpoints
│   │   ├── integrations/ # Twitter, LinkedIn, Claude, DALL-E
│   │   ├── database/     # SQLite + vector store
│   │   └── services/     # Metrics, A/B testing, pipelines
│   └── Dockerfile
├── frontend/         # Next.js dashboard
│   ├── app/              # Pages (dashboard, posts, metrics, settings)
│   ├── components/       # React components
│   └── Dockerfile
├── nginx/            # Reverse proxy configuration
├── docs/             # Project documentation
└── docker-compose.yml
```

## Quick Start

### With Docker (Recommended)

```bash
# Clone and start all services
docker compose up --build
```

Access:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Manual Setup

See [backend/README.md](./backend/README.md) and [frontend/README.md](./frontend/README.md) for individual setup instructions.

## Configuration

Create a `.env` file in the backend directory:

```env
ANTHROPIC_API_KEY=your_anthropic_key
OPENAI_API_KEY=your_openai_key
LINKEDIN_CLIENT_ID=your_linkedin_client_id
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret
```

## Development Environment

This repo includes a DevPod/devcontainer configuration for consistent development environments. See [DEVPOD.md](./DEVPOD.md) for setup instructions.

## Documentation

- [Implementation Plan](./docs/implementation-plan.md) - Architecture and roadmap
- [Tasks](./docs/tasks.md) - Development task tracking
- [Backend README](./backend/README.md) - Backend setup and API reference
- [DevPod Setup](./DEVPOD.md) - Development container configuration

## License

MIT
