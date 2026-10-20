import os
import sys
import whisper

def transcribe_audio(audio_path: str, model_size: str = "base", language: str = None) -> list:
    """
    Transcribes audio with word-level timestamps using OpenAI Whisper.
    Returns a structured list of segments with word timing.
    """
    audio_path = os.path.abspath(audio_path)
    print(f"[*] Loading Whisper model '{model_size}'...")
    model = whisper.load_model(model_size)

    options = {
        "word_timestamps": True,
        "verbose": False
    }
    if language:
        options["language"] = language

    print(f"[*] Transcribing vocal track: {audio_path} (word_timestamps=True)...")
    result = model.transcribe(audio_path, **options)

    detected_lang = result.get("language", "unknown")
    print(f"[+] Transcription finished! Detected language: {detected_lang}")

    segments_data = []
    for seg in result.get("segments", []):
        words = []
        for w in seg.get("words", []):
            words.append({
                "word": w.get("word", "").strip(),
                "start": w.get("start", 0.0),
                "end": w.get("end", 0.0),
                "probability": w.get("probability", 1.0)
            })
        segments_data.append({
            "id": seg.get("id"),
            "start": seg.get("start"),
            "end": seg.get("end"),
            "text": seg.get("text", "").strip(),
            "words": words
        })

    return segments_data

if __name__ == "__main__":
    if len(sys.argv) > 1:
        res = transcribe_audio(sys.argv[1])
        print(f"Extracted {len(res)} segments.")
    else:
        print("Usage: python transcriber.py <vocals_audio_path>")
