from flask import Flask, jsonify, request, send_from_directory, send_file
from flask_cors import CORS
import json
import os
from pathlib import Path
import mimetypes

# make sure MIME supports subtitles
mimetypes.add_type('text/vtt', '.vtt')
mimetypes.add_type('application/x-subrip', '.srt')

app = Flask(__name__, static_folder='../frontend', static_url_path='/')
CORS(
    app,
    resources={
        r"/api/*": {
            "origins": "*",
        }
    }
)

# Data file paths
DATA_DIR = Path(__file__).parent.parent / 'data'
DATA_DIR.mkdir(exist_ok=True)
CHANNELS_FILE = DATA_DIR / 'channels.json'
SEASONS_FILE = DATA_DIR / 'seasons.json'

def get_channels():
    """Load TV channels from file"""
    if CHANNELS_FILE.exists():
        with open(CHANNELS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_channels(channels):
    """Save TV channels to file"""
    with open(CHANNELS_FILE, 'w') as f:
        json.dump(channels, f, indent=2)

def get_seasons():
    """Load VOD seasons from file"""
    if SEASONS_FILE.exists():
        with open(SEASONS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_seasons(seasons):
    """Save VOD seasons to file"""
    with open(SEASONS_FILE, 'w') as f:
        json.dump(seasons, f, indent=2)

def get_files_in_folder(folder_path):
    """Get media files from a folder"""
    video_extensions = {'.mp4', '.mkv', '.avi', '.mov', '.flv', '.wmv', '.webm'}
    try:
        files = [f for f in sorted(os.listdir(folder_path)) 
                if os.path.isfile(os.path.join(folder_path, f)) 
                and Path(f).suffix.lower() in video_extensions]
        return files
    except:
        return []

# ==================== TV CHANNELS ROUTES ====================

@app.route('/api/channels', methods=['GET'])
def list_channels():
    """Get all TV channels"""
    channels = get_channels()
    return jsonify(channels)

@app.route('/api/channels', methods=['POST'])
def add_channel():
    """Add a new TV channel"""
    data = request.json
    folder_path = data.get('folder_path')
    channel_name = data.get('name', Path(folder_path).name)
    
    if not os.path.isdir(folder_path):
        return jsonify({'error': 'Folder does not exist'}), 400
    
    channels = get_channels()
    channel_id = str(len(channels) + 1)
    
    channels[channel_id] = {
        'id': channel_id,
        'name': channel_name,
        'folder_path': folder_path
    }
    
    save_channels(channels)
    return jsonify(channels[channel_id]), 201

@app.route('/api/channels/<channel_id>', methods=['DELETE'])
def delete_channel(channel_id):
    """Delete a TV channel"""
    channels = get_channels()
    if channel_id in channels:
        del channels[channel_id]
        save_channels(channels)
        return jsonify({'status': 'deleted'}), 200
    return jsonify({'error': 'Channel not found'}), 404


@app.route('/api/channels/<channel_id>/episodes', methods=['GET'])
def get_channel_episodes(channel_id):
    """Get all episodes/files in a channel"""
    channels = get_channels()
    if channel_id not in channels:
        return jsonify({'error': 'Channel not found'}), 404
    
    folder_path = channels[channel_id]['folder_path']
    files = get_files_in_folder(folder_path)
    
    episodes = [{'index': i, 'filename': f, 'path': os.path.join(folder_path, f)} 
                for i, f in enumerate(files)]
    return jsonify(episodes), 200

# ==================== VOD ROUTES ====================

@app.route('/api/seasons', methods=['GET'])
def list_seasons():
    """Get all VOD seasons"""
    seasons = get_seasons()
    return jsonify(seasons)

@app.route('/api/seasons', methods=['POST'])
def add_season():
    """Add a new VOD season"""
    data = request.json
    season_name = data.get('name', 'Season 1')
    
    seasons = get_seasons()
    season_id = str(len(seasons) + 1)
    
    new_season = {
        'id': season_id,
        'name': season_name,
        'episodes': []
    }
    
    seasons.append(new_season)
    save_seasons(seasons)
    return jsonify(new_season), 201

@app.route('/api/seasons/<season_id>', methods=['DELETE'])
def delete_season(season_id):
    """Delete a VOD season"""
    seasons = get_seasons()
    seasons = [s for s in seasons if s['id'] != season_id]
    save_seasons(seasons)
    return jsonify({'status': 'deleted'}), 200

@app.route('/api/seasons/<season_id>/episodes', methods=['POST'])
def add_episodes_to_season(season_id):
    """Add episodes from a folder to a season"""
    data = request.json
    folder_path = data.get('folder_path')
    
    if not os.path.isdir(folder_path):
        return jsonify({'error': 'Folder does not exist'}), 400
    
    seasons = get_seasons()
    season = next((s for s in seasons if s['id'] == season_id), None)
    
    if not season:
        return jsonify({'error': 'Season not found'}), 404
    
    files = get_files_in_folder(folder_path)
    episode_id = len(season['episodes'])
    
    for filename in files:
        episode_id += 1
        season['episodes'].append({
            'id': str(episode_id),
            'filename': filename,
            'path': os.path.join(folder_path, filename)
        })
    
    save_seasons(seasons)
    return jsonify(season), 200

SHOWS_FILE = DATA_DIR / 'shows.json'


def get_shows():
    if SHOWS_FILE.exists():
        return json.load(open(SHOWS_FILE))
    return []

def save_shows(shows):
    json.dump(shows, open(SHOWS_FILE, 'w'), indent=2)

# ==================== MEDIA SERVING ====================

@app.route('/api/shows', methods=['GET'])
def list_shows_main():
    if SHOWS_FILE.exists():
        return jsonify(json.load(open(SHOWS_FILE)))
    return jsonify([])

@app.route('/api/video/<path:video_path>', methods=['GET'])
def serve_video(video_path):
    from urllib.parse import unquote
    video_path = unquote(video_path)

    """Serve video files with streaming support"""
    # Decode the path
    video_path = video_path.replace('__SLASH__', '/')
    
    # Security check - ensure the file exists and is accessible
    if not os.path.exists(video_path):
        return jsonify({'error': 'File not found'}), 404
    
    # Get range request support
    range_header = request.headers.get('Range')
    
    try:
        file_size = os.path.getsize(video_path)
        
        if range_header:
            # Parse range header
            range_match = range_header.replace('bytes=', '').split('-')
            start = int(range_match[0]) if range_match[0] else 0
            end = int(range_match[1]) if range_match[1] else file_size - 1
            
            if start > file_size or end > file_size:
                return 'Requested range not satisfiable', 416
            
            with open(video_path, 'rb') as f:
                f.seek(start)
                chunk = f.read(end - start + 1)
            
            mime, _ = mimetypes.guess_type(video_path)
            mime = mime or 'application/octet-stream'
            
            return chunk, 206, {
                'Content-Range': f'bytes {start}-{end}/{file_size}',
                'Accept-Ranges': 'bytes',
                'Content-Length': len(chunk),
                'Content-Type': mime,

                # ✅ REQUIRED FOR LAN VIDEO
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Range',
                'Access-Control-Expose-Headers': 'Content-Range, Accept-Ranges'
            }
        else:
            return send_file(video_path, mimetype='video/mp4'), 200
    except:
        return jsonify({'error': 'Error reading file'}), 500

# ==================== FRONTEND ROUTES ====================

@app.route('/')
def index():
    """Serve the main page"""
    return send_from_directory('../frontend', 'index.html')

@app.errorhandler(404)
def not_found(e):
    """Serve index for frontend routes"""
    return send_from_directory('../frontend', 'index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
