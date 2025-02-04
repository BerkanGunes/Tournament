import json
from datetime import datetime
import os

class TournamentHistory:
    def __init__(self, filename="tournament_records.json"):
        self.filename = filename
        self.current_tournament = {
            "id": None,
            "date": None,
            "participants": [],
            "matches": [],
            "final_standings": []
        }
        self.load_history()
        self.previous_matches = {}

    def load_history(self):
        """Load existing tournament history or create new file if it doesn't exist"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
                if "relationship_matrix" not in self.history:
                    self.history["relationship_matrix"] = {}
                self._load_previous_matches()
            except json.JSONDecodeError:
                self.history = {
                    "tournaments": [],
                    "relationship_matrix": {}
                }
        else:
            self.history = {
                "tournaments": [],
                "relationship_matrix": {}
            }

    def _load_previous_matches(self):
        """Load all previous matches into memory for quick lookup"""
        self.previous_matches = {}
        for tournament in self.history["tournaments"]:
            for match in tournament["matches"]:
                player1 = match["player1"]["name"]
                player2 = match["player2"]["name"]
                winner = match["winner"]
                key1 = f"{player1}-{player2}"
                key2 = f"{player2}-{player1}"
                self.previous_matches[key1] = winner
                self.previous_matches[key2] = winner
    def get_previous_match_winner(self, player1_name, player2_name):
        """Check if these players have met before or if there's a transitive relationship"""
        matrix_data = self.history["relationship_matrix"]
        if matrix_data and player1_name in matrix_data["players"] and player2_name in matrix_data["players"]:
            if matrix_data["matrix"][player1_name][player2_name] == 1:
                return player1_name
            elif matrix_data["matrix"][player2_name][player1_name] == 1:
                return player2_name
        key = f"{player1_name}-{player2_name}"
        return self.previous_matches.get(key)

    def update_matrix_for_match(self, player1, player2, winner):
        """Update relationship matrix for a single match"""
        if not self.history["relationship_matrix"]:
            players = set()
            for tournament in self.history["tournaments"]:
                for participant in tournament["participants"]:
                    players.add(participant["name"])
            players.add(player1)
            players.add(player2)
            players = sorted(list(players))
            
            matrix = {}
            for p1 in players:
                matrix[p1] = {p2: 0 for p2 in players}
            
            self.history["relationship_matrix"] = {
                "players": players,
                "matrix": matrix,
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        else:
            matrix_data = self.history["relationship_matrix"]
            matrix = matrix_data["matrix"]
            
            for new_player in [player1, player2]:
                if new_player not in matrix_data["players"]:
                    matrix_data["players"].append(new_player)
                    matrix_data["players"].sort()
                    matrix[new_player] = {p: 0 for p in matrix_data["players"]}
                    for p in matrix_data["players"]:
                        if p != new_player:
                            matrix[p][new_player] = 0

        if winner == player1:
            self.history["relationship_matrix"]["matrix"][player1][player2] = 1
        else:
            self.history["relationship_matrix"]["matrix"][player2][player1] = 1

        self.update_transitive_relationships()
        self.history["relationship_matrix"]["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def update_transitive_relationships(self):
        """Update matrix based on transitive relationships: if (a,b) and (c,a) are 1, then (c,b) should be 1"""
        matrix_data = self.history["relationship_matrix"]
        players = matrix_data["players"]
        matrix = matrix_data["matrix"]
        
        changes_made = True
        while changes_made:
            changes_made = False
            for a in players:
                for b in players:
                    for c in players:
                        # If c beats a (c,a) and a beats b (a,b), then c should beat b (c,b)
                        if matrix[c][a] == 1 and matrix[a][b] == 1:
                            if matrix[c][b] != 1:
                                matrix[c][b] = 1
                                changes_made = True
                                print(f"\nOtomatik İlişki: {c} -> {b} (Geçişli özellik: {c} -> {a} -> {b})")

    
    def start_new_tournament(self, participants):
        """Start recording a new tournament"""
        self.current_tournament = {
            "id": len(self.history["tournaments"]) + 1,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "participants": [{"name": p["isim"], "initial_points": p["puan"]} 
                           for p in participants if "BOŞ" not in p["isim"]],
            "matches": [],
            "final_standings": []
        }

    def record_match(self, round_number, player1, player2, winner, loser):
        """Record a single match result and update the relationship matrix"""
        match = {
            "round": round_number,
            "player1": {
                "name": player1["isim"],
                "points_before": player1["puan"],
                "points_after": player1["puan"] + (1 if player1 == winner else -1)
            },
            "player2": {
                "name": player2["isim"],
                "points_before": player2["puan"],
                "points_after": player2["puan"] + (1 if player2 == winner else -1)
            },
            "winner": winner["isim"]
        }
        self.current_tournament["matches"].append(match)
        
        key1 = f"{player1['isim']}-{player2['isim']}"
        key2 = f"{player2['isim']}-{player1['isim']}"
        self.previous_matches[key1] = winner["isim"]
        self.previous_matches[key2] = winner["isim"]

        self.update_matrix_for_match(player1["isim"], player2["isim"], winner["isim"])
        self.display_relationship_matrix()

    def record_final_standings(self, standings):
        """Record the final tournament standings"""
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

    
    def display_relationship_matrix(self):
        """Display the stored relationship matrix"""
        if not self.history["relationship_matrix"]:
            print("Matris henüz oluşturulmadı.")
            return

        matrix_data = self.history["relationship_matrix"]
        players = matrix_data["players"]
        matrix = matrix_data["matrix"]

        print("\nİlişki Matrisi:")
        print(f"Son Güncelleme: {matrix_data['last_updated']}")
        
        print("\ni/j", end="")
        for i, p in enumerate(players):
            print(f"{i:^5}", end="")
        print()

        for i, p1 in enumerate(players):
            print(f"{i:<3}", end="")
            for p2 in players:
                print(f"{matrix[p1][p2]:^5}", end="")
            print()

        print("\nOyuncu Referansları:")
        for i, player in enumerate(players):
            print(f"{i}: {player}")

    def get_tournament_history(self):
        """Return all tournament history"""
        return self.history

    def get_tournament_by_id(self, tournament_id):
        """Get a specific tournament by ID"""
        for tournament in self.history["tournaments"]:
            if tournament["id"] == tournament_id:
                return tournament
        return None

    def get_player_history(self, player_name):
        """Get all matches and results for a specific player"""
        player_history = {
            "total_matches": 0,
            "wins": 0,
            "losses": 0,
            "tournaments_participated": 0,
            "matches": []
        }

        for tournament in self.history["tournaments"]:
            participated = False
            for match in tournament["matches"]:
                if player_name in [match["player1"]["name"], match["player2"]["name"]]:
                    participated = True
                    player_history["total_matches"] += 1
                    if match["winner"] == player_name:
                        player_history["wins"] += 1
                    else:
                        player_history["losses"] += 1
                    player_history["matches"].append({
                        "tournament_id": tournament["id"],
                        "round": match["round"],
                        "match": match
                    })
            
            if participated:
                player_history["tournaments_participated"] += 1

        return player_history

    def save_tournament(self):
        """Save the current tournament to history"""
        self.history["tournaments"].append(self.current_tournament)
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, indent=4, ensure_ascii=False)
        self.display_relationship_matrix() 