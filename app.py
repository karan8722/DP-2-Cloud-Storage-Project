"""
=============================================================================
AI Cloud Smart Storage System - Main Flask Application
=============================================================================
This is the main entry point for the Flask web application.
It handles:
  - File upload (saves to AWS S3 and records metadata in SQLite)
  - File listing and access tracking
  - Analytics dashboard
  - AI-based storage tier prediction

Author: [Your Name]
Final Year Project
=============================================================================
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sqlite3
import os
from datetime import datetime

# Import our custom modules
from cloud.aws_upload import upload_to_s3       # Handles AWS S3 uploads
from ai.predict import predict_storage_tier      # AI prediction function

# ─── Create Flask App ─────────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'  # Required for flash messages

# ─── Database Setup ───────────────────────────────────────────────────────────
DATABASE = 'database/storage.db'

def get_db():
    """
    Connect to the SQLite database.
    SQLite is a simple file-based database - no server needed!
    """
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # This lets us access columns by name
    return conn

def init_db():
    """
    Create the database table if it doesn't exist.
    This runs once when the app starts.
    
    Table columns:
      - id: unique identifier for each file (auto-incremented)
      - file_name: original name of the uploaded file
      - file_size: size in bytes
      - access_count: how many times the file has been accessed
      - last_access: date/time of last access
      - upload_date: when the file was uploaded
      - storage_tier: AI-predicted tier (hot/warm/cold)
      - s3_url: the URL of the file in AWS S3
    """
    os.makedirs('database', exist_ok=True)  # Create folder if not exists
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_name TEXT NOT NULL,
            file_size INTEGER NOT NULL,
            access_count INTEGER DEFAULT 0,
            last_access TEXT,
            upload_date TEXT NOT NULL,
            storage_tier TEXT DEFAULT 'cold',
            s3_url TEXT
        )
    ''')
    conn.commit()
    conn.close()

# ─── Routes ───────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    """
    Home page - shows the file upload form and list of uploaded files.
    """
    conn = get_db()
    files = conn.execute('SELECT * FROM files ORDER BY upload_date DESC').fetchall()
    conn.close()
    return render_template('index.html', files=files)


@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Handle file upload:
    1. Get the file from the form
    2. Upload it to AWS S3
    3. Use AI to predict the storage tier
    4. Save file info to the database
    """
    # Step 1: Check if a file was selected
    if 'file' not in request.files:
        flash('No file selected!', 'error')
        return redirect(url_for('index'))
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No file selected!', 'error')
        return redirect(url_for('index'))
    
    # Step 2: Save file temporarily and get its size
    temp_path = os.path.join('uploads', file.filename)
    os.makedirs('uploads', exist_ok=True)
    file.save(temp_path)
    file_size = os.path.getsize(temp_path)
    
    # Step 3: Upload to AWS S3
    s3_url = upload_to_s3(temp_path, file.filename)
    
    # Step 4: Use AI model to predict storage tier
    # New files start with access_count = 0, so they'll be "cold"
    storage_tier = predict_storage_tier(access_count=0, file_size=file_size)
    
    # Step 5: Save file metadata to database
    conn = get_db()
    conn.execute('''
        INSERT INTO files (file_name, file_size, access_count, last_access, upload_date, storage_tier, s3_url)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        file.filename,
        file_size,
        0,                                           # access_count starts at 0
        datetime.now().strftime('%Y-%m-%d %H:%M'),   # current time
        datetime.now().strftime('%Y-%m-%d %H:%M'),   # upload time
        storage_tier,                                 # AI prediction
        s3_url                                        # S3 URL
    ))
    conn.commit()
    conn.close()
    
    # Clean up temporary file
    os.remove(temp_path)
    
    flash(f'File "{file.filename}" uploaded successfully! Storage tier: {storage_tier}', 'success')
    return redirect(url_for('index'))


@app.route('/access/<int:file_id>')
def access_file(file_id):
    """
    Simulate accessing a file:
    - Increments the access count
    - Updates last access time
    - Re-predicts the storage tier using AI
    
    In a real system, this would download/stream the file from S3.
    """
    conn = get_db()
    
    # Get current file info
    file = conn.execute('SELECT * FROM files WHERE id = ?', (file_id,)).fetchone()
    
    if file:
        new_access_count = file['access_count'] + 1
        
        # Re-predict storage tier with updated access count
        new_tier = predict_storage_tier(
            access_count=new_access_count,
            file_size=file['file_size']
        )
        
        # Update the database
        conn.execute('''
            UPDATE files 
            SET access_count = ?, last_access = ?, storage_tier = ?
            WHERE id = ?
        ''', (
            new_access_count,
            datetime.now().strftime('%Y-%m-%d %H:%M'),
            new_tier,
            file_id
        ))
        conn.commit()
        flash(f'File accessed! New tier: {new_tier} (access count: {new_access_count})', 'info')
    
    conn.close()
    return redirect(url_for('index'))


@app.route('/dashboard')
def dashboard():
    """
    Analytics dashboard page.
    Calculates statistics and sends them to the template.
    """
    conn = get_db()
    files = conn.execute('SELECT * FROM files').fetchall()
    
    # ── Calculate Statistics ──────────────────────────────────────────────
    total_files = len(files)
    total_size = sum(f['file_size'] for f in files)  # in bytes
    total_size_mb = round(total_size / (1024 * 1024), 2)  # convert to MB
    
    # Count files in each storage tier
    hot_count = sum(1 for f in files if f['storage_tier'] == 'hot')
    warm_count = sum(1 for f in files if f['storage_tier'] == 'warm')
    cold_count = sum(1 for f in files if f['storage_tier'] == 'cold')
    
    # Calculate estimated monthly cost (based on AWS S3 pricing)
    # Hot: $0.023/GB, Warm: $0.0125/GB, Cold: $0.004/GB
    hot_size_gb = sum(f['file_size'] for f in files if f['storage_tier'] == 'hot') / (1024**3)
    warm_size_gb = sum(f['file_size'] for f in files if f['storage_tier'] == 'warm') / (1024**3)
    cold_size_gb = sum(f['file_size'] for f in files if f['storage_tier'] == 'cold') / (1024**3)
    
    estimated_cost = round(
        hot_size_gb * 0.023 + warm_size_gb * 0.0125 + cold_size_gb * 0.004, 4
    )
    
    # Total accesses across all files
    total_accesses = sum(f['access_count'] for f in files)
    
    conn.close()
    
    return render_template('dashboard.html',
        total_files=total_files,
        total_size_mb=total_size_mb,
        hot_count=hot_count,
        warm_count=warm_count,
        cold_count=cold_count,
        estimated_cost=estimated_cost,
        total_accesses=total_accesses,
        files=files
    )


@app.route('/api/stats')
def api_stats():
    """
    API endpoint that returns statistics as JSON.
    Used by the dashboard's Chart.js charts.
    """
    conn = get_db()
    files = conn.execute('SELECT * FROM files').fetchall()
    
    hot_count = sum(1 for f in files if f['storage_tier'] == 'hot')
    warm_count = sum(1 for f in files if f['storage_tier'] == 'warm')
    cold_count = sum(1 for f in files if f['storage_tier'] == 'cold')
    
    # Get top 10 most accessed files for bar chart
    top_files = sorted(files, key=lambda f: f['access_count'], reverse=True)[:10]
    
    conn.close()
    
    return jsonify({
        'tier_distribution': {
            'hot': hot_count,
            'warm': warm_count,
            'cold': cold_count
        },
        'top_files': [
            {'name': f['file_name'], 'accesses': f['access_count']}
            for f in top_files
        ]
    })


# ─── Start the Application ───────────────────────────────────────────────────
if __name__ == '__main__':
    init_db()          # Create database table on startup
    app.run(debug=True, port=5000)  # Run on http://localhost:5000
