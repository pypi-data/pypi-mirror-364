#!/usr/bin/env python3

import sys  # Add this import
import os
import urllib.request
import urllib.error
import json
from datetime import datetime, timezone
from collections import Counter
import time

# Cross-platform keyboard input handling
try:
    import termios
    import tty
    UNIX_LIKE = True
except ImportError:
    try:
        import msvcrt
        UNIX_LIKE = False
    except ImportError:
        UNIX_LIKE = None  # No keyboard input support

# Version information
__version__ = "0.1.3"

API_URL = "https://api.github.com/users/{}/events"

# ANSI color codes
COLORS = {
    "PushEvent": "\033[92m",      # Green
    "IssuesEvent": "\033[94m",    # Blue
    "WatchEvent": "\033[93m",     # Yellow
    "CreateEvent": "\033[96m",    # Cyan
    "ForkEvent": "\033[95m",      # Magenta
    "PullRequestEvent": "\033[91m",  # Red
    "PullRequestReviewCommentEvent": "\033[90m",  # Dark Gray
    "DeleteEvent": "\033[31m",    # Bright Red
    "ReleaseEvent": "\033[35m",   # Purple
    "default": "\033[0m"           # Reset/No color
}

RESET = "\033[0m"

CACHE_DIR = os.path.expanduser("~/.cache/gh-feed")
CACHE_EXPIRY = 300  # seconds (5 minutes)

# Event types with descriptions for multi-select interface
EVENT_TYPES = [
    ("PushEvent", "Code commits and pushes"),
    ("IssuesEvent", "Issue creation, updates, comments"),
    ("PullRequestEvent", "Pull request creation and updates"),
    ("WatchEvent", "Repository stars"),
    ("CreateEvent", "Repository/branch/tag creation"),
    ("ForkEvent", "Repository forks"),
    ("ReleaseEvent", "Release publications"),
    ("DeleteEvent", "Branch/tag deletions"),
    ("PullRequestReviewCommentEvent", "Pull request review comments"),
]


def get_cache_path(username):
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)
    return os.path.join(CACHE_DIR, f"{username}.json")


def load_cache(username):
    path = get_cache_path(username)
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r") as f:
            cached = json.load(f)
        # Check expiry
        if time.time() - cached.get("timestamp", 0) < CACHE_EXPIRY:
            return cached.get("events")
    except Exception:
        pass
    return None


def save_cache(username, events):
    path = get_cache_path(username)
    try:
        with open(path, "w") as f:
            json.dump({"timestamp": time.time(), "events": events}, f)
    except Exception:
        pass


def get_key():
    """Cross-platform function to get a single keypress"""
    if UNIX_LIKE is None:
        # Fallback to input() if no keyboard support
        return input("Press Enter to continue...").strip()
    
    if UNIX_LIKE:
        # Unix-like systems (Linux, macOS)
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            key = sys.stdin.read(1)
            if key == '\x1b':  # ESC sequence
                key += sys.stdin.read(2)
            return key
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    else:
        # Windows
        key = msvcrt.getch()
        if key == b'\xe0':  # Special keys on Windows
            key += msvcrt.getch()
        return key.decode('utf-8', errors='ignore')


def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')


def fetch_user_activity(username, token=None, use_cache=True):
    # Try cache first
    if use_cache:
        cached_events = load_cache(username)
        if cached_events is not None:
            print(f"(Loaded cached activity for '{username}')")
            return cached_events

    url = API_URL.format(username)
    try:
        request = urllib.request.Request(url)
        if token:
            request.add_header("Authorization", f"token {token}")

        with urllib.request.urlopen(request) as response:
            headers = response.getheaders()
            rate_limit_remaining = dict(headers).get("X-RateLimit-Remaining")
            if rate_limit_remaining is not None and int(rate_limit_remaining) <= 5:
                print(
                    f"Warning: You are nearing the GitHub API rate limit. Only {rate_limit_remaining} requests remaining.")
            data = response.read()
            events = json.loads(data)
            save_cache(username, events)
            return events
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"Error: User '{username}' not found.")
        elif e.code == 403:
            print("Error: Rate limit exceeded. Try again later.")
        else:
            print(f"HTTP Error {e.code}: {e.reason}")
    except urllib.error.URLError as e:
        print(f"Connection error: {e.reason}")
        # Try to load cache even if offline
        cached_events = load_cache(username)
        if cached_events is not None:
            print(f"(Loaded cached activity for '{username}' - offline mode)")
            return cached_events
    return None


