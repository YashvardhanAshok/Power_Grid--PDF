import re
from word2number import w2n
import screen_brightness_control as sbc
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
import keyboard  

def media_control(action):
    key_map = {
        "play": "play/pause media",
        "pause": "play/pause media",
        "next": "next track",
        "previous": "previous track",
        "stop": "stop media"
    }
    if action in key_map:
        keyboard.press_and_release(key_map[action])
        
def brightness(action, value):
    current_brightness = sbc.get_brightness()[0]  
    if action == "set":
        sbc.set_brightness(value)
    elif action == "increase": sbc.set_brightness(min(current_brightness + value, 100))
    elif action in ["reduce", "decrease"]: sbc.set_brightness(max(current_brightness - value, 0))  

def volume(action, value):
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = interface.QueryInterface(IAudioEndpointVolume)
    current_volume = volume.GetMasterVolumeLevelScalar()

    value = value / 100  
    if action == "set": volume.SetMasterVolumeLevelScalar(min(max(value, 0.0), 1.0), None)
    elif action == "increase": volume.SetMasterVolumeLevelScalar(min(current_volume + value, 1.0), None)
    elif action in ["reduce", "decrease"]: volume.SetMasterVolumeLevelScalar(max(current_volume - value, 0.0), None)  

def extract_number(text):
    match = re.search(r'(\b\w+(?:\s\w+)*)\sper\scent', text, re.IGNORECASE)
    return w2n.word_to_num(match.group(1)) if match else None

def process_command(text):
    match = re.search(r"(increase|set|reduce|decrease) (?:the )?(volume|brightness)?", text)  
    if match:
        action, setting = match.groups()
        value = extract_number(text)
        if value is None:
            print("⚠️ No valid number detected.")
            return
        if setting == "volume": volume(action, value)
        elif setting == "brightness": brightness(action, value)
        return

    match = re.search(r"(volume|brightness)?", text)  
    if match:
        setting = match.groups()
        value = extract_number(text)
        if setting == "volume": volume("set", value)
        elif setting == "brightness": brightness("set", value)
    
    media_match = re.search(r"(play|pause|stop|next|previous) (?:track|song|music|media)?", text)
    if media_match: media_control(media_match.group(1))
    return

    print("⚠️ No valid command detected.")

