import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import DiceEmoji

from database import db
from games import DiceGame, CoinFlipGame
from utils import check_achievements, get_xp_for_bet, format_number


async def dice_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enhanced dice game with Telegram's animated dice emoji"""
    user_id = update.effective_user.id
    user_data = db.get_user(user_id)
    
    keyboard = [
        [InlineKeyboardButton("🎲 Play vs Dealer", callback_data="dice_mode_bot")],
        [InlineKeyboardButton("⚔️ Challenge Player (PvP)", callback_data="dice_mode_pvp")],
        [InlineKeyboardButton("📋 View Challenges", callback_data="dice_view_challenges")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    msg = (
        "🎲 <b>DICE GAME</b>\n\n"
        f"💰 Balance: ${format_number(user_data['balance'])}\n\n"
        "🎯 <b>How to Play:</b>\n"
        "• Pick a number from 1-6\n"
        "• Win 5x your bet if you match!\n\n"
        "🎮 <b>Game Modes:</b>\n"
        "🤖 vs Dealer - Play against the house\n"
        "⚔️ PvP - Challenge another player\n\n"
        "Choose your mode:"
    )
    
    await update.message.reply_text(msg, reply_markup=reply_markup, parse_mode='HTML')


async def coinflip_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enhanced coin flip game with Telegram's animated dice emoji"""
    user_id = update.effective_user.id
    user_data = db.get_user(user_id)
    
    keyboard = [
        [InlineKeyboardButton("🦅 Heads", callback_data="coinflip_heads"),
         InlineKeyboardButton("🏛️ Tails", callback_data="coinflip_tails")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    msg = (
        "🪙 <b>COIN FLIP</b>\n\n"
        f"💰 Balance: ${format_number(user_data['balance'])}\n\n"
        "🎯 <b>Make Your Call:</b>\n"
        "🦅 Heads or 🏛️ Tails\n\n"
        "💵 Win 2x your bet!\n"
        "📊 Fair 50/50 odds\n\n"
        "Choose your side and enter your bet amount!"
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
