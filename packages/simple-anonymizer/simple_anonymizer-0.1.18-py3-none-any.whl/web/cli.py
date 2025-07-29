#!/usr/bin/env python3
"""Command line interface for managing the Anon web server."""
from __future__ import annotations

import argparse
import os
import signal
import subprocess
import sys
import platform
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from anonymizer_core.dictionary import (
    add_always_redact_word, 
    remove_always_redact_word, 
    list_always_redact_words
)

# Create dedicated log directory
LOG_DIR = Path.home() / ".anonymizer"
LOG_DIR.mkdir(exist_ok=True)

PID_FILE = LOG_DIR / "web_server.pid"
LOG_FILE = LOG_DIR / f"web_server_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"


def start_server(host: str, port: int) -> None:
    """Start the Flask web server in a background process."""
    if PID_FILE.exists():
        try:
            pid = int(PID_FILE.read_text())
            # Check if process is actually running
            if platform.system() == "Windows":
                result = subprocess.run(['tasklist', '/FI', f'PID eq {pid}'],
                                      capture_output=True, text=True)
                if str(pid) in result.stdout:
                    print(f"✅ Server is already running (PID: {pid})")
                    print(f"🌐 Access at: http://{host}:{port}")
                    return
            else:
                try:
                    os.kill(pid, 0)  # Check if process exists
                    print(f"✅ Server is already running (PID: {pid})")
                    print(f"🌐 Access at: http://{host}:{port}")
                    return
                except OSError:
                    pass  # Process doesn't exist, continue with startup
        except (ValueError, FileNotFoundError):
            pass  # Invalid PID file, continue with startup

    # Clean up stale PID file
    PID_FILE.unlink(missing_ok=True)

    print(f"🚀 Starting Anonymizer Web Server...")
    print(f"🌐 Will be available at: http://{host}:{port}")
    print(f"📝 Logs: {LOG_FILE}")

    # Get the path to the run.py script
    script_path = Path(__file__).parent / "run.py"

    try:
        # Start server in background
        if platform.system() == "Windows":
            # Windows: Use DETACHED_PROCESS
            with open(LOG_FILE, 'w') as log_fp:
                process = subprocess.Popen(
                    [sys.executable, str(script_path), "--host", host, "--port", str(port), "--no-browser"],
                    stdout=log_fp,
                    stderr=subprocess.STDOUT,
                    cwd=str(script_path.parent),
                    creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP,
                    close_fds=False
                )
        else:
            # Unix/Linux/macOS: Use start_new_session
            with open(LOG_FILE, 'w') as log_fp:
                process = subprocess.Popen(
                    [sys.executable, str(script_path), "--host", host, "--port", str(port), "--no-browser"],
                    stdout=log_fp,
                    stderr=subprocess.STDOUT,
                    cwd=str(script_path.parent),
                    start_new_session=True
                )

        # Save PID
        PID_FILE.write_text(str(process.pid))

        print(f"✅ Server started successfully (PID: {process.pid})")
        print(f"✅ You can safely close this terminal")
        print(f"🛑 To stop: anon-web stop")

    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)


