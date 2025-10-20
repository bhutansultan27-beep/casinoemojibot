import asyncio
import random
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from database import db
from games import (
    RouletteGame, BlackjackGame, BasketballGame, SoccerGame,
    BowlingGame, CrashGame, DiceGame, CoinFlipGame
)
from utils import (
    format_number, check_achievements, process_referral,
    get_rank_from_level, format_time_ago, get_xp_for_bet
)
from config import (
    ADMIN_IDS, LTC_RATE, DEPOSIT_FEE, WITHDRAWAL_FEE,
    CONFIRMATION_DELAY, DAILY_BONUS_MIN, DAILY_BONUS_MAX,
    BONUS_COOLDOWN, STREAK_BONUS_DAYS, STREAK_BONUS_AMOUNT,
    ACHIEVEMENTS, REFERRAL_BONUS, REFEREE_BONUS, JACKPOT_CONTRIBUTION
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_data = db.get_user(user.id)
    user_data['username'] = user.username or user.first_name
    
    if context.args and len(context.args) > 0:
        referral_code = context.args[0]
        try:
            referrer_id = int(referral_code)
            if referrer_id != user.id:
                if process_referral(referrer_id, user.id):
                    referrer = db.get_user(referrer_id)
                    await context.bot.send_message(
                        chat_id=referrer_id,
                        text=f"🎁 @{user_data['username']} used your referral! You earned ${REFERRAL_BONUS}!"
                    )
                    await update.message.reply_text(
                        f"🎁 You've been referred by a friend! Received ${REFEREE_BONUS} bonus!"
                    )
        except:
            pass
    
    welcome_msg = (
        f"🎰 <b>Welcome to Casino Emojia, {user.first_name}!</b> 🎰\n\n"
        "🎲 Your premier crypto casino experience on Telegram.\n\n"
        "💰 <b>Getting Started:</b>\n"
        "• Use /bonus to claim daily rewards\n"
        "• Use /balance to check your stats\n"
        "• Use /deposit to add LTC funds\n\n"
        "🎮 <b>Available Games:</b>\n"
        "🎰 /roulette - Classic European roulette\n"
        "🃏 /blackjack - Beat the dealer to 21\n"
        "🏀 /basketball - Free throw predictions\n"
        "⚽ /soccer - Penalty kick bets\n"
        "🎳 /bowling - Strike for jackpot!\n"
        "🚀 /crash - Cashout before crash\n"
        "🎲 /dice - Roll and predict\n"
        "🪙 /coinflip - Heads or tails\n\n"
        "🏆 /leaderboard - Top players\n"
        "🎯 /achievements - Your badges\n"
        "👥 /referral - Invite friends\n"
        "👤 /profile - Your stats\n\n"
        "💡 <b>Tip:</b> Start with /bonus for free money!\n\n"
        "Good luck! 🍀"
    )
    
    await update.message.reply_text(welcome_msg, parse_mode='HTML')


async def deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data = db.get_user(user_id)
    
    address = user_data['ltc_address']
    
    msg = (
        f"💳 <b>Deposit Litecoin</b>\n\n"
        f"Send LTC to this address:\n"
        f"<code>{address}</code>\n\n"
        f"📊 Current rate: ${LTC_RATE:.2f} per LTC\n"
        f"💵 Fee: {DEPOSIT_FEE*100}%\n\n"
        f"After sending, confirm with:\n"
        f"/confirm [transaction_id]\n\n"
        f"Example: /confirm abc123xyz\n\n"
        f"⏱ Confirmation takes ~{CONFIRMATION_DELAY} seconds (demo mode)."
    )
    
    await update.message.reply_text(msg, parse_mode='HTML')


async def confirm_deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not context.args:
        await update.message.reply_text(
            "❌ Please provide transaction ID:\n\n"
            "/confirm [txid]\n\n"
            "Example: /confirm abc123xyz"
        )
        return
    
    txid = context.args[0]
    
    ltc_amount = random.uniform(0.1, 1.0)
    usd_amount = ltc_amount * LTC_RATE
    fee = usd_amount * DEPOSIT_FEE
    final_amount = usd_amount - fee
    
    db.pending_deposits[txid] = {
        'user_id': user_id,
        'amount': final_amount,
        'timestamp': datetime.now()
    }
    
    await update.message.reply_text(
        f"⏳ Deposit pending confirmation...\n"
        f"Amount: ${usd_amount:.2f} ({ltc_amount:.3f} LTC)\n"
        f"Fee: ${fee:.2f}\n"
        f"You'll receive: ${final_amount:.2f}\n\n"
        f"Please wait ~{CONFIRMATION_DELAY} seconds..."
    )
    
    await asyncio.sleep(CONFIRMATION_DELAY)
    
    user_data = db.get_user(user_id)
    user_data['balance'] += final_amount
    
    await context.bot.send_message(
        chat_id=user_id,
        text=(
            f"✅ <b>Deposit Confirmed!</b>\n\n"
            f"💰 Received: ${final_amount:.2f}\n"
            f"💳 Balance: ${format_number(user_data['balance'])}\n\n"
            f"Ready to play! Try /roulette to start."
        ),
        parse_mode='HTML'
    )


async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data = db.get_user(user_id)
    
    rtp = 0.0
    if user_data['total_wagered'] > 0:
        rtp = (user_data['total_won'] / user_data['total_wagered']) * 100
    
    msg = (
        f"💰 <b>Your Balance</b>\n\n"
        f"💵 {format_number(user_data['balance'])}\n"
        f"🎮 Games played: {user_data['games_played']}\n"
        f"💸 Total wagered: {format_number(user_data['total_wagered'])}\n"
        f"🏆 Total won: {format_number(user_data['total_won'])}\n"
        f"📊 RTP: {rtp:.1f}%\n\n"
        f"Use /deposit to add funds\n"
        f"Use /bonus for daily rewards\n"
        f"Use /withdraw to cash out"
    )
    
    await update.message.reply_text(msg, parse_mode='HTML')


async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data = db.get_user(user_id)
    
    if not context.args:
        await update.message.reply_text(
            "❌ Usage: /withdraw [amount]\n\n"
            "Example: /withdraw 50"
        )
        return
    
    try:
        amount = float(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Invalid amount. Use numbers only.")
        return
    
    if amount <= 0:
        await update.message.reply_text("❌ Amount must be greater than 0.")
        return
    
    if amount > user_data['balance']:
        await update.message.reply_text(
            f"❌ Insufficient balance.\n"
            f"💰 Available: {format_number(user_data['balance'])}"
        )
        return
    
    fee = amount * WITHDRAWAL_FEE
    final_usd = amount - fee
    ltc_amount = final_usd / LTC_RATE
    
    user_data['balance'] -= amount
    
    msg = (
        f"✅ <b>Withdrawal Processed</b>\n\n"
        f"💸 Amount: ${amount:.2f}\n"
        f"💵 Fee: ${fee:.2f}\n"
        f"💰 Sent: ~{ltc_amount:.4f} LTC\n"
        f"📍 To: {user_data['ltc_address']}\n\n"
        f"💳 Remaining: {format_number(user_data['balance'])}"
    )
    
    await update.message.reply_text(msg, parse_mode='HTML')


async def daily_bonus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data = db.get_user(user_id)
    
    now = datetime.now()
    last_bonus = user_data.get('last_bonus')
    
    if last_bonus:
        if isinstance(last_bonus, str):
            last_bonus = datetime.fromisoformat(last_bonus)
        
        if (now - last_bonus).total_seconds() < BONUS_COOLDOWN:
            next_bonus = last_bonus + timedelta(seconds=BONUS_COOLDOWN)
            hours_left = int((next_bonus - now).total_seconds() / 3600)
            minutes_left = int((next_bonus - now).total_seconds() % 3600 / 60)
            await update.message.reply_text(
                f"⏰ Daily bonus already claimed!\n"
                f"Come back in {hours_left}h {minutes_left}m"
            )
            return
    
    if last_bonus and isinstance(last_bonus, str):
        last_bonus = datetime.fromisoformat(last_bonus)
    
    if last_bonus and (now - last_bonus).days == 1:
        user_data['bonus_streak'] += 1
    else:
        user_data['bonus_streak'] = 1
    
    user_data['last_bonus'] = now
    
    bonus_amount = random.uniform(DAILY_BONUS_MIN, DAILY_BONUS_MAX)
    user_data['balance'] += bonus_amount
    
    msg = f"🎁 <b>Daily Bonus!</b>\n\n"
    msg += f"💰 You received: ${bonus_amount:.2f}\n"
    msg += f"💳 Balance: {format_number(user_data['balance'])}\n"
    msg += f"🔥 Streak: {user_data['bonus_streak']} days\n\n"
    
    if user_data['bonus_streak'] == STREAK_BONUS_DAYS:
        user_data['balance'] += STREAK_BONUS_AMOUNT
        msg += f"🎉 {STREAK_BONUS_DAYS}-day streak bonus: ${STREAK_BONUS_AMOUNT}!\n"
        user_data['bonus_streak'] = 0
    
    msg += "\n🍀 Come back tomorrow!"
    
    unlocked = check_achievements(user_id)
    if unlocked:
        for ach_id, reward in unlocked:
            ach = ACHIEVEMENTS[ach_id]
            msg += f"\n\n🏆 Achievement unlocked: {ach['name']}\n+${reward}"
    
    await update.message.reply_text(msg, parse_mode='HTML')


async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data = db.get_user(user_id)
    
    rank = get_rank_from_level(user_data['level'])
    created = format_time_ago(user_data.get('created_at'))
    
    msg = (
        f"👤 <b>Player Profile</b>\n\n"
        f"📛 @{user_data['username']}\n"
        f"{rank} - Level {user_data['level']}\n"
        f"⭐ XP: {user_data['xp']}\n\n"
        f"💰 Balance: {format_number(user_data['balance'])}\n"
        f"🎮 Games: {user_data['games_played']}\n"
        f"🏆 Total won: {format_number(user_data['total_won'])}\n"
        f"🔥 Win streak: {user_data['win_streak']}\n"
        f"📈 Best streak: {user_data['max_win_streak']}\n"
        f"🎖️ Achievements: {len(user_data['achievements'])}/{len(ACHIEVEMENTS)}\n"
        f"👥 Referrals: {len(user_data['referrals'])}\n\n"
        f"📅 Member since: {created}"
    )
    
    await update.message.reply_text(msg, parse_mode='HTML')


async def achievements_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data = db.get_user(user_id)
    
    msg = "🎯 <b>Your Achievements</b>\n\n"
    
    for ach_id, ach in ACHIEVEMENTS.items():
        if ach_id in user_data['achievements']:
            msg += f"✅ {ach['name']}\n   {ach['description']}\n\n"
        else:
            msg += f"🔒 {ach['name']}\n   {ach['description']}\n   Reward: ${ach['reward']}\n\n"
    
    await update.message.reply_text(msg, parse_mode='HTML')


async def referral_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data = db.get_user(user_id)
    bot_username = (await context.bot.get_me()).username
    
    referral_link = f"https://t.me/{bot_username}?start={user_id}"
    
    msg = (
        f"👥 <b>Referral Program</b>\n\n"
        f"Invite friends and earn rewards!\n\n"
        f"💰 You earn: ${REFERRAL_BONUS}\n"
        f"🎁 They get: ${REFEREE_BONUS}\n\n"
        f"Your referral link:\n"
        f"<code>{referral_link}</code>\n\n"
        f"📊 Total referrals: {len(user_data['referrals'])}\n"
        f"💵 Total earned: ${len(user_data['referrals']) * REFERRAL_BONUS:.2f}"
    )
    
    await update.message.reply_text(msg, parse_mode='HTML')


async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db.update_leaderboard()
    
    if not db.leaderboard:
        await update.message.reply_text("🏆 Leaderboard is empty. Be the first to play!")
        return
    
    msg = "🏆 <b>CASINO EMOJIA LEADERBOARD</b>\n\n"
    msg += "Top 10 Players:\n\n"
    
    medals = ["🥇", "🥈", "🥉"]
    
    for idx, (user_id, balance) in enumerate(db.leaderboard, 1):
        user_data = db.get_user(user_id)
        medal = medals[idx-1] if idx <= 3 else f"{idx}."
        username = user_data.get('username', 'Anonymous')
        msg += f"{medal} @{username}: {format_number(balance)}\n"
    
    msg += "\n💰 Weekly prizes:\n1st: $1,000 | 2nd: $500 | 3rd: $250"
    
    await update.message.reply_text(msg, parse_mode='HTML')


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        f"📊 <b>Global Statistics</b>\n\n"
        f"👥 Total players: {db.global_stats['total_players']}\n"
        f"🎮 Total bets: {db.global_stats['total_bets']}\n"
        f"💸 Total wagered: {format_number(db.global_stats['total_wagered'])}\n"
        f"🏆 Total won: {format_number(db.global_stats['total_won'])}\n"
        f"🎰 Jackpot pool: {format_number(db.jackpot_pool)}"
    )
    
    await update.message.reply_text(msg, parse_mode='HTML')


async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ Access denied.")
        return
    
    if not context.args:
        msg = (
            "🔧 <b>Admin Panel</b>\n\n"
            "Commands:\n"
            "/admin stats - Global statistics\n"
            "/admin users - Total users\n"
            "/admin jackpot [amount] - Set jackpot\n"
            "/admin give [user_id] [amount] - Give money\n"
            "/admin save - Save database\n"
            "/admin backup - Create backup"
        )
        await update.message.reply_text(msg, parse_mode='HTML')
        return
    
    cmd = context.args[0]
    
    if cmd == "stats":
        msg = (
            f"📊 <b>Admin Statistics</b>\n\n"
            f"👥 Users: {len(db.users)}\n"
            f"🎮 Total bets: {db.global_stats['total_bets']}\n"
            f"💸 Wagered: {format_number(db.global_stats['total_wagered'])}\n"
            f"🏆 Won: {format_number(db.global_stats['total_won'])}\n"
            f"🎰 Jackpot: {format_number(db.jackpot_pool)}\n"
            f"💾 Pending deposits: {len(db.pending_deposits)}\n"
            f"🎯 Active games: {len(db.active_games)}"
        )
        await update.message.reply_text(msg, parse_mode='HTML')
    
    elif cmd == "users":
        await update.message.reply_text(f"👥 Total users: {len(db.users)}")
    
    elif cmd == "jackpot" and len(context.args) > 1:
        try:
            amount = float(context.args[1])
            db.jackpot_pool = amount
            await update.message.reply_text(f"✅ Jackpot set to {format_number(amount)}")
        except:
            await update.message.reply_text("❌ Invalid amount")
    
    elif cmd == "give" and len(context.args) > 2:
        try:
            target_id = int(context.args[1])
            amount = float(context.args[2])
            target_user = db.get_user(target_id)
            target_user['balance'] += amount
            await update.message.reply_text(f"✅ Gave ${amount} to user {target_id}")
        except:
            await update.message.reply_text("❌ Invalid parameters")
    
    elif cmd == "save":
        db.save_data()
        await update.message.reply_text("✅ Database saved")
    
    elif cmd == "backup":
        db.backup_data()
        await update.message.reply_text("✅ Backup created")
