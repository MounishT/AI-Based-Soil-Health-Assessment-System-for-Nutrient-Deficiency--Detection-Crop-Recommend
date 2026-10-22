import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.applications.resnet50 import preprocess_input
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from PIL import Image
import cv2

# Configuration
IMG_SIZE = (224, 224)
BATCH_SIZE = 8
EPOCHS = 1  # For demonstration. Increase for real training.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, "dummy_dataset")
MODEL_SAVE_PATH = os.path.join(BASE_DIR, "..", "models", "cnn_disease_model.h5")

CLASSES = ["Healthy", "Nitrogen_Deficiency", "Phosphorus_Deficiency", "Potassium_Deficiency"]

def create_synthetic_dataset():
    """Generates a dummy dataset so the training script works out-of-the-box."""
    print("Generating synthetic dataset...")
    os.makedirs(DATASET_DIR, exist_ok=True)
    
    for class_name in CLASSES:
        class_dir = os.path.join(DATASET_DIR, class_name)
        os.makedirs(class_dir, exist_ok=True)
        
        # Create 10 dummy images per class
        for i in range(10):
            # Generate random noise image with a slight color tint based on class
            img_array = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
            if class_name == "Healthy":
                img_array[:, :, 1] = 200  # Green tint
            elif class_name == "Nitrogen_Deficiency":
                img_array[:, :, 0] = 200; img_array[:, :, 1] = 200 # Yellow tint
                
            img = Image.fromarray(img_array)
            img.save(os.path.join(class_dir, f"dummy_{i}.jpg"))
            
    print("Synthetic dataset created at:", DATASET_DIR)

def build_model(num_classes):
    """Builds a transfer-learning model based on ResNet50."""
    base_model = ResNet50(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
    
    # Freeze the base model
    base_model.trainable = False
    
    # Add custom classification head
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(128, activation='relu')(x)
    x = Dropout(0.2)(x)
    predictions = Dense(num_classes, activation='softmax')(x)
    
    model = Model(inputs=base_model.input, outputs=predictions)
    
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    return model

def cv2_preprocessing(img_array):
    """Custom OpenCV preprocessing function for data augmentation."""
    # Ensure uint8
    if img_array.dtype != np.uint8:
        img_array = img_array.astype(np.uint8)
        
    # Color Correction
    lab = cv2.cvtColor(img_array, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    cl = clahe.apply(l)
    limg = cv2.merge((cl,a,b))
    img_corrected = cv2.cvtColor(limg, cv2.COLOR_LAB2RGB)
    
    # Noise reduction
    img_smoothed = cv2.GaussianBlur(img_corrected, (5, 5), 0)
    
    # Keras expects float32 in range [0, 1] if rescale=1./255 or preprocessed
    return preprocess_input(img_smoothed.astype(np.float32))

def train():
    create_synthetic_dataset()
    
    print("Preparing data generators...")
    datagen = ImageDataGenerator(
        preprocessing_function=cv2_preprocessing,
        validation_split=0.2,
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        horizontal_flip=True
    )
    
    train_generator = datagen.flow_from_directory(
        DATASET_DIR,
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        subset='training'
    )
    
    val_generator = datagen.flow_from_directory(
        DATASET_DIR,
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        subset='validation'
    )
    
    print("Building model...")
    model = build_model(len(CLASSES))
    
    print("Starting training (Transfer Learning)...")
    model.fit(
        train_generator,
        epochs=EPOCHS,
        validation_data=val_generator
    )
    
    # Ensure models directory exists
    os.makedirs(os.path.dirname(MODEL_SAVE_PATH), exist_ok=True)
    
    print(f"Saving model to {MODEL_SAVE_PATH}...")
    model.save(MODEL_SAVE_PATH)
    print("Training complete! Model saved.")

if __name__ == "__main__":
    train()
