import asyncio
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from database import db
from games import DiceGame
from utils import format_number


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all inline keyboard callbacks"""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    data = query.data

    # Balance action buttons
    if data == "action_deposit":
        msg = (
            "💳 <b>Deposit Instructions</b>\n\n"
            "Use the /deposit command to see your\n"
            "unique LTC deposit address."
        )
        await query.edit_message_text(msg, parse_mode='HTML')
        return

    if data == "action_withdraw":
        msg = (
            "💸 <b>Withdrawal Instructions</b>\n\n"
            "Use: /withdraw [amount]\n\n"
            "Example: /withdraw 50\n\n"
            "Note: You must complete playthrough\n"
            "requirements before withdrawing."
        )
        await query.edit_message_text(msg, parse_mode='HTML')
        return

    if data == "action_full_stats":
        user_data = db.get_user(user_id)
        rtp = 0.0
        if user_data['total_wagered'] > 0:
            rtp = (user_data['total_won'] / user_data['total_wagered']) * 100

        playthrough_remaining = max(0, user_data.get('playthrough_required', 0) - user_data.get('bonus_wagered', 0))

        msg = (
            f"📊 <b>Full Statistics</b>\n\n"
            f"💰 Balance: ${format_number(user_data['balance'])}\n"
            f"🎮 Games played: {user_data['games_played']}\n"
            f"💸 Total wagered: ${format_number(user_data['total_wagered'])}\n"
            f"🏆 Total won: ${format_number(user_data['total_won'])}\n"
            f"📊 RTP: {rtp:.1f}%\n"
            f"🔥 Win streak: {user_data['win_streak']}\n"
            f"📈 Best streak: {user_data['max_win_streak']}\n\n"
        )

        if playthrough_remaining > 0:
            msg += f"🎁 Playthrough remaining: ${playthrough_remaining:.2f}\n\n"

        msg += "Use /profile for more details"

        await query.edit_message_text(msg, parse_mode='HTML')
        return

    # Dice game mode selection
    if data == "dice_mode_bot":
        keyboard = [
            [InlineKeyboardButton(f"🎲 {i}", callback_data=f"dice_select_num_{i}") for i in range(1, 4)],
            [InlineKeyboardButton(f"🎲 {i}", callback_data=f"dice_select_num_{i}") for i in range(4, 7)],
            [InlineKeyboardButton("« Back", callback_data="dice_back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        msg = (
            "🎲 <b>Select Your Number</b>\n\n"
            "Pick a number from 1 to 6\n"
            "Win 5x your bet if you match!\n\n"
            "Next: Enter bet amount"
        )

        await query.edit_message_text(msg, parse_mode='HTML', reply_markup=reply_markup)
        return

    if data.startswith("dice_select_num_"):
        number = int(data.split("_")[-1])

        # Store selected number in user context
        context.user_data['dice_selected_number'] = number

        keyboard = [
            [InlineKeyboardButton("$5", callback_data=f"dice_bet_5")],
            [InlineKeyboardButton("$10", callback_data=f"dice_bet_10")],
            [InlineKeyboardButton("$25", callback_data=f"dice_bet_25")],
            [InlineKeyboardButton("$50", callback_data=f"dice_bet_50")],
            [InlineKeyboardButton("$100", callback_data=f"dice_bet_100")],
            [InlineKeyboardButton("« Back", callback_data="dice_mode_bot")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        msg = (
            f"🎲 <b>Number Selected: {number}</b>\n\n"
            f"Now choose your bet amount:\n\n"
            f"💡 Win 5x if you match the roll!"
        )

        await query.edit_message_text(msg, parse_mode='HTML', reply_markup=reply_markup)
        return

    if data.startswith("dice_bet_"):
        amount = float(data.split("_")[-1])
        number = context.user_data.get('dice_selected_number')

        if not number:
            await query.edit_message_text("❌ Error: Please select a number first.")
            return

        user_data = db.get_user(user_id)

        if amount > user_data['balance']:
            await query.edit_message_text(
                f"❌ Insufficient balance.\n💰 Available: ${format_number(user_data['balance'])}"
            )
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

        # Show rolling animation
        await query.edit_message_text("🎲 Rolling the dice...")

        # Animation
        for i in range(5):
            await asyncio.sleep(0.3)
            import random
            random_num = random.randint(1, 6)
            await query.edit_message_text(f"🎲 Rolling... {DiceGame.get_dice_emoji(random_num)}")

        # Final result
        result = DiceGame.roll()
        result_emoji = DiceGame.get_dice_emoji(result)

        await asyncio.sleep(0.5)

        # Calculate win
        payout = DiceGame.calculate_payout(number, result, amount)
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
                f"🎯 You predicted: {number}\n\n"
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
                f"🎯 You predicted: {number}\n\n"
                f"💰 Bet: ${amount:.2f}\n"
                f"💳 Balance: ${format_number(user_data['balance'])}"
            )

        keyboard = [
            [InlineKeyboardButton("🔄 Play Again", callback_data="dice_mode_bot")],
            [InlineKeyboardButton("💰 Balance", callback_data="action_full_stats")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(result_msg, parse_mode='HTML', reply_markup=reply_markup)
        return

    # Dice PvP challenge handling
    if data == "dice_mode_pvp":
        msg = (
            "👤 <b>Challenge a Player</b>\n\n"
            "Use command:\n"
            "/dice_challenge @username [amount] [number]\n\n"
            "Example:\n"
            "/dice_challenge @friend 20 4\n\n"
            "The first player to match the roll wins!"
        )
        await query.edit_message_text(msg, parse_mode='HTML')
        return

    if data == "dice_view_challenges":
        if not hasattr(db, 'dice_challenges') or not db.dice_challenges:
            await query.edit_message_text(
                "📋 No active challenges.\n\n"
                "Use /dice_challenge to create one!"
            )
            return

        msg = "📋 <b>Active Challenges</b>\n\n"

        user_challenges = [
            (cid, c) for cid, c in db.dice_challenges.items()
            if c['challenger_id'] == user_id or c['target_id'] == user_id
        ]

        if not user_challenges:
            msg += "You have no active challenges."
        else:
            for cid, challenge in user_challenges:
                if challenge['challenger_id'] == user_id:
                    msg += f"⚔️ Challenging @{challenge['target_username']}\n"
                else:
                    msg += f"⚔️ From @{challenge['challenger_username']}\n"
                msg += f"💰 ${challenge['amount']:.2f}\n"
                msg += f"Status: {challenge['status']}\n\n"

        await query.edit_message_text(msg, parse_mode='HTML')
        return

    if data.startswith("dice_accept_"):
        challenge_id = data.replace("dice_accept_", "")

        if not hasattr(db, 'dice_challenges') or challenge_id not in db.dice_challenges:
            await query.edit_message_text("❌ Challenge not found or expired.")
            return

        challenge = db.dice_challenges[challenge_id]

        if challenge['target_id'] != user_id:
            await query.edit_message_text("❌ This challenge is not for you.")
            return

        amount = challenge['amount']
        user_data = db.get_user(user_id)

        if amount > user_data['balance']:
            await query.edit_message_text(
                f"❌ Insufficient balance.\n💰 Need: ${amount:.2f}\n💳 Have: ${format_number(user_data['balance'])}"
            )
            return

        # Deduct target's bet
        user_data['balance'] -= amount

        # Ask target to pick a number
        keyboard = [
            [InlineKeyboardButton(f"🎲 {i}", callback_data=f"dice_pvp_num_{challenge_id}_{i}") for i in range(1, 4)],
            [InlineKeyboardButton(f"🎲 {i}", callback_data=f"dice_pvp_num_{challenge_id}_{i}") for i in range(4, 7)]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        msg = "🎲 <b>Pick Your Number</b>\n\nSelect a number from 1 to 6:"

        await query.edit_message_text(msg, parse_mode='HTML', reply_markup=reply_markup)
        return

    if data.startswith("dice_pvp_num_"):
        parts = data.split("_")
        challenge_id = "_".join(parts[3:-1])
        target_number = int(parts[-1])

        if challenge_id not in db.dice_challenges:
            await query.edit_message_text("❌ Challenge expired.")
            return

        challenge = db.dice_challenges[challenge_id]

        # Execute the PvP match
        await execute_pvp_dice_match(query, context, challenge_id, target_number)
        return

    if data.startswith("dice_decline_"):
        challenge_id = data.replace("dice_decline_", "")

        if not hasattr(db, 'dice_challenges') or challenge_id not in db.dice_challenges:
            await query.edit_message_text("❌ Challenge not found.")
            return

        challenge = db.dice_challenges[challenge_id]

        # Refund challenger
        challenger_data = db.get_user(challenge['challenger_id'])
        challenger_data['balance'] += challenge['amount']

        # Notify challenger
        try:
            await context.bot.send_message(
                chat_id=challenge['challenger_id'],
                text=f"❌ @{challenge['target_username']} declined your challenge.\nYour ${challenge['amount']:.2f} has been refunded."
            )
        except:
            pass

        await query.edit_message_text("❌ Challenge declined.")

        del db.dice_challenges[challenge_id]
        return


async def execute_pvp_dice_match(query, context, challenge_id, target_number):
    """Execute a PvP dice match"""
    challenge = db.dice_challenges[challenge_id]

    challenger_id = challenge['challenger_id']
    target_id = challenge['target_id']
    amount = challenge['amount']
    challenger_number = challenge['challenger_number']

    # Animated roll
    await query.edit_message_text("🎲 Rolling the dice...")

    for i in range(5):
        await asyncio.sleep(0.3)
        import random
        random_num = random.randint(1, 6)
        await query.edit_message_text(f"🎲 Rolling... {DiceGame.get_dice_emoji(random_num)}")

    # Final result
    result = DiceGame.roll()
    result_emoji = DiceGame.get_dice_emoji(result)

    await asyncio.sleep(0.5)

    # Determine winner
    challenger_data = db.get_user(challenger_id)
    target_data = db.get_user(target_id)

    challenger_won = challenger_number == result
    target_won = target_number == result

    if challenger_won and not target_won:
        # Challenger wins
        challenger_data['balance'] += amount * 2
        winner_msg = f"🎉 @{challenge['challenger_username']} WINS!"
        challenger_result = "🎉 YOU WIN!"
        target_result = "❌ You lost!"
    elif target_won and not challenger_won:
        # Target wins
        target_data['balance'] += amount * 2
        winner_msg = f"🎉 @{challenge['target_username']} WINS!"
        challenger_result = "❌ You lost!"
        target_result = "🎉 YOU WIN!"
    else:
        # Draw - refund both
        challenger_data['balance'] += amount
        target_data['balance'] += amount
        winner_msg = "🤝 IT'S A DRAW!"
        challenger_result = "🤝 Draw - bet refunded"
        target_result = "🤝 Draw - bet refunded"

    # Results message
    result_msg = (
        f"🎲 <b>PVP DICE RESULT</b>\n\n"
        f"🎲 Roll: {result_emoji} ({result})\n\n"
        f"🎯 @{challenge['challenger_username']}: {challenger_number}\n"
        f"🎯 @{challenge['target_username']}: {target_number}\n\n"
        f"{winner_msg}\n"
        f"💰 Prize: ${amount * 2:.2f}"
    )

    # Send to target (current user)
    await query.edit_message_text(
        result_msg + f"\n\n{target_result}",
        parse_mode='HTML'
    )

    # Send to challenger
    try:
        await context.bot.send_message(
            chat_id=challenger_id,
            text=result_msg + f"\n\n{challenger_result}",
            parse_mode='HTML'
        )
    except:
        pass

    # Remove challenge
    del db.dice_challenges[challenge_id]