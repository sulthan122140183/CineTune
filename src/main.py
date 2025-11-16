import cv2
from vision.gesture_detector import GestureDetector
from vision.gesture_mapper import GestureMapper

detector = GestureDetector()
mapper = GestureMapper()

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)

    landmarks, frame = detector.detect(frame)
    gesture = mapper.map(landmarks)

    cv2.putText(frame, f"Gesture: {gesture}", (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

    cv2.imshow("Gesture Mapping Test", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
