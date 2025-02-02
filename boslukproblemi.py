import math

# Katılımcı listesini tamamlayan fonksiyon
# Eğer katılımcı sayısı 2^n değilse, eksik yerleri "BOŞ" ile doldurur
def fill_participants(participants):
    n = len(participants)
    next_power_of_2 = 2 ** math.ceil(math.log2(n))  # En yakın 2'nin kuvvetini hesapla
    empty_slots = next_power_of_2 - n  # Eksik sayıyı belirle
    
    for i in range(empty_slots):
        participants.append(f'BOŞ_{i}')  # Boşlukları doldur
    
    return participants

# Katılımcılara sayısal değerler atayan fonksiyon
def assign_numerical_values(participants):
    participant_values = {}
    empty_slot_value = -500  # Boşluklara düşük değer veriyoruz
    
    for p in participants:
        if "BOŞ" in p:
            participant_values[p] = empty_slot_value  # Boş slotlara yüksek değer ata
            empty_slot_value += 1  # Sonraki boş slot için değeri artır
        else:
            participant_values[p] = 0  # Gerçek katılımcılar varsayılan olarak 0 alır, istenirse değiştirilebilir
    
    return participant_values