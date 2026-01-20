import subprocess
from pathlib import Path
import sys

if len(sys.argv) < 2:
    print("Usage: python sync_all.py /path/to/folder")
    sys.exit(1)

folder = Path(sys.argv[1])

for mp4 in folder.glob("*.mp4"):
    srt = mp4.with_suffix(".srt")

    if not srt.exists():
        print(f"Skipping {mp4.name} — no matching SRT")
        continue

    print(f"Syncing: {mp4.name}")
    subprocess.run([
        "alass",
        str(mp4),
        str(srt),
        str(srt)
    ], check=True)

print("Done.")
