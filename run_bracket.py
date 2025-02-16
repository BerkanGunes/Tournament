def run_bracket(elements, history):
    """
    Turnuva başlatır ve eşit tur ve puana sahip olanları eşleştirir.
    """
    round_number = 1

    while True:
        print(f"\n--- Round {round_number}: ---")
        grouped = {}
        for element in elements:
            key = (element["tur"], element["puan"])
            grouped.setdefault(key, []).append(element)

        next_round = []
        changes_made = False

        for key, group in grouped.items():
            for i in range(0, len(group), 2):
                if i + 1 < len(group):
                    elem1 = group[i]
                    elem2 = group[i + 1]
                    if "BOŞ" in elem1["isim"] or "BOŞ" in elem2["isim"]:
                        winner = elem1 if "BOŞ" not in elem1["isim"] else elem2
                        loser = elem2 if "BOŞ" not in elem1["isim"] else elem1
                        winner["puan"] += 1
                        loser["puan"] -= 1
                        winner["tur"] += 1
                        loser["tur"] += 1
                        next_round.extend([winner, loser])
                        
                        
                        if "BOŞ" not in winner["isim"] and "BOŞ" not in loser["isim"]:
                            history.record_match(round_number, elem1, elem2, winner, loser)
                        
                        changes_made = True
                        continue

                    print(f"\n1: {elem1['isim']} (Puan: {elem1['puan']}, Tur: {elem1['tur']}) vs 2: {elem2['isim']} (Puan: {elem2['puan']}, Tur: {elem2['tur']})")
                    
                    
                    previous_winner = history.get_previous_match_winner(elem1["isim"], elem2["isim"])
                    if previous_winner:
                        print(f"Bu oyuncular daha önce karşılaşmış. Önceki sonuç kullanılıyor: {previous_winner} kazandı.")
                        winner = elem1 if elem1["isim"] == previous_winner else elem2
                        loser = elem2 if elem1["isim"] == previous_winner else elem1
                    else:
                        choice = input("Hangisini seçiyorsunuz? (1 veya 2): ").strip()

                        while choice not in ['1', '2']:
                            print("Geçersiz seçim. Lütfen 1 veya 2 seçin.")
                            choice = input("Hangisini seçiyorsunuz? (1 veya 2): ").strip()

                        winner = elem1 if choice == '1' else elem2
                        loser = elem2 if choice == '1' else elem1
                    
                    winner["puan"] += 1
                    loser["puan"] -= 1
                    elem1["tur"] += 1
                    elem2["tur"] += 1
                    next_round.extend([elem1, elem2])
                    
                    
                    history.record_match(round_number, elem1, elem2, winner, loser)
                    
                    changes_made = True
                else:
                    elem = group[i]
                    elem["tur"] += 1
                    next_round.append(elem)

        elements = next_round
        round_number += 1

        if not changes_made:
            break

   
    real_elements = [elem for elem in elements if "BOŞ" not in elem["isim"]]
    real_elements.sort(key=lambda x: x["puan"], reverse=True)
    
    
    history.record_final_standings(real_elements)
    
    print("\nTurnuva sona erdi! Sonuçlar:")
    for elem in real_elements:
        print(f"{elem['isim']}: Puan = {elem['puan']}, Tur = {elem['tur']}")

    return elements


