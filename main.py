from tournament_history import TournamentHistory
import random
from fill_participants import fill_participants
from run_bracket import run_bracket

def main():
    print("Puan ve Tur Sistemli Turnuvaya Hoş Geldiniz!")

    
    history = TournamentHistory()

    
    elements = [
        {"isim": "1", "puan": 0, "tur": 0},
        {"isim": "2", "puan": 0, "tur": 0},
        {"isim": "3", "puan": 0, "tur": 0},
        {"isim": "4", "puan": 0, "tur": 0},
        {"isim": "5", "puan": 0, "tur": 0},
        {"isim": "6", "puan": 0, "tur": 0},
        {"isim": "7", "puan": 0, "tur": 0},
        {"isim": "8", "puan": 0, "tur": 0}
        
    ]

    
    random.shuffle(elements)
    
    
    history.start_new_tournament(elements)
    
    
    elements = fill_participants(elements)

    print("\nKatılımcılar:")
    for elem in elements:
        if "BOŞ" not in elem["isim"]:
            print(f"- {elem['isim']}")

    run_bracket(elements, history)
    
    history.save_tournament()
    
    print("\nTurnuva kaydedildi! Sonuçları tournament_records.json dosyasında bulabilirsiniz.")

if __name__ == "__main__":
    main()