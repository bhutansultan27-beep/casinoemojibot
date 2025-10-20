import asyncio
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import DiceEmoji

from database import db
from games import DiceGame, CoinFlipGame
from utils import check_achievements, get_xp_for_bet, format_number
from config import ACHIEVEMENTS


async def handle_text_bet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle text-based betting for Antaria Casino with Telegram's animated emojis
    """
    user_id = update.effective_user.id
    user_data = db.get_user(user_id)
    text = update.message.text.strip()

    game_state = context.user_data.get('game_state', {})

    if not game_state:
        await handle_casual_text(update, text, user_data)
        return

    game_type = game_state.get('type')

    try:
        amount = float(text)

        if amount <= 0:
            await update.message.reply_text("❌ Amount must be greater than 0.")
            return

        if amount > user_data['balance']:
            await update.message.reply_text(
                f"❌ Insufficient balance.\n"
                f"💰 You have: ${format_number(user_data['balance'])}"
            )
            return

        if game_type == 'dice':
            await handle_dice_bet(update, context, user_id, user_data, game_state, amount)
        elif game_type == 'coinflip':
            await handle_coinflip_bet(update, context, user_id, user_data, game_state, amount)
        else:
            context.user_data['game_state'] = {}
            await update.message.reply_text("❌ Unknown game type. Try /dice or /coinflip")
            return

        context.user_data['game_state'] = {}

    except ValueError:
        await update.message.reply_text("❌ Please enter a valid number.")


async def handle_dice_bet(update, context, user_id, user_data, game_state, amount):
    """Handle dice game bet with Telegram's animated dice emoji"""
    predicted_number = game_state.get('number')

    if not predicted_number or predicted_number < 1 or predicted_number > 6:
        await update.message.reply_text("❌ Invalid number. Please choose 1-6.")
        return

    # Deduct bet
    user_data['balance'] -= amount
    user_data['total_wagered'] += amount
    user_data['games_played'] += 1

    # Track for bonus system
    user_data['wagered_since_withdrawal'] = user_data.get('wagered_since_withdrawal', 0) + amount

    if user_data.get('playthrough_required', 0) > 0:
        user_data['bonus_wagered'] = user_data.get('bonus_wagered', 0) + amount

    db.global_stats['total_bets'] += 1
    db.global_stats['total_wagered'] += amount

    # Send Telegram's animated dice emoji
    dice_message = await context.bot.send_dice(
        chat_id=update.effective_chat.id,
        emoji=DiceEmoji.DICE
    )
    
    # Telegram automatically animates for ~3 seconds
    await asyncio.sleep(4)  # Wait for animation to complete
    
    result = dice_message.dice.value  # Get the actual result (1-6)

    # Calculate win
    won = result == predicted_number
    
    if won:
        payout = amount * 5  # 5x payout
        user_data['balance'] += amount + payout
        user_data['total_won'] += payout
        user_data['win_streak'] += 1
        if user_data['win_streak'] > user_data['max_win_streak']:
            user_data['max_win_streak'] = user_data['win_streak']

        db.global_stats['total_won'] += payout

        result_msg = (
            f"🎉 <b>YOU WIN!</b>\n\n"
            f"🎲 Result: {result}\n"
            f"🎯 You predicted: {predicted_number}\n\n"
            f"💰 Bet: ${amount:.2f}\n"
            f"🏆 Won: ${payout:.2f}\n"
            f"💳 Balance: ${format_number(user_data['balance'])}\n"
            f"🔥 Win streak: {user_data['win_streak']}"
        )
    else:
        user_data['win_streak'] = 0

        result_msg = (
            f"❌ <b>Better luck next time!</b>\n\n"
            f"🎲 Result: {result}\n"
            f"🎯 You predicted: {predicted_number}\n\n"
            f"💰 Bet: ${amount:.2f}\n"
            f"💳 Balance: ${format_number(user_data['balance'])}"
        )

    # Add XP
    xp_gained = get_xp_for_bet(amount)
    user_data['xp'] = user_data.get('xp', 0) + xp_gained

    # Check achievements
    unlocked = check_achievements(user_id)
    if unlocked:
        for ach_id, reward in unlocked:
            ach = ACHIEVEMENTS[ach_id]
            result_msg += f"\n\n🏆 Achievement: {ach['name']}\n+${reward}"

    await update.message.reply_text(result_msg, parse_mode='HTML')


