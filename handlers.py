import asyncio
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from database import db
from games import DiceGame
from utils import format_number


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start and /help commands"""
    user = update.effective_user
    user_data = db.get_user(user.id)
    user_data['username'] = user.username or user.first_name
    
    if not user_data.get('first_bonus_claimed', False):
        user_data['balance'] += 5.0
        user_data['playthrough_required'] = 5.0
        user_data['bonus_wagered'] = 0
        user_data['first_bonus_claimed'] = True
        
        welcome_msg = (
            f"🎰 <b>Welcome to Antaria Casino, {user.first_name}!</b> 🎰\n\n"
            "🎁 <b>First Time Bonus: $5.00!</b>\n"
            "⚠️ You must play through the full $5 before withdrawing.\n\n"
            "💰 <b>Getting Started:</b>\n"
            "• /balance - Check your balance\n"
            "• /bonus - Claim your earnings bonus\n\n"
            "🎮 <b>Available Games:</b>\n"
            "🎲 /dice - Dice game (PvP enabled)\n"
            "🪙 /coinflip - Coin flip game\n\n"
            "📊 <b>Other Commands:</b>\n"
            "👤 /profile - Your profile\n"
            "🏆 /achievements - Your achievements\n"
            "📊 /leaderboard - Top players\n\n"
            "Good luck! 🍀"
        )
    else:
        welcome_msg = (
            f"🎰 <b>Welcome back to Antaria Casino, {user.first_name}!</b> 🎰\n\n"
            "💰 <b>Quick Commands:</b>\n"
            "• /balance - Check your balance\n"
            "• /bonus - Claim your earnings bonus\n\n"
            "🎮 <b>Available Games:</b>\n"
            "🎲 /dice - Dice game (PvP enabled)\n"
            "🪙 /coinflip - Coin flip game\n\n"
            "Good luck! 🍀"
        )
    
    await update.message.reply_text(welcome_msg, parse_mode='HTML')


async def deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /deposit command"""
    user_id = update.effective_user.id
    user_data = db.get_user(user_id)
    
    address = user_data.get('ltc_address', f"LTC_{user_id}_DEMO")
    
    msg = (
        f"💳 <b>Deposit Litecoin</b>\n\n"
        f"Send LTC to this address:\n"
        f"<code>{address}</code>\n\n"
        f"📊 Current rate: $77.00 per LTC\n"
        f"💵 Fee: 1%\n\n"
        f"After sending, confirm with:\n"
        f"/confirm [transaction_id]\n\n"
        f"Example: /confirm abc123\n\n"
        f"⏱ Confirmation takes ~5 seconds (demo mode)."
    )
    
    await update.message.reply_text(msg, parse_mode='HTML')


