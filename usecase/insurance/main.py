# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import os
import requests
import json
import sqlite3
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a random secret key in production

# Configuration
UPLOAD_FOLDER = 'uploads'
DB_PATH = 'claims.db'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'jpg', 'jpeg', 'png'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32MB max upload size

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Database setup
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        
        # Create claims table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS claims (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            status TEXT NOT NULL,
            repository_name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            llm_answer TEXT DEFAULT '',
            agent_name TEXT DEFAULT ''
        )
        ''')
        
        # Create files table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            claim_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            filepath TEXT NOT NULL,
            filesize INTEGER NOT NULL,
            mimetype TEXT,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            api_document_id TEXT,
            FOREIGN KEY (claim_id) REFERENCES claims (id)
        )
        ''')
        
        conn.commit()

# Initialize database
init_db()

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_all_claims():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM claims ORDER BY created_at DESC')
        return cursor.fetchall()

def get_claim_by_id(claim_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Get claim details
        cursor.execute('SELECT * FROM claims WHERE id = ?', (claim_id,))
        claim = cursor.fetchone()
        
        if claim:
            # Get associated files
            cursor.execute('SELECT * FROM files WHERE claim_id = ?', (claim_id,))
            files = cursor.fetchall()
            
            # Convert claim to dict for easier manipulation
            claim_dict = dict(claim)
            claim_dict['files'] = [dict(file) for file in files]
            
            return claim_dict
        
        return None

def update_file_api_document_id(file_id, api_document_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE files SET api_document_id = ? WHERE id = ?',
            (api_document_id, file_id)
        )
        conn.commit()
def update_llm_answer(claim_id,llm_answer):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE claims SET llm_answer = ?, status = ? WHERE id = ?',
            (llm_answer, 'Processed',claim_id)
        )
        conn.commit()

@app.route('/')
def index():
    claims = get_all_claims()
    return render_template('index.html', claims=claims)

@app.route('/claims/new', methods=['GET', 'POST'])
def new_claim():
    if request.method == 'POST':
        # Get form data
        title = request.form.get('title')
        description = request.form.get('description')
        repository_name = request.form.get('repository_name')
        agent_name = request.form.get('agent_name')
        
        # Validate form data
        if not title or not description or not repository_name or not agent_name:
            flash('All fields are required', 'danger')
            return redirect(url_for('new_claim'))
        
        # Handle file uploads
        uploaded_files = []
        if 'documents' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)
            
        files = request.files.getlist('documents')
        
        if not files or files[0].filename == '':
            flash('No files selected', 'danger')
            return redirect(request.url)
        
        # Insert the claim into the database first to get the ID
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO claims (title, description, status, repository_name,agent_name) VALUES (?, ?, ?, ?,?)',
                (title, description, 'Pending', repository_name,agent_name)
            )
            conn.commit()
            claim_id = cursor.lastrowid
        
        # Create upload directory for this claim
        claim_upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], f'claim_{claim_id}')
        os.makedirs(claim_upload_dir, exist_ok=True)
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            for file in files:
                if file and allowed_file(file.filename):
                    # Get original filename and secure it
                    original_filename = file.filename
                    filename = secure_filename(original_filename)
                    
                    # Create a unique filename to avoid collisions
                    base, extension = os.path.splitext(filename)
                    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                    unique_filename = f"{base}_{timestamp}{extension}"
                    
                    # Save file
                    file_path = os.path.join(claim_upload_dir, unique_filename)
                    file.save(file_path)
                    filesize = os.path.getsize(file_path)
                    mimetype = file.content_type
                    
                    # Insert file info into database
                    cursor.execute(
                        'INSERT INTO files (claim_id, filename, filepath, filesize, mimetype) VALUES (?, ?, ?, ?, ?)',
                        (claim_id, original_filename, file_path, filesize, mimetype)
                    )
                    
                    uploaded_files.append({
                        'filename': original_filename,
                        'path': file_path,
                        'size': filesize,
                        'mimetype': mimetype
                    })
                else:
                    flash(f'File type not allowed for {file.filename}', 'warning')
            
            conn.commit()
        
        if not uploaded_files:
            # If no valid files, delete the claim
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM claims WHERE id = ?', (claim_id,))
                conn.commit()
            
            flash('No valid files uploaded', 'danger')
            return redirect(request.url)
        
        flash(f'Claim created successfully with {len(uploaded_files)} document(s)!', 'success')
        return redirect(url_for('index'))
        
    return render_template('new_claim.html')

