# 🎰 Antaria Casino Bot

Welcome to **Antaria Casino** - Your premium Telegram crypto casino experience!

## 🎮 Features

### Games
- **🎲 Dice Game** - Choose your number (1-6) and win 5x your bet!
  - Play vs Bot for instant action
  - Challenge other players for PvP battles
  - Automated Dealer Bot accepts expired challenges
- **🪙 CoinFlip** - Classic heads or tails with 2x payout

### Smart Bonus System
- **First Bonus**: New players get $5 locked bonus
  - Must play through $5 before withdrawing
- **Daily Bonus**: 1% of total amount wagered
  - Resets on every withdrawal
  - Encourages active gameplay
  - No spam withdrawals possible

### Social Features
- 👥 **Referral System** - Invite friends and earn
- 🏆 **Leaderboard** - Compete for top spots
- 🎯 **Achievements** - Unlock badges and rewards
- 👤 **Player Profiles** - Track your stats

### Interactive Features
- ⚡ **Animated Games** - Dice rolls and coin flips in real-time
- 💳 **Quick Actions** - Balance buttons for deposit/withdraw
- 🤖 **Dealer Bot** - Auto-accepts PvP challenges after 60 seconds

## 📁 File Structure

```
antaria-casino/
├── main.py                 # Entry point
├── handlers.py             # Core commands (balance, bonus, etc.)
├── game_handlers.py        # Game logic (dice, coinflip)
├── callback_handlers.py    # Button interactions
├── games.py                # Game mechanics
├── database.py             # Data management
├── config.py               # Configuration
├── utils.py                # Helper functions
├── text_handler.py         # Text message handler
└── casino_data.json        # Database (auto-generated)
```

## 🚀 Setup Instructions

### 1. Prerequisites
- Python 3.9+
- Telegram Bot Token (get from @BotFather)

### 2. Installation

```bash
# Clone or download the code
cd antaria-casino

# Install dependencies
pip install python-telegram-bot==20.7

# Or if you have a requirements.txt:
pip install -r requirements.txt
```

### 3. Configuration

**Option A: Environment Variable (Recommended)**
```bash
export BOT_TOKEN="your_bot_token_here"
python main.py
```

**Option B: Edit config.py**
```python
BOT_TOKEN = "your_bot_token_here"
```

### 4. Run the Bot
```bash
python main.py
```

You should see:
```
🎰 Antaria Casino Bot Starting...
==================================================
✅ Bot initialized successfully!
🎮 Available games: Dice (PvP enabled), CoinFlip
🎁 Features: Smart Bonus System, Achievements, Referrals, Leaderboard
🤖 Dealer Bot: Active
==================================================
🚀 Antaria Casino is now running...
```

## 🎮 How to Play

### Basic Commands
- `/start` - Welcome message & overview
- `/help` - Same as /start
- `/balance` - Check your balance (with action buttons)
- `/bonus` - Claim your daily bonus
- `/profile` - View your stats
- `/deposit` - Get LTC deposit address
- `/withdraw [amount]` - Cash out (must complete playthrough)

### Game Commands

**Dice Game**
```
/dice                    # Show game menu
/dice 10 5               # Quick play: Bet $10 on number 5
/dice_challenge @user 20 3   # Challenge @user with $20 bet on number 3
```

**CoinFlip**
```
/coinflip 10 heads       # Bet $10 on heads
/coinflip 25 tails       # Bet $25 on tails
```

### Social Commands
- `/leaderboard` - Top 10 players
- `/referral` - Get your referral link
- `/achievements` - View unlocked badges
- `/stats` - Global casino statistics

### Admin Commands (if you're an admin)
```
/admin stats             # View admin statistics
/admin give [user_id] [amount]   # Give money to user
/admin jackpot [amount]  # Set jackpot pool
/admin save              # Manual save
/admin backup            # Create backup
```

## 🎲 Game Rules

### Dice Game
- **Choose a number**: 1-6
- **Win condition**: Match the roll
- **Payout**: 5x your bet
- **House edge**: ~3%

**PvP Mode**:
1. Challenge another player
2. Both pick numbers
3. Roll the dice
4. First to match wins double the bet
5. Draw = both refunded

### CoinFlip
- **Choose**: Heads or Tails
- **Win condition**: Match the flip
- **Payout**: 2x your bet (double or nothing)
- **House edge**: ~2%

## 💰 Bonus System Explained

### How It Works

**New Players:**
1. Get $5 locked bonus immediately
2. Must wager $5 to unlock withdrawal
3. Balance shows total money, but can't withdraw until playthrough complete

**Regular Players:**
1. Daily bonus = 1% of total wagered
2. Example: Wagered $10,000 → Get $100 bonus
3. **Important**: Bonus counter resets on withdrawal
4. This prevents spam withdrawals

