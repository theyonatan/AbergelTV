# Streaming Site - TV Channels & VOD

A complete streaming platform with TV Channels and Video on Demand (VOD) functionality.

## Features

### 📺 TV Channels
- Stream media from selected server folders
- Auto-play from middle of the channel
- Navigate episodes with Previous/Next buttons
- Auto-hiding UI (visible on mouse movement)

### 🎬 VOD (Video on Demand)
- Organize content by seasons
- Upload entire folders as episodes
- Browse and select episodes to watch
- Standard video player controls

## Project Structure

```
Ground2/
├── backend/
│   ├── app.py          # Main Flask application
│   └── admin.py        # Admin panel server
├── frontend/
│   ├── index.html      # Main UI
│   ├── css/
│   │   └── style.css   # Styling
│   └── js/
│       └── app.js      # Frontend logic
├── data/               # Data storage (auto-created)
└── requirements.txt    # Python dependencies
```

## Setup Instructions

### 1. Install Python Dependencies

```powershell
cd Ground2
pip install -r requirements.txt
```

### 2. Run the Backend Server

```powershell
cd backend
python app.py
```

The main application will run on: `http://localhost:5000`

### 3. Run the Admin Panel (in a new terminal)

```powershell
cd backend
python admin.py
```

The admin panel will be available at: `http://localhost:5001`

## Usage

### Adding TV Channels

1. Open the admin panel: `http://localhost:5001`
2. In the "Add TV Channel" section:
   - Enter a channel name (e.g., "HBO")
   - Enter the folder path containing your videos
   - Click "Add Channel"
3. The channel will appear in the main app under "TV Channels"

### Adding VOD Seasons and Episodes

1. Open the admin panel: `http://localhost:5001`
2. In the "Add VOD Season" section:
   - Enter a season name
   - Click "Create Season"
3. The season appears in the list
4. In the "Add Episodes to Season" section:
   - Select the season
   - Enter the folder path with episode files
   - Click "Add Episodes"
5. Episodes will be available in the main app under "VOD"

## Accessing the Main Application

Open your browser and go to: `http://localhost:5000`

### Navigation

- **Main Menu**: Choose between TV Channels and VOD
- **TV Channels**: Select a channel to watch
  - Videos play starting from the middle episode
  - Use Previous/Next buttons to navigate
  - UI hides after 3 seconds of inactivity
- **VOD**: Select a season, then pick an episode
  - Standard video player with full controls

## File Format Support

Supported video formats:
- `.mp4`
- `.mkv`
- `.avi`
- `.mov`
- `.flv`
- `.wmv`
- `.webm`

## Data Storage

- Channel and season configurations are stored in `data/channels.json` and `data/seasons.json`
- These files are automatically created in the data directory
- Video files are streamed directly from their source folders

## Notes

- The platform supports HTTP range requests for efficient video streaming
- UI automatically hides during playback for a clean viewing experience
- All network requests use CORS to allow communication between frontend and backend
- The admin panel auto-refreshes every 5 seconds

## Troubleshooting

### Port Already in Use
If port 5000 or 5001 is already in use, modify the port numbers in:
- `backend/app.py` (change port 5000)
- `backend/admin.py` (change port 5001)

### CORS Issues
If you get CORS errors, ensure Flask-CORS is installed correctly

### Video Not Loading
- Verify the folder path exists and contains video files
- Check that file extensions are supported
- Ensure the user has read permissions for the video files

## Development

To modify the styling, edit `frontend/css/style.css`
To modify functionality, edit `frontend/js/app.js`
To modify backend behavior, edit `backend/app.py`
