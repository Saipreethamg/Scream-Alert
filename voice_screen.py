from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
import pyaudio
import wave
import soundfile as sf
from kivy.utils import get_color_from_hex

class VoiceScreen(Screen):
    def __init__(self, db, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.user_id = None
        self.recordings = []

        layout = BoxLayout(orientation='vertical', padding=40, spacing=20)
        layout.size_hint = (0.9, 0.95)
        layout.pos_hint = {'center_x': 0.5, 'center_y': 0.5}

        self.status_label = Label(
            text='Enter a command and record',
            color=get_color_from_hex("#27ae60"),
            font_size='18sp',
            size_hint=(1, 0.1),
            halign='center',
            valign='middle'
        )
        self.status_label.bind(size=self.status_label.setter('text_size'))
        layout.add_widget(self.status_label)

        self.command = TextInput(
            hint_text='Enter Command Text',
            font_size='16sp',
            multiline=False,
            padding_y=(10, 10),
            background_color=get_color_from_hex("#ffffff"),
            foreground_color=get_color_from_hex("#2c3e50"),
            cursor_color=get_color_from_hex("#2980b9")
        )
        layout.add_widget(self.command)

        record_btn = Button(
            text='Record Voice',
            size_hint=(1, 0.15),
            font_size='18sp',
            background_color=get_color_from_hex("#2980b9"),
            color=get_color_from_hex("#ffffff")
        )
        record_btn.bind(on_press=self.record_voice)
        layout.add_widget(record_btn)

        self.listen_btn = Button(
            text='Listen',
            size_hint=(1, 0.12),
            font_size='16sp',
            background_color=get_color_from_hex("#8e44ad"),
            color=get_color_from_hex("#ffffff"),
            disabled=True
        )
        self.listen_btn.bind(on_press=self.play_recording)
        layout.add_widget(self.listen_btn)

        next_btn = Button(
            text='Next',
            size_hint=(1, 0.12),
            font_size='16sp',
            background_color=get_color_from_hex("#27ae60"),
            color=get_color_from_hex("#ffffff")
        )
        next_btn.bind(on_press=self.next_screen)
        layout.add_widget(next_btn)

        self.add_widget(layout)
        print(f"VoiceScreen initialized, user_id: {self.user_id}")

    def on_enter(self):
        print(f"Entered VoiceScreen, user_id: {self.user_id}")
        self.status_label.text = f"User ID: {self.user_id}. Enter a command and record."

    def record_voice(self, instance):
        print(f"Record button pressed, user_id: {self.user_id}, command: {self.command.text}")
        if len(self.recordings) >= 3:
            self.status_label.text = "Maximum recordings (3) reached"
            print("Maximum recordings (3) reached")
            return
        if not self.command.text:
            self.status_label.text = "Please enter a command"
            print("No command text entered")
            return
        if not self.user_id:
            self.status_label.text = "User ID not set"
            print("User ID not set")
            return

        try:
            CHUNK = 1024
            FORMAT = pyaudio.paInt16
            CHANNELS = 1
            RATE = 44100
            RECORD_SECONDS = 5

            self.status_label.text = "Recording..."
            print("Starting recording...")
            p = pyaudio.PyAudio()
            stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                            input=True, frames_per_buffer=CHUNK)

            frames = []
            for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
                data = stream.read(CHUNK)
                frames.append(data)

            stream.stop_stream()
            stream.close()
            p.terminate()

            filename = f"data/recording_{self.user_id}_{len(self.recordings)}.wav"
            wf = wave.open(filename, 'wb')
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
            wf.close()

            self.recordings.append(filename)
            self.db.add_command(self.user_id, self.command.text, filename)
            self.listen_btn.disabled = False
            self.status_label.text = f"Recording saved: {len(self.recordings)}/3"
            print(f"Recording saved: {filename}")
        except Exception as e:
            self.status_label.text = f"Recording failed: {str(e)}"
            print(f"Error during recording: {e}")

    def play_recording(self, instance):
        if not self.recordings:
            self.status_label.text = "No recordings to play"
            print("No recordings to play")
            return
        try:
            self.status_label.text = "Playing last recording..."
            data, samplerate = sf.read(self.recordings[-1])
            sf.write('temp.wav', data, samplerate)
            p = pyaudio.PyAudio()
            stream = p.open(format=pyaudio.paFloat32, channels=1, rate=samplerate, output=True)
            with wave.open('temp.wav', 'rb') as wf:
                data = wf.readframes(1024)
                while data:
                    stream.write(data)
                    data = wf.readframes(1024)
            stream.stop_stream()
            stream.close()
            p.terminate()
            self.status_label.text = "Playback completed"
            print("Playback completed")
        except Exception as e:
            self.status_label.text = f"Playback failed: {str(e)}"
            print(f"Error during playback: {e}")

    def next_screen(self, instance):
        if len(self.recordings) >= 1:
            self.manager.current = 'guardian'
            self.manager.get_screen('guardian').user_id = self.user_id
            print("Transitioning to GuardianScreen")
        else:
            self.status_label.text = "At least one recording required"
            print("At least one recording required")
