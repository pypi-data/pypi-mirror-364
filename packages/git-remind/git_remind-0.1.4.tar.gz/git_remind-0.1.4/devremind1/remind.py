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
        "git_interval": 1,  # Minutes between git reminders
        "git_message": "⏰ Time to commit your changes!",
        "doc_reminders": True,
        "test_reminders": False,
        "review_reminders": True
    },
    "sound": {
        "enabled": True,
        "custom_sound": None,
        "git_sound": None  # Custom sound for git reminders
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
    return DEFAULT_CONFIG.copy()  # Return a copy to avoid modifying defaults

def save_config(config, config_path):
    """Save configuration to file"""
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=4)

def play_sound(config, sound_type="default"):
    """Play sound based on type (default/git)"""
    if not config["sound"]["enabled"]:
        return

    try:
        sound_file = None
        if sound_type == "git" and config["sound"]["git_sound"]:
            sound_file = config["sound"]["git_sound"]
        elif config["sound"]["custom_sound"]:
            sound_file = config["sound"]["custom_sound"]
        
        if sound_file and os.path.exists(sound_file):
            playsound(sound_file)
        else:
            default_sound = files('devremind1').joinpath('alarm.mp3')
            playsound(str(default_sound))
    except Exception as e:
        print(f"🔇 Error playing sound: {e}")

def log_reminder(message, config):
    """Log reminders with timestamp"""
    with open(config["general"]["log_file"], "a") as log:
        log.write(f"{datetime.now()} - {message}\n")

def get_time_based_message(config):
    """Get message based on time of day"""
    now = datetime.now().time()
    if dt_time(6, 0) <= now < dt_time(12, 0):
        base_message = config["messages"]["morning"]
    elif dt_time(12, 0) <= now < dt_time(18, 0):
        base_message = config["messages"]["afternoon"]
    elif dt_time(18, 0) <= now < dt_time(23, 59):
        base_message = config["messages"]["evening"]
    else:
        base_message = config["messages"]["default"]
    
    if config["general"]["urgency"] != "normal":
        base_message = f"[{config['general']['urgency'].upper()}] {base_message}"
    
    return base_message

def get_developer_reminder(config):
    """Get developer-specific reminders"""
    now = datetime.now()
    reminders = []
    
    # Git reminders
    if config["developer"]["git_reminders"]:
        reminders.append(config["developer"]["git_message"])
    
    # Other developer reminders
    if config["developer"]["doc_reminders"] and now.hour % 4 == 0:
        reminders.append("📝 Document your recent changes?")
    if config["developer"]["test_reminders"] and now.hour % 6 == 0:
        reminders.append("🧪 Write some tests!")
    if config["developer"]["review_reminders"] and now.hour % 3 == 0:
        reminders.append("👀 Review recent PRs/code")
    
    return "\n".join(reminders) if reminders else None

def remind_every(config=None, **kwargs):
    """
    Main reminder function that accepts both config object and direct arguments
    """
    # Handle both config and direct arguments
    if config is None:
        config = load_config()
    
    # Override config with direct arguments if provided
    for key, value in kwargs.items():
        if value is not None:
            if key in ["frequency", "urgency"]:
                config["general"][key] = value
            elif key in ["git_reminders", "doc_reminders", "test_reminders", "review_reminders"]:
                config["developer"][key] = value
            elif key == "sound":
                config["sound"]["custom_sound"] = value
            elif key == "no_sound":
                config["sound"]["enabled"] = not value

    print("🚀 Developer Reminder Started!")
    print(f"🔔 General reminders every {config['general']['frequency']} minutes")
    print(f"💾 Git reminders every {config['developer']['git_interval']} minutes")
    print("⏹ Press Ctrl+C to stop\n")

    last_git_reminder = time.time()
    
    try:
        while True:
            current_time = time.time()
            
            # Git reminders
            if (config["developer"]["git_reminders"] and 
                current_time - last_git_reminder >= config["developer"]["git_interval"] * 60):
                git_msg = config["developer"]["git_message"]
                notification.notify(
                    title="💾 Git Commit Reminder",
                    message=git_msg,
                    timeout=5
                )
                print(f"{datetime.now().strftime('%H:%M')} - {git_msg}")
                play_sound(config, "git")
                log_reminder(f"Git Reminder: {git_msg}", config)
                last_git_reminder = current_time
            
            # General reminders
            if current_time % (config["general"]["frequency"] * 60) < 1:
                message = get_time_based_message(config)
                dev_msg = get_developer_reminder(config)
                full_msg = f"{message}\n\n{dev_msg}" if dev_msg else message
                
                notification.notify(
                    title="🧠 Developer Reminder",
                    message=full_msg,
                    timeout=10
                )
                print(f"⏰ {datetime.now().strftime('%H:%M')} - {message}")
                play_sound(config)
                log_reminder(full_msg, config)
            
            time.sleep(1)  # Check every second
            
    except KeyboardInterrupt:
        print("\n✅ Reminder stopped by user")

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Developer Reminder Tool')
    parser.add_argument('--config', type=str, default=None,
                      help='Path to custom config file')
    parser.add_argument('--frequency', type=int, default=None,
                      help='Reminder frequency in minutes')
    parser.add_argument('--git-interval', type=int, default=None,
                      help='Git reminder frequency in minutes')
    parser.add_argument('--urgency', choices=['low', 'normal', 'high'], default=None,
                      help='Notification urgency level')
    parser.add_argument('--sound', type=str, default=None,
                      help='Path to custom sound file')
    parser.add_argument('--git-sound', type=str, default=None,
                      help='Path to custom git reminder sound')
    parser.add_argument('--no-sound', action='store_true',
                      help='Disable all sounds')
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
    
    # Convert args to kwargs for remind_every
    kwargs = {
        'frequency': args.frequency,
        'urgency': args.urgency,
        'sound': args.sound,
        'no_sound': args.no_sound,
        'git_reminders': args.git_reminders,
        'doc_reminders': args.doc_reminders,
        'git_interval': args.git_interval
    }
    
    if args.git_sound:
        config["sound"]["git_sound"] = args.git_sound
    
    remind_every(config, **kwargs)

if __name__ == "__main__":
    main()