import os
import vosk

MODEL_PATH = r"D:\ENTERTERMENT\coding\testing\bot\models\vosk-model-en-us-0.22"

# Check if the model directory exists and contains necessary files
if not os.path.exists(MODEL_PATH):
    raise Exception(f"Model path does not exist: {MODEL_PATH}")

required_files = ["final.mdl", "graph", "phones.txt", "ivector_extractor"]
for file in required_files:
    if not any(file in fname for fname in os.listdir(MODEL_PATH)):
        raise Exception(f"Missing required model file: {file}")

# Load the model
model = vosk.Model(MODEL_PATH)
print("Model loaded successfully!")
