"""Anonymizer GUI package."""

from __future__ import annotations

import os
import sys
import subprocess
import logging
from pathlib import Path
from datetime import datetime

from .gui import ModernAnonymizerGUI, main as _launch

__all__ = ["launch", "ModernAnonymizerGUI"]


def launch() -> None:
    """Launch the GUI application in the background with proper logging."""
    # Create log directory
    log_dir = Path.home() / ".anonymizer"
    log_dir.mkdir(exist_ok=True)

    # Setup log file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"gui_{timestamp}.log"

    # Check if running from command line (detach mode)
    if len(sys.argv) > 1 and sys.argv[1] == "--detach":
        # Background mode - redirect output to log file
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[logging.FileHandler(log_file, encoding='utf-8')]
        )

        logging.info("Starting Anonymizer GUI in background mode")
        _launch()
    else:
        # Foreground mode - check if we should detach
        detach_and_launch(log_file)


def detach_and_launch(log_file: Path) -> None:
    """Detach from terminal and launch GUI in background."""
    import platform

    script_path = Path(__file__).parent / "gui.py"

    # Cross-platform background launch
    try:
        if platform.system() == "Windows":
            # Windows: Use DETACHED_PROCESS
            with open(log_file, 'w', encoding='utf-8') as log_fp:
                subprocess.Popen(
                    [sys.executable, str(script_path)],
                    stdout=log_fp,
                    stderr=subprocess.STDOUT,
                    creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP,
                    close_fds=False
                )
        else:
            # Unix/Linux/macOS: Use start_new_session
            with open(log_file, 'w', encoding='utf-8') as log_fp:
                subprocess.Popen(
                    [sys.executable, str(script_path)],
                    stdout=log_fp,
                    stderr=subprocess.STDOUT,
                    start_new_session=True
                )

        print(f"🚀 Anonymizer GUI launched in background")
        print(f"📝 Logs: {log_file}")
        print("✅ You can safely close this terminal")

    except Exception as e:
        print(f"❌ Failed to launch in background: {e}")
        print("🔄 Launching in foreground mode...")
        # Fallback to foreground mode
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        logging.info(f"Starting Anonymizer GUI - Log file: {log_file}")
        _launch()
