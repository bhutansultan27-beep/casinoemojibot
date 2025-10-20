import asyncio
from telegram import Update
from telegram.ext import ContextTypes

from database import db
from games import RouletteGame, BasketballGame, SoccerGame, BowlingGame, DiceGame, CoinFlipGame
from utils import check_achievements, get_xp_for_bet, format_number
from config import JACKPOT_CONTRIBUTION


async def handle_text_bet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data = db.get_user(user_id)
    text = update.message.text.strip()
    
    game_state = context.user_data.get('game_state', {})
    
    if not game_state:
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
                f"💰 You have: {format_number(user_data['balance'])}"
            )
            return
        
        if game_type == 'roulette':
            await handle_roulette_bet(update, user_id, user_data, game_state, amount)
        elif game_type == 'basketball':
            await handle_basketball_bet(update, user_id, user_data, game_state, amount)
        elif game_type == 'soccer':
            await handle_soccer_bet(update, user_id, user_data, game_state, amount)
        elif game_type == 'bowling':
            await handle_bowling_bet(update, context, user_id, user_data, game_state, amount)
        elif game_type == 'dice':
            await handle_dice_bet(update, user_id, user_data, game_state, amount)
        elif game_type == 'coinflip':
            await handle_coinflip_bet(update, user_id, user_data, game_state, amount)
        
        context.user_data['game_state'] = {}
        
    except ValueError:
        await update.message.reply_text("❌ Please enter a valid number.")


async def handle_roulette_bet(update, user_id, user_data, game_state, amount):
    bet_type = game_state['bet_type']
    
    await update.message.reply_text("🎰 Spinning the wheel...")
    await asyncio.sleep(2)
    
    result = RouletteGame.spin()
    color = RouletteGame.get_color(result)
    payout = RouletteGame.calculate_payout(bet_type, None, result, amount)
    
    if payout > 0:
        user_data['balance'] += payout
        user_data['total_won'] += payout
        user_data['win_streak'] += 1
        if user_data['win_streak'] > user_data['max_win_streak']:
            user_data['max_win_streak'] = user_data['win_streak']
        db.global_stats['total_won'] += payout
        msg = (
            f"🎰 Wheel lands on {color} <b>{result}</b>!\n\n"
            f"🎉 YOU WIN ${payout:.2f}!\n"
            f"💳 Balance: {format_number(user_data['balance'])}"
        )
    else:
        user_data['balance'] -= amount
        user_data['win_streak'] = 0
        msg = (
            f"🎰 Wheel lands on {color} <b>{result}</b>!\n\n"
            f"😔 You lose ${amount:.2f}\n"
            f"💳 Balance: {format_number(user_data['balance'])}"
        )
    
    user_data['total_wagered'] += amount
    user_data['games_played'] += 1
    db.global_stats['total_bets'] += 1
    db.global_stats['total_wagered'] += amount
    
    db.add_xp(user_id, get_xp_for_bet(amount))
    
    unlocked = check_achievements(user_id)
    if unlocked:
        for ach_id, reward in unlocked:
            msg += f"\n\n🏆 Achievement unlocked!\n+${reward}"
    
    await update.message.reply_text(msg, parse_mode='HTML')


async def handle_basketball_bet(update, user_id, user_data, game_state, amount):
    prediction = game_state['prediction']
    
    await update.message.reply_text("🏀 Taking the shot...")
    await asyncio.sleep(2)
    
    result = BasketballGame.shoot()
    payout = BasketballGame.calculate_payout(prediction, result, amount)
    
    result_emoji = "🏀 SCORES!" if result else "❌ MISS!"
    
    if payout > 0:
        user_data['balance'] += payout
        user_data['total_won'] += payout
        user_data['win_streak'] += 1
        if user_data['win_streak'] > user_data['max_win_streak']:
            user_data['max_win_streak'] = user_data['win_streak']
        db.global_stats['total_won'] += payout
        msg = (
            f"🏀 Shot result: {result_emoji}\n\n"
            f"🎉 YOU WIN ${payout:.2f}!\n"
            f"💳 Balance: {format_number(user_data['balance'])}"
        )
    else:
        user_data['balance'] -= amount
        user_data['win_streak'] = 0
        msg = (
            f"🏀 Shot result: {result_emoji}\n\n"
            f"😔 You lose ${amount:.2f}\n"
            f"💳 Balance: {format_number(user_data['balance'])}"
        )
    
    user_data['total_wagered'] += amount
    user_data['games_played'] += 1
    db.global_stats['total_bets'] += 1
    db.global_stats['total_wagered'] += amount
    
    db.add_xp(user_id, get_xp_for_bet(amount))
    
    unlocked = check_achievements(user_id)
    if unlocked:
        for ach_id, reward in unlocked:
            msg += f"\n\n🏆 Achievement unlocked!\n+${reward}"
    
    await update.message.reply_text(msg, parse_mode='HTML')


