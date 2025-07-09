from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from backend.messaging_service import MessagingService
from kivy.utils import get_color_from_hex

class GuardianScreen(Screen):
    def __init__(self, db, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.user_id = None
        self.messaging = MessagingService()

        layout = BoxLayout(orientation='vertical', padding=40, spacing=20)
        layout.size_hint = (0.9, 0.9)
        layout.pos_hint = {"center_x": 0.5, "center_y": 0.5}

        self.status_label = Label(
            text='Add at least one guardian',
            color=get_color_from_hex("#27ae60"),
            font_size='18sp',
            size_hint=(1, 0.1),
            halign='center',
            valign='middle'
        )
        self.status_label.bind(size=self.status_label.setter('text_size'))
        layout.add_widget(self.status_label)

        self.g_name = TextInput(
            hint_text='Guardian Name',
            multiline=False,
            size_hint=(1, 0.1),
            font_size='16sp',
            background_normal='',
            background_color=get_color_from_hex("#f0f0f0"),
            foreground_color=get_color_from_hex("#000000"),
            padding=[10, 10]
        )
        self.g_number = TextInput(
            hint_text='Guardian Number',
            multiline=False,
            size_hint=(1, 0.1),
            font_size='16sp',
            background_normal='',
            background_color=get_color_from_hex("#f0f0f0"),
            foreground_color=get_color_from_hex("#000000"),
            padding=[10, 10]
        )
        self.g_otp = TextInput(
            hint_text='OTP',
            multiline=False,
            size_hint=(1, 0.1),
            font_size='16sp',
            background_normal='',
            background_color=get_color_from_hex("#f0f0f0"),
            foreground_color=get_color_from_hex("#000000"),
            padding=[10, 10]
        )

        send_otp_btn = Button(
            text='Send OTP',
            size_hint=(1, 0.1),
            background_color=get_color_from_hex("#3498db"),
            color=get_color_from_hex("#ffffff"),
            font_size='16sp'
        )
        send_otp_btn.bind(on_press=self.send_otp)

        add_btn = Button(
            text='Add Guardian',
            size_hint=(1, 0.1),
            background_color=get_color_from_hex("#2ecc71"),
            color=get_color_from_hex("#ffffff"),
            font_size='16sp'
        )
        add_btn.bind(on_press=self.add_guardian)

        next_btn = Button(
            text='Finish',
            size_hint=(1, 0.1),
            background_color=get_color_from_hex("#e67e22"),
            color=get_color_from_hex("#ffffff"),
            font_size='16sp'
        )
        next_btn.bind(on_press=self.finish)

        for widget in [self.g_name, self.g_number, self.g_otp, send_otp_btn, add_btn, next_btn]:
            layout.add_widget(widget)

        self.add_widget(layout)
        print("GuardianScreen initialized")

    def on_enter(self):
        print(f"Entered GuardianScreen, user_id: {self.user_id}")
        self.status_label.text = f"User ID: {self.user_id}. Add at least one guardian."

    def send_otp(self, instance):
        if self.g_number.text:
            self.messaging.send_otp(self.g_number.text)
            self.status_label.text = "OTP sent to guardian number"
            print(f"OTP sent to {self.g_number.text}")

    def add_guardian(self, instance):
        if not (self.g_name.text and self.g_number.text and self.g_otp.text):
            self.status_label.text = "All fields required"
            print("Failed to add guardian: Missing fields")
            return
        if self.messaging.verify_otp(self.g_number.text, self.g_otp.text):
            self.db.add_guardian(self.user_id, self.g_name.text, self.g_number.text)
            self.status_label.text = f"Guardian added: {self.g_name.text}"
            print(f"Guardian added: {self.g_name.text}, {self.g_number.text}")
            self.g_name.text = ''
            self.g_number.text = ''
            self.g_otp.text = ''
        else:
            self.status_label.text = "Invalid OTP"
            print("Failed to add guardian: Invalid OTP")

    def finish(self, instance):
        guardians = self.db.get_guardians(self.user_id)
        if len(guardians) >= 1:
            self.manager.current = 'main'
            self.manager.get_screen('main').user_id = self.user_id
            print("Transitioning to MainScreen")
        else:
            self.status_label.text = "At least one guardian required"
            print("At least one guardian required")
