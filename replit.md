# Casino Emojia - Enhanced Telegram Casino Bot

## Overview
This is a professional Telegram casino bot featuring a modular architecture, 8 casino games, achievement system, referral program, and comprehensive player progression mechanics. The bot uses an in-memory database with JSON persistence and includes admin controls for management.

## Recent Changes
- **Date**: 2025-01-20
- Created modular architecture with separate files for games, handlers, and utilities
- Implemented data persistence with JSON backup system
- Added 3 new games: Crash, Dice, and Coin Flip
- Implemented achievements system with 7 unlockable badges
- Added referral program with dual rewards
- Implemented XP and level progression system
- Added per-game cooldowns and rate limiting
- Created admin dashboard for bot management
- Enhanced error handling and logging

## Project Architecture

### Core Files
- `main.py` - Bot initialization and command registration
- `config.py` - All configuration settings and constants
- `database.py` - In-memory database with JSON persistence
- `games.py` - Game logic for all 8 casino games
- `utils.py` - Helper functions for achievements, formatting, etc.

### Handler Files
- `handlers.py` - General command handlers (start, balance, profile, etc.)
- `game_handlers.py` - Game-specific command handlers
- `callback_handlers.py` - Button callback handlers
- `text_handler.py` - Text input processing for bets

### Data Files
- `casino_data.json` - Main database file (auto-created)
- `casino_data_backup_*.json` - Backup files

## User Preferences
- Modular code structure for easy maintenance
- Comprehensive error handling with user-friendly messages
- Automatic data persistence to prevent data loss
- Rate limiting to prevent spam
- Achievement system for player engagement

## Environment Setup

### Required Environment Variables
- `BOT_TOKEN` - Telegram bot token from @BotFather

### Configuration
Edit `config.py` to modify:
- `ADMIN_IDS` - Add admin user IDs (get from Telegram)
- Game parameters (payouts, cooldowns, probabilities)
- Economy settings (starting balance, bonus amounts)
- Achievement definitions

## Game Portfolio

1. **Roulette** (3s cooldown) - European roulette with red/black/odd/even bets
2. **Blackjack** (5s cooldown) - Classic 21 with hit/stand mechanics
3. **Basketball** (2s cooldown) - Free throw prediction, 1.8:1 payout
4. **Soccer** (2s cooldown) - Penalty kick prediction, 2:1 payout
5. **Bowling** (3s cooldown) - Strike betting with progressive jackpot
6. **Crash** (4s cooldown) - Multiplier game with cashout mechanics
7. **Dice** (1s cooldown) - Six-sided dice with multiple bet types
8. **Coin Flip** (1s cooldown) - Simple heads/tails, 1:1 payout

## Key Features

### Economy System
- Starting balance: $1,000
- LTC deposit/withdrawal simulation
- Daily bonus: $10-$100 with streak bonuses
- 5-day streak reward: $200

### Progression System
- XP earned from betting (10% of bet amount)
- Level system with ranks (Bronze → Legend)
- Win streak tracking
- Achievement system with monetary rewards

### Admin Tools
Commands for administrators:
- View global statistics
- Adjust jackpot pool
- Give/remove money from users
- Manual database save/backup
- User count monitoring

### Data Persistence
- Auto-save every 5 minutes
- Manual backup creation
- Loads previous data on restart
- Handles datetime serialization

## Technical Details

### Dependencies
- `python-telegram-bot==20.7` - Telegram bot framework
- Python 3.11+ standard library (json, asyncio, logging, etc.)

### Database Structure
- Users dictionary with detailed player data
- Global statistics tracking
- Jackpot pool management
- Pending deposits tracking
- Rate limiting data

### Error Handling
- Try-catch blocks on all user inputs
- Graceful fallbacks for invalid data
- Comprehensive logging
- User-friendly error messages

## Running the Bot

1. Set environment variable: `BOT_TOKEN="your_token"`
2. Run: `python main.py`
3. Bot will load existing data or create new database
4. Auto-saves every 5 minutes

## Future Enhancements

### Planned Features
- Real cryptocurrency integration (NOWPayments API)
- PostgreSQL database for production
- Tournament system with scheduled competitions
- Web dashboard for analytics
- Multi-language support
- More casino games (slots, poker, baccarat)

### Optimization Ideas
- Redis for caching and rate limiting
- Webhook mode for better performance
- Database connection pooling
- Async database operations

## Notes
- This is currently in simulation mode (no real crypto)
- All transactions are simulated for testing
- Bot token should be kept secret
- Add your Telegram user ID to ADMIN_IDS in config.py for admin access
