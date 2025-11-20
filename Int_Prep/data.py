import os
import json

# ---- 1. data.py joylashgan papka yo‘lini olish ----
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ---- 2. data.json ga absolut path yasash ----
json_path = os.path.join(BASE_DIR, "data.json")

# ---- 3. Faylni o‘qish ----
try:
    with open(json_path, "r") as f:
        data = json.load(f)

    print("JSON file loaded successfully!")
    print(data)

except FileNotFoundError:
    print(f"ERROR: data.json not found at path: {json_path}")

except json.JSONDecodeError:
    print("ERROR: JSON file is not valid (broken JSON).")

