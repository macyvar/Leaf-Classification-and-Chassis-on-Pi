###############################################
#  SIMPLE DASHBOARD + AUTONOMOUS MOTOR CONTROL
###############################################

from flask import Flask, render_template_string, send_file, jsonify
from threading import Thread
import time, json, os

# ---- Motor Driver ----
from motor import forward, stop as motor_stop

app = Flask(__name__)

# Storage for images + results (empty in this version)
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
    while True:
        if robot_state["running"]:
            forward()       # <- Robot moves forward
            time.sleep(0.1)
        else:
            motor_stop()    # <- Robot stays stopped
            time.sleep(0.1)

###############################################
# HTML DASHBOARD TEMPLATE
###############################################

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<style>
body { font-family:Arial; background:#eef; padding:20px; }
.btn { padding:10px 20px; font-size:18px; margin:5px; cursor:pointer; }
.start { background:#4CAF50; color:white; }
.stop { background:#d33; color:white; }
table { width:100%; border-collapse:collapse; margin-top:20px; }
th,td { border:1px solid #444; padding:10px; }
img { width:150px; }
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