async def confirm_deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /confirm [txid] command"""
    user_id = update.effective_user.id
    
    if not context.args:
        await update.message.reply_text(
            "❌ Please provide transaction ID:\n\n"
            "/confirm [txid]\n\n"
            "Example: /confirm abc123"
        )
        return
    
    txid = context.args[0]
    
    import random
    ltc_amount = random.uniform(0.1, 1.0)
    usd_amount = ltc_amount * 77.0
    fee = usd_amount * 0.01
    final_amount = usd_amount - fee
    
    await update.message.reply_text(
        f"⏳ Deposit pending confirmation...\n"
        f"Amount: ${usd_amount:.2f} ({ltc_amount:.3f} LTC)\n"
        f"Fee: ${fee:.2f}\n"
        f"You'll receive: ${final_amount:.2f}\n\n"
        f"Please wait ~5 seconds..."
    )
    
    await asyncio.sleep(5)
    
    user_data = db.get_user(user_id)
    user_data['balance'] += final_amount
    
    await context.bot.send_message(
        chat_id=user_id,
        text=(
            f"✅ <b>Deposit Confirmed!</b>\n\n"
            f"💰 Received: ${final_amount:.2f}\n"
            f"💳 Balance: ${format_number(user_data['balance'])}\n\n"
            f"Ready to play! Try /dice to start."
        ),
        parse_mode='HTML'
    )


async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /balance command"""
    user_id = update.effective_user.id
    user_data = db.get_user(user_id)
    
    keyboard = [
        [InlineKeyboardButton("💳 Deposit", callback_data="action_deposit"),
         InlineKeyboardButton("💸 Withdraw", callback_data="action_withdraw")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    msg = f"💰 ${format_number(user_data['balance'])}"
    
    await update.message.reply_text(msg, parse_mode='HTML', reply_markup=reply_markup)


async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /withdraw [amount] command"""
    user_id = update.effective_user.id
    user_data = db.get_user(user_id)
    
    if not context.args:
        await update.message.reply_text("❌ Usage: /withdraw [amount]\n\nExample: /withdraw 50")
        return
    
    try:
        amount = float(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Invalid amount. Use numbers only.")
        return
    
    if amount <= 0:
        await update.message.reply_text("❌ Amount must be greater than 0.")
        return
    
    playthrough_remaining = max(0, user_data.get('playthrough_required', 0) - user_data.get('bonus_wagered', 0))
    
    if playthrough_remaining > 0:
        await update.message.reply_text(
            f"❌ You must complete playthrough requirements first.\n\n"
            f"Remaining: ${playthrough_remaining:.2f}\n\n"
            f"Play more games to unlock withdrawals!"
        )
        return
    
    if amount > user_data['balance']:
        await update.message.reply_text(
            f"❌ Insufficient balance.\n💰 Available: ${format_number(user_data['balance'])}"
        )
        return
    
    fee = amount * 0.01
    final_usd = amount - fee
    ltc_amount = final_usd / 77.0
    
    user_data['balance'] -= amount
    
    user_data['wagered_since_withdrawal'] = 0
    user_data['last_withdrawal'] = datetime.now().isoformat()
    
    msg = (
        f"✅ <b>Withdrawal Processed</b>\n\n"
        f"💸 Amount: ${amount:.2f}\n"
        f"💵 Fee: ${fee:.2f}\n"
        f"💰 Sent: ~{ltc_amount:.4f} LTC\n"
        f"📍 To: {user_data.get('ltc_address', 'Your LTC Address')}\n\n"
        f"💳 Remaining balance: ${format_number(user_data['balance'])}\n\n"
        f"ℹ️ Your bonus tracker has been reset."
    )
    
    await update.message.reply_text(msg, parse_mode='HTML')


async def daily_bonus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /bonus command - 1% of total wagered since last withdrawal"""
    user_id = update.effective_user.id
    user_data = db.get_user(user_id)
    
    wagered_since_withdrawal = user_data.get('wagered_since_withdrawal', 0)
    
    if wagered_since_withdrawal == 0:
        await update.message.reply_text(
            "❌ No wagering activity since your last withdrawal.\n\n"
            "💡 Play some games to earn your bonus!"
        )
        return
    
    bonus_amount = wagered_since_withdrawal * 0.01
    
    if bonus_amount < 0.01:
        await update.message.reply_text(
            f"❌ Minimum bonus is $0.01\n\n"
            f"💸 Wagered: ${wagered_since_withdrawal:.2f}\n"
            f"📊 Your bonus: ${bonus_amount:.4f}\n\n"
            f"Keep playing to earn more!"
        )
        return
    
    user_data['balance'] += bonus_amount
    user_data['wagered_since_withdrawal'] = 0
    
    msg = (
        f"🎁 <b>Earnings Bonus Claimed!</b>\n\n"
        f"💸 Total wagered: ${wagered_since_withdrawal:.2f}\n"
        f"💰 Bonus (1%): ${bonus_amount:.2f}\n\n"
        f"💳 New balance: ${format_number(user_data['balance'])}\n\n"
        f"🎮 Keep playing to earn more bonuses!"
    )
    
    await update.message.reply_text(msg, parse_mode='HTML')


async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /profile command"""
    user_id = update.effective_user.id
    user = update.effective_user
    user_data = db.get_user(user_id)
    
    rtp = 0.0
    if user_data['total_wagered'] > 0:
        rtp = (user_data['total_won'] / user_data['total_wagered']) * 100
    
    playthrough_remaining = max(0, user_data.get('playthrough_required', 0) - user_data.get('bonus_wagered', 0))
    
    msg = (
        f"👤 <b>Profile: {user.first_name}</b>\n\n"
        f"💰 Balance: ${format_number(user_data['balance'])}\n"
        f"🎮 Games played: {user_data['games_played']}\n"
        f"💸 Total wagered: ${format_number(user_data['total_wagered'])}\n"
        f"🏆 Total won: ${format_number(user_data['total_won'])}\n"
        f"📊 RTP: {rtp:.1f}%\n"
        f"🔥 Win streak: {user_data.get('win_streak', 0)}\n"
        f"📈 Best streak: {user_data.get('max_win_streak', 0)}\n"
        f"🎁 Bonus streak: {user_data.get('bonus_streak', 0)} days\n"
    )
    
    if playthrough_remaining > 0:
        msg += f"\n🎁 Playthrough remaining: ${playthrough_remaining:.2f}\n"
    
    msg += "\nUse /achievements to see your achievements!"
    
    await update.message.reply_text(msg, parse_mode='HTML')


async def achievements_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /achievements command"""
    user_id = update.effective_user.id
    user_data = db.get_user(user_id)
    
    achievements = []
    
    if user_data['games_played'] >= 10:
        achievements.append("🎮 Beginner - Played 10 games")
    if user_data['games_played'] >= 100:
        achievements.append("🎯 Veteran - Played 100 games")
    if user_data['games_played'] >= 1000:
        achievements.append("⭐ Legend - Played 1000 games")
    
    if user_data.get('max_win_streak', 0) >= 3:
        achievements.append("🔥 Hot Streak - 3 wins in a row")
    if user_data.get('max_win_streak', 0) >= 5:
        achievements.append("💥 On Fire - 5 wins in a row")
    if user_data.get('max_win_streak', 0) >= 10:
        achievements.append("🌟 Unstoppable - 10 wins in a row")
    
    if user_data.get('bonus_streak', 0) >= 7:
        achievements.append("📅 Weekly Warrior - 7 day bonus streak")
    if user_data.get('bonus_streak', 0) >= 30:
        achievements.append("🗓️ Monthly Master - 30 day bonus streak")
    
    if user_data['balance'] >= 1000:
        achievements.append("💰 High Roller - $1,000+ balance")
    if user_data['balance'] >= 10000:
        achievements.append("💎 Whale - $10,000+ balance")
    
    msg = f"🏆 <b>Your Achievements</b>\n\n"
    
    if achievements:
        for achievement in achievements:
            msg += f"{achievement}\n"
        msg += f"\n✨ Total: {len(achievements)} achievements unlocked!"
    else:
        msg += "No achievements yet. Keep playing to unlock them!"
    
    await update.message.reply_text(msg, parse_mode='HTML')


async def referral_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /referral command"""
    user_id = update.effective_user.id
    user_data = db.get_user(user_id)
    
    referrals = user_data.get('referrals', 0)
    referral_earnings = user_data.get('referral_earnings', 0)
    
    bot_username = context.bot.username
    referral_link = f"https://t.me/{bot_username}?start=ref_{user_id}"
    
    msg = (
        f"👥 <b>Referral Program</b>\n\n"
        f"🎁 Earn 10% of your referrals' deposits!\n\n"
        f"📊 Your Stats:\n"
        f"• Referrals: {referrals}\n"
        f"• Earnings: ${format_number(referral_earnings)}\n\n"
        f"🔗 Your referral link:\n"
        f"<code>{referral_link}</code>\n\n"
        f"Share this link with friends to start earning!"
    )
    
    await update.message.reply_text(msg, parse_mode='HTML')


async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /leaderboard command"""
    
    all_users = [(uid, data) for uid, data in db.users.items()]
    all_users.sort(key=lambda x: x[1]['balance'], reverse=True)
    top_10 = all_users[:10]
    
    if not top_10:
        await update.message.reply_text("🏆 Leaderboard is empty. Be the first to play!")
        return
    
    msg = "🏆 <b>ANTARIA CASINO LEADERBOARD</b>\n\n"
    msg += "Top 10 Players:\n\n"
    
    medals = ["🥇", "🥈", "🥉"]
    
    for idx, (user_id, user_data) in enumerate(top_10, 1):
        medal = medals[idx-1] if idx <= 3 else f"{idx}."
        username = user_data.get('username', 'Anonymous')
        balance = user_data['balance']
        msg += f"{medal} @{username}: ${format_number(balance)}\n"
    
    msg += "\n💰 Keep playing to reach the top!"
    
    await update.message.reply_text(msg, parse_mode='HTML')


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stats command - Show global stats"""
    
    total_users = len(db.users)
    total_bets = db.global_stats.get('total_bets', 0)
    total_wagered = db.global_stats.get('total_wagered', 0)
    total_won = db.global_stats.get('total_won', 0)
    
    house_edge = 0.0
    if total_wagered > 0:
        house_edge = ((total_wagered - total_won) / total_wagered) * 100
    
    msg = (
        f"📊 <b>Global Casino Stats</b>\n\n"
        f"👥 Total players: {total_users}\n"
        f"🎰 Total bets: {total_bets}\n"
        f"💸 Total wagered: ${format_number(total_wagered)}\n"
        f"🏆 Total won: ${format_number(total_won)}\n"
        f"🏦 House edge: {house_edge:.1f}%\n\n"
        f"🎮 Join the action with /dice or /coinflip!"
    )
    
    await update.message.reply_text(msg, parse_mode='HTML')


async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /admin command - Admin panel (restricted)"""
    user_id = update.effective_user.id
    
    ADMIN_IDS = [123456789]
    
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ You don't have permission to use this command.")
        return
    
    total_users = len(db.users)
    total_balance = sum(u['balance'] for u in db.users.values())
    total_bets = db.global_stats.get('total_bets', 0)
    total_wagered = db.global_stats.get('total_wagered', 0)
    
    msg = (
        f"👑 <b>Admin Panel</b>\n\n"
        f"📊 System Stats:\n"
        f"• Total users: {total_users}\n"
        f"• Total balance in system: ${format_number(total_balance)}\n"
        f"• Total bets placed: {total_bets}\n"
        f"• Total wagered: ${format_number(total_wagered)}\n\n"
        f"⚙️ Database: {len(db.users)} users loaded\n"
    )
    
    await update.message.reply_text(msg, parse_mode='HTML')


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all inline keyboard callbacks"""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    data = query.data

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

        user_data['balance'] -= amount
        user_data['total_wagered'] += amount
        user_data['games_played'] += 1
        user_data['wagered_since_withdrawal'] = user_data.get('wagered_since_withdrawal', 0) + amount

        if user_data.get('playthrough_required', 0) > 0:
            user_data['bonus_wagered'] = user_data.get('bonus_wagered', 0) + amount

        db.global_stats['total_bets'] += 1
        db.global_stats['total_wagered'] += amount

        await query.edit_message_text("🎲 Rolling the dice...")

        for i in range(5):
            await asyncio.sleep(0.3)
            import random
            random_num = random.randint(1, 6)
            await query.edit_message_text(f"🎲 Rolling... {DiceGame.get_dice_emoji(random_num)}")

        result = DiceGame.roll()
        result_emoji = DiceGame.get_dice_emoji(result)

        await asyncio.sleep(0.5)

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

        user_data['balance'] -= amount

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

        await execute_pvp_dice_match(query, context, challenge_id, target_number)
        return

    if data.startswith("dice_decline_"):
        challenge_id = data.replace("dice_decline_", "")

        if not hasattr(db, 'dice_challenges') or challenge_id not in db.dice_challenges:
            await query.edit_message_text("❌ Challenge not found.")
            return

        challenge = db.dice_challenges[challenge_id]

        challenger_data = db.get_user(challenge['challenger_id'])
        challenger_data['balance'] += challenge['amount']

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

    await query.edit_message_text("🎲 Rolling the dice...")

    for i in range(5):
        await asyncio.sleep(0.3)
        import random
        random_num = random.randint(1, 6)
        await query.edit_message_text(f"🎲 Rolling... {DiceGame.get_dice_emoji(random_num)}")

    result = DiceGame.roll()
    result_emoji = DiceGame.get_dice_emoji(result)

    await asyncio.sleep(0.5)

    challenger_data = db.get_user(challenger_id)
    target_data = db.get_user(target_id)

    challenger_won = challenger_number == result
    target_won = target_number == result

    if challenger_won and not target_won:
        challenger_data['balance'] += amount * 2
        winner_msg = f"🎉 @{challenge['challenger_username']} WINS!"
        challenger_result = "🎉 YOU WIN!"
        target_result = "❌ You lost!"
    elif target_won and not challenger_won:
        target_data['balance'] += amount * 2
        winner_msg = f"🎉 @{challenge['target_username']} WINS!"
        challenger_result = "❌ You lost!"
        target_result = "🎉 YOU WIN!"
    else:
        challenger_data['balance'] += amount
        target_data['balance'] += amount
        winner_msg = "🤝 IT'S A DRAW!"
        challenger_result = "🤝 Draw - bet refunded"
        target_result = "🤝 Draw - bet refunded"

    result_msg = (
        f"🎲 <b>PVP DICE RESULT</b>\n\n"
        f"🎲 Roll: {result_emoji} ({result})\n\n"
        f"🎯 @{challenge['challenger_username']}: {challenger_number}\n"
        f"🎯 @{challenge['target_username']}: {target_number}\n\n"
        f"{winner_msg}\n"
        f"💰 Prize: ${amount * 2:.2f}"
    )

    await query.edit_message_text(
        result_msg + f"\n\n{target_result}",
        parse_mode='HTML'
    )

    try:
        await context.bot.send_message(
            chat_id=challenger_id,
            text=result_msg + f"\n\n{challenger_result}",
            parse_mode='HTML'
        )
    except:
        pass

    del db.dice_challenges[challenge_id]
