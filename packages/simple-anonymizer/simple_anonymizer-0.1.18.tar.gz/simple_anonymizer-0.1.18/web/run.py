#!/usr/bin/env python3
"""
Simple runner script for the Anon web application.
"""
import os
import sys
import webbrowser
from threading import Timer

# Add the web directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def open_browser(host: str, port: int) -> None:
    """Open the web browser to the application."""
    # Use localhost for browser access, even if server binds to 0.0.0.0
    browser_host = "localhost" if host == "0.0.0.0" else host
    webbrowser.open(f"http://{browser_host}:{port}")

def main(host: str = "0.0.0.0", port: int = 8080, open_browser_flag: bool = True) -> int:
    """Run the web application."""
    print("[WEB] Starting Anon Web Application...")
    print("=" * 50)

    try:
        # Import and run the web app
        from app import app

        if open_browser_flag:
            # Open browser after 2 seconds
            Timer(2.0, open_browser, args=(host, port)).start()

        print("[OK] Web app starting...")
        # Show localhost URL for browser access
        browser_host = "localhost" if host == "0.0.0.0" else host
        print(f"[WEB] Opening browser to: http://{browser_host}:{port}")
        print("[INFO] Press Ctrl+C to stop the server")
        print("=" * 50)

        # Run the Flask app
        app.run(host=host, port=port, debug=False)
        return 0

    except ImportError as e:
        print(f"[ERROR] Error: {e}")
        print("[TIP] Make sure Flask is installed: pip install flask")
        return 1
    except KeyboardInterrupt:
        print("\n[STOP] Web app stopped.")
        return 0
    except Exception as e:
        print(f"[ERROR] Error starting web app: {e}")
        return 1

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run the Anon web application")
    parser.add_argument("--host", default="0.0.0.0", help="Host interface")
    parser.add_argument("--port", type=int, default=8080, help="Port number")
    parser.add_argument("--no-browser", action="store_true", help="Do not open a browser window")
    args = parser.parse_args()

    sys.exit(main(args.host, args.port, not args.no_browser))