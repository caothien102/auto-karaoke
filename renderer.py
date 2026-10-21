import os
import shutil
import subprocess
import static_ffmpeg

static_ffmpeg.add_paths()

def get_ffmpeg_path():
    venv_ffmpeg = os.path.abspath(os.path.join(os.path.dirname(__file__), ".venv", "bin", "ffmpeg"))
    if os.path.exists(venv_ffmpeg):
        return venv_ffmpeg
    system_ffmpeg = shutil.which("ffmpeg")
    if system_ffmpeg:
        return system_ffmpeg
    return "ffmpeg"

def render_karaoke_video(
    background_video: str,
    beat_audio: str,
    ass_subtitles: str,
    output_video: str,
    vocal_audio: str = None,
    vocal_guide_volume: float = 0.0
) -> str:
    """
    Composites the background video, beat audio (with optional vocal guide), and karaoke .ass subtitles into a final video.
    vocal_guide_volume: 0.0 = clean beat, 0.2 = 20% vocal guide for easier rhythm matching.
    """
    ffmpeg_bin = get_ffmpeg_path()
    background_video = os.path.abspath(background_video)
    beat_audio = os.path.abspath(beat_audio)
    ass_subtitles = os.path.abspath(ass_subtitles)
    output_video = os.path.abspath(output_video)

    os.makedirs(os.path.dirname(output_video) or ".", exist_ok=True)

    # Escape path for FFmpeg subtitles filter
    escaped_sub = ass_subtitles.replace("\\", "/").replace(":", "\\:").replace("'", "\\'")

    print(f"[*] Rendering final Karaoke video (Vocal guide: {int(vocal_guide_volume * 100)}%)...")

    # If vocal guide is enabled and vocal audio exists, mix beat + soft vocals
    if vocal_guide_volume > 0.0 and vocal_audio and os.path.exists(vocal_audio):
        vocal_audio = os.path.abspath(vocal_audio)
        cmd = [
            ffmpeg_bin, "-y",
            "-i", background_video,
            "-i", beat_audio,
            "-i", vocal_audio,
            "-filter_complex",
            f"[0:v:0]subtitles='{escaped_sub}'[v_out];"
            f"[1:a:0]volume=1.0[a_beat];"
            f"[2:a:0]volume={vocal_guide_volume:.2f}[a_vocal];"
            f"[a_beat][a_vocal]amix=inputs=2:duration=first:dropout_transition=2[a_out]",
            "-map", "[v_out]",
            "-map", "[a_out]",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "22",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "320k",
            "-shortest",
            output_video
        ]
    else:
        cmd = [
            ffmpeg_bin, "-y",
            "-i", background_video,
            "-i", beat_audio,
            "-vf", f"subtitles='{escaped_sub}'",
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "22",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "320k",
            "-shortest",
            output_video
        ]

    print("[*] Running FFmpeg rendering pipeline...")
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if proc.returncode != 0:
        print("FFmpeg stderr:\n", proc.stderr)
        raise RuntimeError(f"FFmpeg render failed with exit code {proc.returncode}")

    print(f"[+] Karaoke video rendered successfully: {output_video}")
    return output_video

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 5:
        render_karaoke_video(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        print("Usage: python renderer.py <video> <beat_wav> <ass_file> <output_mp4>")
