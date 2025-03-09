import tkinter as tk
import customtkinter as ctk
import threading
import tkintermapview as ttk_map
import os
import pyaudio
import wave
import keyboard
import threading
import pyautogui


# Custom
from voice_tras.faster_whisper_model import whisper_modle
from modles.modle import role_finder
from modles.modle import llm

# Colors
White = "#ffffff"
black = "#000000"

# Glogel parameters
Thread = False
recording = False

def record_audio():
    
    # gui
    show_textbox()
    
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    CHUNK = 1024
    recorded_audio_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "recorded_audio.wav")
    audio = pyaudio.PyAudio()
    frames = []

    # format      
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

    print("Recording started...")
    while recording:
        data = stream.read(CHUNK)
        frames.append(data)

    print("Recording stopped.")
    stream.stop_stream()
    stream.close()

    wf = wave.open(recorded_audio_file, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    response = whisper_modle(recorded_audio_file)
    role = role_finder(response)
    
    if (role == "type"):
        pyautogui.write(response, interval=0.01)
    else:
        llm(role,response)    
    
    print("response" + response)

    # reset and start _recoding
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


  
# gui
def update_textbox(response_text):
    textbox.configure(state="normal")
    textbox.delete("0.0", "end")
    text_h_cal = len(response_text)/33
    text_h_cal=text_h_cal + response_text.count('\n')

    if len(response_text)%33 == 0:
        hight = text_h_cal * 15  
    else:
        text_h_cal = text_h_cal + 1
        hight = text_h_cal * 15  
    
    if hight >= 350:
        hight = 350
                 
    textbox.configure(height=hight)
    
    textbox.insert("0.0", response_text)
    textbox.configure(state="disabled")

ctk.set_widget_scaling(1.15)  
root = tk.Tk()
root.attributes('-fullscreen', True)
root.overrideredirect(True)  # Remove the title bar
root.attributes('-topmost', True)  # Always on top

transparent_color = "gray25"
root.config(bg=transparent_color)
root.attributes('-transparentcolor', transparent_color)
root.attributes('-alpha', 1.0)

root_text_frame = ctk.CTkFrame(master=root, fg_color="transparent")
root_text_frame.place(relx=1.0, rely=1.0, anchor="se", y=-45, x=-5)

# Textbox
def show_textbox(event=None):
    if textbox.winfo_viewable():  
        textbox.grid_remove()
    else:
        textbox.grid()  
        
textbox = ctk.CTkTextbox(root_text_frame,  height=10,width=250, wrap="word", text_color=black, fg_color=White)
textbox.insert("0.0", "Hi, how can I help you 😊")
textbox.grid(row=1, column=0, sticky="ew", pady=5)
textbox.configure(state="disabled")
textbox.grid_remove()

# Register hotkeys
print("Press Ctrl+Shift+U to start recording and release to stop.")
keyboard.on_press_key('u', start_recording)
keyboard.on_release_key('u', stop_recording)

root.mainloop()