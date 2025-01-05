# Azura AI

🚀 From Doge to Pepe, Azura AI is your galaxy-brain companion in the wild world of memes and memecoins. This AI powerhouse doesn't just analyze memes – it speaks the language of internet culture, tracking everything from the dankest trends to the next potential moonshot in the memecoin universe.

## Features

- 🔍 Meme Radar: Spots viral content before it explodes
- 📈 Memecoin Detective: Tracks the ups and downs of meme-based tokens
- 🎭 Vibe Check: Analyzes social media mood and community reactions
- 🔮 Crystal Ball: Predicts which memes might become the next big thing
- 🌐 Meme Observatory: Watches meme evolution across all major platforms

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

## License

MIT License - see LICENSE file for details.