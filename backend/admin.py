from flask import Flask, render_template_string, request, jsonify
from flask_cors import CORS
import json
import os
from pathlib import Path
import subprocess
import sys

# Admin Flask app
admin_app = Flask(__name__, template_folder='.')
CORS(admin_app)

# Data file paths
DATA_DIR = Path(__file__).parent.parent / 'data'
DATA_DIR.mkdir(exist_ok=True)
CHANNELS_FILE = DATA_DIR / 'channels.json'
SEASONS_FILE = DATA_DIR / 'seasons.json'
UPLOAD_DIR = Path(__file__).parent.parent / 'frontend' / 'posters'
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

DATA_DIR = Path(__file__).parent.parent / 'data'
DATA_DIR.mkdir(exist_ok=True)
SHOWS_FILE = DATA_DIR / 'shows.json'

def get_shows():
    if SHOWS_FILE.exists():
        return json.load(open(SHOWS_FILE))
    return []

def save_shows(shows):
    json.dump(shows, open(SHOWS_FILE, 'w'), indent=2)

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

# ==================== ADMIN ROUTES ====================

@admin_app.route('/api/shows', methods=['POST'])
def add_show():
    name = request.form['name']
    poster = request.files.get('poster')

    shows = get_shows()
    show_id = str(len(shows) + 1)

    poster_filename = ''
    if poster:
        poster_filename = f"{show_id}_{poster.filename}"
        poster.save(UPLOAD_DIR / poster_filename)

    show = {
        "id": show_id,
        "name": name,
        "poster": poster_filename,
        "seasons": []
    }

    shows.append(show)
    save_shows(shows)
    return jsonify(show), 201