async def handle_soccer_bet(update, user_id, user_data, game_state, amount):
    prediction = game_state['prediction']
    
    await update.message.reply_text("⚽ Taking the penalty kick...")
    await asyncio.sleep(2)
    
    result = SoccerGame.kick()
    payout = SoccerGame.calculate_payout(prediction, result, amount)
    
    result_emoji = "⚽ GOAL!" if result else "🧤 SAVED!"
    
    if payout > 0:
        user_data['balance'] += payout
        user_data['total_won'] += payout
        user_data['win_streak'] += 1
        if user_data['win_streak'] > user_data['max_win_streak']:
            user_data['max_win_streak'] = user_data['win_streak']
        db.global_stats['total_won'] += payout
        msg = (
            f"⚽ Kick result: {result_emoji}\n\n"
            f"🎉 YOU WIN ${payout:.2f}!\n"
            f"💳 Balance: {format_number(user_data['balance'])}"
        )
    else:
        user_data['balance'] -= amount
        user_data['win_streak'] = 0
        msg = (
            f"⚽ Kick result: {result_emoji}\n\n"
            f"😔 You lose ${amount:.2f}\n"
            f"💳 Balance: {format_number(user_data['balance'])}"
        )
    
    user_data['total_wagered'] += amount
    user_data['games_played'] += 1
    db.global_stats['total_bets'] += 1
    db.global_stats['total_wagered'] += amount
    
    db.add_xp(user_id, get_xp_for_bet(amount))
    
    unlocked = check_achievements(user_id)
    if unlocked:
        for ach_id, reward in unlocked:
            msg += f"\n\n🏆 Achievement unlocked!\n+${reward}"
    
    await update.message.reply_text(msg, parse_mode='HTML')


async def handle_bowling_bet(update, context, user_id, user_data, game_state, amount):
    prediction = game_state['prediction']
    
    await update.message.reply_text("🎳 Rolling the ball...")
    await asyncio.sleep(2)
    
    result = BowlingGame.roll()
    payout = BowlingGame.calculate_payout(prediction, result, amount)
    
    result_emojis = {
        'strike': '🎳 STRIKE!',
        'spare': '📍 Spare!',
        'miss': '❌ Miss!'
    }
    result_text = result_emojis[result]
    
    if payout > 0:
        user_data['balance'] += payout
        user_data['total_won'] += payout
        user_data['win_streak'] += 1
        if user_data['win_streak'] > user_data['max_win_streak']:
            user_data['max_win_streak'] = user_data['win_streak']
        db.global_stats['total_won'] += payout
        
        jackpot_msg = ""
        if result == 'strike' and prediction == 'strike':
            strikes = context.user_data.get('strike_count', 0) + 1
            context.user_data['strike_count'] = strikes
            
            if strikes >= 3:
                jackpot_win = db.jackpot_pool
                user_data['balance'] += jackpot_win
                jackpot_msg = f"\n\n🏆💰 JACKPOT! You win ${jackpot_win:.2f}! 💰🏆"
                db.jackpot_pool = 5000.0
                context.user_data['strike_count'] = 0
                
                if db.add_achievement(user_id, 'jackpot_winner'):
                    from config import ACHIEVEMENTS
                    reward = ACHIEVEMENTS['jackpot_winner']['reward']
                    user_data['balance'] += reward
                    jackpot_msg += f"\n🏆 Achievement: Jackpot Winner! +${reward}"
        else:
            context.user_data['strike_count'] = 0
        
        msg = (
            f"🎳 Roll result: {result_text}\n\n"
            f"🎉 YOU WIN ${payout:.2f}!{jackpot_msg}\n"
            f"💳 Balance: {format_number(user_data['balance'])}"
        )
    else:
        user_data['balance'] -= amount
        user_data['win_streak'] = 0
        context.user_data['strike_count'] = 0
        msg = (
            f"🎳 Roll result: {result_text}\n\n"
            f"😔 You lose ${amount:.2f}\n"
            f"💳 Balance: {format_number(user_data['balance'])}"
        )
    
    user_data['total_wagered'] += amount
    user_data['games_played'] += 1
    db.global_stats['total_bets'] += 1
    db.global_stats['total_wagered'] += amount
    db.jackpot_pool += amount * JACKPOT_CONTRIBUTION
    
    db.add_xp(user_id, get_xp_for_bet(amount))
    
    unlocked = check_achievements(user_id)
    if unlocked:
        for ach_id, reward in unlocked:
            msg += f"\n\n🏆 Achievement unlocked!\n+${reward}"
    
    await update.message.reply_text(msg, parse_mode='HTML')


