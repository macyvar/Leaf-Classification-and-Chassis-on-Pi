## AUTONOMOUS_ROBOT.PY

import time, json, threading, cv2
from motor import forward, stop, backward, turn_left
from ultrasonic import get_distance
from leaf_cnn_runtime import classify_frame
from dashboard import robot_state
import os

def capture_frame():
    from picamera2 import Picamera2
    cam = Picamera2()
    cam.configure(cam.create_preview_configuration())
    cam.start()
    time.sleep(0.5)
    frame = cam.capture_array()
    cam.stop(); cam.close()
    return cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

def run_robot():
    print("Robot thread active — waiting for dashboard START")

    while True:
        if not robot_state["running"]:
            stop()
            time.sleep(0.2)
            continue

        forward(60)

        # Obstacle avoidance
        if get_distance() < 20:
            stop()
            backward(0.3)
            turn_left(0.4)
            continue

        frame = capture_frame()

        label, conf = classify_frame(frame)

        if label != "NOT_LEAF":
            stop()
            print("Leaf Detected:", label)

            t = time.strftime("%Y%m%d-%H%M%S")
            os.makedirs("logs/images", exist_ok=True)
            img_path = f"logs/images/{t}_{label}.jpg"
            cv2.imwrite(img_path, frame)

            # Log result
            try:
                logs = json.load(open("logs/results.json"))
            except:
                logs = []
            logs.append({"timestamp": t, "result": label, "image": img_path})
            json.dump(logs, open("logs/results.json","w"), indent=2)

            time.sleep(1)

if __name__ == "__main__":
    os.makedirs("logs", exist_ok=True)
    if not os.path.exists("logs/results.json"):
        json.dump([], open("logs/results.json","w"))
    t = threading.Thread(target=run_robot, daemon=True)
    t.start()
    print("Autonomous robot running in background thread.")
    while True:
        time.sleep(1)