@admin_app.route('/')
def admin_panel():
    """Admin dashboard"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Streaming Admin Panel</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }

            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%);
                color: #e0e0e0;
                min-height: 100vh;
                padding: 2rem;
            }

            .container {
                max-width: 1200px;
                margin: 0 auto;
            }

            h1 {
                text-align: center;
                margin-bottom: 3rem;
                background: linear-gradient(135deg, #00d4ff, #7c3aed);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }

            .section {
                background: rgba(26, 31, 58, 0.8);
                border: 1px solid rgba(124, 58, 237, 0.3);
                border-radius: 10px;
                padding: 2rem;
                margin-bottom: 2rem;
            }

            .section h2 {
                margin-bottom: 1.5rem;
                color: #00d4ff;
                font-size: 1.5rem;
            }

            .form-group {
                margin-bottom: 1.5rem;
            }

            label {
                display: block;
                margin-bottom: 0.5rem;
                color: #a0aec0;
                font-weight: 500;
            }

            input[type="text"],
            input[type="file"],
            select {
                width: 100%;
                padding: 0.8rem;
                background: rgba(15, 23, 42, 0.6);
                border: 1px solid rgba(124, 58, 237, 0.5);
                border-radius: 5px;
                color: #e0e0e0;
                font-size: 1rem;
                transition: all 0.3s ease;
            }

            input[type="text"]:focus,
            input[type="file"]:focus,
            select:focus {
                outline: none;
                border-color: #00d4ff;
                background: rgba(15, 23, 42, 0.9);
            }

            button {
                padding: 0.8rem 1.5rem;
                background: linear-gradient(135deg, #7c3aed, #00d4ff);
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 1rem;
                transition: all 0.3s ease;
            }

            button:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 15px rgba(124, 58, 237, 0.4);
            }

            .list-container {
                display: grid;
                gap: 1rem;
            }

            .item {
                background: rgba(30, 41, 59, 0.6);
                padding: 1.5rem;
                border-radius: 5px;
                border-left: 3px solid #7c3aed;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }

            .item-info h3 {
                margin-bottom: 0.3rem;
                color: #00d4ff;
            }

            .item-info p {
                color: #a0aec0;
                font-size: 0.9rem;
            }

            .item-actions {
                display: flex;
                gap: 1rem;
            }

            .btn-delete {
                background: linear-gradient(135deg, #dc2626, #991b1b);
                padding: 0.5rem 1rem;
                font-size: 0.9rem;
            }

            .btn-delete:hover {
                box-shadow: 0 8px 15px rgba(220, 38, 38, 0.4);
            }

            .message {
                padding: 1rem;
                border-radius: 5px;
                margin-bottom: 1rem;
                display: none;
            }

            .message.success {
                background: rgba(16, 185, 129, 0.2);
                border: 1px solid #10b981;
                color: #10b981;
            }

            .message.error {
                background: rgba(239, 68, 68, 0.2);
                border: 1px solid #ef4444;
                color: #ef4444;
            }

            .grid-2 {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 2rem;
            }

            @media (max-width: 768px) {
                .grid-2 {
                    grid-template-columns: 1fr;
                }

                .item {
                    flex-direction: column;
                    align-items: flex-start;
                }

                .item-actions {
                    width: 100%;
                    margin-top: 1rem;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎬 Streaming Admin Panel</h1>

            <!-- Message Display -->
            <div id="message" class="message"></div>

            <div class="grid-2">
                <!-- TV CHANNELS SECTION -->
                <div>
                    <div class="section">
                        <h2>📺 Add TV Channel</h2>
                        <form onsubmit="addChannel(event)">
                            <div class="form-group">
                                <label for="channel-name">Channel Name:</label>
                                <input type="text" id="channel-name" placeholder="e.g., HBO" required>
                            </div>
                            <div class="form-group">
                                <label for="channel-folder">Folder Path:</label>
                                <input type="text" id="channel-folder" placeholder="e.g., C:\\Videos\\HBO" required>
                            </div>
                            <button type="submit">Add Channel</button>
                        </form>
                    </div>

                    <div class="section">
                        <h2>Channels</h2>
                        <div id="channels-list" class="list-container">
                            <p style="text-align: center; color: #a0aec0;">No channels added yet</p>
                        </div>
                    </div>
                </div>

                <!-- VOD SECTION -->
                <div>
                    <div class="section">
                        <h2>🎬 Add VOD Season</h2>
                        <form onsubmit="addSeason(event)">
                            <div class="form-group">
                                <label for="season-name">Season Name:</label>
                                <input type="text" id="season-name" placeholder="e.g., Season 1" required>
                            </div>
                            <button type="submit">Create Season</button>
                        </form>
                    </div>

                    <div class="section">
                        <h2>Seasons</h2>
                        <div id="seasons-list" class="list-container">
                            <p style="text-align: center; color: #a0aec0;">No seasons created yet</p>
                        </div>
                    </div>
                </div>
            </div>

            <div class="section">
                <h2>📺 Add TV Show</h2>

                <form onsubmit="addShow(event)">
                    <div class="form-group">
                        <label>Show Name</label>
                        <input type="text" id="show-name" placeholder="That 70s Show" required>
                    </div>

                    <div class="form-group">
                        <label>Poster Image</label>
                        <input type="file" id="show-poster" accept="image/*">
                    </div>

                    <button type="submit">Add Show</button>
                </form>
            </div>

            <div class="section">
                <h2>TV Shows</h2>
                <div id="shows-list" class="list-container"></div>
            </div>


            <!-- Add Episodes Section -->
            <div class="section" id="episodes-section" style="display: none;">
                <h2>📹 Add Episodes to Season</h2>
                <form onsubmit="addEpisodes(event)">
                    <div class="form-group">
                        <label for="episode-season">Select Season:</label>
                        <select id="episode-season" required>
                            <option value="">Choose a season...</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="episode-folder">Folder with Episodes:</label>
                        <input type="text" id="episode-folder" placeholder="e.g., C:\\Episodes\\Season1" required>
                    </div>
                    <button type="submit">Add Episodes</button>
                </</form>
            </div>
        </div>

        <script>
            const API_URL = 'http://localhost:5001/api';

            function showMessage(message, type = 'success') {
                const msgEl = document.getElementById('message');
                msgEl.textContent = message;
                msgEl.className = `message ${type}`;
                msgEl.style.display = 'block';
                setTimeout(() => {
                    msgEl.style.display = 'none';
                }, 3000);
            }

            async function loadChannels() {
                try {
                    const response = await fetch(`${API_URL}/channels`);
                    const channels = await response.json();
                    const container = document.getElementById('channels-list');
                    container.innerHTML = '';

                    if (Object.keys(channels).length === 0) {
                        container.innerHTML = '<p style="text-align: center; color: #a0aec0;">No channels added yet</p>';
                        return;
                    }

                    Object.values(channels).forEach(channel => {
                        const item = document.createElement('div');
                        item.className = 'item';
                        item.innerHTML = `
                            <div class="item-info">
                                <h3>${channel.name}</h3>
                                <p>${channel.folder_path}</p>
                            </div>
                            <div class="item-actions">
                                <button class="btn-delete" onclick="deleteChannel('${channel.id}')">Delete</button>
                            </div>
                        `;
                        container.appendChild(item);
                    });
                } catch (error) {
                    console.error('Error loading channels:', error);
                }
            }

            async function loadSeasons() {
                try {
                    const response = await fetch(`${API_URL}/seasons`);
                    const seasons = await response.json();
                    const container = document.getElementById('seasons-list');
                    const select = document.getElementById('episode-season');
                    
                    container.innerHTML = '';
                    select.innerHTML = '<option value="">Choose a season...</option>';

                    if (seasons.length === 0) {
                        container.innerHTML = '<p style="text-align: center; color: #a0aec0;">No seasons created yet</p>';
                        document.getElementById('episodes-section').style.display = 'none';
                        return;
                    }

                    document.getElementById('episodes-section').style.display = 'block';

                    seasons.forEach(season => {
                        // Add to list
                        const item = document.createElement('div');
                        item.className = 'item';
                        item.innerHTML = `
                            <div class="item-info">
                                <h3>${season.name}</h3>
                                <p>${season.episodes.length} episodes</p>
                            </div>
                            <div class="item-actions">
                                <button class="btn-delete" onclick="deleteSeason('${season.id}')">Delete</button>
                            </div>
                        `;
                        container.appendChild(item);

                        // Add to select
                        const option = document.createElement('option');
                        option.value = season.id;
                        option.textContent = season.name;
                        select.appendChild(option);
                    });
                } catch (error) {
                    console.error('Error loading seasons:', error);
                }
            }

            async function addShow(e) {
                e.preventDefault();

                const nameInput = document.getElementById('show-name');
                const posterInput = document.getElementById('show-poster');

                const name = nameInput.value.trim();
                const poster = posterInput.files[0];

                if (!name) {
                    showMessage('Show name is required', 'error');
                    return;
                }

                const form = new FormData();
                form.append('name', name);
                if (poster) form.append('poster', poster);

                const res = await fetch(`${API_URL}/shows`, {
                    method: 'POST',
                    body: form
                });

                if (res.ok) {
                    showMessage('Show added!');
                    nameInput.value = '';
                    posterInput.value = '';
                    loadShows();
                } else {
                    showMessage('Failed to add show', 'error');
                }
            }



            async function addChannel(event) {
                event.preventDefault();
                const name = document.getElementById('channel-name').value;
                const folder = document.getElementById('channel-folder').value;

                try {
                    const response = await fetch(`${API_URL}/channels`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ name, folder_path: folder })
                    });

                    if (response.ok) {
                        showMessage('Channel added successfully!');
                        document.getElementById('channel-name').value = '';
                        document.getElementById('channel-folder').value = '';
                        loadChannels();
                    } else {
                        showMessage('Error adding channel', 'error');
                    }
                } catch (error) {
                    showMessage('Error: ' + error.message, 'error');
                }
            }

            async function deleteChannel(channelId) {
                if (confirm('Delete this channel?')) {
                    try {
                        const response = await fetch(`${API_URL}/channels/${channelId}`, { method: 'DELETE' });
                        if (response.ok) {
                            showMessage('Channel deleted!');
                            loadChannels();
                        }
                    } catch (error) {
                        showMessage('Error: ' + error.message, 'error');
                    }
                }
            }

            async function addSeason(event) {
                event.preventDefault();
                const name = document.getElementById('season-name').value;

                try {
                    const response = await fetch(`${API_URL}/seasons`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ name })
                    });

                    if (response.ok) {
                        showMessage('Season created successfully!');
                        document.getElementById('season-name').value = '';
                        loadSeasons();
                    } else {
                        showMessage('Error creating season', 'error');
                    }
                } catch (error) {
                    showMessage('Error: ' + error.message, 'error');
                }
            }

            async function deleteSeason(seasonId) {
                if (confirm('Delete this season?')) {
                    try {
                        const response = await fetch(`${API_URL}/seasons/${seasonId}`, { method: 'DELETE' });
                        if (response.ok) {
                            showMessage('Season deleted!');
                            loadSeasons();
                        }
                    } catch (error) {
                        showMessage('Error: ' + error.message, 'error');
                    }
                }
            }


            async function addEpisodes(event) {
                event.preventDefault();
                const seasonId = document.getElementById('episode-season').value;
                const folderPath = document.getElementById('episode-folder').value;

                try {
                    const response = await fetch(`${API_URL}/seasons/${seasonId}/episodes`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ folder_path: folderPath })
                    });

                    if (response.ok) {
                        showMessage('Episodes added successfully!');
                        document.getElementById('episode-folder').value = '';
                        loadSeasons();
                    } else {
                        showMessage('Error adding episodes', 'error');
                    }
                } catch (error) {
                    showMessage('Error: ' + error.message, 'error');
                }
            }

            // Load initial data
            document.addEventListener('DOMContentLoaded', () => {
                loadChannels();
                loadSeasons();
                // Refresh every 5 seconds
                setInterval(() => {
                    loadChannels();
                    loadSeasons();
                }, 5000);
            });
        </script>
    </body>
    </html>
    """
    return render_template_string(html)

if __name__ == '__main__':
    admin_app.run(debug=True, host='0.0.0.0', port=5001)
