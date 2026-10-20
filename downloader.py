import os
import shutil
import yt_dlp

def get_ffmpeg_path():
    venv_ffmpeg = os.path.abspath(os.path.join(os.path.dirname(__file__), ".venv", "bin", "ffmpeg"))
    if os.path.exists(venv_ffmpeg):
        return venv_ffmpeg
    system_ffmpeg = shutil.which("ffmpeg")
    if system_ffmpeg:
        return system_ffmpeg
    return None

def download_youtube(url: str, output_dir: str = "downloads") -> dict:
    """
    Downloads video and extracts high-quality audio from a YouTube URL.
    Returns a dictionary with paths to the video file, audio file, and metadata.
    """
    os.makedirs(output_dir, exist_ok=True)
    ffmpeg_path = get_ffmpeg_path()
    
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': os.path.join(output_dir, '%(id)s.%(ext)s'),
        'merge_output_format': 'mp4',
        'noplaylist': True,
        'quiet': False,
    }
    if ffmpeg_path:
        ydl_opts['ffmpeg_location'] = os.path.dirname(ffmpeg_path)

    print(f"[*] Downloading YouTube content from: {url}")
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        video_id = info.get('id', 'video')
        title = info.get('title', 'Unknown Title')
        duration = info.get('duration', 0)

        video_path = os.path.join(output_dir, f"{video_id}.mp4")
        audio_path = os.path.join(output_dir, f"{video_id}.wav")

        if os.path.exists(video_path) and os.path.exists(audio_path):
            print(f"[+] Reusing existing video and audio for {video_id}")
            return {
                "id": video_id,
                "title": title,
                "duration": duration,
                "video_path": os.path.abspath(video_path),
                "audio_path": os.path.abspath(audio_path)
            }

        # Download if not present
        ydl.download([url])

    # Extract clean WAV audio (44.1kHz, 16-bit stereo) for AI models
    print(f"[*] Extracting audio to WAV format: {audio_path}")
    ffmpeg_bin = ffmpeg_path if ffmpeg_path else "ffmpeg"
    cmd = f'"{ffmpeg_bin}" -y -i "{video_path}" -vn -acodec pcm_s16le -ar 44100 -ac 2 "{audio_path}"'
    ret = os.system(cmd)
    if ret != 0:
        raise RuntimeError(f"FFmpeg audio extraction failed with return code {ret}")

    return {
        "id": video_id,
        "title": title,
        "duration": duration,
        "video_path": os.path.abspath(video_path),
        "audio_path": os.path.abspath(audio_path)
    }

if __name__ == "__main__":
    import sys
    test_url = sys.argv[1] if len(sys.argv) > 1 else "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    res = download_youtube(test_url)
    print("Download result:", res)
