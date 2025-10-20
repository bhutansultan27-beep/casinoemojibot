from telegram.ext import CommandHandler, ContextTypes
from database import db
from utils import validate_bet, format_balance, check_daily_reward
from games import roll_dice, coin_flip
import time
import random

async def start(update, context):
    user_id = update.effective_user.id
    player = db.get_player(user_id)
    welcome = "Welcome to Antaria Casino! 🎰\n"
    welcome += f"Balance: {format_balance(player['balance'])}\n"
    welcome += "Commands: /balance, /dice <amount> <number>, /coinflip <amount> <heads/tails>, /bonus, /profile, /help"
    await update.message.reply_text(welcome)

async def balance(update, context):
    user_id = update.effective_user.id
    player = db.get_player(user_id)
    check_daily_reward(player, user_id, db)  # Check for daily reward
    await update.message.reply_text(f"Balance: {format_balance(player['balance'])}")

async def dice(update, context):
    user_id = update.effective_user.id
    args = context.args
    if len(args) != 2:
        await update.message.reply_text("Usage: /dice <amount> <number (1-6)>, e.g., /dice 10 5")
        return
    bet, number = args[0], args[1]
    if not validate_bet(bet) or not (1 <= int(number) <= 6):
        await update.message.reply_text("Invalid bet or number. Use /dice <amount> <number (1-6)>")
        return
    bet = float(bet)
    player = db.get_player(user_id)
    if player["balance"] < bet:
        await update.message.reply_text("Insufficient balance!")
        return

    # Simulate rolling dice with emoji animation
    await update.message.reply_text("Rolling... 🎲")
    for _ in range(3):  # 3 "rolls" for effect
        roll = random.randint(1, 6)
        await update.message.reply_text(f"🎲 {roll}")
        time.sleep(0.5)  # Pause for 0.5 seconds to show animation

    # Final roll and result
    roll, profit, message = roll_dice(bet, int(number))
    player["balance"] += profit
    player["total_wagered"] += bet
    db.update_player(user_id, player)
    await update.message.reply_text(f"🎲 {roll} - {message} New balance: {format_balance(player['balance'])}")

async def coinflip(update, context):
    user_id = update.effective_user.id
    args = context.args
    if len(args) != 2:
        await update.message.reply_text("Usage: /coinflip <amount> <heads/tails>, e.g., /coinflip 10 heads")
        return
    bet, choice = args[0], args[1]
    if not validate_bet(bet) or choice.lower() not in ["heads", "tails"]:
        await update.message.reply_text("Invalid bet or choice. Use /coinflip <amount> <heads/tails>")
        return
    bet = float(bet)
    player = db.get_player(user_id)
    if player["balance"] < bet:
        await update.message.reply_text("Insufficient balance!")
        return
    result, profit, message = coin_flip(bet, choice)
    player["balance"] += profit
    player["total_wagered"] += bet
    db.update_player(user_id, player)
    await update.message.reply_text(f"Flipped: {result} 🎯 {message} New balance: {format_balance(player['balance'])}")

async def bonus(update, context):
    user_id = update.effective_user.id
    player = db.get_player(user_id)
    if player["bonus_locked"] > 0 and player["total_wagered"] >= 5.0:
        player["balance"] += player["bonus_locked"]
        player["bonus_locked"] = 0.0
        db.update_player(user_id, player)
        await update.message.reply_text(f"Unlocked $5 bonus! New balance: {format_balance(player['balance'])}")
    elif player["bonus_locked"] > 0:
        await update.message.reply_text(f"Bonus locked. Wager $5 to unlock. Total wagered: ${player['total_wagered']:.2f}")
    else:
        await update.message.reply_text("No bonus available.")

async def profile(update, context):
    user_id = update.effective_user.id
    player = db.get_player(user_id)
    check_daily_reward(player, user_id, db)  # Check for daily reward
    await update.message.reply_text(f"Profile:\nBalance: {format_balance(player['balance'])}\nTotal Wagered: ${player['total_wagered']:.2f}\nAchievements: {', '.join(player['achievements'] or ['None'])}")

async def help_command(update, context):
    help_text = "/start - Start the bot\n/balance - Check your balance\n/dice <amount> <number> - Bet on a dice roll (1-6)\n/coinflip <amount> <heads/tails> - Flip a coin\n/bonus - Claim your $5 bonus (wager $5 to unlock)\n/profile - View your stats\n/help - Show this message"
    await update.message.reply_text(help_text)
