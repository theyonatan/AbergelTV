import argparse
import os
import subprocess
import shutil
from pathlib import Path

# ===== CONFIG =====
OUTPUT_DIR = "output"
CRF = 20
PRESET = "veryfast"
AUDIO_BITRATE = "192k"
EXTENSIONS = (".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm")
# ==================

def main():
    parser = argparse.ArgumentParser(
        description="Convert video files (mkv, avi, etc.) to MP4 using ffmpeg, recursively."
    )
    parser.add_argument(
        "folder",
        nargs="?",
        default=None,
        help="Optional specific folder to process recursively. If omitted, processes the current directory and all subfolders."
    )
    args = parser.parse_args()

    start_dir = Path.cwd()
    output_root = start_dir / OUTPUT_DIR
    output_root.mkdir(exist_ok=True)

    # Check if ffmpeg is available
    if not shutil.which("ffmpeg"):
        print("Error: ffmpeg is not installed or not in your PATH.")
        return

    # Determine the directory to process
    if args.folder is None:
        process_dir = start_dir
    else:
        process_dir = (start_dir / args.folder).resolve()

    if not process_dir.is_dir():
        print(f"Error: '{process_dir}' is not a valid directory.")
        return

    # Ensure the process directory is within or equal to the current directory
    try:
        base_rel = process_dir.relative_to(start_dir)
    except ValueError:
        print("Error: The specified folder must be the current directory or a subdirectory.")
        return

    # Walk through the directory and convert files
    for dirpath, _, filenames in os.walk(process_dir):
        current_dir = Path(dirpath)
        rel_dir = current_dir.relative_to(process_dir)
        full_rel_dir = base_rel / rel_dir

        out_dir = output_root / full_rel_dir
        out_dir.mkdir(parents=True, exist_ok=True)

        for filename in filenames:
            if filename.lower().endswith(EXTENSIONS):
                input_path = current_dir / filename
                output_path = out_dir / (Path(filename).stem + ".mp4")

                if output_path.exists():
                    print(f"SKIP: {input_path}")
                else:
                    print(f"CONVERT: {input_path} → {output_path}")

                    ffmpeg_cmd = [
                        "ffmpeg", "-y", "-i", str(input_path),
                        "-map", "0:v:0", "-map", "0:a?",
                        "-c:v", "libx264", "-pix_fmt", "yuv420p",
                        "-preset", PRESET, "-crf", str(CRF),
                        "-c:a", "aac", "-b:a", AUDIO_BITRATE,
                        str(output_path)
                    ]

                    try:
                        subprocess.run(ffmpeg_cmd, check=True)
                        if input_path.suffix.lower() == '.mkv':
                            os.remove(str(input_path))
                            print(f"DELETED original MKV: {input_path}")
                    except subprocess.CalledProcessError:
                        print(f"FAILED: Conversion failed for {input_path}")

    print("\nDONE!")

if __name__ == "__main__":
    main()