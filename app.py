from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, session
import sqlite3
from PIL import Image
import os
import time
from functools import wraps
from dotenv import load_dotenv
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_limiter.errors import RateLimitExceeded

load_dotenv()

def is_rate_limit_enabled():
    try:
        with open('.env-limit', 'r') as f:
            return f.read().strip().lower() == 'true'
    except:
        return True

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

UPLOAD_FOLDER = 'static/covers'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.secret_key = os.getenv('ADMIN_PASSWORD')
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "100 per hour"],
    storage_uri="memory://"
)

@app.errorhandler(RateLimitExceeded)
def handle_ratelimit_error(e):
    flash(str(e.description))
    return redirect(url_for('index'))

def dynamic_limiter():
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if is_rate_limit_enabled():
                return limiter.limit("5 per minute")(f)(*args, **kwargs)
            return f(*args, **kwargs)
        return wrapped
    return decorator

def init_db():
    conn = sqlite3.connect('albums.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS albums
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
         artist_name TEXT NOT NULL,
         album_name TEXT NOT NULL,
         cover_path TEXT NOT NULL,
         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
@dynamic_limiter()
def index():
    conn = sqlite3.connect('albums.db')
    c = conn.cursor()
    c.execute('SELECT * FROM albums ORDER BY created_at DESC')
    albums = [
        {
            'id': row[0],
            'artist_name': row[1],
            'album_name': row[2],
            'cover_url': f'/static/covers/{os.path.basename(row[3])}'
        }
        for row in c.fetchall()
    ]
    conn.close()
    return render_template('main.html', albums=albums)

@app.route('/upload', methods=['POST'])
@limiter.limit("2 per hour", error_message="You can only upload 2 album covers per hour. Please try again later.")
def upload():
    if 'cover' not in request.files:
        flash('Please select a file')
        return redirect(url_for('index'))
    
    file = request.files['cover']
    artist_name = request.form.get('artist_name')
    album_name = request.form.get('album_name')
    
    if not file or not artist_name or not album_name:
        flash('Please fill in all fields')
        return redirect(url_for('index'))
    
    try:
        img = Image.open(file)
        if img.size != (1920, 1920):
            flash('Image must be 1920x1920 pixels')
            return redirect(url_for('index'))
        
        file_name = f"{int(time.time())}_{file.filename.replace(' ', '_')}"
        file_path = os.path.join(UPLOAD_FOLDER, file_name)
        
        img = img.convert('RGBA')
        img.save(file_path, format='PNG', optimize=True)
        
        conn = sqlite3.connect('albums.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO albums (artist_name, album_name, cover_path)
            VALUES (?, ?, ?)
        ''', (artist_name, album_name, file_path))
        conn.commit()
        conn.close()
        
        flash('Album cover uploaded successfully')
    except Exception as e:
        print(f"Error: {e}")
        flash('An error occurred')
    
    return redirect(url_for('index'))

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == os.getenv('ADMIN_PASSWORD'):
            session['admin_logged_in'] = True
            flash('Welcome, Administrator')
            return redirect(url_for('admin_panel'))
        flash('Invalid password')
    return render_template('admin_login.html')

@app.route('/admin')
@admin_required
def admin_panel():
    conn = sqlite3.connect('albums.db')
    c = conn.cursor()
    c.execute('SELECT * FROM albums ORDER BY created_at DESC')
    albums = [
        {
            'id': row[0],
            'artist_name': row[1],
            'album_name': row[2],
            'cover_url': f'/static/covers/{os.path.basename(row[3])}',
            'cover_path': row[3]
        }
        for row in c.fetchall()
    ]
    conn.close()
    return render_template('admin_panel.html', albums=albums)

@app.route('/admin/delete/<int:id>', methods=['POST'])
@admin_required
def delete_album(id):
    try:
        conn = sqlite3.connect('albums.db')
        c = conn.cursor()
        
        c.execute('SELECT cover_path FROM albums WHERE id = ?', (id,))
        cover_path = c.fetchone()[0]
        
        c.execute('DELETE FROM albums WHERE id = ?', (id,))
        conn.commit()
        conn.close()
        
        if os.path.exists(cover_path):
            os.remove(cover_path)
        
        flash('Album deleted successfully')
    except Exception as e:
        print(f"Error: {e}")
        flash('An error occurred')
    
    return redirect(url_for('admin_panel'))

@app.route('/admin/logout')
@admin_required
def admin_logout():
    session.clear()
    flash('Logged out successfully')
    return redirect(url_for('admin_login'))

if __name__ == '__main__':
    app.run(debug=True)