import os
import sys
import subprocess
import torch

def separate_audio(audio_path: str, output_dir: str = "separated", model_name: str = "htdemucs") -> dict:
    """
    Separates an audio file into vocals and instrumental (beat) tracks using Demucs.
    Returns a dict with paths to vocals.wav and no_vocals.wav.
    """
    os.makedirs(output_dir, exist_ok=True)
    audio_path = os.path.abspath(audio_path)
    base_name = os.path.splitext(os.path.basename(audio_path))[0]

    target_dir = os.path.join(output_dir, model_name, base_name)
    vocals_path = os.path.join(target_dir, "vocals.wav")
    no_vocals_path = os.path.join(target_dir, "no_vocals.wav")

    # If already separated, reuse existing files to save time
    if os.path.exists(vocals_path) and os.path.exists(no_vocals_path):
        print(f"[+] Reusing existing separated files from {target_dir}")
        return {
            "vocals_path": os.path.abspath(vocals_path),
            "beat_path": os.path.abspath(no_vocals_path)
        }

    # Note: Demucs htdemucs conv1d has channel dimensions not yet supported by Apple MPS.
    # Apple Silicon CPU has high-performance SIMD/NEON cores and processes audio very fast.
    device = "cpu"
    if torch.cuda.is_available():
        device = "cuda"

    print(f"[*] Separating audio using Demucs (model: {model_name}, device: {device})...")
    
    cmd = [
        sys.executable, "-m", "demucs.separate",
        "-n", model_name,
        "--two-stems", "vocals",
        "-d", device,
        "-o", output_dir,
        audio_path
    ]
    
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if result.returncode != 0:
        print("Demucs output:\n", result.stdout)
        raise RuntimeError(f"Demucs failed with exit code {result.returncode}")

    target_dir = os.path.join(output_dir, model_name, base_name)
    vocals_path = os.path.join(target_dir, "vocals.wav")
    no_vocals_path = os.path.join(target_dir, "no_vocals.wav")

    if not os.path.exists(vocals_path) or not os.path.exists(no_vocals_path):
        raise FileNotFoundError(f"Separated files not found in {target_dir}")

    print(f"[+] Separation completed!")
    print(f"    - Vocals: {vocals_path}")
    print(f"    - Beat:   {no_vocals_path}")

    return {
        "vocals_path": os.path.abspath(vocals_path),
        "beat_path": os.path.abspath(no_vocals_path)
    }

if __name__ == "__main__":
    if len(sys.argv) > 1:
        separate_audio(sys.argv[1])
    else:
        print("Usage: python separator.py <audio_path>")
