# Casino Emojia - Professional Telegram Casino Bot

A feature-rich Telegram casino bot with modular architecture, achievements system, and comprehensive game selection.

## Features

### 🎮 Games
- **Roulette** - Classic European roulette with multiple bet types
- **Blackjack** - Interactive 21 card game with hit/stand mechanics
- **Basketball** - Free throw prediction betting
- **Soccer** - Penalty kick outcome bets
- **Bowling** - Strike for progressive jackpot
- **Crash** - Multiplier-based cashout game
- **Dice** - Roll prediction with multiple betting options
- **Coin Flip** - Simple heads or tails betting

### 💰 Economy System
- LTC deposits and withdrawals (simulated)
- Daily bonus with streak rewards
- Starting balance: $1,000
- Automatic data persistence with JSON backup

### 🏆 Progression
- **Achievements** - 7 unlockable badges with rewards
- **Level System** - XP-based progression with ranks
- **Leaderboard** - Top 10 players by balance
- **Referral Program** - Earn rewards for inviting friends

### 🎯 Achievements
- 🎲 First Bet - Place your first bet
- 💎 High Roller - Bet $1,000 in a single game
- 🍀 Lucky Seven - Win 7 games in a row
- 🏆 Jackpot Winner - Win the bowling jackpot
- ⭐ Veteran - Play 100 games
- 🐋 Whale - Reach $10,000 balance
- 🔥 Streak Master - 10-day login streak

### 🔧 Admin Controls
- User management
- Jackpot manipulation
- Balance adjustments
- Database backups
- Global statistics

## Setup

### Requirements
- Python 3.11+
- python-telegram-bot v20.7+

### Installation

1. **Get Bot Token from BotFather**
   - Open Telegram and search for @BotFather
   - Send `/newbot` and follow instructions
   - Copy the bot token provided

2. **Set Bot Token as Environment Secret**
   - In Replit: Go to Tools > Secrets
   - Add a new secret: `BOT_TOKEN` with your token value
   - Never commit the token to the repository

3. **Install Dependencies** (already done in Replit)
   ```bash
   pip install python-telegram-bot==20.7
   ```

4. **Run the Bot**
   ```bash
   python main.py
   ```

### ⚠️ Security Note
**NEVER** hardcode your bot token in the code. Always use environment variables or Replit Secrets. The bot will not run without a valid `BOT_TOKEN` environment variable.

### Configuration

Edit `config.py` to customize:
- `ADMIN_IDS` - Set admin user IDs (get your Telegram user ID by sending `/start` to the bot)
- `STARTING_BALANCE` - Initial balance for new users
- `DAILY_BONUS_MIN/MAX` - Bonus amount range
- `GAME_COOLDOWNS` - Per-game cooldown times
- Game-specific parameters

**Important**: `BOT_TOKEN` must be set as an environment variable/secret, NOT in the config file.

## Bot Commands

### General
- `/start` - Welcome message and game list
- `/help` - Show available commands
- `/balance` - Check your balance and stats
- `/profile` - View detailed player profile
- `/stats` - Global casino statistics

### Economy
- `/deposit` - Get LTC deposit address
- `/confirm [txid]` - Confirm LTC transaction
- `/withdraw [amount]` - Withdraw funds to LTC
- `/bonus` - Claim daily bonus

### Games
- `/roulette` - Play roulette
- `/blackjack` - Play blackjack
- `/basketball` - Basketball free throw bets
- `/soccer` - Soccer penalty bets
- `/bowling` - Bowling with jackpot
- `/crash` - Crash multiplier game
- `/dice` - Dice roll betting
- `/coinflip` - Coin flip betting

### Social
- `/leaderboard` - Top 10 players
- `/achievements` - Your unlocked badges
- `/referral` - Get your referral link

### Admin (Admin Only)
- `/admin stats` - Global statistics
- `/admin users` - Total user count
- `/admin jackpot [amount]` - Set jackpot pool
- `/admin give [user_id] [amount]` - Give money to user
- `/admin save` - Manually save database
- `/admin backup` - Create database backup

## Architecture

### Modular Design
```
config.py           - Configuration and constants
database.py         - In-memory DB with JSON persistence
games.py            - All game logic classes
utils.py            - Helper functions and utilities
handlers.py         - Command handlers
game_handlers.py    - Game command handlers
callback_handlers.py - Button callback handlers
text_handler.py     - Text input handlers
main.py             - Bot initialization and runner
```

### Data Persistence
- Automatic save every 5 minutes
- JSON file storage (`casino_data.json`)
- Manual backup creation via admin command
- Data includes: users, balances, stats, jackpot pool

### Rate Limiting
- Global rate limit: 10 actions per 60 seconds
- Per-game cooldowns (configurable)
- Prevents spam and abuse

## Development

### Adding New Games

1. Create game class in `games.py`:
```python
class NewGame:
    @staticmethod
    def play():
        # Game logic
        pass
    
    @staticmethod
    def calculate_payout(prediction, result, amount):
        # Payout calculation
        pass
```

2. Add command handler in `game_handlers.py`
3. Add callback handler in `callback_handlers.py`
4. Register handler in `main.py`
5. Add cooldown to `config.py`

### Database Schema

User object structure:
```python
{
    'balance': float,
    'username': str,
    'total_wagered': float,
    'total_won': float,
    'games_played': int,
    'last_bonus': datetime,
    'bonus_streak': int,
    'ltc_address': str,
    'achievements': list,
    'referrals': list,
    'referred_by': int,
    'level': int,
    'xp': int,
    'win_streak': int,
    'max_win_streak': int,
    'created_at': str,
    'last_seen': str
}
```

## Security

- Environment variable for bot token
- Admin-only commands with ID verification
- Rate limiting to prevent abuse
- No real cryptocurrency transactions (simulation mode)
- Input validation on all user inputs

## Support

For issues or questions:
1. Check the code comments
2. Review configuration in `config.py`
3. Check logs for error messages
4. Verify bot token is set correctly

## License

Custom build for personal/educational use.

## Credits

Built with:
- python-telegram-bot library
- Telegram Bot API
