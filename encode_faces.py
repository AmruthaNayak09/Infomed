import os
import pickle
import face_recognition
from pathlib import Path
import hashlib
import json

KNOWN_FACES_DIR = "known_faces"
ENCODINGS_FILE = "encodings.pkl"
CACHE_FILE = ".face_cache.json"

def hash_file(filepath):
    """Generate MD5 hash of file contents to detect changes."""
    try:
        with open(filepath, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()
    except Exception as e:
        print(f"[ERROR] Failed to hash {filepath}: {e}")
        return None

def load_cache():
    """Load previous cache of image hashes."""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"[WARNING] Could not load cache: {e}")
    return {}

def save_cache(cache):
    """Save current hash states."""
    try:
        with open(CACHE_FILE, "w") as f:
            json.dump(cache, f, indent=2)
    except Exception as e:
        print(f"[WARNING] Could not save cache: {e}")

def should_update(cache, current):
    """Compare current and cached state of images."""
    return cache != current

def encode_faces():
    print("[INFO] Checking for face updates...")
    current_state = {}
    known_encodings = []
    known_names = []

    # Step 1: Hash each image using relative path
    for person_dir in Path(KNOWN_FACES_DIR).iterdir():
        if person_dir.is_dir():
            for image_path in person_dir.glob("*.jpg"):
                hash_val = hash_file(image_path)
                if hash_val:
                    relative_path = str(image_path.relative_to(KNOWN_FACES_DIR))
                    current_state[relative_path] = hash_val

    # Step 2: Compare with cached state
    cached_state = load_cache()
    if not should_update(cached_state, current_state):
        print("[INFO] No changes in known_faces. Skipping encoding.")
        return False

    print("[INFO] New or updated faces found. Encoding...")

    # Step 3: Perform encoding
    for person_dir in Path(KNOWN_FACES_DIR).iterdir():
        if person_dir.is_dir():
            name = person_dir.name
            for image_path in person_dir.glob("*.jpg"):
                try:
                    image = face_recognition.load_image_file(image_path)
                    encodings = face_recognition.face_encodings(image)
                    if encodings:
                        known_encodings.append(encodings[0])
                        known_names.append(name)
                        print(f"[ENCODED] {name} - {image_path.name}")
                    else:
                        print(f"[WARNING] No face found in {image_path.name}")
                except Exception as e:
                    print(f"[ERROR] Failed to process {image_path.name}: {e}")

    # Step 4: Save encodings and cache
    with open(ENCODINGS_FILE, "wb") as f:
        pickle.dump((known_encodings, known_names), f)

    save_cache(current_state)
    print(f"[INFO] Encoded {len(known_encodings)} faces.")
    return True