def time_ago(iso_time):
    event_time = datetime.strptime(
        iso_time, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    delta = now - event_time

    seconds = delta.total_seconds()
    if seconds < 60:
        return f"{int(seconds)}s ago"
    elif seconds < 3600:
        return f"{int(seconds // 60)}m ago"
    elif seconds < 86400:
        return f"{int(seconds // 3600)}h ago"
    else:
        return f"{int(seconds // 86400)}d ago"


def colorize(text, event_type):
    color = COLORS.get(event_type, COLORS["default"])
    return f"{color}{text}{RESET}"


def display_activity(events, filter_types=None):
    if not events:
        print("No recent public activity found.")
        return

    count = 0
    type_counter = Counter()
    repos = set()

    for event in events:
        if count >= 7:
            break

        event_type = event["type"]
        
        # Handle filtering by multiple types
        if filter_types:
            if isinstance(filter_types, str):
                # Single filter type (backward compatibility)
                if filter_types.lower() not in event_type.lower():
                    continue
            elif isinstance(filter_types, list):
                # Multiple filter types
                if not any(ft.lower() in event_type.lower() for ft in filter_types):
                    continue

        type_counter[event_type] += 1
        repos.add(event["repo"]["name"])

        repo = event["repo"]["name"]
        created_at = event.get("created_at", "")
        timestamp = f"({time_ago(created_at)})" if created_at else ""

        if event_type == "PushEvent":
            commit_count = len(event["payload"]["commits"])
            message = f"- Pushed {commit_count} commit{'s' if commit_count > 1 else ''} to {repo} {timestamp}"
        elif event_type == "IssuesEvent":
            action = event["payload"]["action"]
            message = f"- {action.capitalize()} an issue in {repo} {timestamp}"
        elif event_type == "WatchEvent":
            message = f"- Starred {repo} {timestamp}"
        elif event_type == "CreateEvent":
            ref_type = event["payload"]["ref_type"]
            message = f"- Created a new {ref_type} in {repo} {timestamp}"
        elif event_type == "ForkEvent":
            forkee = event["payload"]["forkee"]["full_name"]
            message = f"- Forked {repo} to {forkee} {timestamp}"
        elif event_type == "PullRequestEvent":
            action = event["payload"]["action"]
            message = f"- {action.capitalize()} a pull request in {repo} {timestamp}"
        elif event_type == "PullRequestReviewCommentEvent":
            message = f"- Commented on a pull request in {repo} {timestamp}"
        elif event_type == "DeleteEvent":
            ref_type = event["payload"]["ref_type"]
            ref = event["payload"]["ref"]
            message = f"- Deleted {ref_type} '{ref}' in {repo} {timestamp}"
        elif event_type == "ReleaseEvent":
            action = event["payload"]["action"]
            release_name = event["payload"]["release"]["name"]
            message = f"- {action.capitalize()} release '{release_name}' in {repo} {timestamp}"
        else:
            message = f"- {event_type} in {repo} {timestamp}"

        print(colorize(message, event_type))
        count += 1

    if count > 0:
        print("\nSummary:")
        for etype, num in type_counter.items():
            if etype == "PushEvent":
                label = "push commit"
            elif etype == "IssuesEvent":
                label = "issue opened"
            elif etype == "PullRequestEvent":
                label = "pull request sent"
            elif etype == "WatchEvent":
                label = "repo starred"
            elif etype == "ForkEvent":
                label = "repo forked"
            elif etype == "CreateEvent":
                label = "repo created"
            elif etype == "DeleteEvent":
                label = "item deleted"
            elif etype == "ReleaseEvent":
                label = "release published"
            elif etype == "PullRequestReviewCommentEvent":
                label = "PR comment"
            else:
                label = etype

            print(f"- {label}: {num}")

        print(f"- Activity in {len(repos)} repos")


def export_to_json(events, filename="activity.json"):
    try:
        with open(filename, "w") as f:
            json.dump(events[:7], f, indent=2)
        print(f"Exported events to {filename}")
    except IOError as e:
        print(f"Error saving file: {e}")


def multi_select_event_types():
    """Interactive multi-select interface for choosing event types"""
    if UNIX_LIKE is None:
        # Fallback to simple input if no keyboard support
        print("Keyboard navigation not supported on this system.")
        filter_input = input("Enter event types separated by commas (or leave blank for all): ").strip()
        if not filter_input:
            return None
        return [t.strip() for t in filter_input.split(",")]
    
    # Initialize state
    options = EVENT_TYPES + [("Select All", "Show all event types")]
    selected = [False] * len(options)
    cursor = 0
    select_all_idx = len(options) - 1
    
    while True:
        clear_screen()
        print("Available Event Types:")
        print("Use ↑↓ or j/k to navigate, SPACE to toggle, ENTER to confirm, ESC to cancel")
        print()
        
        for i, (event_type, description) in enumerate(options):
            cursor_marker = ">" if i == cursor else " "
            selected_marker = "[X]" if selected[i] else "[ ]"
            print(f"  {cursor_marker} {selected_marker} {event_type:<25} - {description}")
        
        # Show current selection
        selected_types = [options[i][0] for i in range(len(options) - 1) if selected[i]]
        if selected[select_all_idx]:
            selected_types = ["All event types"]
        
        print()
        print(f"Selected: {', '.join(selected_types) if selected_types else 'None'}")
        print()
        
        try:
            key = get_key()
            
            # Handle different key inputs
            if key in ['\x1b[A', 'k']:  # Up arrow or k (vim)
                cursor = (cursor - 1) % len(options)
            elif key in ['\x1b[B', 'j']:  # Down arrow or j (vim)
                cursor = (cursor + 1) % len(options)
            elif key == ' ':  # Space to toggle
                if cursor == select_all_idx:
                    # Toggle "Select All"
                    select_all = not selected[select_all_idx]
                    selected = [select_all] * len(options)
                else:
                    # Toggle individual item
                    selected[cursor] = not selected[cursor]
                    selected[select_all_idx] = False  # Uncheck "Select All"
            elif key in ['\r', '\n']:  # Enter to confirm
                if selected[select_all_idx]:
                    return None  # Return None for "all events"
                selected_events = [options[i][0] for i in range(len(options) - 1) if selected[i]]
                return selected_events if selected_events else None
            elif key == '\x1b':  # ESC to cancel
                return None
                
        except KeyboardInterrupt:
            return None


def interactive_mode(username=None):
    print("Welcome to Interactive Mode!")
    
    if not username:
        print("Press ENTER without typing a username to exit.")
        while True:
            username = input("Enter GitHub username: ").strip()
            if not username:
                print("Exiting interactive mode.")
                return
            break  # Any non-empty input is accepted as a username
    else:
        print(f"Using username: {username}")

    token = os.getenv("GITHUB_TOKEN")
    token_choice = input("Use GitHub token? (y/n): ").strip().lower()
    if token_choice == 'y':
        token_input = input(
            "Enter GitHub token (leave blank to use $GITHUB_TOKEN): ").strip()
        if token_input:
            token = token_input

    # Enhanced multi-select event type filtering
    print("\nEvent Filtering Options:")
    print("1. Show all events")
    print("2. Enter event type manually") 
    print("3. Use interactive multi-select")
    
    filter_choice = input("Choose option (1-3, default: 1): ").strip()
    filter_types = None
    
    if filter_choice == "2":
        filter_input = input("Filter by event type (leave blank for all): ").strip()
        filter_types = filter_input if filter_input else None
    elif filter_choice == "3":
        print("\nStarting multi-select interface...")
        time.sleep(1)  # Brief pause before clearing screen
        filter_types = multi_select_event_types()
        clear_screen()
        print(f"Selected event types: {', '.join(filter_types) if filter_types else 'All'}")
    
    export = input("Export results to JSON? (y/n): ").strip().lower() == 'y'

    events = fetch_user_activity(username, token)
    if events is not None:
        display_activity(events, filter_types)
        if export:
            export_to_json(events)


def print_help():
    help_text = """
gh-feed - GitHub User Activity CLI Tool

USAGE:
    gh-feed <username> [OPTIONS]
    gh-feed --interactive
    gh-feed <username> --interactive
    gh-feed --help

ARGUMENTS:
    <username>          GitHub username to fetch activity for

OPTIONS:
    --filter <type>     Filter events by type (e.g., PushEvent, IssuesEvent)
    --json              Export results to activity.json file
    --token <token>     Use GitHub personal access token for authentication
    --interactive       Start interactive mode with guided prompts
    --version, -v       Show version information
    --help, -h          Show this help message

EXAMPLES:
    gh-feed octocat
    gh-feed octocat --filter PushEvent
    gh-feed octocat --json --token your_token_here
    gh-feed --interactive
    gh-feed octocat --interactive

ENVIRONMENT VARIABLES:
    GITHUB_TOKEN        GitHub personal access token (alternative to --token)

SUPPORTED EVENT TYPES:
    PushEvent, IssuesEvent, PullRequestEvent, WatchEvent, ForkEvent,
    CreateEvent, DeleteEvent, ReleaseEvent, PullRequestReviewCommentEvent

For more information, visit: https://github.com/bhantsi/gh-feed
"""
    print(help_text.strip())


def print_version():
    print(f"gh-feed version {__version__}")


def check_for_updates():
    """Check PyPI for newer version and notify user"""
    try:
        # Try main PyPI first, then fallback to TestPyPI
        urls = [
            "https://pypi.org/pypi/gh-feed/json",
            "https://test.pypi.org/pypi/gh-feed/json"
        ]
        
        for url in urls:
            try:
                request = urllib.request.Request(url)
                request.add_header('User-Agent', f'gh-feed/{__version__}')
                
                with urllib.request.urlopen(request, timeout=3) as response:
                    data = json.loads(response.read())
                    latest_version = data["info"]["version"]
                    
                    if latest_version != __version__:
                        print(f"📦 New version available: {latest_version} (current: {__version__})")
                        print("💡 Run 'pip install --upgrade gh-feed' to update")
                        print()
                    return  # Success, no need to try other URLs
            except urllib.error.HTTPError:
                continue  # Try next URL
                
    except Exception:
        # Silently fail if no internet or PyPI unavailable
        pass


def main():
    # Check for help flag first - BEFORE any other processing
    if "--help" in sys.argv or "-h" in sys.argv:
        print_help()
        return

    # Check for version flag
    if "--version" in sys.argv or "-v" in sys.argv:
        print_version()
        return

    # Check for interactive flag (can be combined with username)
    if "--interactive" in sys.argv:
        username = None
        # If there are more than 2 arguments and one is --interactive,
        # try to extract username from the other arguments (skip flags)
        if len(sys.argv) > 2:
            i = 1
            while i < len(sys.argv):
                arg = sys.argv[i]
                if arg == "--interactive":
                    i += 1
                    continue
                elif arg.startswith("--"):
                    # Skip flag and its potential value
                    if arg in ["--filter", "--token"]:
                        i += 2  # Skip flag and its value
                    else:
                        i += 1  # Skip flag only
                    continue
                else:
                    # This should be the username
                    username = arg
                    break
        interactive_mode(username)
        return

    if len(sys.argv) < 2:
        print(
            "Usage: gh-feed <github_username> [--filter <event_type>] [--json] [--token <token>] | --interactive")
        print("Run 'gh-feed --help' for more information.")
        sys.exit(1)

    # Check for updates (non-blocking)
    check_for_updates()

    # Only assign username AFTER checking for help and interactive flags
    username = sys.argv[1]
    filter_type = None
    export_json = "--json" in sys.argv
    token = os.getenv("GITHUB_TOKEN")

    if "--token" in sys.argv:
        try:
            token_index = sys.argv.index("--token")
            token = sys.argv[token_index + 1]
        except IndexError:
            print("Error: --token flag must be followed by a token")
            sys.exit(1)

    if "--filter" in sys.argv:
        try:
            filter_index = sys.argv.index("--filter")
            filter_type = sys.argv[filter_index + 1]
        except IndexError:
            print("Error: --filter flag must be followed by an event type")
            sys.exit(1)

    events = fetch_user_activity(username, token)

    if events is not None:
        display_activity(events, filter_type)
        if export_json:
            export_to_json(events)


if __name__ == "__main__":
    main()
