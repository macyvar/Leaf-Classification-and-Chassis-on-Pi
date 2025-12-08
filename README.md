# Plant Health Monitoring Robot
### Autonomous Leaf Detection • Disease Classification • Obstacle Avoidance • Web Dashboard Control

This robot uses a Raspberry Pi, camera, TB6612 motor driver, ultrasonic sensor, and a machine-learning leaf classifier to autonomously navigate, detect plants, capture images, and classify plant health.

This README includes:

- Full wiring guide  
- Hardware pinout tables  
- System testing guide  
- Dashboard and autonomous mode instructions  
- Model training pipeline  
- Data preprocessing steps  
- Gate-based classification logic  
- TensorFlow Lite inference pipeline  
- Autonomous navigation overview  

---

# Pinout & Wiring Guide

This section describes how to wire the motors, TB6612 motor driver, battery pack, Raspberry Pi, and US-100 ultrasonic sensor.

## Motor Wiring

### Left Side Motors (2 motors)

**Motor A**
- Red → TB6612 **A01**
- Black → TB6612 **A02**

**Motor B**
- Red → TB6612 **A01** (same as Motor A red)
- Black → TB6612 **A02** (same as Motor A black)

### Right Side Motors (2 motors)

**Motor C**
- Red → TB6612 **B01**
- Black → TB6612 **B02**

**Motor D**
- Red → TB6612 **B01** (same as Motor C red)
- Black → TB6612 **B02** (same as Motor C black)

## TB6612 Motor Driver Pinout

| TB6612 Pin | Connects To |
|------------|-------------|
| A01 | Motor A red, Motor B red |
| A02 | Motor A black, Motor B black |
| B01 | Motor C red, Motor D red |
| B02 | Motor C black, Motor D black |
| AIN1 | Raspberry Pi GPIO **17** |
| AIN2 | Raspberry Pi GPIO **27** |
| BIN1 | Raspberry Pi GPIO **22** |
| BIN2 | Raspberry Pi GPIO **23** |
| PWMA | Raspberry Pi GPIO **12** (Left PWM speed) |
| PWMB | Raspberry Pi GPIO **13** (Right PWM speed) |
| STBY | Raspberry Pi GPIO **24** |
| VCC | Raspberry Pi **3.3V** |
| VM | Battery **+** |
| GND | Battery **–**, Raspberry Pi **GND** |


## Power System

### Battery Pack (4×AA or 6V motor pack)

- **Battery + (red)** → TB6612 **VM**
- **Battery – (black)** → TB6612 **GND**  

The Raspberry Pi is powered separately via USB-C.  
The battery ground **must be shared** with Raspberry Pi GND.


## Raspberry Pi Power to Breadboard

| Pi Pin | Connects To |
|--------|-------------|
| 5V | Breadboard **5V rail** |
| GND | Breadboard **GND rail** |


## US-100 Ultrasonic Sensor Wiring

| US-100 Pin | Connects To |
|------------|-------------|
| VCC | Breadboard **5V rail** |
| GND | Breadboard **GND rail** |
| TRIG | Raspberry Pi GPIO **5** |
| ECHO | Raspberry Pi GPIO **6** |


## Raspberry Pi GPIO Summary

| Function | GPIO Pin |
|---------|----------|
| Motor AIN1 | 17 |
| Motor AIN2 | 27 |
| Motor BIN1 | 22 |
| Motor BIN2 | 23 |
| Left Motor PWM | 12 |
| Right Motor PWM | 13 |
| Ultrasonic TRIG | 5 |
| Ultrasonic ECHO | 6 |
| TB6612 Standby (STBY) | 24 |

---

# System Testing Guide

Use these tests before running the full robot system.


## Camera Test

```bash
python3 - << 'EOF'
from picamera2 import Picamera2
import time

cam = Picamera2()
cam.configure(cam.create_preview_configuration())
cam.start()
time.sleep(1)
frame = cam.capture_array()
cam.stop()
print("Camera OK. Frame shape:", frame.shape)
EOF
```

Expected:
```
Camera OK. Frame shape: (480, 640, 3)
```


## Motor Test

```bash
cd plant_robot
python3 - << 'EOF'
from motor import forward, stop
import time

print("Motors test: forward 1 sec")
forward(60)
time.sleep(1)
stop()
EOF
```

