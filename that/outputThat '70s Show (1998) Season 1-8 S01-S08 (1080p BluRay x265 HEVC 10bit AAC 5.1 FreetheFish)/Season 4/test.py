# transcribe_70s_show.py
import stable_whisper

def main():
    # === Customize these values ===
    audio_file = r"That '70s Show (1998) - S04E24 - That '70s Musical (1080p BluRay x265 FreetheFish).mp4"
    model_size = "large-v3"
    language   = "en"
    task       = "transcribe"
    output_ext = ".srt"
    
    # === Usually no need to change below ===
    print(f"Loading model: {model_size} ...")
    model = stable_whisper.load_faster_whisper(
        model_size,
        device="cuda",           # we already know you have GPU
        download_root=None       # uses default huggingface cache
    )
    
    print(f"\nTranscribing: {audio_file}")
    print("This might take a while depending on length and GPU...\n")
    
    result = model.transcribe(
        audio_file,
        language=language,
        batch_size=16,           # ← big speedup
        compute_type="int8_float16",   # ← even faster, less memory
        task=task,
        verbose=True,            # shows progress
        # Optional useful flags - uncomment if needed:
        # batch_size=16,         # faster on good GPUs
        # temperature=0,         # more deterministic
        # vad=True,              # better silence handling (default anyway)
    )
    
    # Save as SRT
    output_file = audio_file.rsplit(".", 1)[0] + output_ext
    result.save_as_srt(output_file)
    # result.to_srt(output_file)  # alternative method - same result
    
    print(f"\nDone! Subtitle file saved as:")
    print(f"→ {output_file}")

if __name__ == "__main__":
    main()