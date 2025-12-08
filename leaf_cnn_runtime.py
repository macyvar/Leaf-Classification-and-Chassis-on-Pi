## LEAF_CNN_RUNTIME.PY

import cv2
import numpy as np
import tflite_runtime.interpreter as tflite

MODEL_PATH = "leaf_cnn.tflite"

# OUTPUT = [diseased_prob, healthy_prob]
# Gate system converts this to: NOT_LEAF / UNSURE / HEALTHY / DISEASED
CLASS_NAMES = ["DISEASED", "HEALTHY"]

# THRESHOLDS
GATE1_THRESHOLD = 0.80   # Leaf vs Not Leaf
GATE2_THRESHOLD = 0.60   # Healthy vs Diseased confidence

interpreter = tflite.Interpreter(MODEL_PATH)
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

def preprocess(frame):
    img = cv2.resize(frame, (224, 224))
    img = img.astype(np.float32) / 255.0
    return np.expand_dims(img, axis=0)

def classify_frame(frame):
    # Preprocess image 
    img = preprocess(frame)

    # Run model 
    interpreter.set_tensor(input_details[0]["index"], img)
    interpreter.invoke()
    output = interpreter.get_tensor(output_details[0]["index"])[0]  
    # output → [diseased_prob, healthy_prob]

    # gET prediction info 
    class_id = int(np.argmax(output))
    conf = float(np.max(output))


    # GATE 1 — Leaf vs Not Leaf
    if conf < GATE1_THRESHOLD:
        return "NOT_LEAF", conf
    # GATE 2 — Healthy vs Diseased
    if conf < GATE2_THRESHOLD:
        return "UNSURE", conf
    # Otherwise return real class
    if class_id == 1:
        return "HEALTHY", conf
    else:
        return "DISEASED", conf