async def handle_dice_bet(update, user_id, user_data, game_state, amount):
    prediction = game_state['prediction']
    
    await update.message.reply_text("🎲 Rolling the dice...")
    await asyncio.sleep(2)
    
    result = DiceGame.roll()
    payout = 0.0
    
    if prediction == "high" and result >= 4:
        payout = amount * 1.5
    elif prediction == "low" and result <= 3:
        payout = amount * 1.5
    elif prediction == "even" and result % 2 == 0:
        payout = amount
    elif prediction == "odd" and result % 2 == 1:
        payout = amount
    
    if payout > 0:
        user_data['balance'] += payout
        user_data['total_won'] += payout
        user_data['win_streak'] += 1
        if user_data['win_streak'] > user_data['max_win_streak']:
            user_data['max_win_streak'] = user_data['win_streak']
        db.global_stats['total_won'] += payout
        msg = (
            f"🎲 Dice result: <b>{result}</b>\n\n"
            f"🎉 YOU WIN ${payout:.2f}!\n"
            f"💳 Balance: {format_number(user_data['balance'])}"
        )
    else:
        user_data['balance'] -= amount
        user_data['win_streak'] = 0
        msg = (
            f"🎲 Dice result: <b>{result}</b>\n\n"
            f"😔 You lose ${amount:.2f}\n"
            f"💳 Balance: {format_number(user_data['balance'])}"
        )
    
    user_data['total_wagered'] += amount
    user_data['games_played'] += 1
    db.global_stats['total_bets'] += 1
    db.global_stats['total_wagered'] += amount
    
    db.add_xp(user_id, get_xp_for_bet(amount))
    
    unlocked = check_achievements(user_id)
    if unlocked:
        for ach_id, reward in unlocked:
            msg += f"\n\n🏆 Achievement unlocked!\n+${reward}"
    
    await update.message.reply_text(msg, parse_mode='HTML')


async def handle_coinflip_bet(update, user_id, user_data, game_state, amount):
    prediction = game_state['prediction']
    
    await update.message.reply_text("🪙 Flipping the coin...")
    await asyncio.sleep(2)
    
    result = CoinFlipGame.flip()
    payout = CoinFlipGame.calculate_payout(prediction, result, amount)
    
    result_emoji = "🪙 HEADS" if result == "heads" else "🪙 TAILS"
    
    if payout > 0:
        user_data['balance'] += payout
        user_data['total_won'] += payout
        user_data['win_streak'] += 1
        if user_data['win_streak'] > user_data['max_win_streak']:
            user_data['max_win_streak'] = user_data['win_streak']
        db.global_stats['total_won'] += payout
        msg = (
            f"🪙 Coin flip result: {result_emoji}\n\n"
            f"🎉 YOU WIN ${payout:.2f}!\n"
            f"💳 Balance: {format_number(user_data['balance'])}"
        )
    else:
        user_data['balance'] -= amount
        user_data['win_streak'] = 0
        msg = (
            f"🪙 Coin flip result: {result_emoji}\n\n"
            f"😔 You lose ${amount:.2f}\n"
            f"💳 Balance: {format_number(user_data['balance'])}"
        )
    
    user_data['total_wagered'] += amount
    user_data['games_played'] += 1
    db.global_stats['total_bets'] += 1
    db.global_stats['total_wagered'] += amount
    
    db.add_xp(user_id, get_xp_for_bet(amount))
    
    unlocked = check_achievements(user_id)
    if unlocked:
        for ach_id, reward in unlocked:
            msg += f"\n\n🏆 Achievement unlocked!\n+${reward}"
    
    await update.message.reply_text(msg, parse_mode='HTML')
