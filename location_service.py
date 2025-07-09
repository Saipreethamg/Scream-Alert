import googlemaps
import time
import threading
from datetime import datetime

class LocationService:
    def __init__(self, db, user_id):
        self.db = db
        self.user_id = user_id
        self.gmaps = googlemaps.Client(key='')  # Add your Google API key
        self.tracking = False
        self.tracking_thread = None
        self.update_interval = 30  # Update every 30 seconds

    def get_location(self):
        try:
            geolocation = self.gmaps.geolocate()
            if geolocation and 'location' in geolocation:
                lat = geolocation['location']['lat']
                lon = geolocation['location']['lng']
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.db.save_location(self.user_id, lat, lon, timestamp)
                print(f"Current location retrieved: Lat {lat}, Lon {lon}")
                return (lat, lon)
            else:
                print("Google Maps Geolocation API failed to retrieve location")
                return None
        except Exception as e:
            print(f"Error getting location: {e}")
            return None

    def get_last_location(self):
        try:
            location = self.db.get_last_location(self.user_id)
            if location:
                lat, lon = location
                print(f"Using last known location: Lat {lat}, Lon {lon}")
                return (lat, lon)
            else:
                print("No previous location found")
                return None
        except Exception as e:
            print(f"Error retrieving last location: {e}")
            return None

    def start_live_tracking(self, callback):
        if self.tracking:
            print("Live location tracking already running")
            return
        self.tracking = True
        self.tracking_thread = threading.Thread(target=self._track_location, args=(callback,))
        self.tracking_thread.daemon = True
        self.tracking_thread.start()
        print(f"Live location tracking started for user_id {self.user_id}")

    def stop_live_tracking(self):
        self.tracking = False
        if self.tracking_thread:
            self.tracking_thread.join(timeout=1)
            self.tracking_thread = None
        print("Live location tracking stopped")

    def _track_location(self, callback):
        while self.tracking:
            location = self.get_location() or self.get_last_location()
            if location:
                callback(location)
            time.sleep(self.update_interval)