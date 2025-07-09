import pyaudio
import numpy as np
import wave
from backend.scream_detector import ScreamDetector
from backend.messaging_service import MessagingService
from backend.location_service import LocationService
import time
import threading

class AudioMonitor:
    def __init__(self, user_id, db, main_screen=None):
        self.user_id = user_id
        self.db = db
        self.main_screen = main_screen
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.GAIN = 5.0
        self.detector = ScreamDetector()
        self.messaging = MessagingService()
        self.location = LocationService(self.db, self.user_id)
        self.running = False
        self.thread = None

    def start_monitoring(self):
        if self.running:
            print("Monitoring already running")
            return
        self.running = True
        self.thread = threading.Thread(target=self._monitor_audio)
        self.thread.daemon = True
        self.thread.start()
        print(f"Audio monitoring started for user_id {self.user_id}")

    def stop_monitoring(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)
        print("Audio monitoring stopped")

    def _monitor_audio(self):
        try:
            p = pyaudio.PyAudio()
            stream = p.open(format=self.FORMAT, channels=self.CHANNELS, rate=self.RATE, input=True, frames_per_buffer=self.CHUNK)
            print("Monitoring audio in background... Scream loudly to test!")
            while self.running:
                data = stream.read(self.CHUNK, exception_on_overflow=False)
                audio_data = np.frombuffer(data, dtype=np.int16) * self.GAIN
                if self.check_command(audio_data):
                    self.record_and_analyze(stream, p)
            stream.stop_stream()
            stream.close()
            p.terminate()
        except Exception as e:
            print(f"Error in audio monitoring: {e}")
            self.running = False

    def check_command(self, audio_data):
        max_amplitude = np.max(np.abs(audio_data))
        is_loud = max_amplitude > 50
        print(f"Audio check: max amplitude={max_amplitude}, loud={is_loud}")
        return is_loud

    def record_and_analyze(self, stream, p):
        frames = []
        RECORD_SECONDS = 5
        print(f"Recording {RECORD_SECONDS} seconds of audio...")
        for _ in range(0, int(self.RATE / self.CHUNK * RECORD_SECONDS)):
            if not self.running:
                break
            data = stream.read(self.CHUNK, exception_on_overflow=False)
            frames.append(data)
        filename = f"data/emergency_{self.user_id}_{int(time.time())}.wav"
        try:
            wf = wave.open(filename, 'wb')
            wf.setnchannels(self.CHANNELS)
            wf.setsampwidth(p.get_sample_size(self.FORMAT))
            wf.setframerate(self.RATE)
            wf.writeframes(b''.join(frames))
            wf.close()
            print(f"Audio recorded: {filename}")
        except Exception as e:
            print(f"Error saving audio file {filename}: {e}")
            return

        try:
            if self.detector.analyze_audio(filename):
                print(f"Scream detected in {filename}")
                guardians = self.db.get_guardians(self.user_id)
                if not guardians:
                    print(f"No guardians found for user_id {self.user_id}")
                    return
                guardian_numbers = [g[1] for g in guardians]
                location = self.location.get_location() or self.location.get_last_location()
                numbers_to_alert = guardian_numbers
                print(f"Sending alert to: {numbers_to_alert}, Location: {location}")
                self.messaging.send_emergency_alert(numbers_to_alert, location, self.location, self.main_screen)
            else:
                print(f"No scream detected in {filename}")
        except Exception as e:
            print(f"Error processing scream detection or alert: {e}")