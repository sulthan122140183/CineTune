import csv
import os

# ==========================================
# RESOLVE PATHS (lebih aman & fleksibel)
# ==========================================
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
QUESTIONS_CSV = os.path.join(BASE_DIR, "data", "questions.csv")
GESTURES_CSV  = os.path.join(BASE_DIR, "data", "gestures.csv")
# ==========================================


def load_questions():
    questions = []
    try:
        with open(QUESTIONS_CSV, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                questions.append({
                    "id": int(row["id"]),
                    "image": os.path.join(BASE_DIR, row["image_path"]),   # RESOLVED PATH
                    "audio": os.path.join(BASE_DIR, row["audio_path"]),   # RESOLVED PATH
                    "options": {
                        "A": row["option_a"],
                        "B": row["option_b"],
                        "C": row["option_c"],
                        "D": row["option_d"],
                    },
                    "answer": row["answer"].strip().upper(),
                })
    except Exception as e:
        print("[ERROR] Gagal load questions:", e)
    return questions


def load_gesture_map():
    gestures = {}
    try:
        with open(GESTURES_CSV, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                gestures[row["gesture_name"]] = row["answer"].strip().upper()
        print("[DEBUG] Gesture map loaded:", gestures)   # <= TAMBAH INI
    except Exception as e:
        print("[ERROR] Gagal load gestures:", e)
    return gestures



if __name__ == "__main__":
    print("[TEST] Path file:")
    print("Questions CSV:", QUESTIONS_CSV)
    print("Gestures CSV :", GESTURES_CSV)

    qs = load_questions()
    print("\nLoaded questions:", len(qs))
    if qs:
        print("Sample question:", qs[0])

    gm = load_gesture_map()
    print("\nGesture map:", gm)
