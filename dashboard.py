###############################################
#  LEAF ROBOT DASHBOARD + AUTONOMOUS CONTROL  #
###############################################

from flask import Flask, render_template_string, send_file, jsonify
from threading import Thread
import time, json, os
import cv2

# ---- Motor Driver ----
from motor import forward, stop as motor_stop

# ---- Sensors & Classifier ----
from ultrasonic import get_distance
from picamera2 import Picamera2
from leaf_cnn_runtime import classify_frame

app = Flask(__name__)

# Storage for images + results
os.makedirs("logs/images", exist_ok=True)
results_path = "logs/results.json"
if not os.path.exists(results_path):
    json.dump([], open(results_path, "w"))

# Shared state
robot_state = {"running": False}


def set_state(v):
    robot_state["running"] = v
    print("Robot state ->", v)


###############################################
# AUTONOMOUS CONTROL LOOP (runs in background)
###############################################

def autonomous_loop():
    print("Autonomous loop running...")

    # Start camera
    cam = Picamera2()
    cam.configure(cam.create_preview_configuration())
    cam.start()
    time.sleep(1)

    while True:
        if robot_state["running"]:

            # -------------------------------
            #  BASIC DRIVING
            # -------------------------------
            forward(60)
            time.sleep(0.1)

            # -------------------------------
            #  OBSTACLE AVOIDANCE
            # -------------------------------
            try:
                dist = get_distance()
                if dist < 20:
                    print("Obstacle detected:", dist, "cm")
                    motor_stop()
                    time.sleep(0.5)
                    continue
            except:
                pass

            # -------------------------------
            #  CAPTURE FRAME
            # -------------------------------
            frame = cam.capture_array()
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            # -------------------------------
            #  CLASSIFY FRAME
            # -------------------------------
            label, conf = classify_frame(frame_bgr)

            if label != "NOT_LEAF":
                motor_stop()
                print("Leaf Detected:", label)

                # Save image
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                safe_timestamp = timestamp.replace(":", "-")
                img_path = f"logs/images/{safe_timestamp}_{label}.jpg"
                cv2.imwrite(img_path, frame_bgr)

                # Log result
                try:
                    logs = json.load(open(results_path))
                except:
                    logs = []

                logs.append({
                    "timestamp": timestamp,
                    "result": label,
                    "image": img_path
                })

                json.dump(logs, open(results_path, "w"), indent=2)

                time.sleep(1)

        else:
            motor_stop()
            time.sleep(0.1)


###############################################
# HTML DASHBOARD
###############################################

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<style>
body { font-family:Arial; background:#eef; padding:20px; }
.btn { padding:12px 24px; font-size:18px; margin:5px; cursor:pointer; border-radius:6px; }
.start { background:#4CAF50; color:white; }
.stop { background:#d33; color:white; }
table { width:100%; border-collapse:collapse; margin-top:20px; font-size:16px; }
th,td { border:1px solid #444; padding:10px; text-align:center; }
img { width:150px; border-radius:4px; }
</style>
</head>
<body>

<h1>Leaf Inspection Dashboard</h1>

<h3>Status:
  <span style="color:{{ 'green' if running else 'red' }}">
    {{ 'RUNNING' if running else 'STOPPED' }}
  </span>
</h3>

<button class="btn start" onclick="send('start')">Start Robot</button>
<button class="btn stop" onclick="send('stop')">Stop Robot</button>

<script>
function send(cmd) {
    fetch('/' + cmd, {method:'POST'})
    .then(r => r.json()).then(_ => location.reload());
}
setTimeout(()=>location.reload(), 3000);
</script>

<table>
<tr><th>Time</th><th>Result</th><th>Image</th></tr>
{% for e in logs %}
<tr>
    <td>{{e.timestamp}}</td>
    <td>{{e.result}}</td>
    <td><img src="/img/{{loop.index0}}"></td>
</tr>
{% endfor %}
</table>

</body></html>
"""


###############################################
# ROUTES
###############################################

@app.route("/")
def index():
    try:
        logs = json.load(open(results_path))
    except:
        logs = []
    return render_template_string(TEMPLATE, logs=logs, running=robot_state["running"])


@app.route("/img/<int:i>")
def image(i):
    logs = json.load(open(results_path))
    
    if i >= len(logs):
        from flask import Response
        return Response(b"\x89PNG\r\n\x1a\n", mimetype="image/png")

    return send_file(logs[i]["image"])


@app.route("/start", methods=["POST"])
def start():
    print("Start pressed!")
    set_state(True)
    return jsonify({"status": "running"})


@app.route("/stop", methods=["POST"])
def stop():
    print("Stop pressed!")
    set_state(False)
    motor_stop()
    return jsonify({"status": "stopped"})


###############################################
# START THREAD + RUN SERVER
###############################################

if __name__ == "__main__":
    t = Thread(target=autonomous_loop, daemon=True)
    t.start()

    print("Starting dashboard on http://0.0.0.0:5000 ...")
    app.run(host="0.0.0.0", port=5000)
