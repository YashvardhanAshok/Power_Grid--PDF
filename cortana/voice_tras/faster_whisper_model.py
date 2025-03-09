
import GPUtil
import faster_whisper

try:
    gpus = GPUtil.getGPUs()
    faster_whisper_model = faster_whisper.WhisperModel("small", device="cuda" if any(gpu.name == "NVIDIA GeForce RTX 3060 Laptop GPU" for gpu in gpus) else "cpu")
except:
    # medium, small
    faster_whisper_model = faster_whisper.WhisperModel("small", device="cpu")
    # faster_whisper_model = faster_whisper.WhisperModel("medium", device="cpu")

def whisper_modle(filename):
    """Transcribes the recorded audio to text."""
    segments, _ = faster_whisper_model.transcribe(filename)
    
    return "\n".join(segment.text for segment in segments if segment.text)