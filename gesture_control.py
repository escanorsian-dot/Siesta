import cv2
import pyautogui
import time
from cvzone.HandTrackingModule import HandDetector

pyautogui.FAILSAFE = False

detector = HandDetector(
    staticMode=False,
    maxHands=1,
    detectionCon=0.75,
    minTrackCon=0.7
)

last_trigger_time = 0.0
gesture_cooldown = 1.5

stable_gesture = None
stable_since = 0.0
hold_time_required = 0.8


def press_key(key):
    print(f"Gesture pressed: {key}")
    pyautogui.press(key)


def fingers_to_key(fingers):
    if fingers == [0, 0, 0, 0, 0]:
        return "x"

    if fingers == [1, 1, 1, 1, 1]:
        return "a"

    if fingers == [0, 1, 0, 0, 0]:
        return "q"

    if fingers == [0, 1, 1, 0, 0]:
        return "w"

    if fingers == [0, 1, 1, 1, 0]:
        return "e"

    if fingers == [0, 1, 1, 1, 1]:
        return "r"

    return None


def handle_stable_gesture(current_key):
    global stable_gesture, stable_since, last_trigger_time

    now = time.time()

    if current_key is None:
        stable_gesture = None
        stable_since = 0.0
        return

    if current_key != stable_gesture:
        stable_gesture = current_key
        stable_since = now
        return

    held_for = now - stable_since

    if held_for >= hold_time_required and now - last_trigger_time >= gesture_cooldown:
        press_key(current_key)
        last_trigger_time = now
        stable_gesture = None
        stable_since = 0.0


def run_gesture_control():
    cap = cv2.VideoCapture(0)

    while True:
        success, img = cap.read()
        if not success:
            continue

        img = cv2.flip(img, 1)

        hands, img = detector.findHands(img, draw=True, flipType=False)

        detected_key = None
        fingers = None

        if hands:
            hand = hands[0]
            fingers = detector.fingersUp(hand)
            detected_key = fingers_to_key(fingers)
            handle_stable_gesture(detected_key)
        else:
            handle_stable_gesture(None)

        info1 = f"Fingers: {fingers if fingers else '-'}"
        info2 = f"Gesture: {detected_key if detected_key else '-'}"
        info3 = f"Holding: {stable_gesture if stable_gesture else '-'}"

        progress = 0
        if stable_gesture and stable_since > 0:
            progress = min(int(((time.time() - stable_since) / hold_time_required) * 100), 100)

        info4 = f"Progress: {progress}%"

        cv2.putText(img, info1, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        cv2.putText(img, info2, (20, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        cv2.putText(img, info3, (20, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        cv2.putText(img, info4, (20, 145), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

        cv2.imshow("Siesta Gesture Control", img)

        key = cv2.waitKey(1) & 0xFF
        if key == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    run_gesture_control()