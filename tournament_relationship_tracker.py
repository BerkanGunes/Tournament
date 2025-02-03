    def _update_transitive_relationships(self):
        
        matrix = self.history["relationship_matrix"]
        players = list(matrix.keys())
        
        changes_made = True
        while changes_made:
            changes_made = False
            for a in players:
                for b in players:
                    if matrix[a].get(b, 0) == 1:  # If A beats B
                        for c in players:
                            if matrix[b].get(c, 0) == 1:  # And B beats C
                                if matrix[a].get(c, 0) != 1:  # Then A should beat C
                                    matrix[a][c] = 1
                                    changes_made = True
                                    print(f"\nOtomatik İlişki Bulundu!")
                                    print(f"→ {a} > {c}")
                                    print(f"  (Çünkü: {a} > {b} > {c})")

    def display_relationship_matrix(self):
        """Display the relationship matrix in terminal with colored wins"""
        if not self.history.get("relationship_matrix"):
            print("\nMatris henüz oluşturulmadı.")
            return

        matrix = self.history["relationship_matrix"]
        players = sorted(list(matrix.keys()))

        print("\nİlişki Matrisi (Relationship Matrix):")
        print("-" * 80)
        
        # Print header with player names
        print(f"{'':20}", end="")
        for p in players:
            print(f"{p[:15]:15}", end=" ")
        print("\n" + "-" * 80)
        
        # Print matrix rows with colored wins
        for p1 in players:
            print(f"{p1[:20]:20}", end="")
            for p2 in players:
                value = matrix[p1].get(p2, 0)
                if p1 == p2:
                    print(f"{'X':15}", end=" ")  # Diagonal
                elif value == 1:
                    print(f"\033[92m{'WIN':15}\033[0m", end=" ")  # Green for wins
                else:
                    print(f"{'':15}", end=" ")  # Empty for no relationship
            print()
        print("-" * 80)
        
        # Print transitive relationships if any exist
        transitive_found = False
        for p1 in players:
            for p2 in players:
                for p3 in players:
                    if (matrix[p1].get(p2, 0) == 1 and 
                        matrix[p2].get(p3, 0) == 1 and 
                        matrix[p1].get(p3, 0) == 1):
                        if not transitive_found:
                            print("\nGeçişli İlişkiler (Transitive Relationships):")
                            transitive_found = True
                        print(f"• {p1} > {p2} > {p3}")
        if transitive_found:
            print("-" * 80) 