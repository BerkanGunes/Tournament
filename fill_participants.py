import math
def fill_participants(elements):
    """
    Katılımcı sayısını 2'nin kuvveti olacak şekilde BOŞ elemanlarla tamamlar
    """
    n = len(elements)
    next_power_of_2 = 2 ** math.ceil(math.log2(n))
    empty_slots = next_power_of_2 - n
    
    for i in range(empty_slots):
        elements.append({
            "isim": f"BOŞ_{i}", 
            "puan": -500 - i, 
            "tur": 0
        })
    
    return elements