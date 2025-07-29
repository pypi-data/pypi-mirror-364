#!/usr/bin/env python3
"""
Professional Flask web application for Anon.
Provides a clean, modern interface for text anonymization.
"""
import os
import sys
import tempfile
import re
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file, session, abort
from werkzeug.utils import secure_filename

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from anonymizer_core import redact
from anonymizer_core.dictionary import (
    add_always_redact_word, 
    remove_always_redact_word, 
    list_always_redact_words
)

# Initialize Flask app
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'anon-dev-key-change-in-production')

# Allowed file extensions
ALLOWED_EXTENSIONS = {'txt'}

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Main application page."""
    return render_template('index.html')

@app.route('/api/v1/anonymize', methods=['POST'])
def anonymize_text():
    """
    API endpoint for text anonymization.
    """
    try:
        if not request.content_type or not request.content_type.startswith('application/json'):
            return jsonify({'error': 'Content-Type must be application/json'}), 415
        try:
            data = request.get_json(force=False, silent=False)
        except Exception:
            return jsonify({'error': 'Malformed JSON'}), 400
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        text = data.get('text', '').strip()
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        options = data.get('options', {})
        include_entity_count = options.get('include_entity_count', True)
        include_mapping = options.get('include_mapping', False)
        
        # Perform anonymization (now includes always redact words from secure storage)
        result = redact(text)
        result_text = result.text
        
        response = {
            'success': True,
            'anonymized_text': result_text,
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0'
        }
        if include_entity_count:
            response['entity_count'] = len(result.mapping)
        if include_mapping:
            response['entities_found'] = list(result.mapping.keys())
        return jsonify(response)
    except Exception as e:
        app.logger.error(f"Anonymization error: {str(e)}")
        return jsonify({'error': 'Anonymization failed', 'details': str(e)}), 500

@app.route('/api/v1/upload', methods=['POST'])
def upload_file():
    """
    Handle file uploads for anonymization.

    Returns the anonymized content as a downloadable file.
    """
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if not allowed_file(file.filename):
            return jsonify({'error': 'Only .txt files are allowed'}), 400

        # Read file content
        content = file.read().decode('utf-8')

        # Perform anonymization (now includes always redact words from secure storage)
        result = redact(content)
        result_text = result.text

        # Create temporary file for download
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp:
            tmp.write(result_text)
            tmp_path = tmp.name

        # Generate safe filename
        original_name = secure_filename(file.filename or "")
        base_name = os.path.splitext(original_name)[0]
        download_name = f"anonymized_{base_name}.txt"

        return send_file(
            tmp_path,
            as_attachment=True,
            download_name=download_name,
            mimetype='text/plain'
        )

    except Exception as e:
        app.logger.error(f"File upload error: {str(e)}")
        return jsonify({'error': 'File processing failed', 'details': str(e)}), 500

@app.route('/api/v1/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'service': 'Anon Web API'
    })

@app.route('/api/v1/info')
def api_info():
    """API information endpoint."""
    return jsonify({
        'name': 'Anon Web API',
        'version': '1.0.0',
        'description': 'Privacy-first text anonymization service',
        'endpoints': {
            'anonymize': '/api/v1/anonymize',
            'upload': '/api/v1/upload',
            'health': '/api/v1/health',
            'always_redact': {
                'list': '/api/v1/always-redact',
                'add': '/api/v1/always-redact/add',
                'remove': '/api/v1/always-redact/remove'
            }
        },
        'features': [
            'Dual-layer anonymization (Presidio + text-anonymizer)',
            'File upload support',
            'Always redact words management (API + CLI)',
            'Real-time file refresh (changes picked up immediately)',
            'RESTful API',
            'Entity counting',
            'Secure file handling'
        ]
    })

@app.route('/api/v1/always-redact', methods=['GET'])
def list_always_redact():
    """
    List all always-redact words.
    """
    try:
        words = list_always_redact_words()
        return jsonify({
            'words': sorted(list(words)),
            'count': len(words)
        })
    except Exception as e:
        return jsonify({'error': f'Failed to list always-redact words: {str(e)}'}), 500

@app.route('/api/v1/always-redact/add', methods=['POST'])
def add_always_redact():
    """
    Add a word to the always-redact list.
    Expected JSON: {"word": "sensitive_term"}
    """
    try:
        if not request.content_type or not request.content_type.startswith('application/json'):
            return jsonify({'error': 'Content-Type must be application/json'}), 415
        
        try:
            data = request.get_json(force=False, silent=False)
        except Exception:
            return jsonify({'error': 'Malformed JSON'}), 400
            
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        word = data.get('word', '').strip()
        if not word:
            return jsonify({'error': 'Word cannot be empty'}), 400
            
        if len(word) > 100:  # Reasonable limit
            return jsonify({'error': 'Word too long (max 100 characters)'}), 400
            
        success = add_always_redact_word(word)
        if success:
            return jsonify({
                'message': f'Successfully added "{word}" to always-redact list',
                'word': word,
                'action': 'added'
            })
        else:
            return jsonify({
                'message': f'"{word}" is already in the always-redact list',
                'word': word,
                'action': 'already_exists'
            })
            
    except Exception as e:
        return jsonify({'error': f'Failed to add word: {str(e)}'}), 500

@app.route('/api/v1/always-redact/remove', methods=['POST'])
def remove_always_redact():
    """
    Remove a word from the always-redact list.
    Expected JSON: {"word": "term_to_remove"}
    """
    try:
        if not request.content_type or not request.content_type.startswith('application/json'):
            return jsonify({'error': 'Content-Type must be application/json'}), 415
        
        try:
            data = request.get_json(force=False, silent=False)
        except Exception:
            return jsonify({'error': 'Malformed JSON'}), 400
            
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        word = data.get('word', '').strip()
        if not word:
            return jsonify({'error': 'Word cannot be empty'}), 400
            
        success = remove_always_redact_word(word)
        if success:
            return jsonify({
                'message': f'Successfully removed "{word}" from always-redact list',
                'word': word,
                'action': 'removed'
            })
        else:
            return jsonify({
                'message': f'"{word}" not found in always-redact list',
                'word': word,
                'action': 'not_found'
            })
            
    except Exception as e:
        return jsonify({'error': f'Failed to remove word: {str(e)}'}), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(413)
def too_large(error):
    """Handle file too large errors."""
    return jsonify({'error': 'File too large (max 16MB)'}), 413

@app.errorhandler(500)
def internal_error(error):
    """Handle internal server errors."""
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Development server
    app.run(host='0.0.0.0', port=8080, debug=False)