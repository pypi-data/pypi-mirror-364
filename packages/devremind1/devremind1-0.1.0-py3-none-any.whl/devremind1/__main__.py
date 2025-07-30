import argparse
from .remind import remind_every

def main():
    parser = argparse.ArgumentParser(description="Developer break reminder CLI")
    parser.add_argument('--minutes', type=int, default=60, help="Interval in minutes")
    parser.add_argument('--message', type=str, default="Time to take a break!", help="Reminder message")

    args = parser.parse_args()
    remind_every(args.minutes, args.message)

if __name__ == "__main__":
    main()
