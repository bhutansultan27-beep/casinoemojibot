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


async def dice_challenge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /dice_challenge command to challenge another player"""
    user = update.effective_user
    user_id = user.id
    
    if len(context.args) < 3:
        await update.message.reply_text(
            "❌ Usage: /dice_challenge @username [amount] [number]\n\n"
            "Example: /dice_challenge @friend 20 4\n\n"
            "Challenge a player to a dice match!"
        )
        return
    
    target_username = context.args[0].replace('@', '')
    
    try:
        amount = float(context.args[1])
        challenger_number = int(context.args[2])
    except ValueError:
        await update.message.reply_text("❌ Invalid amount or number. Use: /dice_challenge @user [amount] [number]")
        return
    
    if not (1 <= challenger_number <= 6):
        await update.message.reply_text("❌ Number must be between 1 and 6.")
        return
    
    if amount <= 0:
        await update.message.reply_text("❌ Amount must be greater than 0.")
        return
    
    user_data = db.get_user(user_id)
    
    if amount > user_data['balance']:
        await update.message.reply_text(
            f"❌ Insufficient balance.\n💰 Available: ${format_number(user_data['balance'])}"
        )
        return
    
    user_data['balance'] -= amount
    
    if not hasattr(db, 'dice_challenges'):
        db.dice_challenges = {}
    
    import uuid
    challenge_id = str(uuid.uuid4())
    
    db.dice_challenges[challenge_id] = {
        'challenger_id': user_id,
        'challenger_username': user.username or user.first_name,
        'target_username': target_username,
        'target_id': None,
        'amount': amount,
        'challenger_number': challenger_number,
        'status': 'pending',
        'created_at': asyncio.get_event_loop().time()
    }
    
    keyboard = [
        [InlineKeyboardButton("✅ Accept", callback_data=f"dice_accept_{challenge_id}"),
         InlineKeyboardButton("❌ Decline", callback_data=f"dice_decline_{challenge_id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    msg = (
        f"⚔️ <b>DICE CHALLENGE</b>\n\n"
        f"@{user.username or user.first_name} challenges @{target_username}!\n\n"
        f"💰 Bet: ${amount:.2f}\n"
        f"🎲 Challenger's number: Hidden\n"
        f"🏆 Winner takes: ${amount * 2:.2f}\n\n"
        f"@{target_username}, accept or decline?"
    )
    
    await update.message.reply_text(msg, parse_mode='HTML', reply_markup=reply_markup)
    
    await update.message.reply_text(
        f"✅ Challenge sent to @{target_username}!\n"
        f"💰 ${amount:.2f} locked in escrow.\n"
        f"🎲 Your number: {challenger_number}"
    )


class DealerBot:
    """Dealer bot for monitoring and handling challenges"""
    
    async def monitor_challenges(self, app):
        """Monitor active challenges and clean up expired ones"""
        while True:
            await asyncio.sleep(60)
            
            if hasattr(db, 'dice_challenges'):
                current_time = asyncio.get_event_loop().time()
                expired = []
                
                for challenge_id, challenge in db.dice_challenges.items():
                    if current_time - challenge['created_at'] > 300:
                        expired.append(challenge_id)
                
                for challenge_id in expired:
                    challenge = db.dice_challenges[challenge_id]
                    challenger_data = db.get_user(challenge['challenger_id'])
                    challenger_data['balance'] += challenge['amount']
                    
                    try:
                        await app.bot.send_message(
                            chat_id=challenge['challenger_id'],
                            text=f"⏱ Your dice challenge expired. ${challenge['amount']:.2f} refunded."
                        )
                    except:
                        pass
                    
                    del db.dice_challenges[challenge_id]


dealer_bot = DealerBot()
