import json
import os
from datetime import datetime
from typing import Dict, Any


class Database:
    def __init__(self, filename='casino_data.json'):
        self.filename = filename
        self.users: Dict[int, Dict[str, Any]] = {}
        self.pending_deposits = {}
        self.active_games = {}
        self.dice_challenges = {}  # New for PvP
        self.jackpot_pool = 5000.0
        self.global_stats = {
            'total_bets': 0,
            'total_wagered': 0.0,
            'total_won': 0.0,
            'total_players': 0
        }
        self.leaderboard = []
        self.load_data()

    def get_user(self, user_id: int) -> Dict[str, Any]:
        """Get or create user data"""
        if user_id not in self.users:
            self.users[user_id] = {
                'balance': 1000.0,  # Starting balance
                'username': '',
                'total_wagered': 0.0,
                'total_won': 0.0,
                'games_played': 0,
                'last_bonus': None,
                'bonus_streak': 0,
                'ltc_address': f"LTC{user_id % 1000000}xyz",
                'achievements': [],
                'referrals': [],
                'referred_by': None,
                'level': 1,
                'xp': 0,
                'win_streak': 0,
                'max_win_streak': 0,
                'created_at': datetime.now().isoformat(),
                'last_seen': datetime.now().isoformat(),
                # New bonus system fields
                'bonus_locked': 0.0,
                'playthrough_required': 0.0,
                'bonus_wagered': 0.0,
            }
            self.global_stats['total_players'] += 1

        self.users[user_id]['last_seen'] = datetime.now().isoformat()
        return self.users[user_id]

    def update_leaderboard(self):
        """Update the leaderboard with top players"""
        sorted_users = sorted(
            self.users.items(),
            key=lambda x: x[1]['balance'],
            reverse=True
        )
        self.leaderboard = [(uid, data['balance']) for uid, data in sorted_users[:10]]

    def save_data(self):
        """Save database to JSON file"""
        data = {
            'users': {str(k): v for k, v in self.users.items()},
            'jackpot_pool': self.jackpot_pool,
            'global_stats': self.global_stats,
            'version': '2.1'
        }

        try:
            with open(self.filename, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving database: {e}")

    def load_data(self):
        """Load database from JSON file"""
        if not os.path.exists(self.filename):
            print("No existing database found. Creating new one.")
            return

        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)

            self.users = {int(k): v for k, v in data.get('users', {}).items()}
            self.jackpot_pool = data.get('jackpot_pool', 5000.0)
            self.global_stats = data.get('global_stats', {
                'total_bets': 0,
                'total_wagered': 0.0,
                'total_won': 0.0,
                'total_players': len(self.users)
            })

            # Migrate existing users to new bonus system
            for user_id, user_data in self.users.items():
                if 'bonus_locked' not in user_data:
                    user_data['bonus_locked'] = 0.0
                if 'playthrough_required' not in user_data:
                    user_data['playthrough_required'] = 0.0
                if 'bonus_wagered' not in user_data:
                    user_data['bonus_wagered'] = 0.0

            print(f"Database loaded: {len(self.users)} users")
        except Exception as e:
            print(f"Error loading database: {e}")

    def backup_data(self):
        """Create a backup of the database"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"casino_data_backup_{timestamp}.json"

        try:
            with open(self.filename, 'r') as original:
                data = original.read()

            with open(backup_filename, 'w') as backup:
                backup.write(data)

            print(f"Backup created: {backup_filename}")
            return backup_filename
        except Exception as e:
            print(f"Error creating backup: {e}")
            return None


# Global database instance
db = Database()