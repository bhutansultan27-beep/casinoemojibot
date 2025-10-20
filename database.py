import json
import time
import random
import shutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
from pathlib import Path

from config import (
    DATA_FILE, STARTING_BALANCE, RATE_LIMIT_WINDOW, 
    RATE_LIMIT_MAX, JACKPOT_STARTING, GAME_COOLDOWNS
)


class CasinoDatabase:
    
    def __init__(self):
        self.users: Dict[int, Dict] = {}
        self.pending_deposits: Dict[str, Dict] = {}
        self.active_games: Dict[str, Dict] = {}
        self.leaderboard: List[Tuple[int, float]] = []
        self.rate_limits: Dict[int, List[float]] = defaultdict(list)
        self.game_cooldowns: Dict[Tuple[int, str], float] = {}
        self.jackpot_pool = JACKPOT_STARTING
        self.global_stats = {
            'total_bets': 0,
            'total_wagered': 0.0,
            'total_won': 0.0,
            'total_players': 0
        }
        self.last_backup = time.time()
        self.load_data()
    
    def get_user(self, user_id: int) -> Dict:
        if user_id not in self.users:
            self.users[user_id] = {
                'balance': STARTING_BALANCE,
                'username': '',
                'total_wagered': 0.0,
                'total_won': 0.0,
                'games_played': 0,
                'last_bonus': None,
                'bonus_streak': 0,
                'ltc_address': f"LTC{random.randint(100000, 999999)}xyz",
                'achievements': [],
                'referrals': [],
                'referred_by': None,
                'level': 1,
                'xp': 0,
                'win_streak': 0,
                'max_win_streak': 0,
                'created_at': datetime.now().isoformat(),
                'last_seen': datetime.now().isoformat()
            }
            self.global_stats['total_players'] += 1
        
        self.users[user_id]['last_seen'] = datetime.now().isoformat()
        return self.users[user_id]
    
    def check_rate_limit(self, user_id: int) -> bool:
        now = time.time()
        self.rate_limits[user_id] = [
            ts for ts in self.rate_limits[user_id] 
            if now - ts < RATE_LIMIT_WINDOW
        ]
        
        if len(self.rate_limits[user_id]) >= RATE_LIMIT_MAX:
            return False
        
        self.rate_limits[user_id].append(now)
        return True
    
    def check_game_cooldown(self, user_id: int, game_type: str) -> bool:
        key = (user_id, game_type)
        now = time.time()
        
        if key in self.game_cooldowns:
            cooldown = GAME_COOLDOWNS.get(game_type, 3)
            if now - self.game_cooldowns[key] < cooldown:
                return False
        
        self.game_cooldowns[key] = now
        return True
    
    def get_cooldown_remaining(self, user_id: int, game_type: str) -> int:
        key = (user_id, game_type)
        if key not in self.game_cooldowns:
            return 0
        
        now = time.time()
        cooldown = GAME_COOLDOWNS.get(game_type, 3)
        elapsed = now - self.game_cooldowns[key]
        remaining = max(0, cooldown - elapsed)
        return int(remaining)
    
    def update_leaderboard(self):
        self.leaderboard = sorted(
            [(uid, data['balance']) for uid, data in self.users.items()],
            key=lambda x: x[1],
            reverse=True
        )[:10]
    
    def add_achievement(self, user_id: int, achievement_id: str) -> bool:
        user = self.get_user(user_id)
        if achievement_id not in user['achievements']:
            user['achievements'].append(achievement_id)
            return True
        return False
    
    def add_referral(self, referrer_id: int, referee_id: int) -> bool:
        referrer = self.get_user(referrer_id)
        referee = self.get_user(referee_id)
        
        if referee['referred_by'] is not None:
            return False
        
        referee['referred_by'] = referrer_id
        referrer['referrals'].append(referee_id)
        return True
    
    def calculate_level(self, xp: int) -> int:
        return min(100, int((xp / 1000) ** 0.5) + 1)
    
    def add_xp(self, user_id: int, amount: int):
        user = self.get_user(user_id)
        old_level = user['level']
        user['xp'] += amount
        new_level = self.calculate_level(user['xp'])
        user['level'] = new_level
        return new_level > old_level
    
    def save_data(self):
        data = {
            'users': {str(k): v for k, v in self.users.items()},
            'jackpot_pool': self.jackpot_pool,
            'global_stats': self.global_stats,
            'version': '2.0'
        }
        
        try:
            with open(DATA_FILE, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def load_data(self):
        if not Path(DATA_FILE).exists():
            return
        
        try:
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
            
            self.users = {int(k): v for k, v in data.get('users', {}).items()}
            self.jackpot_pool = data.get('jackpot_pool', JACKPOT_STARTING)
            self.global_stats = data.get('global_stats', self.global_stats)
            
            for user_data in self.users.values():
                if 'last_bonus' in user_data and user_data['last_bonus']:
                    user_data['last_bonus'] = datetime.fromisoformat(user_data['last_bonus'])
            
            print(f"✅ Loaded data for {len(self.users)} users")
        except Exception as e:
            print(f"Error loading data: {e}")
    
    def backup_data(self):
        if not Path(DATA_FILE).exists():
            return
        
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = f'casino_data_backup_{timestamp}.json'
            shutil.copy2(DATA_FILE, backup_file)
            print(f"✅ Backup created: {backup_file}")
        except Exception as e:
            print(f"Error creating backup: {e}")
    
    def auto_save(self):
        now = time.time()
        if now - self.last_backup > 300:
            self.save_data()
            self.last_backup = now


db = CasinoDatabase()
