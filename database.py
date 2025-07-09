import sqlite3
import threading

class Database:
    def __init__(self):
        # Use check_same_thread=False to allow multi-threaded access
        self.conn = sqlite3.connect('data/database.db', check_same_thread=False)
        self.lock = threading.Lock()  # Thread lock for safe access
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        with self.lock:
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                                (id INTEGER PRIMARY KEY, name TEXT, mobile TEXT UNIQUE, 
                                password TEXT, gender TEXT, dob TEXT)''')
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS guardians 
                                (id INTEGER PRIMARY KEY, user_id INTEGER, name TEXT, number TEXT,
                                FOREIGN KEY(user_id) REFERENCES users(id))''')
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS commands 
                                (id INTEGER PRIMARY KEY, user_id INTEGER, command_text TEXT, audio_file TEXT,
                                FOREIGN KEY(user_id) REFERENCES users(id))''')
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS locations 
                                (id INTEGER PRIMARY KEY, user_id INTEGER, latitude REAL, longitude REAL, timestamp TEXT,
                                FOREIGN KEY(user_id) REFERENCES users(id))''')
            self.conn.commit()
            print("Database tables created or verified")

    def add_user(self, name, mobile, password, gender, dob):
        with self.lock:
            try:
                self.cursor.execute('INSERT INTO users (name, mobile, password, gender, dob) VALUES (?, ?, ?, ?, ?)',
                                  (name, mobile, password, gender, dob))
                self.conn.commit()
                user_id = self.cursor.lastrowid
                print(f"User added: {name}, ID: {user_id}")
                return user_id
            except sqlite3.IntegrityError as e:
                print(f"Error adding user: {e}")
                raise

    def get_user(self, mobile):
        with self.lock:
            self.cursor.execute('SELECT * FROM users WHERE mobile = ?', (mobile,))
            user = self.cursor.fetchone()
            print(f"User fetched: {user}")
            return user

    def add_guardian(self, user_id, name, number):
        with self.lock:
            self.cursor.execute('INSERT INTO guardians (user_id, name, number) VALUES (?, ?, ?)',
                              (user_id, name, number))
            self.conn.commit()
            print(f"Guardian added for user_id {user_id}: {name}, {number}")

    def get_guardians(self, user_id):
        with self.lock:
            self.cursor.execute('SELECT name, number FROM guardians WHERE user_id = ?', (user_id,))
            guardians = self.cursor.fetchall()
            print(f"Guardians for user_id {user_id}: {guardians}")
            return guardians

    def add_command(self, user_id, command_text, audio_file):
        with self.lock:
            self.cursor.execute('INSERT INTO commands (user_id, command_text, audio_file) VALUES (?, ?, ?)',
                              (user_id, command_text, audio_file))
            self.conn.commit()
            print(f"Command added for user_id {user_id}: {command_text}, {audio_file}")

    def get_commands(self, user_id):
        with self.lock:
            self.cursor.execute('SELECT command_text, audio_file FROM commands WHERE user_id = ?', (user_id,))
            commands = self.cursor.fetchall()
            print(f"Commands for user_id {user_id}: {commands}")
            return commands

    def save_location(self, user_id, latitude, longitude, timestamp):
        with self.lock:
            self.cursor.execute('INSERT INTO locations (user_id, latitude, longitude, timestamp) VALUES (?, ?, ?, ?)',
                              (user_id, latitude, longitude, timestamp))
            self.conn.commit()
            print(f"Location saved for user_id {user_id}: Lat {latitude}, Lon {longitude}")

    def get_last_location(self, user_id):
        with self.lock:
            self.cursor.execute('SELECT latitude, longitude FROM locations WHERE user_id = ? ORDER BY timestamp DESC LIMIT 1',
                              (user_id,))
            location = self.cursor.fetchone()
            print(f"Last location for user_id {user_id}: {location}")
            return location