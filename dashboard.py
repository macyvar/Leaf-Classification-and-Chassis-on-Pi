## DASHBOARD.PY

from flask import Flask, render_template_string, send_file, jsonify
import json, os

app = Flask(__name__)

os.makedirs("logs/images", exist_ok=True)
results_path = "logs/results.json"
if not os.path.exists(results_path):
    json.dump([], open(results_path, "w"))

robot_state = {"running": False}


def set_state(v):
    robot_state["running"] = v
    print("Robot state ->", v)

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
setTimeout(()=>location.reload(), 5000);
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

@app.route("/")
def index():
    try:
        logs = json.load(open("logs/results.json"))
    except:
        logs = []
    return render_template_string(TEMPLATE, logs=logs, running=robot_state["running"])

@app.route("/img/<int:i>")
def image(i):
    logs = json.load(open("logs/results.json"))
    
    if i >= len(logs):
        from flask import Response
        return Response(b"\x89PNG\r\n\x1a\n", mimetype="image/png")

    return send_file(logs[i]["image"])

@app.route("/start", methods=["POST"])
def start():
    set_state(True)
    return jsonify({"status":"running"})


@app.route("/stop", methods=["POST"])
def stop():
    set_state(False)
    return jsonify({"status":"stopped"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
