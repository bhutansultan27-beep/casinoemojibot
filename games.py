import random
from typing import List, Optional, Tuple


class RouletteGame:
    
    RED_NUMBERS = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
    BLACK_NUMBERS = [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35]
    
    @staticmethod
    def spin() -> int:
        return random.randint(0, 36)
    
    @staticmethod
    def get_color(number: int) -> str:
        if number == 0:
            return "🟢"
        return "🔴" if number in RouletteGame.RED_NUMBERS else "⚫"
    
    @staticmethod
    def calculate_payout(bet_type: str, bet_number: Optional[int], result: int, amount: float) -> float:
        if bet_type == "number" and bet_number == result:
            return amount * 35
        elif bet_type == "red" and result in RouletteGame.RED_NUMBERS:
            return amount
        elif bet_type == "black" and result in RouletteGame.BLACK_NUMBERS:
            return amount
        elif bet_type == "odd" and result % 2 == 1 and result != 0:
            return amount
        elif bet_type == "even" and result % 2 == 0 and result != 0:
            return amount
        elif bet_type == "dozen":
            if bet_number == 1 and 1 <= result <= 12:
                return amount * 2
            elif bet_number == 2 and 13 <= result <= 24:
                return amount * 2
            elif bet_number == 3 and 25 <= result <= 36:
                return amount * 2
        return 0.0


class BlackjackGame:
    
    CARD_VALUES = {
        'A': 11, '2': 2, '3': 3, '4': 4, '5': 5,
        '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
        'J': 10, 'Q': 10, 'K': 10
    }
    
    @staticmethod
    def deal_card() -> str:
        return random.choice(list(BlackjackGame.CARD_VALUES.keys()))
    
    @staticmethod
    def calculate_hand_value(cards: List[str]) -> int:
        value = sum(BlackjackGame.CARD_VALUES[card] for card in cards)
        aces = cards.count('A')
        
        while value > 21 and aces > 0:
            value -= 10
            aces -= 1
        
        return value
    
    @staticmethod
    def is_blackjack(cards: List[str]) -> bool:
        return len(cards) == 2 and BlackjackGame.calculate_hand_value(cards) == 21


class BasketballGame:
    
    @staticmethod
    def shoot() -> bool:
        return random.random() < 0.55
    
    @staticmethod
    def calculate_payout(prediction: str, result: bool, amount: float) -> float:
        if (prediction == "score" and result) or (prediction == "miss" and not result):
            return amount * 1.8
        return 0.0


class SoccerGame:
    
    @staticmethod
    def kick() -> bool:
        return random.random() < 0.45
    
    @staticmethod
    def calculate_payout(prediction: str, result: bool, amount: float) -> float:
        if (prediction == "goal" and result) or (prediction == "save" and not result):
            return amount * 2
        return 0.0


class BowlingGame:
    
    @staticmethod
    def roll() -> str:
        roll = random.random()
        if roll < 0.10:
            return "strike"
        elif roll < 0.50:
            return "spare"
        return "miss"
    
    @staticmethod
    def calculate_payout(prediction: str, result: str, amount: float) -> float:
        if prediction == "strike" and result == "strike":
            return amount * 20
        elif prediction == "spare" and result in ["spare", "miss"]:
            return amount
        return 0.0


class CrashGame:
    
    @staticmethod
    def generate_multiplier() -> float:
        rand = random.random()
        
        if rand < 0.33:
            return round(random.uniform(1.0, 1.5), 2)
        elif rand < 0.66:
            return round(random.uniform(1.5, 3.0), 2)
        elif rand < 0.90:
            return round(random.uniform(3.0, 10.0), 2)
        else:
            return round(random.uniform(10.0, 50.0), 2)
    
    @staticmethod
    def did_crash(multiplier: float, cashout_at: float) -> Tuple[bool, float]:
        if cashout_at <= multiplier:
            return True, cashout_at
        return False, 0.0


class DiceGame:
    
    @staticmethod
    def roll() -> int:
        return random.randint(1, 6)
    
    @staticmethod
    def calculate_payout(prediction: str, result: int, amount: float) -> float:
        if prediction == "specific":
            return amount * 5
        elif prediction == "high" and result >= 4:
            return amount * 1.5
        elif prediction == "low" and result <= 3:
            return amount * 1.5
        elif prediction == "even" and result % 2 == 0:
            return amount
        elif prediction == "odd" and result % 2 == 1:
            return amount
        return 0.0


class CoinFlipGame:
    
    @staticmethod
    def flip() -> str:
        return random.choice(['heads', 'tails'])
    
    @staticmethod
    def calculate_payout(prediction: str, result: str, amount: float) -> float:
        if prediction == result:
            return amount
        return 0.0
