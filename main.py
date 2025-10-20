import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters

from config import BOT_TOKEN
from database import db
from handlers import (
    start, deposit, confirm_deposit, balance, withdraw, daily_bonus,
    profile, achievements_command, referral_command, leaderboard,
    stats_command, admin_command
)
from game_handlers import (
    roulette_command, blackjack_command, basketball_command,
    soccer_command, bowling_command, crash_command, dice_command,
    coinflip_command
)
from callback_handlers import handle_callback
from text_handler import handle_text_bet


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

logging.getLogger("httpx").setLevel(logging.WARNING)


async def error_handler(update, context):
    logger.error(f"Update {update} caused error {context.error}")


async def periodic_save(app):
    while True:
        await asyncio.sleep(300)
        db.save_data()
        logger.info("Database auto-saved")


def main():
    if not BOT_TOKEN:
        print("❌ Error: BOT_TOKEN not set!")
        print("Please set the BOT_TOKEN environment variable or update config.py")
        return
    
    print("🎰 Casino Emojia Bot Starting...")
    print("=" * 50)
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", start))
    application.add_handler(CommandHandler("deposit", deposit))
    application.add_handler(CommandHandler("confirm", confirm_deposit))
    application.add_handler(CommandHandler("balance", balance))
    application.add_handler(CommandHandler("withdraw", withdraw))
    application.add_handler(CommandHandler("bonus", daily_bonus))
    application.add_handler(CommandHandler("profile", profile))
    application.add_handler(CommandHandler("achievements", achievements_command))
    application.add_handler(CommandHandler("referral", referral_command))
    application.add_handler(CommandHandler("leaderboard", leaderboard))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("admin", admin_command))
    
    application.add_handler(CommandHandler("roulette", roulette_command))
    application.add_handler(CommandHandler("blackjack", blackjack_command))
    application.add_handler(CommandHandler("basketball", basketball_command))
    application.add_handler(CommandHandler("soccer", soccer_command))
    application.add_handler(CommandHandler("bowling", bowling_command))
    application.add_handler(CommandHandler("crash", crash_command))
    application.add_handler(CommandHandler("dice", dice_command))
    application.add_handler(CommandHandler("coinflip", coinflip_command))
    
    application.add_handler(CallbackQueryHandler(handle_callback))
    
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_bet))
    
    application.add_error_handler(error_handler)
    
    loop = asyncio.get_event_loop()
    loop.create_task(periodic_save(application))
    
    print("✅ Bot initialized successfully!")
    print("🎮 Available games: Roulette, Blackjack, Basketball, Soccer, Bowling, Crash, Dice, CoinFlip")
    print("🎁 Features: Achievements, Referrals, Leaderboard, Daily Bonus")
    print("=" * 50)
    print("🚀 Bot is now running...")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Bot stopped by user")
        db.save_data()
        print("💾 Database saved")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        db.save_data()
