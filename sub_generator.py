import os
import math

def format_ass_time(seconds: float) -> str:
    """Formats seconds into ASS timestamp: H:MM:SS.cc"""
    if seconds < 0:
        seconds = 0
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    centis = int(round((seconds - int(seconds)) * 100))
    if centis == 100:
        secs += 1
        centis = 0
    return f"{hours}:{minutes:02d}:{secs:02d}.{centis:02d}"

def generate_ass_karaoke(segments: list, output_ass_path: str, title: str = "Karaoke"):
    r"""
    Generates a professional ASS subtitle file with smooth \kf karaoke wipes.
    Supports alternating 2-line layout standard for karaoke videos.
    """
    header = f"""[Script Info]
Title: {title}
ScriptType: v4.00+
Collisions: Normal
PlayDepth: 0
Timer: 100.0000
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: KaraokeLine1,Arial,52,&H0000FFFF,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,3.5,2.0,2,40,40,90,1
Style: KaraokeLine2,Arial,52,&H0000FFFF,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,3.5,2.0,2,40,40,35,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    dialogue_lines = []
    
    # Filter valid segments
    valid_segments = [s for s in segments if s.get("words")]

    for i, seg in enumerate(valid_segments):
        words = seg["words"]
        if not words:
            continue

        style = "KaraokeLine1" if (i % 2 == 0) else "KaraokeLine2"
        
        line_start = seg["start"]
        line_end = seg["end"]

        # Build karaoke text with \kf tags
        # \kf<centiseconds> creates smooth progressive sweep
        karaoke_text_parts = []
        current_time = line_start

        for w_idx, w in enumerate(words):
            w_start = max(w["start"], line_start)
            w_end = min(w["end"], line_end)
            
            # If there was a silence before this word, wait
            if w_start > current_time:
                silence_cs = int(round((w_start - current_time) * 100))
                if silence_cs > 0:
                    karaoke_text_parts.append(f"{{\\kf{silence_cs}}}")

            duration_cs = max(1, int(round((w_end - w_start) * 100)))
            word_str = w["word"].strip()
            
            # Append space after word unless it's punctuation
            space = " " if w_idx < len(words) - 1 else ""
            karaoke_text_parts.append(f"{{\\kf{duration_cs}}}{word_str}{space}")
            current_time = w_end

        # Show line slightly before singing starts (0.6s lead-in) for singer preparation
        display_start = max(0.0, line_start - 0.6)
        display_end = line_end + 0.8

        start_str = format_ass_time(display_start)
        end_str = format_ass_time(display_end)
        full_karaoke_text = "".join(karaoke_text_parts)

        dialogue = f"Dialogue: 0,{start_str},{end_str},{style},,0,0,0,,{full_karaoke_text}"
        dialogue_lines.append(dialogue)

    with open(output_ass_path, "w", encoding="utf-8") as f:
        f.write(header)
        f.write("\n".join(dialogue_lines) + "\n")

    print(f"[+] Karaoke ASS subtitles generated: {output_ass_path} ({len(dialogue_lines)} lines)")
    return os.path.abspath(output_ass_path)

if __name__ == "__main__":
    test_segments = [
        {
            "start": 1.0,
            "end": 4.5,
            "words": [
                {"word": "Xin", "start": 1.0, "end": 1.5},
                {"word": "chào", "start": 1.5, "end": 2.2},
                {"word": "Việt", "start": 2.5, "end": 3.2},
                {"word": "Nam", "start": 3.3, "end": 4.5},
            ]
        }
    ]
    generate_ass_karaoke(test_segments, "test.ass", "Test Song")
