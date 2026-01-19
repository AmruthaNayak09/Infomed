import cv2 
import face_recognition
import pickle
import time
import webbrowser
import os

ENCODING_FILE = "encodings.pkl"
KNOWN_FACES_DIR = "known_faces"
RECOGNITION_DURATION = 3  # seconds

def recognize_face(trigger_callback):
    with open(ENCODING_FILE, "rb") as f:
        known_face_encodings, known_face_names = pickle.load(f)

    face_timers = {}
    webpage_opened = False

    video_capture = cv2.VideoCapture(0)
    if not video_capture.isOpened():
        print("[ERROR] Could not open webcam.")
        return

    print("[INFO] Starting face recognition...")

    while True:
        ret, frame = video_capture.read()
        if not ret:
            break

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        locations = face_recognition.face_locations(rgb)
        encodings = face_recognition.face_encodings(rgb, locations)

        for (top, right, bottom, left), encoding in zip(locations, encodings):
            distances = face_recognition.face_distance(known_face_encodings, encoding)
            min_distance = min(distances)

            if min_distance < 0.4:
                best_match_index = distances.tolist().index(min_distance)
                name = known_face_names[best_match_index]

                if name not in face_timers:
                    face_timers[name] = time.time()
                else:
                    elapsed = time.time() - face_timers[name]
                    if elapsed > RECOGNITION_DURATION and not webpage_opened:
                        print(f"[INFO] Recognized: {name} (distance={min_distance:.2f})")

                        trigger_callback(name)
                        time.sleep(1)
                        webbrowser.open(f"http://127.0.0.1:5000/?name={name}")
                        webpage_opened = True
                        video_capture.release()
                        cv2.destroyAllWindows()
                        return

                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            else:
                # Optional: Show 'Unknown' for unmatched faces
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                cv2.putText(frame, "Unknown", (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

        cv2.imshow("Face Detection", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()
