import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from database import db
from games import (
    RouletteGame, BlackjackGame, BasketballGame, SoccerGame,
    BowlingGame, CrashGame, DiceGame, CoinFlipGame
)
from utils import check_achievements, get_xp_for_bet, format_number
from config import JACKPOT_CONTRIBUTION


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_data = db.get_user(user_id)
    data = query.data
    
    if 'game_state' not in context.user_data:
        context.user_data['game_state'] = {}
    
    if data.startswith("roulette_"):
        bet_type = data.split("_")[1]
        context.user_data['game_state'] = {'type': 'roulette', 'bet_type': bet_type}
        await query.edit_message_text(
            f"🎰 Roulette - {bet_type.upper()} selected\n\n"
            f"Now enter your bet amount (e.g., 10)"
        )
    
    elif data.startswith("basketball_"):
        prediction = data.split("_")[1]
        context.user_data['game_state'] = {'type': 'basketball', 'prediction': prediction}
        await query.edit_message_text(
            f"🏀 Free Throw - {prediction.upper()} selected\n\n"
            f"Now enter your bet amount (e.g., 20)"
        )
    
    elif data.startswith("soccer_"):
        prediction = data.split("_")[1]
        context.user_data['game_state'] = {'type': 'soccer', 'prediction': prediction}
        await query.edit_message_text(
            f"⚽ Penalty - {prediction.upper()} selected\n\n"
            f"Now enter your bet amount (e.g., 15)"
        )
    
    elif data.startswith("bowling_"):
        prediction = data.split("_")[1]
        context.user_data['game_state'] = {'type': 'bowling', 'prediction': prediction}
        await query.edit_message_text(
            f"🎳 Bowling - {prediction.upper()} selected\n\n"
            f"Now enter your bet amount (e.g., 25)"
        )
    
    elif data.startswith("dice_"):
        prediction = data.split("_")[1]
        context.user_data['game_state'] = {'type': 'dice', 'prediction': prediction}
        await query.edit_message_text(
            f"🎲 Dice - {prediction.upper()} selected\n\n"
            f"Now enter your bet amount (e.g., 15)"
        )
    
    elif data.startswith("coinflip_"):
        prediction = data.split("_")[1]
        context.user_data['game_state'] = {'type': 'coinflip', 'prediction': prediction}
        await query.edit_message_text(
            f"🪙 Coin Flip - {prediction.upper()} selected\n\n"
            f"Now enter your bet amount (e.g., 20)"
        )
    
    elif data.startswith("crash_"):
        amount = int(data.split("_")[1])
        
        if user_data['balance'] < amount:
            await query.edit_message_text(
                f"❌ Insufficient balance.\n"
                f"💰 You have: {format_number(user_data['balance'])}"
            )
            return
        
        keyboard = [
            [InlineKeyboardButton("1.5x", callback_data=f"crash_cashout_{amount}_1.5"),
             InlineKeyboardButton("2x", callback_data=f"crash_cashout_{amount}_2"),
             InlineKeyboardButton("5x", callback_data=f"crash_cashout_{amount}_5")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"🚀 Crash - Bet: ${amount}\n\n"
            f"Select your cashout multiplier:",
            reply_markup=reply_markup
        )
    
    elif data.startswith("crash_cashout_"):
        parts = data.split("_")
        amount = int(parts[2])
        cashout_multiplier = float(parts[3])
        
        await query.edit_message_text("🚀 Launching...")
        await asyncio.sleep(2)
        
        actual_multiplier = CrashGame.generate_multiplier()
        success, payout_multiplier = CrashGame.did_crash(actual_multiplier, cashout_multiplier)
        
        if success:
            winnings = amount * (cashout_multiplier - 1)
            user_data['balance'] += winnings
            user_data['total_won'] += winnings
            user_data['win_streak'] += 1
            if user_data['win_streak'] > user_data['max_win_streak']:
                user_data['max_win_streak'] = user_data['win_streak']
            msg = (
                f"🚀 Multiplier reached: {actual_multiplier}x\n"
                f"💰 Cashed out at: {cashout_multiplier}x\n\n"
                f"🎉 YOU WIN ${winnings:.2f}!\n"
                f"💳 Balance: {format_number(user_data['balance'])}"
            )
        else:
            user_data['balance'] -= amount
            user_data['win_streak'] = 0
            msg = (
                f"💥 CRASHED at {actual_multiplier}x!\n"
                f"Target was: {cashout_multiplier}x\n\n"
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
        
        await query.edit_message_text(msg)
    
    elif data.startswith("blackjack_"):
        await handle_blackjack_callback(query, context, data, user_id, user_data)


async def handle_blackjack_callback(query, context, data, user_id, user_data):
    if data == "blackjack_hit":
        game_state = context.user_data.get('blackjack_hand', {})
        if not game_state:
            await query.edit_message_text("❌ No active game. Start with /blackjack")
            return
        
        player_cards = game_state['player_cards']
        new_card = BlackjackGame.deal_card()
        player_cards.append(new_card)
        
        player_value = BlackjackGame.calculate_hand_value(player_cards)
        dealer_cards = game_state['dealer_cards']
        bet_amount = game_state['bet']
        
        if player_value > 21:
            user_data['balance'] -= bet_amount
            user_data['total_wagered'] += bet_amount
            user_data['games_played'] += 1
            user_data['win_streak'] = 0
            db.global_stats['total_bets'] += 1
            db.global_stats['total_wagered'] += bet_amount
            
            msg = (
                f"🃏 <b>BLACKJACK - BUST</b>\n\n"
                f"Your cards: {' '.join(player_cards)} = {player_value}\n"
                f"Dealer: {' '.join(dealer_cards)}\n\n"
                f"💥 BUST! You lose ${bet_amount:.2f}\n"
                f"💳 Balance: {format_number(user_data['balance'])}"
            )
            await query.edit_message_text(msg, parse_mode='HTML')
            del context.user_data['blackjack_hand']
        else:
            keyboard = [
                [InlineKeyboardButton("🎴 Hit", callback_data="blackjack_hit"),
                 InlineKeyboardButton("✋ Stand", callback_data="blackjack_stand")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            msg = (
                f"🃏 <b>BLACKJACK</b>\n\n"
                f"Your cards: {' '.join(player_cards)} = {player_value}\n"
                f"Dealer: {dealer_cards[0]} ?\n\n"
                f"What's your move?"
            )
            await query.edit_message_text(msg, reply_markup=reply_markup, parse_mode='HTML')
            game_state['player_cards'] = player_cards
            context.user_data['blackjack_hand'] = game_state
    
    elif data == "blackjack_stand":
        game_state = context.user_data.get('blackjack_hand', {})
        if not game_state:
            await query.edit_message_text("❌ No active game. Start with /blackjack")
            return
        
        player_cards = game_state['player_cards']
        dealer_cards = game_state['dealer_cards']
        bet_amount = game_state['bet']
        
        while BlackjackGame.calculate_hand_value(dealer_cards) < 17:
            dealer_cards.append(BlackjackGame.deal_card())
        
        player_value = BlackjackGame.calculate_hand_value(player_cards)
        dealer_value = BlackjackGame.calculate_hand_value(dealer_cards)
        
        if dealer_value > 21:
            winnings = bet_amount
            user_data['balance'] += winnings
            user_data['total_won'] += winnings
            user_data['win_streak'] += 1
            if user_data['win_streak'] > user_data['max_win_streak']:
                user_data['max_win_streak'] = user_data['win_streak']
            db.global_stats['total_won'] += winnings
            result = f"🎉 Dealer BUST! You win ${winnings:.2f}!"
        elif player_value > dealer_value:
            winnings = bet_amount
            user_data['balance'] += winnings
            user_data['total_won'] += winnings
            user_data['win_streak'] += 1
            if user_data['win_streak'] > user_data['max_win_streak']:
                user_data['max_win_streak'] = user_data['win_streak']
            db.global_stats['total_won'] += winnings
            result = f"🎉 You WIN! +${winnings:.2f}"
        elif player_value == dealer_value:
            result = "🤝 PUSH! Bet returned."
        else:
            user_data['balance'] -= bet_amount
            user_data['win_streak'] = 0
            result = f"😔 Dealer wins. -${bet_amount:.2f}"
        
        user_data['total_wagered'] += bet_amount
        user_data['games_played'] += 1
        db.global_stats['total_bets'] += 1
        db.global_stats['total_wagered'] += bet_amount
        
        db.add_xp(user_id, get_xp_for_bet(bet_amount))
        
        msg = (
            f"🃏 <b>BLACKJACK - FINAL</b>\n\n"
            f"Your cards: {' '.join(player_cards)} = {player_value}\n"
            f"Dealer: {' '.join(dealer_cards)} = {dealer_value}\n\n"
            f"{result}\n"
            f"💳 Balance: {format_number(user_data['balance'])}"
        )
        
        unlocked = check_achievements(user_id)
        if unlocked:
            for ach_id, reward in unlocked:
                msg += f"\n\n🏆 Achievement unlocked!\n+${reward}"
        
        await query.edit_message_text(msg, parse_mode='HTML')
        del context.user_data['blackjack_hand']
    
    else:
        amount = int(data.split("_")[1])
        
        if user_data['balance'] < amount:
            await query.edit_message_text(
                f"❌ Insufficient balance.\n"
                f"💰 You have: {format_number(user_data['balance'])}"
            )
            return
        
        player_cards = [BlackjackGame.deal_card(), BlackjackGame.deal_card()]
        dealer_cards = [BlackjackGame.deal_card(), BlackjackGame.deal_card()]
        
        player_value = BlackjackGame.calculate_hand_value(player_cards)
        
        if BlackjackGame.is_blackjack(player_cards):
            if BlackjackGame.is_blackjack(dealer_cards):
                msg = (
                    f"🃏 <b>BLACKJACK</b>\n\n"
                    f"Your cards: {' '.join(player_cards)} = BLACKJACK!\n"
                    f"Dealer: {' '.join(dealer_cards)} = BLACKJACK!\n\n"
                    f"🤝 PUSH! Both have blackjack.\n"
                    f"💳 Balance: {format_number(user_data['balance'])}"
                )
            else:
                winnings = amount * 1.5
                user_data['balance'] += winnings
                user_data['total_won'] += winnings
                user_data['win_streak'] += 1
                msg = (
                    f"🃏 <b>BLACKJACK</b>\n\n"
                    f"Your cards: {' '.join(player_cards)} = BLACKJACK!\n"
                    f"Dealer: {' '.join(dealer_cards)}\n\n"
                    f"🎰 BLACKJACK! You win ${winnings:.2f}!\n"
                    f"💳 Balance: {format_number(user_data['balance'])}"
                )
            user_data['games_played'] += 1
            db.add_xp(user_id, get_xp_for_bet(amount))
            await query.edit_message_text(msg, parse_mode='HTML')
            return
        
        elif BlackjackGame.is_blackjack(dealer_cards):
            user_data['balance'] -= amount
            user_data['total_wagered'] += amount
            user_data['games_played'] += 1
            user_data['win_streak'] = 0
            msg = (
                f"🃏 <b>BLACKJACK</b>\n\n"
                f"Your cards: {' '.join(player_cards)} = {player_value}\n"
                f"Dealer: {' '.join(dealer_cards)} = BLACKJACK!\n\n"
                f"😔 Dealer has blackjack. You lose ${amount:.2f}\n"
                f"💳 Balance: {format_number(user_data['balance'])}"
            )
            await query.edit_message_text(msg, parse_mode='HTML')
            return
        
        keyboard = [
            [InlineKeyboardButton("🎴 Hit", callback_data="blackjack_hit"),
             InlineKeyboardButton("✋ Stand", callback_data="blackjack_stand")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        msg = (
            f"🃏 <b>BLACKJACK</b>\n\n"
            f"💰 Bet: ${amount}\n\n"
            f"Your cards: {' '.join(player_cards)} = {player_value}\n"
            f"Dealer: {dealer_cards[0]} ?\n\n"
            f"What's your move?"
        )
        
        context.user_data['blackjack_hand'] = {
            'player_cards': player_cards,
            'dealer_cards': dealer_cards,
            'bet': amount
        }
        
        await query.edit_message_text(msg, reply_markup=reply_markup, parse_mode='HTML')
