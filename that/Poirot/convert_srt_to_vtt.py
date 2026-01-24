import subprocess
from pathlib import Path

ROOT_DIR = Path(r".")

for srt_path in ROOT_DIR.rglob("*.srt"):
    vtt_path = srt_path.with_suffix(".vtt")

    print(f"Converting: {srt_path} -> {vtt_path}")

    subprocess.run(
        [
            "ffmpeg",
            "-y",              # overwrite if exists
            "-i", str(srt_path),
            str(vtt_path)
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

print("Done.")
