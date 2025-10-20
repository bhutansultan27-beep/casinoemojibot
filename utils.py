from datetime import datetime
from typing import Optional
from database import db
from config import ACHIEVEMENTS, REFERRAL_BONUS, REFEREE_BONUS


def format_number(num: float) -> str:
    if num >= 1_000_000:
        return f"${num/1_000_000:.2f}M"
    elif num >= 1_000:
        return f"${num/1_000:.2f}K"
    return f"${num:.2f}"


def check_achievements(user_id: int):
    user = db.get_user(user_id)
    unlocked = []
    
    if 'first_bet' not in user['achievements'] and user['games_played'] >= 1:
        if db.add_achievement(user_id, 'first_bet'):
            reward = ACHIEVEMENTS['first_bet']['reward']
            user['balance'] += reward
            unlocked.append(('first_bet', reward))
    
    if 'veteran' not in user['achievements'] and user['games_played'] >= 100:
        if db.add_achievement(user_id, 'veteran'):
            reward = ACHIEVEMENTS['veteran']['reward']
            user['balance'] += reward
            unlocked.append(('veteran', reward))
    
    if 'whale' not in user['achievements'] and user['balance'] >= 10000:
        if db.add_achievement(user_id, 'whale'):
            reward = ACHIEVEMENTS['whale']['reward']
            user['balance'] += reward
            unlocked.append(('whale', reward))
    
    if 'lucky_7' not in user['achievements'] and user['win_streak'] >= 7:
        if db.add_achievement(user_id, 'lucky_7'):
            reward = ACHIEVEMENTS['lucky_7']['reward']
            user['balance'] += reward
            unlocked.append(('lucky_7', reward))
    
    if 'streak_master' not in user['achievements'] and user['bonus_streak'] >= 10:
        if db.add_achievement(user_id, 'streak_master'):
            reward = ACHIEVEMENTS['streak_master']['reward']
            user['balance'] += reward
            unlocked.append(('streak_master', reward))
    
    return unlocked


def process_referral(referrer_id: int, referee_id: int) -> bool:
    if db.add_referral(referrer_id, referee_id):
        referrer = db.get_user(referrer_id)
        referee = db.get_user(referee_id)
        
        referrer['balance'] += REFERRAL_BONUS
        referee['balance'] += REFEREE_BONUS
        
        return True
    return False


def get_rank_from_level(level: int) -> str:
    if level >= 50:
        return "🌟 Legend"
    elif level >= 40:
        return "💎 Diamond"
    elif level >= 30:
        return "🏆 Master"
    elif level >= 20:
        return "🥇 Gold"
    elif level >= 10:
        return "🥈 Silver"
    else:
        return "🥉 Bronze"


def calculate_house_edge(game_type: str) -> float:
    edges = {
        'roulette': 2.7,
        'blackjack': 0.5,
        'basketball': 10.0,
        'soccer': 10.0,
        'bowling': 5.0,
        'crash': 3.0,
        'dice': 8.3,
        'coinflip': 0.0
    }
    return edges.get(game_type, 5.0)


def format_time_ago(dt: Optional[datetime]) -> str:
    if not dt:
        return "Never"
    
    if isinstance(dt, str):
        dt = datetime.fromisoformat(dt)
    
    delta = datetime.now() - dt
    
    if delta.days > 0:
        return f"{delta.days}d ago"
    elif delta.seconds >= 3600:
        hours = delta.seconds // 3600
        return f"{hours}h ago"
    elif delta.seconds >= 60:
        minutes = delta.seconds // 60
        return f"{minutes}m ago"
    else:
        return "Just now"


def get_xp_for_bet(amount: float) -> int:
    return int(amount * 0.1)
