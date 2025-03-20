import sounddevice as sd
import queue
import json
from vosk import Model, KaldiRecognizer
from module import *


MODEL_PATH = r"Cirtana-lite\vosk-model-en-in-0.5"
model = Model(MODEL_PATH)

q = queue.Queue()

SAMPLE_RATE = 16000
BLOCK_SIZE = 8000  

def callback(indata, frames, time, status):
    if status: print(status)
    q.put(bytes(indata))  


recognizer = KaldiRecognizer(model, SAMPLE_RATE)

print("how can we help you")
with sd.RawInputStream(samplerate=SAMPLE_RATE, blocksize=BLOCK_SIZE, dtype="int16", channels=1, callback=callback):
    while True:
        data = q.get()
        if recognizer.AcceptWaveform(data):
            text = json.loads(recognizer.Result()).get("text", "").lower()
            match = re.search(r"(cortana)?", text)
            if match:
                print(text)
                process_command(text)
