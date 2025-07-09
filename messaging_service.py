from twilio.rest import Client
import random
import time
import threading

class MessagingService:
    def __init__(self):
        self.account_sid = "" # Add your Twilio SID
        self.auth_token = "" # Add your Twilio Auth Token
        self.twilio_number = "" # Add your Twilio Phone Number
        try:
            self.client = Client(self.account_sid, self.auth_token)
            print("Twilio client initialized")
        except Exception as e:
            print(f"Failed to initialize Twilio client: {e}")
            raise
        self.otp_store = {}

    def send_otp(self, number):
        if not number.startswith('+91'):
            number = '+91' + number
        otp = str(random.randint(100000, 999999))
        self.otp_store[number] = otp
        try:
            message = self.client.messages.create(
                body=f'Your OTP is {otp}',
                from_=self.twilio_number,
                to=number
            )
            print(f"OTP sent to {number}: {otp}, SID: {message.sid}")
        except Exception as e:
            print(f"Failed to send OTP to {number}: {e}")

    def verify_otp(self, number, otp):
        if not number.startswith('+91'):
            number = '+91' + number
        result = self.otp_store.get(number) == otp
        print(f"OTP verification for {number}: {otp} -> {result}")
        return result

    def send_emergency_alert(self, to_numbers, location, location_service=None, main_screen=None):
        if not to_numbers:
            print("No numbers to send alert to")
            return
        # Send initial alert
        maps_url = "Location unavailable"
        if location and isinstance(location, tuple):
            lat, lon = location
            maps_url = f"https://www.google.com/maps?q={lat},{lon}"
        for number in to_numbers:
            if not number.startswith('+91'):
                number = '+91' + number
            try:
                message = self.client.messages.create(
                    body=f"EMERGENCY ALERT! View location: {maps_url}",
                    from_=self.twilio_number,
                    to=number
                )
                print(f"Alert sent to {number}: SID {message.sid}, Maps URL: {maps_url}")
            except Exception as e:
                print(f"Failed to send alert to {number}: {e}")

        # Show Stop Location Sharing button on MainScreen
        if main_screen:
            main_screen.show_stop_button()

        # Start live location updates if location_service is provided
        if location_service:
            def location_callback(location):
                maps_url = "Location unavailable"
                if location and isinstance(location, tuple):
                    lat, lon = location
                    maps_url = f"https://www.google.com/maps?q={lat},{lon}"
                for number in to_numbers:
                    if not number.startswith('+91'):
                        number = '+91' + number
                    try:
                        message = self.client.messages.create(
                            body=f"Live Location Update: View location: {maps_url}",
                            from_=self.twilio_number,
                            to=number
                        )
                        print(f"Live update sent to {number}: SID {message.sid}, Maps URL: {maps_url}")
                    except Exception as e:
                        print(f"Failed to send live update to {number}: {e}")
            
            location_service.start_live_tracking(location_callback)
            # Stop tracking after 5 minutes
            def stop_tracking():
                time.sleep(300)  # 5 minutes
                location_service.stop_live_tracking()
                if main_screen:
                    main_screen.hide_stop_button()
            threading.Thread(target=stop_tracking, daemon=True).start()