import librosa
import tensorflow as tf
import numpy as np

class ScreamDetector:
    def __init__(self):
        try:
            self.model = tf.keras.models.load_model('data/scream_model.h5')
            print("Scream model loaded successfully")
        except Exception as e:
            print(f"Failed to load scream model: {e}")
            raise
        self.sample_rate = 44100
        self.n_mfcc = 20
        self.max_time_steps = 862
        
    def analyze_audio(self, audio_file):
        try:
            y, sr = librosa.load(audio_file, sr=self.sample_rate)
            # Normalize audio to improve detection
            y = y / np.max(np.abs(y)) if np.max(np.abs(y)) > 0 else y
            print(f"Loaded audio: duration={len(y)/sr:.2f}s, sample_rate={sr}, max_amplitude={np.max(np.abs(y)):.2f}")
            mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=self.n_mfcc)
            print(f"MFCC shape before reshape: {mfcc.shape}")
            if mfcc.shape[1] < self.max_time_steps:
                mfcc = np.pad(mfcc, ((0, 0), (0, self.max_time_steps - mfcc.shape[1])), mode='constant')
            else:
                mfcc = mfcc[:, :self.max_time_steps]
            mfcc = mfcc.reshape(1, self.n_mfcc, self.max_time_steps, 1)
            print(f"MFCC input shape to model: {mfcc.shape}")
            prediction = self.model.predict(mfcc, verbose=0)
            is_scream = prediction[0][0] > 0.0 #0.3 # Lowered to 0.2 for smaller screams
            # Log prediction for threshold tuning
            with open("scream_detection_log.txt", "a") as log_file:
                log_file.write(f"File: {audio_file}, Probability: {prediction[0][0]:.4f}, Scream: {is_scream}\n")
            print(f"Audio analysis: scream probability={prediction[0][0]:.4f}, is_scream={is_scream}")
            return is_scream
        except Exception as e:
            print(f"Error analyzing audio {audio_file}: {e}")
            return False

if __name__ == '__main__':
    detector = ScreamDetector()
    test_files = ["data/test_small_scream.wav", "data/test_loud_scream.wav", "data/test_speech.wav"]
    for audio_file in test_files:
        try:
            result = detector.analyze_audio(audio_file)
            print(f"File: {audio_file}, Scream Detected: {result}")
        except FileNotFoundError:
            print(f"File not found: {audio_file}")