### Example Flow
```
New player:
- Balance: $1,000 (starting)
- Claim bonus: +$5 locked
- Play $5 worth of games
- Can now withdraw

Experienced player:
- Total wagered: $50,000
- Claim bonus: +$500 (1%)
- Can withdraw immediately (no playthrough)
- After withdrawal, wagered counter resets
```

## 🎯 Achievements

Unlock special badges by completing challenges:
- 🎲 First Bet - Place your first bet
- 💰 High Roller - Bet over $100
- 🔥 Win Streak - Win 5 games in a row
- 🎰 Jackpot - Win the jackpot
- 👥 Referrer - Refer 10 friends
- 📈 Leveled Up - Reach level 10

## 🔧 Configuration Options

Edit `config.py` to customize:

```python
# Bot Token
BOT_TOKEN = "your_token"

# Admin user IDs (can use admin commands)
ADMIN_IDS = [your_telegram_id]

# Crypto rates
LTC_RATE = 75.00  # USD per LTC

# Fees
DEPOSIT_FEE = 0.02    # 2%
WITHDRAWAL_FEE = 0.03  # 3%

# Bonus settings
DAILY_BONUS_MIN = 5.0
DAILY_BONUS_MAX = 20.0
BONUS_COOLDOWN = 86400  # 24 hours

# Streak bonus
STREAK_BONUS_DAYS = 7
STREAK_BONUS_AMOUNT = 50.0

# Referral rewards
REFERRAL_BONUS = 25.0   # Referrer gets
REFEREE_BONUS = 10.0     # New user gets
```

## 🛡️ Security Features

- **Balance tracking** with transaction logs
- **Playthrough requirements** prevent bonus abuse
- **Rate limiting** on bonus claims (24h cooldown)
- **Admin verification** for large withdrawals
- **Automated backups** every 5 minutes
- **Anti-spam** measures on withdrawals

## 📊 Database

The bot uses JSON for data storage (`casino_data.json`):
- Automatically created on first run
- Auto-saves every 5 minutes
- Manual backups via `/admin backup`

### Backup Strategy
1. Auto-save every 5 minutes
2. Manual backups with timestamps
3. Backups named: `casino_data_backup_YYYYMMDD_HHMMSS.json`

## 🐛 Troubleshooting

### Bot not starting
```bash
# Check if token is set
echo $BOT_TOKEN

# Check Python version
python --version  # Should be 3.9+

# Reinstall dependencies
pip install --upgrade python-telegram-bot
```

### Database errors
```bash
# Delete corrupted database (CAUTION: loses data)
rm casino_data.json

# Or restore from backup
cp casino_data_backup_*.json casino_data.json
```

### Games not working
- Check balance: `/balance`
- Verify playthrough: Complete bonus requirements
- Try smaller bet amounts

## 🚀 Advanced Features

### Running on Server

**Using screen (keeps running after logout):**
```bash
screen -S casino
python main.py
# Press Ctrl+A, then D to detach
# Reattach with: screen -r casino
```

**Using systemd service:**
```bash
# Create /etc/systemd/system/antaria-casino.service
[Unit]
Description=Antaria Casino Bot
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/antaria-casino
Environment="BOT_TOKEN=your_token"
ExecStart=/usr/bin/python3 main.py
Restart=always

[Install]
WantedBy=multi-user.target

# Enable and start
sudo systemctl enable antaria-casino
sudo systemctl start antaria-casino
```

### Monitoring
```bash
# View logs
tail -f /var/log/antaria-casino.log

# Check status
systemctl status antaria-casino
```

## 📈 Roadmap

- [ ] Add tournament system
- [ ] Implement VIP tiers
- [ ] Add more games (slots, poker)
- [ ] Real blockchain integration
- [ ] Mobile app version
- [ ] Multi-language support

## 🤝 Contributing

Want to improve Antaria Casino? Here's how:

1. Report bugs via issues
2. Suggest features
3. Submit pull requests
4. Improve documentation

## ⚠️ Legal Disclaimer

**Important**: This bot is for educational/entertainment purposes. 

- Check your local gambling laws
- Implement age verification for production
- Add responsible gambling features
- Consider licensing requirements
- Use at your own risk

## 📧 Support

- **Issues**: Open a GitHub issue
- **Questions**: Check documentation first
- **Feature Requests**: Submit via issues

## 📜 License

MIT License - Feel free to use and modify!

---

## 🎊 Quick Start Summary

```bash
# 1. Get token from @BotFather
# 2. Install dependencies
pip install python-telegram-bot==20.7

# 3. Set token
export BOT_TOKEN="your_token_here"

# 4. Run
python main.py

# 5. Open Telegram and start your bot!
```

**Enjoy Antaria Casino! 🎰💰**
