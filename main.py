from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from frontend.login_screen import LoginScreen
from frontend.signup_screen import SignupScreen
from frontend.voice_screen import VoiceScreen
from frontend.guardian_screen import GuardianScreen
from frontend.main_screen import MainScreen
from backend.database import Database


class VoiceGuardianApp(App):
    def build(self):
        self.db = Database()
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login', db=self.db))
        sm.add_widget(SignupScreen(name='signup', db=self.db))
        sm.add_widget(VoiceScreen(name='voice', db=self.db))
        sm.add_widget(GuardianScreen(name='guardian', db=self.db))
        sm.add_widget(MainScreen(name='main', db=self.db))
        return sm


if __name__ == '__main__':
    VoiceGuardianApp().run()

