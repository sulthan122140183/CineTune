import cv2
import mediapipe as mp

class GestureDetector:
    def __init__(self):
        self.hands = mp.solutions.hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        self.drawer = mp.solutions.drawing_utils

    def detect(self, frame):
        """
        Input: frame BGR (opencv)
        Output:
            - landmarks: list berisi 21 titik (x, y)
            - frame: frame dengan landmark digambar
        """

        # Convert BGR → RGB
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Proses tangan
        results = self.hands.process(rgb)

        landmarks = None

        # Jika ada tangan
        if results.multi_hand_landmarks:
            handLms = results.multi_hand_landmarks[0]
            
            # Draw landmarks di frame
            self.drawer.draw_landmarks(
                frame, 
                handLms,
                mp.solutions.hands.HAND_CONNECTIONS
            )

            # Extract koordinat setiap titik
            h, w, _ = frame.shape
            landmarks = [(int(lm.x * w), int(lm.y * h)) for lm in handLms.landmark]

        return landmarks, frame
