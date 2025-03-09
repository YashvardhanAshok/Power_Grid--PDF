# tinyllama:latest    2644915ede35    637 MB    
# llama3.2:1b         baf6a787fdff    1.3 GB    
# phi4:latest         ac896e5b8b34    9.1 GB    
# deepseek-r1:8b      28f8fd6cdc67    4.9 GB    
# gemma2:2b           8ccf136fdd52    1.6 GB    

import json
import os
from ollama import chat

# token
def role_finder(text):
    labels = {
        "rewrite": ["rewrite", "reword", "paraphrase"],
        "summarize": ["summarize", "shorten", "condense"],
        "translate": ["translate", "convert to"],
        "code": ["wright a code", "give me a code"],
        "type": ["type"]
    }

    for label, keywords in labels.items():
        if any(keyword in text.lower() for keyword in keywords):

            print("Detected Intent:", label)
            return label

    return "unknown"



# llm
roles_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "roles.json")
with open(roles_file, "r", encoding="utf-8") as file:
    role_data = json.load(file)

def llm(role_type, user_message):
    role = role_data["roles"].get(role_type, role_data["roles"]["default"])
    
    print(f"Selected Role: {role_type}")    

    messages = [
        {"role": role["role"], "content": role["content"]},
        {"role": "user", "content": user_message}
    ]

    response = chat(model="llama3.2:1b", messages=messages)  

    return response["message"]["content"]




