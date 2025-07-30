import argparse
import os
from .remind import remind_every, DEFAULT_CONFIG, load_config

SOUND_PATH = os.path.join(os.path.dirname(__file__), "alarm.mp3")

def main():
    parser = argparse.ArgumentParser(description="Developer break reminder CLI")
    parser.add_argument('--minutes', type=int, default=None, help="Interval in minutes")
    parser.add_argument('--message', type=str, default=None, help="Reminder message")
    parser.add_argument('--config', type=str, default=None, help="Path to config file")

    parser.add_argument('--urgency', choices=['low', 'normal', 'high'], default=None)
    parser.add_argument('--sound', type=str, default=None)
    parser.add_argument('--no-sound', action='store_true')
    parser.add_argument('--git-reminders', action='store_true', default=None)
    parser.add_argument('--no-git-reminders', action='store_false', dest='git_reminders')
    parser.add_argument('--doc-reminders', action='store_true', default=None)
    parser.add_argument('--no-doc-reminders', action='store_false', dest='doc_reminders')

    args = parser.parse_args()

    if args.config:
        config = load_config(args.config)
        remind_every(config=config)
    else:
        cli_args = {
            'minutes': args.minutes,
            'message': args.message,
            'urgency': args.urgency,
            'sound': args.sound,
            'no_sound': args.no_sound,
            'git_reminders': args.git_reminders,
            'doc_reminders': args.doc_reminders
        }
        # Remove None values
        clean_args = {k: v for k, v in cli_args.items() if v is not None}
        remind_every(**clean_args)

if __name__ == "__main__":
    main()
