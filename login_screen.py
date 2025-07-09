from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from backend.messaging_service import MessagingService
from kivy.utils import get_color_from_hex
import sqlite3

class LoginScreen(Screen):
    def __init__(self, db, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.messaging = MessagingService()

        layout = BoxLayout(orientation='vertical', padding=40, spacing=20)
        layout.size_hint = (0.9, 0.9)
        layout.pos_hint = {"center_x": 0.5, "center_y": 0.5}

        layout.add_widget(Label(
            text='[b]Login[/b]',
            markup=True,
            font_size='24sp',
            size_hint=(1, 0.2),
            halign='center',
            color=get_color_from_hex("#333333")
        ))

        self.error_label = Label(
            text='',
            size_hint=(1, 0.1),
            color=(1, 0, 0, 1)
        )
        layout.add_widget(self.error_label)

        self.mobile = TextInput(
            hint_text='Mobile Number',
            multiline=False,
            size_hint=(1, 0.1),
            font_size='18sp',
            background_normal='',
            background_color=get_color_from_hex("#f0f0f0"),
            foreground_color=get_color_from_hex("#000000"),
            padding=[10, 10]
        )
        self.otp = TextInput(
            hint_text='OTP',
            multiline=False,
            size_hint=(1, 0.1),
            font_size='18sp',
            background_normal='',
            background_color=get_color_from_hex("#f0f0f0"),
            foreground_color=get_color_from_hex("#000000"),
            padding=[10, 10]
        )
        self.password = TextInput(
            hint_text='Password (Optional)',
            password=True,
            multiline=False,
            size_hint=(1, 0.1),
            font_size='18sp',
            background_normal='',
            background_color=get_color_from_hex("#f0f0f0"),
            foreground_color=get_color_from_hex("#000000"),
            padding=[10, 10]
        )

        layout.add_widget(self.mobile)
        layout.add_widget(self.otp)
        layout.add_widget(self.password)

        send_otp_btn = Button(
            text='Send OTP',
            size_hint=(1, 0.1),
            background_color=get_color_from_hex("#3498db"),
            color=get_color_from_hex("#ffffff"),
            font_size='16sp'
        )
        send_otp_btn.bind(on_press=self.send_otp)

        login_btn = Button(
            text='Login',
            size_hint=(1, 0.1),
            background_color=get_color_from_hex("#2ecc71"),
            color=get_color_from_hex("#ffffff"),
            font_size='16sp'
        )
        login_btn.bind(on_press=self.verify_login)

        signup_btn = Button(
            text='Create New Account',
            size_hint=(1, 0.1),
            background_color=get_color_from_hex("#e67e22"),
            color=get_color_from_hex("#ffffff"),
            font_size='16sp'
        )
        signup_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'signup'))

        layout.add_widget(send_otp_btn)
        layout.add_widget(login_btn)
        layout.add_widget(signup_btn)

        self.add_widget(layout)

    def send_otp(self, instance):
        if self.mobile.text:
            self.messaging.send_otp(self.mobile.text)
            self.error_label.text = "OTP sent. Check your phone."
            print(f"OTP sent to {self.mobile.text}")
        else:
            self.error_label.text = "Please enter mobile number"

    def verify_login(self, instance):
        self.error_label.text = ""
        if not self.messaging.verify_otp(self.mobile.text, self.otp.text):
            self.error_label.text = "Invalid OTP"
            print("Login failed: Invalid OTP")
            return

        # Use the existing get_user method to fetch the user by mobile number
        user = self.db.get_user(self.mobile.text)  # Changed here
        if user:
            if self.password.text and user[3] != self.password.text:  # user[3] is the password field
                self.error_label.text = "Incorrect password"
                print("Login failed: Incorrect password")
                return
            self.manager.current = 'voice'
            voice_screen = self.manager.get_screen('voice')
            voice_screen.user_id = user[0]  # user[0] is the user id
            print(f"Login successful: User ID {user[0]}")
        else:
            self.error_label.text = "User not found"
            print("Login failed: User not found")
