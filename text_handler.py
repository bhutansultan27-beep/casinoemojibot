import asyncio
from telegram import Update
from telegram.ext import ContextTypes

from database import db
from games import DiceGame, CoinFlipGame
from utils import check_achievements, get_xp_for_bet, format_number
from config import JACKPOT_CONTRIBUTION, ACHIEVEMENTS


async def handle_text_bet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle text-based betting for Antaria Casino
    Updated for new dice/coinflip only system
    """
    user_id = update.effective_user.id
    user_data = db.get_user(user_id)
    text = update.message.text.strip()

    # Check if user is in a game state
    game_state = context.user_data.get('game_state', {})

    if not game_state:
        # No active game state - provide helpful responses
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

        # Route to appropriate game handler
        if game_type == 'dice':
            await handle_dice_bet(update, user_id, user_data, game_state, amount)
        elif game_type == 'coinflip':
            await handle_coinflip_bet(update, user_id, user_data, game_state, amount)
        else:
            # Unknown game type - clear state
            context.user_data['game_state'] = {}
            await update.message.reply_text("❌ Unknown game type. Try /dice or /coinflip")
            return

        # Clear game state after bet
        context.user_data['game_state'] = {}

    except ValueError:
        await update.message.reply_text("❌ Please enter a valid number.")


async def handle_dice_bet(update, user_id, user_data, game_state, amount):
    """Handle dice game bet with animation"""
    predicted_number = game_state.get('number')

    if not predicted_number or predicted_number < 1 or predicted_number > 6:
        await update.message.reply_text("❌ Invalid number. Please choose 1-6.")
        return

    # Deduct bet
    user_data['balance'] -= amount
    user_data['total_wagered'] += amount
    user_data['games_played'] += 1

    # Track bonus playthrough
    if user_data.get('playthrough_required', 0) > 0:
        user_data['bonus_wagered'] = user_data.get('bonus_wagered', 0) + amount

    db.global_stats['total_bets'] += 1
    db.global_stats['total_wagered'] += amount

    # Animated dice roll
    msg = await update.message.reply_text("🎲 Rolling the dice...")

    # Animation frames
    for i in range(5):
        await asyncio.sleep(0.3)
        import random
        random_num = random.randint(1, 6)
        await msg.edit_text(f"🎲 Rolling... {DiceGame.get_dice_emoji(random_num)}")

    # Final result
    result = DiceGame.roll()
    result_emoji = DiceGame.get_dice_emoji(result)

    await asyncio.sleep(0.5)

    # Calculate win
    payout = DiceGame.calculate_payout(predicted_number, result, amount)
    won = payout > 0

    if won:
        user_data['balance'] += amount + payout
        user_data['total_won'] += payout
        user_data['win_streak'] += 1
        if user_data['win_streak'] > user_data['max_win_streak']:
            user_data['max_win_streak'] = user_data['win_streak']

        db.global_stats['total_won'] += payout

        result_msg = (
            f"🎉 <b>YOU WIN!</b>\n\n"
            f"🎲 Result: {result_emoji} ({result})\n"
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
            f"🎲 Result: {result_emoji} ({result})\n"
            f"🎯 You predicted: {predicted_number}\n\n"
            f"💰 Bet: ${amount:.2f}\n"
            f"💳 Balance: ${format_number(user_data['balance'])}"
        )

    # Add XP
    xp_gained = get_xp_for_bet(amount)
    user_data['xp'] += xp_gained

    # Check achievements
    unlocked = check_achievements(user_id)
    if unlocked:
        for ach_id, reward in unlocked:
            ach = ACHIEVEMENTS[ach_id]
            result_msg += f"\n\n🏆 Achievement: {ach['name']}\n+${reward}"

    await msg.edit_text(result_msg, parse_mode='HTML')


async def handle_coinflip_bet(update, user_id, user_data, game_state, amount):
    """Handle coinflip bet with animation"""
    prediction = game_state.get('prediction')

    if prediction not in ['heads', 'tails']:
        await update.message.reply_text("❌ Invalid prediction. Choose heads or tails.")
        return

    # Deduct bet
    user_data['balance'] -= amount
    user_data['total_wagered'] += amount
    user_data['games_played'] += 1

    # Track bonus playthrough
    if user_data.get('playthrough_required', 0) > 0:
        user_data['bonus_wagered'] = user_data.get('bonus_wagered', 0) + amount

    db.global_stats['total_bets'] += 1
    db.global_stats['total_wagered'] += amount

    # Animated coin flip
    msg = await update.message.reply_text("🪙 Flipping coin...")

    # Animation frames
    frames = ["🪙", "🔄", "🪙", "🔄", "🪙", "🔄"]
    for frame in frames:
        await asyncio.sleep(0.4)
        await msg.edit_text(f"{frame} Flipping...")

    # Final result
    result = CoinFlipGame.flip()
    result_emoji = CoinFlipGame.get_coin_emoji(result)

    await asyncio.sleep(0.5)

    # Calculate win
    payout = CoinFlipGame.calculate_payout(prediction, result, amount)
    won = payout > 0

    if won:
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
    user_data['xp'] += xp_gained

    # Check achievements
    unlocked = check_achievements(user_id)
    if unlocked:
        for ach_id, reward in unlocked:
            ach = ACHIEVEMENTS[ach_id]
            result_msg += f"\n\n🏆 Achievement: {ach['name']}\n+${reward}"

    await msg.edit_text(result_msg, parse_mode='HTML')


async def handle_casual_text(update, text, user_data):
    """Handle casual text when not in game state"""
    text_lower = text.lower()

    # Natural language dice betting
    if any(word in text_lower for word in ['dice', 'roll']) and any(char.isdigit() for char in text):
        await update.message.reply_text(
            "🎲 Want to play dice?\n\n"
            "Use: /dice [amount] [number]\n"
            "Example: /dice 10 5\n\n"
            "Or just type /dice for the menu!"
        )
        return

    # Natural language coinflip
    if any(word in text_lower for word in ['flip', 'coin', 'heads', 'tails']):
        await update.message.reply_text(
            "🪙 Want to flip a coin?\n\n"
            "Use: /coinflip [amount] [heads/tails]\n"
            "Example: /coinflip 20 heads\n\n"
            "Try it now!"
        )
        return

    # Balance inquiry
    if any(word in text_lower for word in ['balance', 'money', 'funds', 'how much']):
        await update.message.reply_text(
            f"💰 Your balance: ${format_number(user_data['balance'])}\n\n"
            f"Use /balance for full details!"
        )
        return

    # Bonus inquiry
    if any(word in text_lower for word in ['bonus', 'free', 'daily', 'claim']):
        await update.message.reply_text(
            "🎁 Claim your bonus with /bonus\n\n"
            "New players: Get $5!\n"
            "Regular players: Get 1% of total wagered!"
        )
        return

    # PvP challenge
    if any(word in text_lower for word in ['challenge', 'pvp', 'battle', 'vs']) and '@' in text:
        await update.message.reply_text(
            "⚔️ Want to challenge someone?\n\n"
            "Use: /dice_challenge @username [amount] [number]\n"
            "Example: /dice_challenge @friend 20 4"
        )
        return

    # Help request
    if any(word in text_lower for word in ['help', 'how', 'guide', 'commands']):
        await update.message.reply_text(
            "🎰 <b>Antaria Casino</b>\n\n"
            "🎮 Games:\n"
            "/dice - Roll the dice (PvP available!)\n"
            "/coinflip - Flip a coin\n\n"
            "💰 Money:\n"
            "/balance - Check balance\n"
            "/bonus - Daily bonus\n"
            "/withdraw - Cash out\n\n"
            "Use /start for full guide!",
            parse_mode='HTML'
        )
        return

    # Don't respond to every message to avoid spam
    # Only respond occasionally
    import random
    if random.random() < 0.15:  # 15% chance
        await update.message.reply_text(
            "💡 Try /dice or /coinflip to play!\n"
            "Or /help for all commands."
        )