Expected:
- Robot wheels spin forward for 1 second.


## Ultrasonic Sensor Test

```bash
python3 - << 'EOF'
from ultrasonic import get_distance
import time

for i in range(5):
    print("Distance:", get_distance(), "cm")
    time.sleep(1)
EOF
```

Expected output around:
```
Distance: 34.2 cm
Distance: 36.1 cm
Distance: 35.5 cm
```

---

# Dashboard Web Interface

The dashboard lets you:

- Start/stop robot  
- View live classification logs  
- View saved leaf images  


## Step 1 — Start Dashboard (On Raspberry Pi)

```bash
cd plant_robot
python3 dashboard.py
```

You should see:

```
Running on http://0.0.0.0:5000
```

---

## Step 2 — Get Pi IP Address

```bash
hostname -I
```


## Step 3 — Open Dashboard (On Laptop/Phone)

Visit:

```
http://<PI-IP>:5000
```

You should see:

- Robot status (RUNNING/STOPPED)  
- Start / Stop buttons  
- Classification table  
- Images  

---

# Autonomous Robot Mode

Run in a second SSH window:

```bash
cd plant_robot
python3 autonomous_robot.py
```

Then click **Start Robot** on the dashboard.

Robot will:

- Drive forward  
- Detect obstacles and turn  
- Capture images  
- Classify HEALTHY / DISEASED  
- Save logs + snapshots  

---

# Machine Learning Model Pipeline

This section documents how the leaf classifier was trained.

## Dataset

We used **PlantVillage**, containing:

- Tomato leaves  
- Potato leaves  
- Pepper leaves  

From these, only two final classes were used:

```
healthy
diseased
```

Non-leaf detection is handled via confidence thresholds (see Gate System).


# Data Processing & Augmentation

Each image is:

- Resized to **224×224**
- Normalized (pixel / 255)
- Augmented with:
  - rotations  
  - width/height shifts  
  - zoom  
  - horizontal flips  
  - brightness changes  

This creates a robust model that generalizes well to real Pi camera input.


# Model Architecture

We use **MobileNetV2** pretrained on **ImageNet**.

Why MobileNetV2?

- Lightweight  
- Fast (real-time on Raspberry Pi)  
- Proven feature extractor  
- Great accuracy with small datasets  

Loaded using:

```
base = MobileNetV2(include_top=False, weights="imagenet")
base.trainable = False
```

A small custom head is added:

- GlobalAveragePooling2D  
- Dense(128, relu)  
- Dropout(0.3)  
- Dense(2, softmax)  

---

# Training Objective

Loss: **categorical_crossentropy**  
Optimizer: **Adam**  
Metric: **accuracy**

Training typically achieves:

- **97–99% validation accuracy**
- Low train/val gap → minimal overfitting


# Gate-Based Classification System

Although the model predicts:

```
[diseased_prob, healthy_prob]
```

We use thresholds to stabilize predictions in the field.

## Gate 1 — Leaf vs Not-Leaf

If:

```
max_probability < 0.80
```

Then return:

```
NOT_LEAF
```

This rejects:

- floor  
- walls  
- hands  
- distant plants  
- blurred frames  


## Gate 2 — Health Classification

If Gate 1 passes:

```
if confidence < 0.60:
    return UNSURE
else:
    return HEALTHY or DISEASED
```

This reduces false positives.

---

# TFLite Inference

The Keras model is converted using:

```python
converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()
```

TFLite advantages:

- Very fast (<50ms inference)
- Very small
- Perfect for Raspberry Pi robots


# On-Device Inference Pipeline

1. Capture image from Pi camera  
2. Convert to BGR → RGB  
3. Resize to **224×224**  
4. Normalize (divide by 255)  
5. Expand dims for model  
6. Run TFLite inference  
7. Apply Gate 1 + 2  
8. Save result + snapshot  
9. Update dashboard  

---

# Autonomous Navigation Overview

Robot loop:

1. **Drive forward**
2. **Check ultrasonic distance**
   
   ```
   if < 20 cm → stop, reverse, turn left
   ```

3. **Capture image**
4. **Run leaf classifier**
5. If HEALTHY/DISEASED:
   - stop  
   - save frame  
   - log results  
   - resume driving  
6. Loop indefinitely  


