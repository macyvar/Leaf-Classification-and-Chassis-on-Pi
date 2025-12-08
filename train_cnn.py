import tensorflow as tf
import tensorflow.keras as keras
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import matplotlib.pyplot as plt

# PARAMS
IMAGE_SIZE = 224
BATCH_SIZE = 32
DATASET = "dataset"   # structure: dataset/{healthy,diseased}

# DATA AUG
train_aug = ImageDataGenerator(
    rescale=1/255.0,
    rotation_range=25,
    width_shift_range=0.1,
    height_shift_range=0.1,
    zoom_range=0.15,
    horizontal_flip=True,
    brightness_range=[0.6, 1.4],
    validation_split=0.2
)

# for train
train_gen = train_aug.flow_from_directory(
    DATASET, target_size=(IMAGE_SIZE, IMAGE_SIZE),
    class_mode="categorical", batch_size=BATCH_SIZE, subset="training"
)

# for val
val_gen = train_aug.flow_from_directory(
    DATASET, target_size=(IMAGE_SIZE, IMAGE_SIZE),
    class_mode="categorical", batch_size=BATCH_SIZE, subset="validation"
)

# Print class label mapping 
print("\nClass indices:", train_gen.class_indices)
# Expected: "diseased": 0, "healthy": 1

# BUILD MODEL 
base = keras.applications.MobileNetV2(
    input_shape=(IMAGE_SIZE, IMAGE_SIZE, 3),
    include_top=False,
    weights="imagenet"
)
base.trainable = False

model = keras.Sequential([
    base,
    keras.layers.GlobalAveragePooling2D(),
    keras.layers.Dense(128, activation="relu"),
    keras.layers.Dropout(0.3),
    # 2 classes only 
    keras.layers.Dense(2, activation="softmax") 
])

model.compile(
    optimizer="adam",
    loss="categorical_crossentropy",
    metrics=["accuracy"]
)

model.summary()


# TRAINING
history = model.fit(
    train_gen,
    validation_data=val_gen,
    epochs=8
)

# Final accuracy print
print("\nFinal Training Accuracy:", history.history["accuracy"][-1])
print("Final Validation Accuracy:", history.history["val_accuracy"][-1])

# SAVE
model.save("leaf_cnn.h5")
converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
tflite_model = converter.convert()
open("leaf_cnn.tflite", "wb").write(tflite_model)


# PLOT ACCURACCY
plt.figure()
plt.plot(history.history["accuracy"], label="Train Acc")
plt.plot(history.history["val_accuracy"], label="Val Acc")
plt.title("Accuracy")
plt.legend()
plt.tight_layout()
plt.savefig("accuracy_plot.png")
plt.close()


# PLOT LOSS
plt.figure()
plt.plot(history.history["loss"], label="Train Loss")
plt.plot(history.history["val_loss"], label="Val Loss")
plt.title("Loss")
plt.legend()
plt.tight_layout()
plt.savefig("loss_plot.png")
plt.close()
