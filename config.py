import os
from typing import Set

BOT_TOKEN = os.getenv("BOT_TOKEN", "")

ADMIN_IDS: Set[int] = {123456789}

LTC_RATE = 77.0
DEPOSIT_FEE = 0.01
WITHDRAWAL_FEE = 0.01
CONFIRMATION_DELAY = 5

RATE_LIMIT_WINDOW = 60
RATE_LIMIT_MAX = 10

GAME_COOLDOWNS = {
    'roulette': 3,
    'blackjack': 5,
    'basketball': 2,
    'soccer': 2,
    'bowling': 3,
    'crash': 4,
    'dice': 1,
    'coinflip': 1
}

STARTING_BALANCE = 1000.0
DAILY_BONUS_MIN = 10.0
DAILY_BONUS_MAX = 100.0
BONUS_COOLDOWN = 86400
STREAK_BONUS_DAYS = 5
STREAK_BONUS_AMOUNT = 200.0

JACKPOT_STARTING = 5000.0
JACKPOT_CONTRIBUTION = 0.02

REFERRAL_BONUS = 50.0
REFEREE_BONUS = 25.0

ACHIEVEMENTS = {
    'first_bet': {'name': '🎲 First Bet', 'description': 'Place your first bet', 'reward': 10},
    'high_roller': {'name': '💎 High Roller', 'description': 'Bet $1000 in a single game', 'reward': 100},
    'lucky_7': {'name': '🍀 Lucky Seven', 'description': 'Win 7 games in a row', 'reward': 77},
    'jackpot_winner': {'name': '🏆 Jackpot Winner', 'description': 'Win the bowling jackpot', 'reward': 500},
    'veteran': {'name': '⭐ Veteran', 'description': 'Play 100 games', 'reward': 200},
    'whale': {'name': '🐋 Whale', 'description': 'Reach $10,000 balance', 'reward': 1000},
    'streak_master': {'name': '🔥 Streak Master', 'description': '10-day login streak', 'reward': 500}
}

DATA_FILE = 'casino_data.json'
BACKUP_INTERVAL = 300
