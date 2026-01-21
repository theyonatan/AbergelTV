import os
import re

# 🔧 CHANGE THESE PATHS
VIDEO_DIR = r"D:\.New\otherProjects\Ground2\that\output\outputThat '70s Show (1998) Season 1-8 S01-S08 (1080p BluRay x265 HEVC 10bit AAC 5.1 FreetheFish)\Season 6"
SUB_DIR   = VIDEO_DIR

VIDEO_EXTS = (".mkv", ".mp4", ".avi")

def extract_episode(name):
    """
    Extracts S06E01 → returns 'S06E01'
    """
    match = re.search(r"S\d{2}E\d{2}", name, re.IGNORECASE)
    return match.group(0).upper() if match else None


# Build episode → video filename map
videos = {}
for f in os.listdir(VIDEO_DIR):
    if f.lower().endswith(VIDEO_EXTS):
        ep = extract_episode(f)
        if ep:
            videos[ep] = f

print(f"Found {len(videos)} video episodes")

# Rename subtitles
for sub in os.listdir(SUB_DIR):
    if not sub.lower().endswith(".srt"):
        continue

    ep = extract_episode(sub)
    if not ep:
        print(f"⚠️  No episode found in subtitle: {sub}")
        continue

    if ep not in videos:
        print(f"❌ No matching video for {sub}")
        continue

    video_name = videos[ep]
    new_name = os.path.splitext(video_name)[0] + ".srt"

    src = os.path.join(SUB_DIR, sub)
    dst = os.path.join(SUB_DIR, new_name)

    if os.path.exists(dst):
        print(f"⚠️  Already exists, skipping: {new_name}")
        continue

    os.rename(src, dst)
    print(f"✅ {sub} → {new_name}")

print("🎉 Done!")
