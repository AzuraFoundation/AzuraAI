# Azura AI

<div align="center">
  <img src="docs/images/banner_notext.jpg" alt="Azura AI Banner" width="100%">
  <br/>
  <p><em>Your AI companion in the world of memes and memecoins 🚀</em></p>
</div>

## About

From Doge to Pepe, Azura AI is your galaxy-brain companion in the wild world of memes and memecoins. This AI powerhouse doesn't just analyze memes – it speaks the language of internet culture, tracking everything from the dankest trends to the next potential moonshot in the memecoin universe.

## Features

- 🔍 Meme Radar: Spots viral content before it explodes
- 📈 Memecoin Detective: Tracks the ups and downs of meme-based tokens
- 🎭 Vibe Check: Analyzes social media mood and community reactions
- 🔮 Crystal Ball: Predicts which memes might become the next big thing
- 🌐 Meme Observatory: Watches meme evolution across all major platforms

### Coming Soon

#### Enhanced Analysis
- 🧠 AI-Powered Insights: Deep learning for meme context understanding
- 🎯 Template Detection: Track meme format evolution and variations
- 🔄 Cross-Platform Correlation: Connect trends across different platforms
- 📊 Historical Pattern Analysis: Learn from past viral memes

#### Trading Features
- ⚡ Real-time Alerts: Get notified of emerging meme trends
- 💹 Price Impact Prediction: Estimate market effects of viral memes
- 🎲 Risk Assessment: Evaluate memecoin investment risks

#### Community Features
- 👥 Crowd Sentiment: Aggregate community reactions
- 🏆 Meme Rankings: Daily/weekly top performing memes
- 🌍 Geographic Trends: Track regional meme popularity
- 🤝 Community Voting: Let users rate meme potential

#### Advanced Tools
- 📈 Technical Analysis: Combined with meme sentiment
- 🤖 Trading Bot Integration: Automated trading strategies
- 🔒 Portfolio Tracking: Monitor your memecoin investments

#### Developer Tools
- 🛠️ API Access: Integrate meme analysis in your apps
- 🔌 Webhook Support: Real-time data integration
- 📚 SDK: Developer tools and libraries

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Initialize database:
```bash
# Create initial migration (if not exists)
alembic revision --autogenerate -m "initial"

# Apply migrations
alembic upgrade head
```

4. Start the bot:
```bash
# Development
python bot.py

# Production (using pm2)
pm2 start bot.py --name azura-bot --interpreter python3
```

## Bot Configuration

1. Create a new bot with [@BotFather](https://t.me/BotFather) on Telegram
2. Get your bot token and add it to `.env`:
```
TELEGRAM_BOT_TOKEN=your_bot_token_here
```
3. Start chatting with your bot!

Send any meme image to the bot for analysis, or use these commands:
- `/start` - Show welcome message and available commands
- `/radar` - Spot trending memes
- `/detective` - Track memecoin movements
- `/vibe` - Check social sentiment
- `/crystal` - Get meme predictions
- `/observe` - Monitor meme evolution

## Database Migrations

We use Alembic for database migrations. Common commands:

```bash
# Create a new migration
alembic revision -m "describe_your_changes"

# Apply all pending migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1

# View migration history
alembic history

# View current database version
alembic current
```

## Development

### Setup Development Environment

1. Install development dependencies:
```bash
pip install -r requirements.txt
```

2. Install pre-commit hooks:
```bash
pre-commit install
```

### Code Quality

We use several tools to maintain code quality:

- **Black**: Code formatting
- **Ruff**: Fast Python linter
- **MyPy**: Static type checking

Run linters manually:
```bash
# Format code
black .

# Run linter
ruff check .

# Type checking
mypy src/
```

### Testing

Run tests with coverage:
```bash
pytest tests/ --cov=src/
```

### CI/CD

GitHub Actions automatically run:
- Code formatting check
- Linting
- Type checking
- Tests with coverage reporting

## License

MIT License - see LICENSE file for details.