import cv2
import mediapipe as mp
from scipy.spatial import distance
from gtts import gTTS
import pygame
import io
import time

# Setup pygame mixer
pygame.mixer.init()

# Setup Mediapipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# Fungsi EAR
def eye_aspect_ratio(eye):
    A = distance.euclidean(eye[1], eye[5])
    B = distance.euclidean(eye[2], eye[4])
    C = distance.euclidean(eye[0], eye[3])
    ear = (A + B) / (2.0 * C)
    return ear

# Landmark mata di Face Mesh
LEFT_EYE = [362, 385, 387, 263, 373, 380]
RIGHT_EYE = [33, 160, 158, 133, 153, 144]

# Threshold EAR dan counter
EAR_THRESHOLD = 0.25
EAR_CONSEC_FRAMES = 20
counter = 0
alert_played = False
alert_text = ""
alert_start_time = 0
ALERT_DISPLAY_SECONDS = 3

cap = cv2.VideoCapture(0)

def play_tts(text):
    mp3_fp = io.BytesIO()
    tts = gTTS(text=text, lang="id")
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    pygame.mixer.music.load(mp3_fp, "mp3")
    pygame.mixer.music.play()

def draw_hud(frame, ear, is_drowsy):
    h, w, _ = frame.shape
    
    # Colors
    color_safe = (0, 255, 0)
    color_danger = (0, 0, 255)
    color_ui = (255, 255, 0) # Cyan/Yellowish
    
    # 1. Sci-Fi Borders
    cv2.line(frame, (20, 20), (100, 20), color_ui, 2)
    cv2.line(frame, (20, 20), (20, 100), color_ui, 2)
    cv2.line(frame, (w-20, 20), (w-100, 20), color_ui, 2)
    cv2.line(frame, (w-20, 20), (w-20, 100), color_ui, 2)
    
    cv2.line(frame, (20, h-20), (100, h-20), color_ui, 2)
    cv2.line(frame, (20, h-20), (20, h-100), color_ui, 2)
    cv2.line(frame, (w-20, h-20), (w-100, h-20), color_ui, 2)
    cv2.line(frame, (w-20, h-20), (w-20, h-100), color_ui, 2)

    # 2. EAR Bar (Left Side)
    bar_height = 200
    bar_width = 20
    bar_x = 30
    bar_y = h // 2 - bar_height // 2
    
    # Draw container
    cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), color_ui, 1)
    
    # Draw fill
    fill_height = int(min(ear / 0.4, 1.0) * bar_height)
    fill_color = color_safe if ear > EAR_THRESHOLD else color_danger
    cv2.rectangle(frame, (bar_x + 2, bar_y + bar_height - fill_height), (bar_x + bar_width - 2, bar_y + bar_height), fill_color, -1)
    
    # Label
    cv2.putText(frame, f"EAR: {ear:.2f}", (bar_x, bar_y - 10), cv2.FONT_HERSHEY_PLAIN, 1, color_ui, 1)

    # 3. Status Text (Top Right)
    status_text = "SYSTEM: ACTIVE"
    cv2.putText(frame, status_text, (w - 200, 40), cv2.FONT_HERSHEY_PLAIN, 1.2, color_ui, 1)
    
    drowsy_text = "STATUS: DROWSY" if is_drowsy else "STATUS: ALERT"
    drowsy_color = color_danger if is_drowsy else color_safe
    cv2.putText(frame, drowsy_text, (w - 200, 65), cv2.FONT_HERSHEY_PLAIN, 1.2, drowsy_color, 1)

    # 4. Red Overlay Alert
    if is_drowsy:
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, h), color_danger, -1)
        cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)
        
        cv2.putText(frame, "WARNING: DROWSINESS DETECTED", (w//2 - 250, h//2), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 3)

while True:
    ret, frame = cap.read()
    if not ret:
        break
        
    # Flip frame horizontal
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb_frame)

    current_ear = 0
    is_drowsy = False

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            # 3D Face Mesh Visualization REMOVED as per user request
            # mp_drawing.draw_landmarks(...) 

            h, w, _ = frame.shape
            left_eye = [(int(face_landmarks.landmark[i].x * w), int(face_landmarks.landmark[i].y * h)) for i in LEFT_EYE]
            right_eye = [(int(face_landmarks.landmark[i].x * w), int(face_landmarks.landmark[i].y * h)) for i in RIGHT_EYE]

            leftEAR = eye_aspect_ratio(left_eye)
            rightEAR = eye_aspect_ratio(right_eye)
            current_ear = (leftEAR + rightEAR) / 2.0

            if current_ear < EAR_THRESHOLD:
                counter += 1
                if counter >= EAR_CONSEC_FRAMES:
                    is_drowsy = True
                    if not alert_played:
                        alert_text = "Kamu ngantuk Khalifa! Segera tidur ya"
                        alert_start_time = time.time()
                        play_tts(alert_text)
                        alert_played = True
            else:
                counter = 0
                alert_played = False
                is_drowsy = False

    # Draw HUD and Overlays
    draw_hud(frame, current_ear, is_drowsy)

    cv2.imshow("Ngantuk Detector 3D", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
        