async def handle_coinflip_bet(update, context, user_id, user_data, game_state, amount):
    """Handle coinflip bet with Telegram's animated dart emoji (used for coin flip)"""
    prediction = game_state.get('prediction')

    if prediction not in ['heads', 'tails']:
        await update.message.reply_text("❌ Invalid prediction. Choose heads or tails.")
        return

    # Deduct bet
    user_data['balance'] -= amount
    user_data['total_wagered'] += amount
    user_data['games_played'] += 1

    # Track for bonus system
    user_data['wagered_since_withdrawal'] = user_data.get('wagered_since_withdrawal', 0) + amount

    if user_data.get('playthrough_required', 0) > 0:
        user_data['bonus_wagered'] = user_data.get('bonus_wagered', 0) + amount

    db.global_stats['total_bets'] += 1
    db.global_stats['total_wagered'] += amount

    # Send animated dice for coin flip (we'll use dice but interpret as coin)
    dice_message = await context.bot.send_dice(
        chat_id=update.effective_chat.id,
        emoji=DiceEmoji.DICE
    )
    
    await asyncio.sleep(4)  # Wait for animation
    
    dice_value = dice_message.dice.value  # 1-6
    # Map dice result to coin: 1-3=heads, 4-6=tails
    result = 'heads' if dice_value <= 3 else 'tails'
    
    result_emoji = "🦅" if result == "heads" else "🏛️"

    # Calculate win
    won = result == prediction
    
    if won:
        payout = amount  # 2x total (1x profit)
        user_data['balance'] += amount + payout
        user_data['total_won'] += payout
        user_data['win_streak'] += 1
        if user_data['win_streak'] > user_data['max_win_streak']:
            user_data['max_win_streak'] = user_data['win_streak']

        db.global_stats['total_won'] += payout

        result_msg = (
            f"🎉 <b>YOU WIN!</b>\n\n"
            f"{result_emoji} Result: {result.upper()}\n"
            f"🎯 You called: {prediction.upper()}\n\n"
            f"💰 Bet: ${amount:.2f}\n"
            f"🏆 Won: ${payout:.2f}\n"
            f"💳 Balance: ${format_number(user_data['balance'])}\n"
            f"🔥 Win streak: {user_data['win_streak']}"
        )
    else:
        user_data['win_streak'] = 0

        result_msg = (
            f"❌ <b>Better luck next time!</b>\n\n"
            f"{result_emoji} Result: {result.upper()}\n"
            f"🎯 You called: {prediction.upper()}\n\n"
            f"💰 Bet: ${amount:.2f}\n"
            f"💳 Balance: ${format_number(user_data['balance'])}"
        )

    # Add XP
    xp_gained = get_xp_for_bet(amount)
    user_data['xp'] = user_data.get('xp', 0) + xp_gained

    # Check achievements
    unlocked = check_achievements(user_id)
    if unlocked:
        for ach_id, reward in unlocked:
            ach = ACHIEVEMENTS[ach_id]
            result_msg += f"\n\n🏆 Achievement: {ach['name']}\n+${reward}"

    await update.message.reply_text(result_msg, parse_mode='HTML')


async def handle_casual_text(update, text, user_data):
    """Handle casual text when not in game state"""
    text_lower = text.lower()

    if any(word in text_lower for word in ['dice', 'roll']) and any(char.isdigit() for char in text):
        await update.message.reply_text(
            "🎲 Want to play dice?\n\n"
            "Just type /dice to get started!\n"
            "Watch the animated dice roll!"
        )
        return

    if any(word in text_lower for word in ['flip', 'coin', 'heads', 'tails']):
        await update.message.reply_text(
            "🪙 Want to flip a coin?\n\n"
            "Use /coinflip to start!\n"
            "See the animated flip!"
        )
        return

    if any(word in text_lower for word in ['balance', 'money', 'funds', 'how much']):
        await update.message.reply_text(
            f"💰 Your balance: ${format_number(user_data['balance'])}\n\n"
            f"Use /balance for full details!"
        )
        return

    if any(word in text_lower for word in ['bonus', 'free', 'daily', 'claim']):
        await update.message.reply_text(
            "🎁 Claim your bonus with /bonus\n\n"
            "New players: Get $5!\n"
            "Regular players: Get 1% of total wagered!"
        )
        return

    if any(word in text_lower for word in ['challenge', 'pvp', 'battle', 'vs']) and '@' in text:
        await update.message.reply_text(
            "⚔️ Want to challenge someone?\n\n"
            "Use: /dice_challenge @username [amount] [number]\n"
            "Example: /dice_challenge @friend 20 4"
        )
        return

    if any(word in text_lower for word in ['help', 'how', 'guide', 'commands']):
        await update.message.reply_text(
            "🎰 <b>Antaria Casino</b>\n\n"
            "🎮 Games:\n"
            "/dice - Animated dice roll (PvP available!)\n"
            "/coinflip - Animated coin flip\n\n"
            "💰 Money:\n"
            "/balance - Check balance\n"
            "/bonus - Daily bonus\n"
            "/withdraw - Cash out\n\n"
            "Use /start for full guide!",
            parse_mode='HTML'
        )
        return

    import random
    if random.random() < 0.15:
        await update.message.reply_text(
            "💡 Try /dice or /coinflip to play!\n"
            "Watch the animated emojis! 🎲🪙"
        )
