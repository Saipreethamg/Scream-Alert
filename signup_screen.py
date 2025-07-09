from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from backend.messaging_service import MessagingService
import sqlite3
from kivy.utils import get_color_from_hex

class SignupScreen(Screen):
    def __init__(self, db, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.messaging = MessagingService()

        layout = BoxLayout(orientation='vertical', padding=40, spacing=20)
        layout.size_hint = (0.9, 0.95)
        layout.pos_hint = {'center_x': 0.5, 'center_y': 0.5}

        self.error_label = Label(
            text='',
            color=get_color_from_hex('#e74c3c'),
            font_size='16sp',
            size_hint=(1, 0.1),
            halign='center',
            valign='middle'
        )
        self.error_label.bind(size=self.error_label.setter('text_size'))
        layout.add_widget(self.error_label)

        title_label = Label(
            text='Sign Up',
            font_size='24sp',
            bold=True,
            color=get_color_from_hex("#2c3e50"),
            size_hint=(1, 0.1),
            halign='center',
            valign='middle'
        )
        title_label.bind(size=title_label.setter('text_size'))
        layout.add_widget(title_label)

        self.name_input = TextInput(
            hint_text='Full Name',
            multiline=False,
            padding_y=(10, 10),
            font_size='16sp'
        )
        self.mobile = TextInput(
            hint_text='Mobile Number',
            multiline=False,
            input_filter='int',
            padding_y=(10, 10),
            font_size='16sp'
        )
        self.otp = TextInput(
            hint_text='OTP',
            multiline=False,
            input_filter='int',
            padding_y=(10, 10),
            font_size='16sp'
        )
        self.password = TextInput(
            hint_text='Password',
            password=True,
            multiline=False,
            padding_y=(10, 10),
            font_size='16sp'
        )
        self.re_password = TextInput(
            hint_text='Confirm Password',
            password=True,
            multiline=False,
            padding_y=(10, 10),
            font_size='16sp'
        )
        self.gender = Spinner(
            text='Gender',
            values=('Male', 'Female', 'Others'),
            size_hint=(1, None),
            height=44,
            font_size='16sp',
            background_color=get_color_from_hex("#ecf0f1"),
            color=get_color_from_hex("#2c3e50")
        )
        self.dob = TextInput(
            hint_text='Date of Birth (DD-MM-YYYY)',
            multiline=False,
            padding_y=(10, 10),
            font_size='16sp'
        )

        for widget in [self.name_input, self.mobile, self.otp, self.password,
                       self.re_password, self.gender, self.dob]:
            widget.background_color = get_color_from_hex("#ffffff")
            widget.foreground_color = get_color_from_hex("#2c3e50")
            widget.cursor_color = get_color_from_hex("#2980b9")
            layout.add_widget(widget)

        send_otp_btn = Button(
            text='Send OTP',
            size_hint=(1, 0.15),
            background_color=get_color_from_hex("#2980b9"),
            color=get_color_from_hex("#ffffff"),
            font_size='16sp'
        )
        send_otp_btn.bind(on_press=self.send_otp)

        signup_btn = Button(
            text='Sign Up',
            size_hint=(1, 0.15),
            background_color=get_color_from_hex("#27ae60"),
            color=get_color_from_hex("#ffffff"),
            font_size='16sp'
        )
        signup_btn.bind(on_press=self.create_account)

        layout.add_widget(send_otp_btn)
        layout.add_widget(signup_btn)
        self.add_widget(layout)
        print("SignupScreen initialized")

    def send_otp(self, instance):
        if self.mobile.text:
            self.messaging.send_otp(self.mobile.text)
            self.error_label.text = "OTP sent. Check your phone."
            print(f"OTP sent to {self.mobile.text}")

    def create_account(self, instance):
        self.error_label.text = ""
        if not (self.password.text == self.re_password.text):
            self.error_label.text = "Passwords do not match"
            print("Signup failed: Password mismatch")
            return
        if not self.messaging.verify_otp(self.mobile.text, self.otp.text):
            self.error_label.text = "Invalid OTP"
            print("Signup failed: Invalid OTP")
            return

        try:
            user_id = self.db.add_user(self.name_input.text, self.mobile.text,
                                       self.password.text, self.gender.text, self.dob.text)
            print(f"Signup successful, user_id: {user_id}, transitioning to VoiceScreen")
            self.manager.current = 'voice'
            voice_screen = self.manager.get_screen('voice')
            voice_screen.user_id = user_id
        except sqlite3.IntegrityError:
            self.error_label.text = "Mobile number already registered"
            print(f"Signup failed: Mobile number {self.mobile.text} already exists")
