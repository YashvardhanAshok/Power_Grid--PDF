import tkinter as tk
import customtkinter as ctk
from ollama import chat
import threading


# remove
import pyttsx3

engine = pyttsx3.init()
def robot(text):
    engine.setProperty("rate", 150)  # Speed of speech
    engine.setProperty("volume", 1.0)  # Volume (0.0 to 1.0)

    engine.say(text)
    engine.runAndWait()
# remove


# Colors
White = "#ffffff"
black = "#000000"

def llm(text, model_name):
    response = chat(model=model_name, messages=[{'role': 'user', 'content': text}])
    root.after(0, update_textbox, response["message"]["content"])  

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
    
    # button.configure(state="normal")  
    entry.configure(state="normal")


# Root window setup
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

# Model selection dropdown
row_1_frame = ctk.CTkFrame(master=root_text_frame, fg_color="transparent")
row_1_frame.grid(row=0, column=0, sticky="e")

model_names = ["tinyllama:latest", "llama3.2:1b", "gemma2:2b", "deepseek-r1:8b", "phi4:latest"]
model_namesoption = ctk.CTkOptionMenu(row_1_frame, values=model_names, text_color=black, fg_color=White,
                                      button_color=White, button_hover_color="gray", dropdown_fg_color=White,
                                      dropdown_text_color=black, dropdown_hover_color="gray")
model_namesoption.set("llama3.2:1b")
model_namesoption.grid(row=0, column=0, sticky="e")

# speker  
def speek():
    text = str(textbox.get("1.0", "end"))

    speek_thread = threading.Thread(target=robot, args=(text,))
    speek_thread.start()
    
# button = ctk.CTkButton(row_1_frame, text="+",command=speek, width=25, height=25,text_color=black, fg_color="green", hover_color="gray")
# button.grid(row=0, column=1 ,sticky="e",padx=(5,0))

# Textbox
textbox = ctk.CTkTextbox(root_text_frame,  height=10, wrap="word", text_color=black, fg_color=White)
textbox.insert("0.0", "Hi, how can I help you 😊")
textbox.configure(state="disabled")
textbox.grid(row=1, column=0, sticky="ew", pady=5)

# Function to handle button click
def button_event(event=None):
    text = entry.get().strip()
    if not text:
        return

    entry.delete(0, "end")
    # button.configure(state="disabled")
    entry.configure(state="disabled")
    
    textbox.configure(state="normal")
    textbox.delete("0.0", "end")
    textbox.insert("0.0", "Thinking... 🤔")
    textbox.configure(state="disabled")


    thread = threading.Thread(target=llm, args=(text, model_namesoption.get()), daemon=True)
    thread.start()

# Frame for entry and button
text_send_frame = ctk.CTkFrame(master=root_text_frame, fg_color="transparent")
text_send_frame.grid(row=2, column=0, sticky="e")

# Entry widget
entry = ctk.CTkEntry(text_send_frame, placeholder_text="Enter text...", width=200, fg_color=White, text_color=black)
entry.grid(row=0, column=1, sticky="ew")
entry.bind("<Return>", button_event)  

# mic
mic_button = ctk.CTkButton(text_send_frame, text="mic", command=button_event, width=25, height=25,
                        text_color=black, fg_color=White, hover_color="gray")
mic_button.grid(row=0,padx=(0,2), column=0,sticky="w")

# Send button
button = ctk.CTkButton(text_send_frame, text=">", command=button_event, width=25, height=25,
                        text_color=black, fg_color="green", hover_color="gray")
button.grid(row=0, column=3,padx=(2,0),sticky="e")

root.mainloop()
