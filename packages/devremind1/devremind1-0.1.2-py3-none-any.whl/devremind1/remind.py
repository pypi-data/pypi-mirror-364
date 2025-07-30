import time
from datetime import datetime
from plyer import notification
from playsound import playsound
import sys
try:
    from importlib.resources import files  
except ImportError:
    from importlib_resources import files  


def play_sound():
    """
    Plays the packaged alarm.mp3 file using playsound.
    """
    try:
        sound_file = files('devremind1').joinpath('alarm.mp3')
        playsound(str(sound_file))
    except Exception as e:
        print(f"🔇 Error playing sound: {e}")


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


def main():
    # You could parse CLI arguments here if needed
    remind_every(minutes=60, message="Time to stretch or drink water!")


if __name__ == "__main__":
    main()
