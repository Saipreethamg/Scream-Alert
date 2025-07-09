import pyaudio
import numpy as np
import threading
import time
import speech_recognition as sr
import wave
from backend.location_service import LocationService
from backend.scream_detector import ScreamDetector

class CommandDetector:
    def __init__(self, messaging_service, db, user_id, main_screen=None):
        self.messaging_service = messaging_service
        self.db = db
        self.user_id = user_id
        self.main_screen = main_screen
        self.location = LocationService(self.db, self.user_id)
        self.detector = ScreamDetector()
        self.running = False
        self.thread = None
        self.keyword = "help"
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.RECORD_SECONDS = 5

    def start_listening(self):
        if self.running:
            print("Command detection already running")
            return
        self.running = True
        self.thread = threading.Thread(target=self._listen_for_command)
        self.thread.daemon = True
        self.thread.start()
        print("Command detection started")

    def stop_listening(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)
        print("Command detection stopped")

    def _listen_for_command(self):
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
            print("Listening for command...")
            while self.running:
                try:
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                    command = self.recognizer.recognize_google(audio)
                    print(f"Heard command: {command}")
                    if self.keyword.lower() in command.lower():
                        print(f"Keyword '{self.keyword}' detected! Recording 5 seconds of audio...")
                        audio_file = self.record_audio()
                        if audio_file and self.detector.analyze_audio(audio_file):
                            print(f"Scream detected in {audio_file}! Sending emergency alert...")
                            self.send_emergency_alert()
                        else:
                            print(f"No scream detected in {audio_file}")
                        time.sleep(10)
                except sr.WaitTimeoutError:
                    continue
                except sr.UnknownValueError:
                    print("Didn't understand audio")
                    continue
                except Exception as e:
                    print(f"Error in listening: {e}")
                    continue

    def record_audio(self):
        try:
            p = pyaudio.PyAudio()
            stream = p.open(format=self.FORMAT, channels=self.CHANNELS,
                            rate=self.RATE, input=True, frames_per_buffer=self.CHUNK)
            print(f"Recording {self.RECORD_SECONDS} seconds of audio...")
            frames = []
            for _ in range(0, int(self.RATE / self.CHUNK * self.RECORD_SECONDS)):
                if not self.running:
                    break
                data = stream.read(self.CHUNK, exception_on_overflow=False)
                frames.append(data)
            stream.stop_stream()
            stream.close()
            p.terminate()
            audio_data = np.frombuffer(b''.join(frames), dtype=np.int16)
            max_amplitude = np.max(np.abs(audio_data))
            if max_amplitude < 20:
                print(f"Audio too quiet: max amplitude={max_amplitude}")
                return None
            filename = f"data/command_{self.user_id}_{int(time.time())}.wav"
            wf = wave.open(filename, 'wb')
            wf.setnchannels(self.CHANNELS)
            wf.setsampwidth(p.get_sample_size(self.FORMAT))
            wf.setframerate(self.RATE)
            wf.writeframes(b''.join(frames))
            wf.close()
            print(f"Audio recorded: {filename}, max amplitude={max_amplitude}")
            return filename
        except Exception as e:
            print(f"Error recording audio: {e}")
            return None

    def send_emergency_alert(self):
        try:
            guardians = self.db.get_guardians(self.user_id)
            if not guardians:
                print(f"No guardians found for user_id {self.user_id}")
                return
            guardian_numbers = [g[1] for g in guardians]
            location = self.location.get_location() or self.location.get_last_location()
            numbers_to_alert = guardian_numbers + ['+91100']
            print(f"Sending alert to: {numbers_to_alert}, Location: {location}")
            self.messaging_service.send_emergency_alert(numbers_to_alert, location, self.location, self.main_screen)
        except Exception as e:
            print(f"Failed to send alert: {e}")