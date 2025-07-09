import os
import numpy as np
import librosa
import tensorflow as tf
from tensorflow.keras import layers, models
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report

# Paths to your dataset
NON_SCREAMING_PATH = r"D:\Project_HSD\archive\NotScreaming"
SCREAMING_PATH = r"D:\Project_HSD\archive\Screaming"
MODEL_PATH = r"data\scream_model.h5"

# Parameters
SAMPLE_RATE = 44100
DURATION = 5  # Assuming 5-second clips; adjust as needed
N_MFCC = 20
MAX_TIME_STEPS = 862  # Adjust based on your longest audio file after MFCC extraction

def load_audio_files(path, label):
    audio_data = []
    labels = []
    for filename in os.listdir(path):
        if filename.endswith('.wav'):
            file_path = os.path.join(path, filename)
            try:
                y, sr = librosa.load(file_path, sr=SAMPLE_RATE, duration=DURATION)
                mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=N_MFCC)
                # Pad or truncate to fixed length
                if mfcc.shape[1] < MAX_TIME_STEPS:
                    mfcc = np.pad(mfcc, ((0, 0), (0, MAX_TIME_STEPS - mfcc.shape[1])), mode='constant')
                else:
                    mfcc = mfcc[:, :MAX_TIME_STEPS]
                audio_data.append(mfcc)
                labels.append(label)
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
    return audio_data, labels

def prepare_data(use_cnn=True):
    # Load screaming data
    scream_data, scream_labels = load_audio_files(SCREAMING_PATH, 1)
    # Load non-screaming data
    non_scream_data, non_scream_labels = load_audio_files(NON_SCREAMING_PATH, 0)
    
    # Combine datasets
    X = np.array(scream_data + non_scream_data)
    y = np.array(scream_labels + non_scream_labels)
    
     # Split into train and test sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    if use_cnn:
        # Reshape for CNN (add channel dimension)
        X_train = X_train.reshape(X_train.shape[0], N_MFCC, MAX_TIME_STEPS, 1)
        X_test = X_test.reshape(X_test.shape[0], N_MFCC, MAX_TIME_STEPS, 1)
        return X_train, X_test, y_train, y_test, None  # CNN doesn't use class weights in this implementation
    else:
        # Flatten MFCC for SVM
        X_train_flat = X_train.reshape(X_train.shape[0], -1)
        X_test_flat = X_test.reshape(X_test.shape[0], -1)
        
         # Feature scaling for SVM
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train_flat)
        X_test_scaled = scaler.transform(X_test_flat)
        
        # Compute class weights to handle imbalance
        class_weights = compute_class_weight('balanced', classes=np.unique(y_train), y=y_train)
        class_weight_dict = {0: class_weights[0], 1: class_weights[1]}
        return X_train_scaled, X_test_scaled, y_train, y_test, class_weight_dict

def build_cnn_model():
    model = models.Sequential([
        layers.Input(shape=(N_MFCC, MAX_TIME_STEPS, 1)),
        layers.Conv2D(32, (3, 3), activation='relu', padding='same'),
        layers.MaxPooling2D((2, 2)),
        layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
        layers.MaxPooling2D((2, 2)),
        layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
        layers.MaxPooling2D((2, 2)),
        layers.Flatten(),
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.5),
        layers.Dense(1, activation='sigmoid')
    ])
    
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    return model

def train_cnn_model():
    X_train, X_test, y_train, y_test, _ = prepare_data(use_cnn=True)
    
    model = build_cnn_model()
    model.summary()
    
    # Train the model
    history = model.fit(X_train, y_train, 
                       epochs=20,  # Increased epochs
                       batch_size=32, 
                       validation_data=(X_test, y_test))
    
    # Evaluate the model
    loss, accuracy = model.evaluate(X_test, y_test)
    print(f"CNN Test Accuracy: {accuracy * 100:.2f}%")
    
    # Save the model
    model.save(MODEL_PATH)
    print(f"CNN Model saved to {MODEL_PATH}")
    
    return model, history

def train_svm_model():
    X_train, X_test, y_train, y_test, class_weight_dict = prepare_data(use_cnn=False)
    
    # Create SVM model
    svm_model = SVC(kernel='rbf', C=1.0, class_weight=class_weight_dict) # You can adjust kernel and C
    
    # Train the SVM model
    svm_model.fit(X_train, y_train)
    
    # Make predictions
    y_pred = svm_model.predict(X_test)
    
    # Evaluate the model
    accuracy = accuracy_score(y_test, y_pred)
    print(f"SVM Test Accuracy: {accuracy * 100:.2f}%")
    print(classification_report(y_test, y_pred))
    
    return svm_model

if __name__ == '__main__':
    # Train and evaluate CNN
    cnn_model, cnn_history = train_cnn_model()
    
    # Train and evaluate SVM
    svm_model = train_svm_model()
    
    # You can choose to use either the CNN or SVM model based on their performance
    # or you can combine their predictions (ensemble method) to potentially improve accuracy.
