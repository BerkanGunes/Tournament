import json
from datetime import datetime
import os

class TournamentHistory:
    def __init__(self, filename="data/tournament_records.json"):
        self.filename = filename
        self.current_tournament = None
        self.history = {"tournaments": [], "relationship_matrix": {}}
        self.load_history()

    def load_history(self):
        """Load existing tournament history"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
            except json.JSONDecodeError:
                pass

    def start_new_tournament(self, contestants):
        """Start a new tournament"""
        self.current_tournament = {
            "id": len(self.history["tournaments"]) + 1,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "participants": [
                {"name": c["isim"], "initial_points": c["puan"]} 
                for c in contestants if "BOŞ" not in c["isim"]
            ],
            "matches": [],
            "final_standings": []
        }

    def record_match(self, winner, loser):
        """Record a match result"""
        if not self.current_tournament:
            return

        match = {
            "round": max(winner["tur"], loser["tur"]),
            "winner": winner["isim"],
            "loser": loser["isim"],
            "winner_points": winner["puan"],
            "loser_points": loser["puan"]
        }
        self.current_tournament["matches"].append(match)
        self._update_relationship_matrix(winner["isim"], loser["isim"])

    def _update_relationship_matrix(self, winner, loser):
        """Update the relationship matrix"""
        matrix = self.history.setdefault("relationship_matrix", {})
        
        # Initialize if needed
        for player in [winner, loser]:
            if player not in matrix:
                matrix[player] = {}
        
        # Record the win
        matrix[winner][loser] = 1
        
        # Update transitive relationships
        self._update_transitive_relationships()

    def _update_transitive_relationships(self):
        """Update transitive relationships in matrix"""
        matrix = self.history["relationship_matrix"]
        players = list(matrix.keys())
        
        changes_made = True
        while changes_made:
            changes_made = False
            for a in players:
                for b in players:
                    for c in players:
                        # If c beats a and a beats b, then c should beat b
                        if (c in matrix and a in matrix[c] and matrix[c][a] == 1 and
                            a in matrix and b in matrix[a] and matrix[a][b] == 1):
                            if b not in matrix[c] or matrix[c][b] != 1:
                                matrix[c][b] = 1
                                changes_made = True

    def record_final_standings(self, standings):
        """Record final tournament standings"""
        if not self.current_tournament:
            return

        self.current_tournament["final_standings"] = [
            {
                "position": i + 1,
                "name": player["isim"],
                "final_points": player["puan"],
                "rounds_played": player["tur"]
            }
            for i, player in enumerate(standings)
            if "BOŞ" not in player["isim"]
        ]

    def save_tournament(self):
        """Save current tournament to history"""
        if self.current_tournament:
            self.history["tournaments"].append(self.current_tournament)
            os.makedirs(os.path.dirname(self.filename), exist_ok=True)
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=4, ensure_ascii=False)
            self.current_tournament = None

    def get_matrix_display(self):
        """Get relationship matrix for display"""
        matrix = self.history["relationship_matrix"]
        if not matrix:
            return None
            
        players = sorted(matrix.keys())
        display_data = {
            "players": players,
            "matrix": [[matrix.get(p1, {}).get(p2, 0) for p2 in players] for p1 in players]
        }
        return display_data 