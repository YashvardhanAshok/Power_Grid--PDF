import pyttsx3

engine = pyttsx3.init()

# text = "Hello, this is an offline text-to-speech example."

def robot(text):
    engine.setProperty("rate", 150)  # Speed of speech
    engine.setProperty("volume", 1.0)  # Volume (0.0 to 1.0)

    engine.say(text)
    engine.runAndWait()

    print("Speech saved as output.mp3")

