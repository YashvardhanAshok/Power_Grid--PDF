import os
import pyaudio
import wave
import keyboard
import threading
import pyperclip
import time

# Custom
import voice_tras.faster_whisper_model as whisper_model
import llm.llm as llm
import words.typing as typing

# Audio parameters
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
OUTPUT_FILENAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), "recorded_audio.wav")

Thread = False
recording = False
frames = []
audio = pyaudio.PyAudio()

def record_audio():
    """Records audio in a separate thread until recording stops."""
    global frames
    frames = []
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)

    print("Recording started...")
    while recording:
        data = stream.read(CHUNK)
        frames.append(data)

    print("Recording stopped.")
    stream.stop_stream()
    stream.close()

    wf = wave.open(OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    print(f"Audio saved at: {OUTPUT_FILENAME}")

    response = whisper_model.transcribe_audio(OUTPUT_FILENAME)
    
    a = response.split(' ')
    matched = False  

    for word in a[:5]:  
        word = word.lower() 

        if word == "cortana":
            llm_response = llm.model("gemma2:2b", response, word)
            matched = True
            break  

        elif word == "summarize":
            copy_message = pyperclip.paste()  
            llm_response = llm.model("gemma2:2b", copy_message, word)  
            matched = True
            break  

        elif word == "rewrite":
            copy_message = pyperclip.paste()  
            llm_response = llm.model("gemma2 :2b", copy_message, word)  
            matched = True
            break  

        elif word == "write a program":
            llm_response = llm.model("gemma2:2b", response, word)  
            matched = True
            break  

        elif word == "custom":
            matched = True
            pass  

    if not matched:
        llm_response = llm.model("gemma2:2b", response, "default")

    print("response" + response)
    print("llm response" + llm_response)
    typing.typing(llm_response)

    global Thread
    Thread = False
    

def start_recording(event):
    global recording
    global Thread
    if not recording:
        recording = True
        if Thread:
            print("wait in process")
        else:
            Thread = True
            threading.Thread(target=record_audio, daemon=True).start()

def stop_recording(event):
    global recording
    recording = False

print("Press Ctrl+Shift+U to start recording and release to stop.")

# Register hotkeys
keyboard.on_press_key('u', start_recording)
keyboard.on_release_key('u', stop_recording)

keyboard.wait()  

