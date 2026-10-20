import os
import json
import urllib.request
import ssl
import yt_dlp
from transcriber import transcribe_audio

# Ensure SSL doesn't fail on macOS
try:
    ssl._create_default_https_context = ssl._create_unverified_context
except AttributeError:
    pass

def extract_youtube_official_subtitles(youtube_url: str, preferred_lang: str = "vi") -> list:
    """
    Extracts official author-provided subtitles directly from YouTube video metadata.
    Returns structured segments with word-level timing, or None if no official sub exists.
    """
    print(f"[*] Checking for official subtitles on YouTube: {youtube_url}")
    ydl_opts = {'skip_download': True, 'quiet': True}
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=False)
            subs = info.get('subtitles', {})

            # Look for preferred language or fallback to any available
            target_subs = None
            if preferred_lang in subs:
                target_subs = subs[preferred_lang]
            elif 'vi' in subs:
                target_subs = subs['vi']
            elif 'en' in subs:
                target_subs = subs['en']

            if not target_subs:
                print("[-] No official author subtitles found on YouTube.")
                return None

            # Prefer json3 format for millisecond accuracy
            sub_url = None
            for s in target_subs:
                if s.get('ext') == 'json3':
                    sub_url = s.get('url')
                    break
            if not sub_url and target_subs:
                sub_url = target_subs[0].get('url')

            if not sub_url:
                return None

            print(f"[✓] Found official YouTube subtitle stream! Downloading...")
            req = urllib.request.Request(sub_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode('utf-8'))

            events = data.get('events', [])
            segments = []
            for ev in events:
                segs = ev.get('segs', [])
                text = ''.join([s.get('utf8', '') for s in segs]).strip()
                if not text or text == '\n':
                    continue

                start_sec = ev.get('tStartMs', 0) / 1000.0
                dur_sec = ev.get('dDurationMs', 0) / 1000.0
                end_sec = start_sec + dur_sec

                # Distribute timing across words
                raw_words = text.split()
                if not raw_words:
                    continue
                word_dur = dur_sec / len(raw_words)
                words = []
                for w_idx, w in enumerate(raw_words):
                    w_start = start_sec + w_idx * word_dur
                    w_end = w_start + word_dur
                    words.append({'word': w, 'start': w_start, 'end': w_end})

                segments.append({
                    'start': start_sec,
                    'end': end_sec,
                    'text': text,
                    'words': words
                })

            if segments:
                print(f"[✓] Successfully parsed {len(segments)} official lyrics lines from YouTube!")
                return segments

    except Exception as e:
        print(f"[!] Warning: Could not extract YouTube subtitles: {e}")

    return None

def get_smart_karaoke_lyrics(youtube_url: str, vocals_path: str, model_size: str = "base", language: str = "vi") -> list:
    """
    Full-auto 2-tier lyrics engine:
    1. First tries to fetch 100% accurate official author subtitles from YouTube.
    2. Falls back to OpenAI Whisper AI speech recognition if no official sub exists.
    """
    # Tier 1: YouTube Official Subtitles
    official_segs = extract_youtube_official_subtitles(youtube_url, preferred_lang=language)
    if official_segs:
        return official_segs

    # Tier 2: AI Speech Recognition Fallback
    print(f"[*] Fallback to AI Whisper model '{model_size}' for vocal transcription...")
    return transcribe_audio(vocals_path, model_size=model_size, language=language)
