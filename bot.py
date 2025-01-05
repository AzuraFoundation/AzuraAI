from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ParseMode, InputFile
import os
from dotenv import load_dotenv
from src.analyzers.meme_analyzer import MemeAnalyzer
from src.database.database import Database

# Load environment variables
load_dotenv()

# Initialize bot and dispatcher
bot = Bot(token=os.getenv('TELEGRAM_BOT_TOKEN'))
dp = Dispatcher(bot)
db = Database()  # We'll implement this later
meme_analyzer = MemeAnalyzer(db)

async def on_startup(dp):
    """Initialize database on startup"""
    await db.init_db()

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    welcome_text = """
🚀 Welcome to Azura AI - Your Meme & Memecoin Analysis Companion!
    
Use these commands to navigate:
/radar - Spot trending memes
/detective - Track memecoin movements
/vibe - Check social sentiment
/crystal - Get meme predictions
/observe - Monitor meme evolution

📸 Send me any meme image and I'll analyze it for you!
    """
    await message.reply(welcome_text)

@dp.message_handler(content_types=['photo'])
async def analyze_sent_meme(message: types.Message):
    """Analyzes meme images sent by users"""
    await message.reply("🔍 Analyzing your meme...")
    
    try:
        # Get the photo file_id (largest size)
        photo = message.photo[-1]
        
        # Get file info and download URL
        file_info = await bot.get_file(photo.file_id)
        file_url = f"https://api.telegram.org/file/bot{bot.token}/{file_info.file_path}"
        
        # Get caption if exists
        caption = message.caption if message.caption else ""
        
        # Prepare content for analysis
        content = {
            'image_url': file_url,
            'caption': caption,
            'file_id': photo.file_id,
            'source': 'telegram',
            'timestamp': message.date.isoformat()
        }
        
        # Get analysis
        analysis = await meme_analyzer.analyze_meme(content)
        
        # Format response
        response = f"""
🎯 Meme Analysis Results:

📊 Virality Potential: {analysis['virality_score'] * 100:.1f}%

🎭 Sentiment:
• Positive: {analysis['sentiment']['positive'] * 100:.1f}%
• Negative: {analysis['sentiment']['negative'] * 100:.1f}%
• Neutral: {analysis['sentiment']['neutral'] * 100:.1f}%

📈 Trend Indicators:
• Topics: {', '.join(analysis['trend_indicators']['trending_topics']) or 'None detected'}
• Related Memes: {len(analysis['trend_indicators']['related_memes'])}
• Popularity Score: {analysis['trend_indicators']['popularity_metrics'].get('score', 0) * 100:.1f}%

💰 Potential Memecoin Impact: {'High' if analysis['virality_score'] > 0.7 else 'Medium' if analysis['virality_score'] > 0.4 else 'Low'}
"""
        await message.reply(response)
        
    except Exception as e:
        await message.reply(f"😅 Oops! Something went wrong while analyzing your meme: {str(e)}")

@dp.message_handler(commands=['trending'])
async def send_trending_memes(message: types.Message):
    """Sends trending memes with analysis"""
    await message.reply("🔍 Analyzing trending memes...")
    
    try:
        trending_memes = await meme_analyzer.analyze_trending_memes()
        
        for meme in trending_memes:
            analysis_text = f"""
🎯 Meme Analysis:
📊 Popularity: {meme.popularity_score * 100:.1f}%
🎭 Sentiment: {meme.sentiment}
🌍 Origin: {meme.platform_origin}
🚀 Viral Potential: {meme.viral_potential * 100:.1f}%
💰 Related Coins: {', '.join(meme.related_coins)}
            """
            
            # Send meme image with analysis
            await message.answer_photo(
                photo=meme.image_url,
                caption=analysis_text,
                parse_mode=ParseMode.MARKDOWN
            )
    except Exception as e:
        await message.reply(f"😅 Oops! Something went wrong: {str(e)}")

@dp.message_handler(commands=['radar'])
async def meme_radar(message: types.Message):
    """Spots viral content before it explodes"""
    # TODO: Implement meme trend detection
    # - Analyze popular social media platforms
    # - Track meme template usage
    # - Monitor engagement metrics
    await message.reply("🔍 Meme Radar analysis: TBD")

@dp.message_handler(commands=['detective'])
async def memecoin_detective(message: types.Message):
    """Tracks memecoin market movements"""
    # TODO: Implement memecoin tracking
    # - Monitor memecoin prices
    # - Track trading volume
    # - Analyze market sentiment
    await message.reply("📈 Memecoin Detective report: TBD")

@dp.message_handler(commands=['vibe'])
async def vibe_check(message: types.Message):
    """Analyzes social sentiment"""
    # TODO: Implement sentiment analysis
    # - Analyze social media posts
    # - Track community reactions
    # - Measure engagement metrics
    await message.reply("🎭 Vibe Check results: TBD")

@dp.message_handler(commands=['crystal'])
async def crystal_ball(message: types.Message):
    """Predicts upcoming meme trends"""
    # TODO: Implement trend prediction
    # - Analyze early signals
    # - Track emerging patterns
    # - Predict potential viral content
    await message.reply("🔮 Crystal Ball prediction: TBD")

@dp.message_handler(commands=['observe'])
async def meme_observatory(message: types.Message):
    """Monitors meme evolution across platforms"""
    # TODO: Implement cross-platform monitoring
    # - Track meme spread across platforms
    # - Monitor meme variations
    # - Analyze platform-specific trends
    await message.reply("🌐 Meme Observatory report: TBD")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup) 