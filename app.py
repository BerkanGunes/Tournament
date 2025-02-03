from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
from werkzeug.utils import secure_filename
from tournament_history import TournamentHistory
import random
import math

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Required for flashing messages and sessions

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create uploads folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def fill_participants(elements):
    """Katılımcı sayısını 2'nin kuvveti olacak şekilde BOŞ elemanlarla tamamlar"""
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

def parse_contestants(file_path):
    contestants = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            name = line.strip()
            if name:  # Skip empty lines
                contestants.append({"isim": name, "puan": 0, "tur": 0})
    return contestants

def get_next_match(contestants):
    """Get next match based on points and rounds"""
    # Group contestants by tour and points
    grouped = {}
    for contestant in contestants:
        key = (contestant["tur"], contestant["puan"])
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(contestant)
    
    # Find first group with at least 2 contestants
    for key in sorted(grouped.keys()):
        group = grouped[key]
        if len(group) >= 2:
            return {
                "player1": group[0],
                "player2": group[1]
            }
    
    return None

@app.route('/')
def index():
    history = TournamentHistory()
    tournaments = history.get_tournament_history()
    return render_template('index.html', tournaments=tournaments)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('Dosya seçilmedi')
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        flash('Dosya seçilmedi')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Parse contestants and start tournament
        contestants = parse_contestants(filepath)
        if len(contestants) < 2:
            flash('En az 2 katılımcı gerekli')
            return redirect(url_for('index'))
        
        # Fill with BOŞ contestants if needed
        contestants = fill_participants(contestants)
        
        # Store contestants in session
        session['contestants'] = contestants
        session['filename'] = filename
        
        # Initialize tournament history
        history = TournamentHistory()
        history.start_new_tournament(contestants)
        
        return redirect(url_for('tournament'))
    
    flash('Geçersiz dosya tipi')
    return redirect(url_for('index'))

@app.route('/tournament')
def tournament():
    if 'contestants' not in session:
        flash('Önce turnuva başlatmalısınız')
        return redirect(url_for('index'))
    
    contestants = session['contestants']
    current_match = get_next_match(contestants)
    history = TournamentHistory()
    
    return render_template('tournament.html', 
                         contestants=contestants,
                         current_match=current_match)

@app.route('/match', methods=['POST'])
def record_match():
    if 'contestants' not in session:
        flash('Turnuva bulunamadı')
        return redirect(url_for('index'))
    
    winner_name = request.form.get('winner')
    contestants = session['contestants']
    
    # Find winner and loser
    winner = None
    loser = None
    for contestant in contestants:
        if contestant["isim"] == winner_name:
            winner = contestant
        elif contestant["isim"] in [request.form.get('player1'), request.form.get('player2')]:
            loser = contestant
    
    if winner and loser:
        # Update points and rounds
        winner["puan"] += 1
        loser["puan"] -= 1
        winner["tur"] += 1
        loser["tur"] += 1
        
        # Record match in history
        history = TournamentHistory()
        history.record_match(winner["tur"], winner, loser, winner, loser)
        
        # Update session
        session['contestants'] = contestants
        
        # Check if tournament is finished
        current_match = get_next_match(contestants)
        if not current_match:
            # Sort contestants by points
            real_contestants = [c for c in contestants if "BOŞ" not in c["isim"]]
            real_contestants.sort(key=lambda x: x["puan"], reverse=True)
            
            # Record final standings
            history.record_final_standings(real_contestants)
            history.save_tournament()
            
            # Clear session
            session.pop('contestants', None)
            session.pop('filename', None)
            
            flash('Turnuva tamamlandı!')
            return redirect(url_for('index'))
    
    return redirect(url_for('tournament'))

if __name__ == '__main__':
    app.run(debug=True) 