@app.route('/claims/<int:claim_id>')
def view_claim(claim_id):
    claim = get_claim_by_id(claim_id)
    if not claim:
        flash('Claim not found', 'danger')
        return redirect(url_for('index'))
    
    return render_template('view_claim.html', claim=claim)

@app.route('/claims/<int:claim_id>/process', methods=['POST'])
def process_claim(claim_id):
    # Find the claim
    claim = get_claim_by_id(claim_id)
    if not claim:
        flash('Claim not found', 'danger')
        return redirect(url_for('index'))
    
    try:
        # Get repository name and files
        repository_name = claim.get('repository_name', 'default_repository')
        agent_name = claim.get('agent_name', 'default_agent')
        files_data = claim.get('files', [])
        
        if not files_data:
            flash('No files found for this claim', 'danger')
            return redirect(url_for('view_claim', claim_id=claim_id))
        
        # Prepare multipart request
        multipart_data = {'repository_name': repository_name,'agent_name':agent_name}
        multipart_files = []
        
        for file_data in files_data:
            file_id = file_data['id']
            filepath = file_data['filepath']
            filename = file_data['filename']
            
            # Check if file exists
            if not os.path.exists(filepath):
                flash(f'File not found: {filename}', 'warning')
                continue
            
            # Prepare file for multipart upload
            with open(filepath, 'rb') as f:
                file_content = f.read()
                multipart_files.append(
                    ('file', (filename, file_content, file_data.get('mimetype', 'application/octet-stream')))
                )
        
                if not multipart_files:
                    flash('No valid files to process', 'danger')
                    return redirect(url_for('view_claim', claim_id=claim_id))
                
                # Send API request
                upload_response = requests.post(
                    "http://localhost:8000/api_upload_document/upload",
                    data=multipart_data,
                    files=multipart_files,
                    timeout=60  # Increase timeout for large uploads
                )
              
             
                if upload_response.status_code != 200:
                    flash(f'Document upload API error: {upload_response.text}', 'danger')
                    return redirect(url_for('view_claim', claim_id=claim_id))
                
                # Get document IDs from response
                upload_data = upload_response.json()
                llm_answer = upload_data.get('llm_answer', 'No Answer')
                
                # Update claim status in database
                with get_db_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        'UPDATE claims SET status = ?, llm_answer = ? WHERE id = ?', 
                        ('Processed',llm_answer, claim_id)
                    )
                    conn.commit()
                
                flash(f'Successfully uploaded  and AI processed documents for processing', 'success')
                
    except requests.exceptions.RequestException as e:
            flash(f'API connection error: {str(e)}', 'danger')
    except Exception as e:
            flash(f'Error processing claim: {str(e)}', 'danger')
        
    return redirect(url_for('view_claim', claim_id=claim_id))

@app.route('/claims/<int:claim_id>/update-status', methods=['POST'])
def update_claim_status(claim_id):
    new_status = request.form.get('status')
    
    if not new_status:
        flash('No status provided', 'danger')
        return redirect(url_for('index'))
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE claims SET status = ? WHERE id = ?',
            (new_status, claim_id)
        )
        conn.commit()
    
    flash(f'Claim status updated to {new_status}', 'success')
    return redirect(url_for('view_claim', claim_id=claim_id))

@app.route('/files/download/<int:file_id>')
def download_file(file_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM files WHERE id = ?', (file_id,))
        file_data = cursor.fetchone()
        
        if not file_data:
            flash('File not found', 'danger')
            return redirect(url_for('index'))
        
        file_path = file_data['filepath']
        original_filename = file_data['filename']
        
        if not os.path.exists(file_path):
            flash('File not found on server', 'danger')
            return redirect(url_for('index'))
        
        return send_file(file_path, as_attachment=True, download_name=original_filename)

@app.route('/api/claims', methods=['GET'])
def api_claims():
    claims = get_all_claims()
    return jsonify([dict(claim) for claim in claims])

@app.route('/api/claims/<int:claim_id>', methods=['GET'])
def api_claim(claim_id):
    claim = get_claim_by_id(claim_id)
    if not claim:
        return jsonify({'error': 'Claim not found'}), 404
    
    return jsonify(claim)

if __name__ == '__main__':
    app.run(debug=True)