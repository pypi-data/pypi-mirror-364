# DevRemind1 🧠⏰

A Python CLI tool that reminds developers to take breaks during long coding sessions.

## Features

- Custom interval reminders
- System notifications (Windows/macOS/Linux)
- Simple CLI interface

## Installation

```bash
pip install -e .



#help for all the commands 
python remind.py -h
# Change frequencies
python remind.py --frequency 30 --git-interval 2

# Custom messages
python remind.py --git-message "COMMIT NOW: Don't lose your work!"

# Disable features
python remind.py --no-git --no-sound

