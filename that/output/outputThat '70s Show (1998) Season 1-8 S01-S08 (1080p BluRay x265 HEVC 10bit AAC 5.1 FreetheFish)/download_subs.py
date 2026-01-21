from opensubtitlescom import OpenSubtitles
import os

# Your credentials
API_KEY = "cMPgDnuWvWnT94ja7Xjd4aUTcgPQPnCs"
USERNAME = "idka"
PASSWORD = "123123"

# Show details
SHOW_NAME = "That 70s Show"             # Try "That '70s Show" if fewer results
SEASON = 6
EPISODES = range(1, 26)                 # 25 episodes in season 6

# Folder to save subtitles
SAVE_FOLDER = "subtitles/that_70s_show_s06_hebrew"
os.makedirs(SAVE_FOLDER, exist_ok=True)

# Initialize and login
subtitles = OpenSubtitles("MySubtitleDownloader v1.0", API_KEY)
subtitles.login(USERNAME, PASSWORD)
print("Logged in successfully!")

# Loop through episodes
for episode in EPISODES:
    print(f"Searching for {SHOW_NAME} S{SEASON:02d}E{episode:02d} in Hebrew...")
    
    response = subtitles.search(
        query=SHOW_NAME,
        season_number=SEASON,
        episode_number=episode,
        languages="he"  # "he" seems to work for you; alternative: "heb"
    )
    
    if not response.data:
        print(f"  No Hebrew subtitles found for S{SEASON:02d}E{episode:02d}")
        continue
    
    # Get the most downloaded one (safe access)
    top_subtitle = max(response.data, key=lambda x: x.download_count or 0)
    downloads = top_subtitle.download_count
    print(f"  Found top subtitle with {downloads} downloads")
    
    # Download and save
    srt_bytes = subtitles.download(top_subtitle)
    srt_content = srt_bytes.decode("utf-8", errors="replace")

    filename = f"That.70s.Show.S{SEASON:02d}E{episode:02d}.he.srt"
    filepath = os.path.join(SAVE_FOLDER, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(srt_content)

    print(f"  Saved: {filename}")
    break


print("Done! All top Hebrew subtitles for Season 6 downloaded.")