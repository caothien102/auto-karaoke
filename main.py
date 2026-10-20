import os
import sys
import argparse
import time
import static_ffmpeg

# Ensure ffmpeg binary is in system PATH for Whisper and all subprocesses
static_ffmpeg.add_paths()

def process_karaoke(
    youtube_url: str,
    output_dir: str = "output",
    whisper_model: str = "base",
    demucs_model: str = "htdemucs",
    language: str = "vi"
):
    from downloader import download_youtube
    from separator import separate_audio
    from transcriber import transcribe_audio
    from sub_generator import generate_ass_karaoke
    from renderer import render_karaoke_video

    start_time = time.time()
    os.makedirs(output_dir, exist_ok=True)
    
    print("\n" + "=" * 60)
    print(" 🎤 AUTO-KARAOKE GENERATOR PIPELINE ")
    print("=" * 60)
    print(f"Target URL:    {youtube_url}")
    print(f"Output Dir:    {output_dir}")
    print(f"Whisper Model: {whisper_model}")
    print(f"Demucs Model:  {demucs_model}")
    print(f"Language:      {language or 'Auto-detect'}")
    print("=" * 60 + "\n")

    # Step 1: Download video & extract audio
    print("\n--- STEP 1/4: Downloading YouTube Content ---")
    media_info = download_youtube(youtube_url, output_dir=os.path.join(output_dir, "downloads"))
    song_id = media_info["id"]
    song_title = media_info["title"]
    video_path = media_info["video_path"]
    audio_path = media_info["audio_path"]
    print(f"[✓] Downloaded '{song_title}' ({song_id})")

    # Step 2: Separate vocals and beat
    print("\n--- STEP 2/4: Separating Vocals and Instrumental Beat ---")
    stems = separate_audio(
        audio_path=audio_path,
        output_dir=os.path.join(output_dir, "separated"),
        model_name=demucs_model
    )
    vocals_path = stems["vocals_path"]
    beat_path = stems["beat_path"]
    print(f"[✓] Vocals and Beat separated.")

    # Step 3: Smart Lyrics extraction (Full-Auto)
    print("\n--- STEP 3/4: Fetching Smart Accurate Lyrics & Timing ---")
    from lyrics_engine import get_smart_karaoke_lyrics
    segments = get_smart_karaoke_lyrics(
        youtube_url=youtube_url,
        vocals_path=vocals_path,
        model_size=whisper_model,
        language=language or "vi"
    )
    
    ass_path = os.path.join(output_dir, f"{song_id}_karaoke.ass")
    generate_ass_karaoke(segments, ass_path, title=song_title)
    print(f"[✓] Generated karaoke subtitles (.ass)")

    # Step 4: Render final karaoke video
    print("\n--- STEP 4/4: Rendering Final Karaoke Video ---")
    final_output_path = os.path.join(output_dir, f"{song_id}_karaoke.mp4")
    render_karaoke_video(
        background_video=video_path,
        beat_audio=beat_path,
        ass_subtitles=ass_path,
        output_video=final_output_path
    )

    elapsed = time.time() - start_time
    print("\n" + "=" * 60)
    print(f" 🎉 SUCCESS! Completed in {elapsed:.1f} seconds")
    print(f" Final Karaoke Video: {os.path.abspath(final_output_path)}")
    print("=" * 60 + "\n")

    return final_output_path

def main():
    parser = argparse.ArgumentParser(description="Auto Karaoke Video Generator")
    parser.add_argument("--url", "-u", type=str, required=True, help="YouTube video URL")
    parser.add_argument("--output", "-o", type=str, default="output", help="Directory to save generated files")
    parser.add_argument("--whisper-model", "-w", type=str, default="base", choices=["tiny", "base", "small", "medium", "large"], help="Whisper model size")
    parser.add_argument("--demucs-model", "-d", type=str, default="htdemucs", help="Demucs model (default: htdemucs)")
    parser.add_argument("--lang", "-l", type=str, default="vi", help="Song language code (e.g. 'vi', 'en') or leave empty for auto")

    args = parser.parse_args()
    process_karaoke(
        youtube_url=args.url,
        output_dir=args.output,
        whisper_model=args.whisper_model,
        demucs_model=args.demucs_model,
        language=args.lang if args.lang != "auto" else None
    )

if __name__ == "__main__":
    main()
