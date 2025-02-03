from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
from werkzeug.utils import secure_filename
from models.tournament import Tournament
from models.history import TournamentHistory

app = Flask(__name__, 
           template_folder='templates',
           static_folder='static')
app.secret_key = 'your_secret_key_here'

# Configure upload folder
UPLOAD_FOLDER = '../data/uploads'
ALLOWED_EXTENSIONS = {'txt'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create required directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_contestants(file_path):
    """Load contestants from file"""
    names = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            name = line.strip()
            if name:
                names.append(name)
    return names

@app.route('/')
def index():
    history = TournamentHistory()
    return render_template('index.html', tournaments=history.history)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('Dosya seçilmedi')
        return redirect(url_for('index'))
    
    file = request.files['file']
    if file.filename == '':
        flash('Dosya seçilmedi')
        return redirect(url_for('index'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Start new tournament
        names = load_contestants(filepath)
        if len(names) < 2:
            flash('En az 2 katılımcı gerekli')
            return redirect(url_for('index'))
        
        # Initialize tournament
        tournament = Tournament()
        contestants = tournament.add_contestants(names)
        
        # Store in session
        session['tournament_state'] = {
            'contestants': contestants,
            'filename': filename
        }
        
        # Initialize history
        history = TournamentHistory()
        history.start_new_tournament(contestants)
        
        return redirect(url_for('tournament'))
    
    flash('Geçersiz dosya tipi')
    return redirect(url_for('index'))

@app.route('/tournament')
def tournament():
    if 'tournament_state' not in session:
        flash('Önce turnuva başlatmalısınız')
        return redirect(url_for('index'))
    
    state = session['tournament_state']
    tournament = Tournament()
    tournament.contestants = state['contestants']
    
    current_match = tournament.get_next_match()
    history = TournamentHistory()
    matrix = history.get_matrix_display()
    
    return render_template('tournament.html',
                         contestants=tournament.contestants,
                         current_match=current_match,
                         matrix=matrix)

@app.route('/match', methods=['POST'])
def record_match():
    if 'tournament_state' not in session:
        flash('Turnuva bulunamadı')
        return redirect(url_for('index'))
    
    state = session['tournament_state']
    tournament = Tournament()
    tournament.contestants = state['contestants']
    
    winner_name = request.form.get('winner')
    player1_name = request.form.get('player1')
    player2_name = request.form.get('player2')
    
    if tournament.record_match_result(winner_name, player1_name, player2_name):
        # Update session
        session['tournament_state']['contestants'] = tournament.contestants
        
        # Record in history
        history = TournamentHistory()
        winner = next(c for c in tournament.contestants if c["isim"] == winner_name)
        loser = next(c for c in tournament.contestants if c["isim"] in [player1_name, player2_name] and c["isim"] != winner_name)
        history.record_match(winner, loser)
        
        # Check if tournament is finished
        if tournament.is_tournament_finished():
            standings = tournament.get_standings()
            history.record_final_standings(standings)
            history.save_tournament()
            
            session.pop('tournament_state', None)
            flash('Turnuva tamamlandı!')
            return redirect(url_for('index'))
    
    return redirect(url_for('tournament'))

if __name__ == '__main__':
    app.run(debug=True, port=5001) 