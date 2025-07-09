from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from backend.audio_monitor import AudioMonitor
from backend.messaging_service import MessagingService
from backend.command_detector import CommandDetector
from kivy.utils import get_color_from_hex

class MainScreen(Screen):
    def __init__(self, db, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.user_id = None
        self.monitor = AudioMonitor(self.user_id, self.db, self)
        self.messaging = MessagingService()
        self.command_detector = None
        self.monitoring_active = False

        # Main layout
        self.layout = BoxLayout(orientation='vertical', padding=40, spacing=20)
        self.layout.size_hint = (0.9, 0.9)
        self.layout.pos_hint = {'center_x': 0.5, 'center_y': 0.5}
        self.status_label = Label(
            text='Welcome to VoiceGuardian',
            color=get_color_from_hex("#27ae60"),
            font_size='20sp',
            size_hint=(1, 0.1),
            halign='center',
            valign='middle'
        )
        self.status_label.bind(size=self.status_label.setter('text_size'))
        self.layout.add_widget(self.status_label)

        # Standard buttons
        guardian_btn = Button(
            text='Manage Guardians',
            size_hint=(1, 0.15),
            background_color=get_color_from_hex("#2ecc71"),
            color=get_color_from_hex("#ffffff"),
            font_size='18sp'
        )
        guardian_btn.bind(on_press=self.go_to_guardian)
        emergency_btn = Button(
            text='Emergency Services',
            size_hint=(1, 0.15),
            background_color=get_color_from_hex("#e74c3c"),
            color=get_color_from_hex("#ffffff"),
            font_size='18sp'
        )
        emergency_btn.bind(on_press=self.show_emergency)

        # Stop Location Sharing button (initially hidden)
        self.stop_tracking_btn = Button(
            text='Stop Location Sharing',
            size_hint=(None, None),
            size=(0, 0),  # Hidden by default
            background_color=get_color_from_hex("#e67e22"),
            color=get_color_from_hex("#ffffff"),
            font_size='18sp'
        )
        self.stop_tracking_btn.bind(on_press=self.stop_live_tracking)

        # Add buttons to layout
        for btn in [guardian_btn, emergency_btn, self.stop_tracking_btn]:
            self.layout.add_widget(btn)
        self.add_widget(self.layout)
        print("MainScreen initialized")

    def show_stop_button(self):
        """Show the Stop Location Sharing button."""
        self.stop_tracking_btn.size_hint = (1, 0.15)
        self.stop_tracking_btn.size = (self.layout.width, 0)  # Adjust size dynamically
        self.status_label.text = "Emergency active: Sharing location"
        print("Stop Location Sharing button shown")

    def hide_stop_button(self):
        """Hide the Stop Location Sharing button."""
        self.stop_tracking_btn.size_hint = (None, None)
        self.stop_tracking_btn.size = (0, 0)
        self.status_label.text = f"User ID: {self.user_id}. Ready." if self.user_id else "Welcome to VoiceGuardian"
        print("Stop Location Sharing button hidden")

    def on_enter(self):
        print(f"Entered MainScreen, user_id: {self.user_id}")
        if self.user_id:
            self.status_label.text = f"User ID: {self.user_id}. Ready."
            self.monitor.user_id = self.user_id
            if not self.command_detector:
                self.command_detector = CommandDetector(self.messaging, self.db, self.user_id, self)
                self.command_detector.start_listening()
        else:
            self.status_label.text = "Error: User ID not set"
            print("Error: User ID not set on MainScreen")

    def go_to_guardian(self, instance):
        try:
            if not self.user_id:
                self.status_label.text = "Error: User ID not set"
                print("Guardian error: User ID not set")
                return
            self.manager.current = 'guardian'
            self.manager.get_screen('guardian').user_id = self.user_id
            self.status_label.text = "Switched to Guardian screen"
        except Exception as e:
            print(f"Error switching to guardian screen: {e}")

    def show_emergency(self, instance):
        self.status_label.text = "Emergency services not implemented"
        print("Emergency services button pressed")

    def stop_live_tracking(self, instance):
        self.monitor.location.stop_live_tracking()
        self.hide_stop_button()
        print("Live location tracking stopped by user")