def stop_server() -> None:
    """Stop the background Flask web server."""
    if not PID_FILE.exists():
        print("❌ No running server found.")
        return

    try:
        pid = int(PID_FILE.read_text())

        if platform.system() == "Windows":
            # Windows: Use taskkill
            result = subprocess.run(['taskkill', '/F', '/PID', str(pid)],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Server stopped (PID: {pid})")
            else:
                print(f"⚠️  Server process not found (PID: {pid})")
        else:
            # Unix/Linux/macOS: Use kill
            try:
                os.kill(pid, signal.SIGTERM)
                print(f"✅ Server stopped (PID: {pid})")
            except ProcessLookupError:
                print(f"⚠️  Server process not found (PID: {pid})")

    except (ValueError, FileNotFoundError) as e:
        print(f"❌ Error reading PID file: {e}")
    finally:
        PID_FILE.unlink(missing_ok=True)


def status_server() -> None:
    """Check the status of the web server."""
    if not PID_FILE.exists():
        print("❌ No server running")
        return

    try:
        pid = int(PID_FILE.read_text())

        # Check if process is running
        if platform.system() == "Windows":
            result = subprocess.run(['tasklist', '/FI', f'PID eq {pid}'],
                                  capture_output=True, text=True)
            if str(pid) in result.stdout:
                print(f"✅ Server is running (PID: {pid})")
                print(f"📝 Current log file: {LOG_FILE}")
            else:
                print(f"❌ Server not running (stale PID: {pid})")
                PID_FILE.unlink(missing_ok=True)
        else:
            try:
                os.kill(pid, 0)  # Check if process exists
                print(f"✅ Server is running (PID: {pid})")
                print(f"📝 Current log file: {LOG_FILE}")
            except OSError:
                print(f"❌ Server not running (stale PID: {pid})")
                PID_FILE.unlink(missing_ok=True)

    except (ValueError, FileNotFoundError):
        print("❌ Invalid PID file")
        PID_FILE.unlink(missing_ok=True)


def show_logs() -> None:
    """Show recent server logs."""
    if LOG_FILE.exists():
        print(f"📝 Recent logs from {LOG_FILE}:")
        print("-" * 50)
        try:
            with open(LOG_FILE, 'r') as f:
                lines = f.readlines()
                # Show last 20 lines
                for line in lines[-20:]:
                    print(line.rstrip())
        except Exception as e:
            print(f"❌ Error reading log file: {e}")
    else:
        print("❌ No log file found")

    # Also check for other recent log files
    recent_logs = list(LOG_DIR.glob("web_server_*.log"))
    if len(recent_logs) > 1:
        print(f"\n📁 Found {len(recent_logs)} log files in {LOG_DIR}")
        for log in sorted(recent_logs, key=lambda x: x.stat().st_mtime, reverse=True)[:5]:
            print(f"   {log.name} ({log.stat().st_size} bytes)")


def clean_logs() -> None:
    """Clean old log files, preserving always_redact.txt."""
    log_files = list(LOG_DIR.glob("*.log"))
    
    # Always mention that always_redact.txt is preserved
    always_redact_file = LOG_DIR / "always_redact.txt"
    always_redact_exists = always_redact_file.exists()
    
    if not log_files:
        print("✅ No log files to clean")
        if always_redact_exists:
            print("✅ Preserved always_redact.txt file")
        return

    # Keep only the 5 most recent log files
    sorted_logs = sorted(log_files, key=lambda x: x.stat().st_mtime, reverse=True)
    to_delete = sorted_logs[5:]

    if to_delete:
        for log_file in to_delete:
            log_file.unlink()
        print(f"🗑️  Cleaned {len(to_delete)} old log files")
        print(f"📁 Kept {min(5, len(sorted_logs))} recent log files")
        print("✅ Preserved always_redact.txt file")
    else:
        print("✅ All log files are recent, nothing to clean")
        if always_redact_exists:
            print("✅ Preserved always_redact.txt file")


def add_redact_term(term: str) -> None:
    """Add a term to the always redact list."""
    if not term or not term.strip():
        print("❌ Please provide a term to add")
        return
        
    if add_always_redact_word(term):
        print(f"✅ Added '{term}' to always redact list")
    else:
        print(f"⚠️  Term '{term}' already exists in always redact list")


def remove_redact_term(term: str) -> None:
    """Remove a term from the always redact list."""
    if not term or not term.strip():
        print("❌ Please provide a term to remove")
        return
        
    if remove_always_redact_word(term):
        print(f"✅ Removed '{term}' from always redact list")
    else:
        print(f"⚠️  Term '{term}' not found in always redact list")


def list_redact_terms() -> None:
    """List all terms in the always redact list."""
    terms = list_always_redact_words()
    
    if not terms:
        print("✅ No terms in always redact list")
        return
        
    print(f"📋 Always redact list ({len(terms)} terms):")
    print("-" * 40)
    for term in sorted(terms):
        print(f"  • {term}")


def main() -> None:
    """Main CLI function with enhanced commands."""
    parser = argparse.ArgumentParser(
        description="🌐 Anonymizer Web Server Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  anon-web start                    # Start on default host:port (127.0.0.1:8080)
  anon-web start --host 0.0.0.0     # Start on all interfaces
  anon-web start --port 5000        # Start on custom port
  anon-web stop                     # Stop the server
  anon-web status                   # Check server status
  anon-web logs                     # Show recent logs
  anon-web clean                    # Clean old log files (preserves always_redact.txt)
  anon-web add-redact "term"        # Add term to always redact list
  anon-web remove-redact "term"     # Remove term from always redact list
  anon-web list-redact              # List all always redacted terms
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Start command
    start_parser = subparsers.add_parser("start", help="Start the web server in background")
    start_parser.add_argument("--host", default="127.0.0.1", help="Host interface (default: 127.0.0.1)")
    start_parser.add_argument("--port", type=int, default=8080, help="Port number (default: 8080)")

    # Stop command
    subparsers.add_parser("stop", help="Stop the running web server")

    # Status command
    subparsers.add_parser("status", help="Check server status")

    # Logs command
    subparsers.add_parser("logs", help="Show recent server logs")

    # Clean command
    subparsers.add_parser("clean", help="Clean old log files (preserves always_redact.txt)")

    # Always redact management commands
    add_redact_parser = subparsers.add_parser("add-redact", help="Add a term to always redact list")
    add_redact_parser.add_argument("term", help="Term to add to always redact list")
    
    remove_redact_parser = subparsers.add_parser("remove-redact", help="Remove a term from always redact list")
    remove_redact_parser.add_argument("term", help="Term to remove from always redact list")
    
    subparsers.add_parser("list-redact", help="List all terms in always redact list")

    args = parser.parse_args()

    if args.command == "start":
        start_server(args.host, args.port)
    elif args.command == "stop":
        stop_server()
    elif args.command == "status":
        status_server()
    elif args.command == "logs":
        show_logs()
    elif args.command == "clean":
        clean_logs()
    elif args.command == "add-redact":
        add_redact_term(args.term)
    elif args.command == "remove-redact":
        remove_redact_term(args.term)
    elif args.command == "list-redact":
        list_redact_terms()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
