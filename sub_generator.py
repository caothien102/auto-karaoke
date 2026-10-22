import os
import math

def format_ass_time(seconds: float) -> str:
    """Formats seconds into ASS timestamp: H:MM:SS.cc"""
    if seconds < 0:
        seconds = 0.0
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    centis = int(round((seconds - int(seconds)) * 100))
    if centis >= 100:
        secs += 1
        centis = 0
    return f"{hours}:{minutes:02d}:{secs:02d}.{centis:02d}"

def generate_ass_karaoke(segments: list, output_ass_path: str, title: str = "Karaoke"):
    r"""
    Generates a professional ASS subtitle file with:
    1. Proper 1280x720 canvas resolution so text is never truncated.
    2. Intro / Solo Countdown dots (● ● ● ●) for rhythm entry.
    3. Early line visibility (lead-in) so singer can prepare breath and read ahead.
    4. Two-line alternating layout standard for karaoke.
    """
    header = f"""[Script Info]
Title: {title}
ScriptType: v4.00+
Collisions: Normal
PlayDepth: 0
Timer: 100.0000
WrapStyle: 0
PlayResX: 1280
PlayResY: 720

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: KaraokeLine1,Arial,40,&H0000FFFF,&H00FFFFFF,&H00000000,&H90000000,-1,0,0,0,100,100,0,0,1,2.8,1.5,2,50,50,85,1
Style: KaraokeLine2,Arial,40,&H0000FFFF,&H00FFFFFF,&H00000000,&H90000000,-1,0,0,0,100,100,0,0,1,2.8,1.5,2,50,50,30,1
Style: KaraokeCountdown,Arial,34,&H0000FFFF,&H00FFFFFF,&H00000000,&H90000000,-1,0,0,0,100,100,4,0,1,2.2,1.2,2,50,50,140,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    dialogue_lines = []
    
    # Filter valid segments
    valid_segments = [s for s in segments if s.get("words")]

    prev_line_end = 0.0

    for i, seg in enumerate(valid_segments):
        words = seg["words"]
        if not words:
            continue

        style = "KaraokeLine1" if (i % 2 == 0) else "KaraokeLine2"
        line_start = seg["start"]
        line_end = seg["end"]

        # Check for Intro or Solo countdown (>= 3.0 seconds gap)
        gap = line_start - prev_line_end if i > 0 else line_start
        if gap >= 2.8:
            countdown_dur = min(3.0, gap)
            countdown_start = line_start - countdown_dur
            cd_cs = max(1, int(round((countdown_dur / 4.0) * 100)))
            cd_text = f"{{\\kf{cd_cs}}}●  {{\\kf{cd_cs}}}●  {{\\kf{cd_cs}}}●  {{\\kf{cd_cs}}}●"
            dialogue_lines.append(
                f"Dialogue: 1,{format_ass_time(countdown_start)},{format_ass_time(line_start)},KaraokeCountdown,,0,0,0,,{cd_text}"
            )
            display_start = countdown_start
        else:
            # Show line at least 1.5s ahead so singer has time to read
            display_start = max(prev_line_end, line_start - 1.5)

        # Build karaoke text with \kf tags
        karaoke_text_parts = []
        current_time = line_start

        # If line displays before singing, wait until singing starts
        if line_start > display_start:
            initial_wait_cs = int(round((line_start - display_start) * 100))
            if initial_wait_cs > 0:
                karaoke_text_parts.append(f"{{\\kf{initial_wait_cs}}}")

        for w_idx, w in enumerate(words):
            w_start = max(w["start"], line_start)
            w_end = min(w["end"], line_end)
            
            # Silence before this word within the line
            if w_start > current_time:
                silence_cs = int(round((w_start - current_time) * 100))
                if silence_cs > 0:
                    karaoke_text_parts.append(f"{{\\kf{silence_cs}}}")

            duration_cs = max(1, int(round((w_end - w_start) * 100)))
            word_str = w["word"].strip()
            
            space = " " if w_idx < len(words) - 1 else ""
            karaoke_text_parts.append(f"{{\\kf{duration_cs}}}{word_str}{space}")
            current_time = w_end

        display_end = line_end + 0.8
        prev_line_end = line_end

        start_str = format_ass_time(display_start)
        end_str = format_ass_time(display_end)
        full_karaoke_text = "".join(karaoke_text_parts)

        dialogue = f"Dialogue: 0,{start_str},{end_str},{style},,0,0,0,,{full_karaoke_text}"
        dialogue_lines.append(dialogue)

    with open(output_ass_path, "w", encoding="utf-8") as f:
        f.write(header)
        f.write("\n".join(dialogue_lines) + "\n")

    print(f"[+] Professional Karaoke ASS subtitles generated: {output_ass_path} ({len(dialogue_lines)} events)")
    return os.path.abspath(output_ass_path)

if __name__ == "__main__":
    test_segments = [
        {
            "start": 4.0,
            "end": 7.5,
            "words": [
                {"word": "Một", "start": 4.0, "end": 4.8},
                {"word": "chiều", "start": 4.8, "end": 5.4},
                {"word": "mưa", "start": 5.4, "end": 6.2},
                {"word": "trong", "start": 6.2, "end": 6.8},
                {"word": "lòng", "start": 6.8, "end": 7.5},
            ]
        }
    ]
    generate_ass_karaoke(test_segments, "test_cd.ass", "Test")
