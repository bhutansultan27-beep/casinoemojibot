import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from database import db
from games import (
    RouletteGame, BlackjackGame, BasketballGame, SoccerGame,
    BowlingGame, CrashGame, DiceGame, CoinFlipGame
)
from utils import check_achievements, get_xp_for_bet, format_number


async def roulette_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data = db.get_user(user_id)
    
    if not db.check_game_cooldown(user_id, 'roulette'):
        remaining = db.get_cooldown_remaining(user_id, 'roulette')
        await update.message.reply_text(f"⏱ Cooldown active. Wait {remaining}s")
        return
    
    keyboard = [
        [InlineKeyboardButton("🔴 Red", callback_data="roulette_red"),
         InlineKeyboardButton("⚫ Black", callback_data="roulette_black")],
        [InlineKeyboardButton("Odd", callback_data="roulette_odd"),
         InlineKeyboardButton("Even", callback_data="roulette_even")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    msg = (
        "🎰 <b>ROULETTE</b>\n\n"
        f"💰 Balance: {format_number(user_data['balance'])}\n\n"
        "Select your bet type:\n"
        "🔴 Red/⚫ Black - 1:1 payout\n"
        "Odd/Even - 1:1 payout\n\n"
        "After selecting, type your bet amount"
    )
    
    await update.message.reply_text(msg, reply_markup=reply_markup, parse_mode='HTML')


async def blackjack_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data = db.get_user(user_id)
    
    if not db.check_game_cooldown(user_id, 'blackjack'):
        remaining = db.get_cooldown_remaining(user_id, 'blackjack')
        await update.message.reply_text(f"⏱ Cooldown active. Wait {remaining}s")
        return
    
    keyboard = [
        [InlineKeyboardButton("$10", callback_data="blackjack_10"),
         InlineKeyboardButton("$25", callback_data="blackjack_25"),
         InlineKeyboardButton("$50", callback_data="blackjack_50")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    msg = (
        "🃏 <b>BLACKJACK</b>\n\n"
        f"💰 Balance: {format_number(user_data['balance'])}\n\n"
        "Beat the dealer to 21!\n"
        "🎰 Blackjack - 3:2 payout\n"
        "✅ Win - 1:1 payout\n\n"
        "Select your bet:"
    )
    
    await update.message.reply_text(msg, reply_markup=reply_markup, parse_mode='HTML')


async def basketball_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data = db.get_user(user_id)
    
    if not db.check_game_cooldown(user_id, 'basketball'):
        remaining = db.get_cooldown_remaining(user_id, 'basketball')
        await update.message.reply_text(f"⏱ Cooldown active. Wait {remaining}s")
        return
    
    keyboard = [
        [InlineKeyboardButton("🏀 Score", callback_data="basketball_score"),
         InlineKeyboardButton("❌ Miss", callback_data="basketball_miss")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    msg = (
        "🏀 <b>BASKETBALL FREE THROW</b>\n\n"
        f"💰 Balance: {format_number(user_data['balance'])}\n\n"
        "Bet on the free throw outcome:\n"
        "🏀 Score - 1.8:1 (55% chance)\n"
        "❌ Miss - 1.8:1 (45% chance)\n\n"
        "After selecting, type your bet amount"
    )
    
    await update.message.reply_text(msg, reply_markup=reply_markup, parse_mode='HTML')


async def soccer_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data = db.get_user(user_id)
    
    if not db.check_game_cooldown(user_id, 'soccer'):
        remaining = db.get_cooldown_remaining(user_id, 'soccer')
        await update.message.reply_text(f"⏱ Cooldown active. Wait {remaining}s")
        return
    
    keyboard = [
        [InlineKeyboardButton("⚽ Goal", callback_data="soccer_goal"),
         InlineKeyboardButton("🧤 Save", callback_data="soccer_save")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    msg = (
        "⚽ <b>SOCCER PENALTY</b>\n\n"
        f"💰 Balance: {format_number(user_data['balance'])}\n\n"
        "Bet on the penalty outcome:\n"
        "⚽ Goal - 2:1 (45% chance)\n"
        "🧤 Save - 2:1 (55% chance)\n\n"
        "After selecting, type your bet amount"
    )
    
    await update.message.reply_text(msg, reply_markup=reply_markup, parse_mode='HTML')


async def bowling_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data = db.get_user(user_id)
    
    if not db.check_game_cooldown(user_id, 'bowling'):
        remaining = db.get_cooldown_remaining(user_id, 'bowling')
        await update.message.reply_text(f"⏱ Cooldown active. Wait {remaining}s")
        return
    
    keyboard = [
        [InlineKeyboardButton("🎳 Strike", callback_data="bowling_strike"),
         InlineKeyboardButton("📍 Spare", callback_data="bowling_spare")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    msg = (
        "🎳 <b>BOWLING JACKPOT</b>\n\n"
        f"💰 Balance: {format_number(user_data['balance'])}\n"
        f"🏆 Jackpot: {format_number(db.jackpot_pool)}\n\n"
        "Bet on the roll:\n"
        "🎳 Strike - 20:1 (10% chance)\n"
        "📍 Spare - 1:1 (90% chance)\n\n"
        "💎 3 strikes in a row = JACKPOT!\n\n"
        "After selecting, type your bet amount"
    )
    
    await update.message.reply_text(msg, reply_markup=reply_markup, parse_mode='HTML')


async def crash_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data = db.get_user(user_id)
    
    if not db.check_game_cooldown(user_id, 'crash'):
        remaining = db.get_cooldown_remaining(user_id, 'crash')
        await update.message.reply_text(f"⏱ Cooldown active. Wait {remaining}s")
        return
    
    keyboard = [
        [InlineKeyboardButton("$10", callback_data="crash_10"),
         InlineKeyboardButton("$25", callback_data="crash_25"),
         InlineKeyboardButton("$50", callback_data="crash_50")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    msg = (
        "🚀 <b>CRASH GAME</b>\n\n"
        f"💰 Balance: {format_number(user_data['balance'])}\n\n"
        "Bet and set a cashout multiplier!\n"
        "Multiplier increases until crash\n\n"
        "Select your bet:"
    )
    
    await update.message.reply_text(msg, reply_markup=reply_markup, parse_mode='HTML')


async def dice_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data = db.get_user(user_id)
    
    if not db.check_game_cooldown(user_id, 'dice'):
        remaining = db.get_cooldown_remaining(user_id, 'dice')
        await update.message.reply_text(f"⏱ Cooldown active. Wait {remaining}s")
        return
    
    keyboard = [
        [InlineKeyboardButton("High (4-6)", callback_data="dice_high"),
         InlineKeyboardButton("Low (1-3)", callback_data="dice_low")],
        [InlineKeyboardButton("Even", callback_data="dice_even"),
         InlineKeyboardButton("Odd", callback_data="dice_odd")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    msg = (
        "🎲 <b>DICE ROLL</b>\n\n"
        f"💰 Balance: {format_number(user_data['balance'])}\n\n"
        "Predict the dice roll:\n"
        "High/Low - 1.5:1 payout\n"
        "Even/Odd - 1:1 payout\n\n"
        "After selecting, type your bet amount"
    )
    
    await update.message.reply_text(msg, reply_markup=reply_markup, parse_mode='HTML')


async def coinflip_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data = db.get_user(user_id)
    
    if not db.check_game_cooldown(user_id, 'coinflip'):
        remaining = db.get_cooldown_remaining(user_id, 'coinflip')
        await update.message.reply_text(f"⏱ Cooldown active. Wait {remaining}s")
        return
    
    keyboard = [
        [InlineKeyboardButton("🪙 Heads", callback_data="coinflip_heads"),
         InlineKeyboardButton("🪙 Tails", callback_data="coinflip_tails")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    msg = (
        "🪙 <b>COIN FLIP</b>\n\n"
        f"💰 Balance: {format_number(user_data['balance'])}\n\n"
        "Call it! Heads or Tails?\n"
        "1:1 payout (50% chance)\n\n"
        "After selecting, type your bet amount"
    )
    
    await update.message.reply_text(msg, reply_markup=reply_markup, parse_mode='HTML')
