import time
import argparse
import json
import os
from datetime import datetime, time as dt_time
from plyer import notification
from playsound import playsound
import sys
try:
    from importlib.resources import files  
except ImportError:
    from importlib_resources import files  

# Default configuration
DEFAULT_CONFIG = {
    "general": {
        "frequency": 60,
        "log_file": "reminder_log.txt",
        "urgency": "normal"  
    },
    "messages": {
        "morning": "Time to start your day! Review your tasks.",
        "afternoon": "Time to stretch or drink water!",
        "evening": "Have you committed your work today?",
        "default": "Time to take a break!"
    },
    "developer": {
        "git_reminders": True,
        "doc_reminders": True,
        "test_reminders": False,
        "review_reminders": True
    },
    "sound": {
        "enabled": True,
        "custom_sound": None
    }
}

def load_config(config_path=None):
    """Load configuration from file or use defaults"""
    if config_path and os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
        for key in DEFAULT_CONFIG:
            if key not in config:
                config[key] = DEFAULT_CONFIG[key]
            elif isinstance(DEFAULT_CONFIG[key], dict):
                config[key].update({k: v for k, v in DEFAULT_CONFIG[key].items() if k not in config[key]})
        return config
    return DEFAULT_CONFIG

def save_config(config, config_path):
    """Save configuration to file"""
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=4)

def play_sound(config):
    """
    Plays the alarm sound based on configuration
    """
    if not config["sound"]["enabled"]:
        return

    try:
        if config["sound"]["custom_sound"] and os.path.exists(config["sound"]["custom_sound"]):
            playsound(config["sound"]["custom_sound"])
        else:
            sound_file = files('devremind1').joinpath('alarm.mp3')
            playsound(str(sound_file))
    except Exception as e:
        print(f"🔇 Error playing sound: {e}")

def log_reminder(message, config):
    """
    Logs reminder messages to a file with a timestamp
    """
    with open(config["general"]["log_file"], "a") as log:
        log.write(f"{datetime.now()} - {message}\n")

def get_time_based_message(config):
    """Get appropriate message based on time of day"""
    now = datetime.now().time()
    if dt_time(6, 0) <= now < dt_time(12, 0):
        base_message = config["messages"]["morning"]
    elif dt_time(12, 0) <= now < dt_time(18, 0):
        base_message = config["messages"]["afternoon"]

    elif dt_time(18, 0) <= now < dt_time(23, 59):
        base_message = config["messages"]["evening"]
    else:
        base_message = config["messages"]["default"]
    urgency = config["general"]["urgency"]
    if urgency != "normal":
        base_message = f"[{urgency.upper()}] {base_message}"
    
    return base_message

def get_developer_reminder(config):
    """Get developer-specific reminder if appropriate"""
    now = datetime.now()
    day_part = now.hour // 6  
    
    reminders = []
    if config["developer"]["doc_reminders"] and now.hour % 4 == 0:  
        reminders.append("Have you documented your recent code changes?")
    if config["developer"]["test_reminders"] and day_part == 2:  
        reminders.append("Time to write some tests for your code!")
    if config["developer"]["review_reminders"] and now.hour % 3 == 0:  
        reminders.append("Consider reviewing recent code changes or PRs.")
    if config["developer"]["git_reminders"] and dt_time(18, 0) <= now.time() < dt_time(23, 59):
        reminders.append("Don't forget to commit your work!")
    
    return " ".join(reminders) if reminders else None

def remind_every(config):
    """
    Sends desktop notifications based on configuration
    """
    frequency = config["general"]["frequency"]
    
    print(f"🔁 Starting reminders every {frequency} minutes...")
    print(f"⚙️ Urgency level: {config['general']['urgency']}")
    print("⏹ Press Ctrl+C to stop.\n")

    try:
        while True:
            message = get_time_based_message(config)
            dev_reminder = get_developer_reminder(config)
            if dev_reminder:
                message = f"{message}\n\nDeveloper Tip: {dev_reminder}"
            notification.notify(
                title="🧠 Developer Reminder",
                message=message,
                timeout=10
            )
            
            print(f"🔔 Reminder: {message}")
            play_sound(config)
            log_reminder(message, config)

            time.sleep(frequency * 60)

    except KeyboardInterrupt:
        print("\n✅ Reminder stopped by user.")

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Developer Reminder Tool')
    parser.add_argument('--config', type=str, default=None,
                      help='Path to custom config file')
    parser.add_argument('--frequency', type=int, default=None,
                      help='Reminder frequency in minutes')
    parser.add_argument('--urgency', choices=['low', 'normal', 'high'], default=None,
                      help='Notification urgency level (display only)')
    parser.add_argument('--sound', type=str, default=None,
                      help='Path to custom sound file')
    parser.add_argument('--no-sound', action='store_true',
                      help='Disable sound notifications')
    parser.add_argument('--git-reminders', action='store_true', default=None,
                      help='Enable git commit reminders')
    parser.add_argument('--no-git-reminders', action='store_false', dest='git_reminders',
                      help='Disable git commit reminders')
    parser.add_argument('--doc-reminders', action='store_true', default=None,
                      help='Enable documentation reminders')
    parser.add_argument('--no-doc-reminders', action='store_false', dest='doc_reminders',
                      help='Disable documentation reminders')
    return parser.parse_args()

def main():
    args = parse_args()
    config = load_config(args.config)
    if args.frequency is not None:
        config["general"]["frequency"] = args.frequency
    if args.urgency is not None:
        config["general"]["urgency"] = args.urgency
    if args.sound is not None:
        config["sound"]["custom_sound"] = args.sound
    if args.no_sound:
        config["sound"]["enabled"] = False
    if args.git_reminders is not None:
        config["developer"]["git_reminders"] = args.git_reminders
    if args.doc_reminders is not None:
        config["developer"]["doc_reminders"] = args.doc_reminders
    
    remind_every(config)

if __name__ == "__main__":
    main()