import time
from datetime import datetime
from plyer import notification  
from playsound import playsound  
import os



SOUND_PATH = r"C:\Users\Princelab\Desktop\devremind1\alarm.mp3"

def play_sound():
    """
    Plays an MP3 notification sound.
    """
    if os.path.exists(SOUND_PATH):
        try:
            playsound(SOUND_PATH)
        except Exception as e:
            print(f"⚠️ Error playing sound: {e}")
    else:
        print("🔇 Sound file not found.")

def log_reminder(message):
    """
    Logs reminder messages to a file with a timestamp.
    """
    with open("reminder_log.txt", "a") as log:
        log.write(f"{datetime.now()} - {message}\n")

def remind_every(minutes=60, message="Time to take a break!"):
    """
    Sends a desktop notification and plays a sound immediately,
    then every X minutes thereafter.
    """
    print(f"🔁 Starting reminder every {minutes} minutes...")
    print("⏹ Press Ctrl+C to stop.\n")
    try:
        while True:
            notification.notify(
                title="🧠 Developer Reminder",
                message=message,
                timeout=10
            )
            print(f"🔔 Reminder: {message}")
            play_sound()
            log_reminder(message)
            time.sleep(minutes * 60)
    except KeyboardInterrupt:
        print("\n✅ Reminder stopped by user.")

if __name__ == "__main__":

    remind_every(minutes=60, message="Time to stretch or drink water!")
