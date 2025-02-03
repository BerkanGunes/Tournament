import math
import random

class Tournament:
    def __init__(self):
        self.contestants = []
        self.current_round = 1

    def add_contestants(self, names):
        """Add contestants from a list of names"""
        self.contestants = [{"isim": name, "puan": 0, "tur": 0} for name in names]
        self.fill_with_empty_slots()
        return self.contestants

    def fill_with_empty_slots(self):
        """Fill with BOŞ contestants to reach next power of 2"""
        n = len(self.contestants)
        next_power_of_2 = 2 ** math.ceil(math.log2(n))
        empty_slots = next_power_of_2 - n
        
        for i in range(empty_slots):
            self.contestants.append({
                "isim": f"BOŞ_{i}", 
                "puan": -500 - i,
                "tur": 0
            })

    def get_next_match(self):
        """Get next match based on points and rounds"""
        grouped = {}
        for contestant in self.contestants:
            key = (contestant["tur"], contestant["puan"])
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(contestant)
        
        for key in sorted(grouped.keys()):
            group = grouped[key]
            if len(group) >= 2:
                return {
                    "player1": group[0],
                    "player2": group[1]
                }
        
        return None

    def record_match_result(self, winner_name, player1_name, player2_name):
        """Record a match result"""
        winner = None
        loser = None
        
        for contestant in self.contestants:
            if contestant["isim"] == winner_name:
                winner = contestant
            elif contestant["isim"] in [player1_name, player2_name]:
                loser = contestant
        
        if winner and loser:
            winner["puan"] += 1
            loser["puan"] -= 1
            winner["tur"] += 1
            loser["tur"] += 1
            return True
        
        return False

    def get_standings(self):
        """Get current standings (excluding BOŞ contestants)"""
        real_contestants = [c for c in self.contestants if "BOŞ" not in c["isim"]]
        return sorted(real_contestants, key=lambda x: x["puan"], reverse=True)

    def is_tournament_finished(self):
        """Check if tournament is finished"""
        return self.get_next_match() is None 