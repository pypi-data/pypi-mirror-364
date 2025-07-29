#!/usr/bin/env python3
"""
Modern Tkinter GUI for the anonymizer application.
Enhanced with modern styling and improved user experience.
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import queue
import os
import sys
from datetime import datetime

# Add the parent directory to the path to import anonymizer_core
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from anonymizer_core import redact
from anonymizer_core.dictionary import add_always_redact_word, remove_always_redact_word


class ModernAnonymizerGUI:
    """Modern GUI class using tkinter with enhanced styling and UX."""

    def __init__(self, root, test_mode=False):
        self.root = root
        self.test_mode = test_mode
        self.root.title("🕵️ Anon - Privacy-First Text Anonymizer")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)

        # Set window icon with cross-platform support
        self.set_window_icon()

        # Configure modern style
        self.setup_modern_style()

        # Set root window background to match theme
        self.root.configure(bg=self.colors['background'])

        # Create main container with padding
        self.main_container = ttk.Frame(root, padding="20")
        self.main_container.grid(row=0, column=0, sticky="nsew")

        # Configure grid weights for responsive design
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        self.main_container.columnconfigure(0, weight=1)
        self.main_container.rowconfigure(2, weight=1)  # Text areas row

        # Note: Always redact words are now managed securely in ~/.anonymizer/always_redact.txt
        # The GUI does not display these terms for security, only allows add/remove

        # Create modern widgets
        self.create_modern_widgets()

        # Message queue for thread communication
        self.message_queue = queue.Queue()
        self.root.after(100, self.check_queue)

        # Bind keyboard shortcuts
        self.bind_shortcuts()

        # --- Compatibility aliases for tests ---
        self.input_text = self.text_input
        self.output_text = self.text_output
        self.load_text = self.load_file
        self.save_text = self.save_result
        self.copy_text = self.copy_result

    def set_window_icon(self):
        """Set window icon with cross-platform support."""
        import platform
        import os

        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        resources_dir = os.path.join(os.path.dirname(script_dir), 'resources')

        system = platform.system().lower()

        try:
            if system == 'darwin':  # macOS
                # Use .icns file for macOS
                icon_path = os.path.join(resources_dir, 'icon.icns')
                if os.path.exists(icon_path):
                    # For macOS, we need to set the icon differently
                    self.root.iconphoto(True, tk.PhotoImage(file=icon_path))
            elif system == 'windows':  # Windows
                # Use .ico file for Windows
                icon_path = os.path.join(resources_dir, 'icon.ico')
                if os.path.exists(icon_path):
                    self.root.iconbitmap(icon_path)
            else:  # Linux and other Unix-like systems
                # Try .ico first, then fallback to PNG
                icon_path = os.path.join(resources_dir, 'icon.ico')
                if os.path.exists(icon_path):
                    self.root.iconbitmap(icon_path)
                else:
                    # Try PNG if available
                    png_path = os.path.join(resources_dir, 'icon.png')
                    if os.path.exists(png_path):
                        self.root.iconphoto(True, tk.PhotoImage(file=png_path))
        except Exception as e:
            # Silently fail if icon setting fails
            pass

    def setup_modern_style(self):
        """Setup modern application styling."""
        style = ttk.Style()

        import platform
        system = platform.system().lower()

        # Debug: Print platform information
        print(f"Platform detected: {system}")
        print(f"Available themes: {style.theme_names()}")
        print(f"Current theme before change: {style.theme_use()}")

        # Use appropriate theme based on platform
        try:
            if system == 'windows':
                style.theme_use('vista')  # Better for Windows
                print("Applied Windows 'vista' theme")
            elif system == 'darwin':
                style.theme_use('aqua')   # Better for macOS
                print("Applied macOS 'aqua' theme")
            else:
                style.theme_use('clam')   # Better for Linux
                print("Applied Linux 'clam' theme")
        except Exception as e:
            print(f"Theme selection failed: {e}")
            try:
                style.theme_use('clam')
                print("Fallback to 'clam' theme")
            except Exception as e2:
                print(f"Fallback theme failed: {e2}")

        print(f"Final theme: {style.theme_use()}")        # Define platform-appropriate color scheme
        if system == 'windows':
            # Windows-friendly colors with better contrast
            self.colors = {
                'primary': '#0078d4',      # Windows Blue
                'secondary': '#5c5c5c',    # Medium Gray
                'success': '#107c10',      # Windows Green
                'warning': '#ff8c00',      # Orange
                'error': '#d13438',        # Windows Red
                'background': '#f3f2f1',   # Windows light gray
                'surface': '#ffffff',      # White
                'text': '#323130',         # Windows dark text
                'text_secondary': '#605e5c' # Windows medium text
            }
            print(f"Applied Windows color scheme - Primary: {self.colors['primary']}")
        else:
            # macOS/Linux colors (original)
            self.colors = {
                'primary': '#2563eb',      # Blue
                'secondary': '#64748b',    # Gray
                'success': '#059669',      # Green
                'warning': '#d97706',      # Orange
                'error': '#dc2626',        # Red
                'background': '#f8fafc',   # Light gray
                'surface': '#ffffff',      # White
                'text': '#1e293b',        # Dark gray
                'text_secondary': '#64748b' # Medium gray
            }
            print(f"Applied macOS/Linux color scheme - Primary: {self.colors['primary']}")

        # Configure modern styles
        style.configure('Modern.TFrame', background=self.colors['background'])
        style.configure('Modern.TLabel',
                       background=self.colors['background'],
                       foreground=self.colors['text'],
                       font=('Segoe UI', 10))

        style.configure('Title.TLabel',
                       background=self.colors['background'],
                       foreground=self.colors['primary'],
                       font=('Segoe UI', 24, 'bold'))

        style.configure('Subtitle.TLabel',
                       background=self.colors['background'],
                       foreground=self.colors['text_secondary'],
                       font=('Segoe UI', 12))

        style.configure('Success.TLabel',
                       background=self.colors['background'],
                       foreground=self.colors['success'],
                       font=('Segoe UI', 10, 'bold'))

        style.configure('Error.TLabel',
                       background=self.colors['background'],
                       foreground=self.colors['error'],
                       font=('Segoe UI', 10, 'bold'))

        # Platform-specific button styles with better contrast
        if system == 'windows':
            print("Configuring Windows button styles...")
            # On Windows, ttk buttons don't respect background colors well
            # We'll use regular tk.Button with custom styling instead
            self.use_tk_buttons = True

            # Define button configurations for tk.Button
            self.button_configs = {
                'Primary': {
                    'bg': self.colors['primary'],
                    'fg': 'white',
                    'font': ('Segoe UI', 10, 'bold'),
                    'relief': 'raised',
                    'borderwidth': 1,
                    'activebackground': '#106ebe',
                    'activeforeground': 'white',
                    'cursor': 'hand2'
                },
                'Secondary': {
                    'bg': self.colors['secondary'],
                    'fg': 'white',
                    'font': ('Segoe UI', 10),
                    'relief': 'raised',
                    'borderwidth': 1,
                    'activebackground': '#484644',
                    'activeforeground': 'white',
                    'cursor': 'hand2'
                },
                'Success': {
                    'bg': self.colors['success'],
                    'fg': 'white',
                    'font': ('Segoe UI', 10, 'bold'),
                    'relief': 'raised',
                    'borderwidth': 1,
                    'activebackground': '#0e6e0e',
                    'activeforeground': 'white',
                    'cursor': 'hand2'
                },
                'Warning': {
                    'bg': self.colors['warning'],
                    'fg': 'white',
                    'font': ('Segoe UI', 10, 'bold'),
                    'relief': 'raised',
                    'borderwidth': 1,
                    'activebackground': '#cc7a00',
                    'activeforeground': 'white',
                    'cursor': 'hand2'
                },
                'Error': {
                    'bg': self.colors['error'],
                    'fg': 'white',
                    'font': ('Segoe UI', 10, 'bold'),
                    'relief': 'raised',
                    'borderwidth': 1,
                    'activebackground': '#a42b2f',
                    'activeforeground': 'white',
                    'cursor': 'hand2'
                }
            }

            print("Windows tk.Button configurations ready")
            print(f"Primary button will use background: {self.button_configs['Primary']['bg']}")
        else:
            # Use ttk buttons for macOS/Linux
            self.use_tk_buttons = False
            # macOS/Linux button styles (original)
            style.configure('Primary.TButton',
                           background=self.colors['primary'],
                           foreground='white',
                           font=('Segoe UI', 10, 'bold'),
                           padding=(20, 10))

            style.configure('Secondary.TButton',
                           background=self.colors['secondary'],
                           foreground='white',
                           font=('Segoe UI', 10),
                           padding=(15, 8))

            style.configure('Success.TButton',
                           background=self.colors['success'],
                           foreground='white',
                           font=('Segoe UI', 10, 'bold'),
                           padding=(15, 8))

        # Modern entry style with platform-specific improvements
        if system == 'windows':
            style.configure('Modern.TEntry',
                           fieldbackground='white',
                           foreground=self.colors['text'],
                           font=('Segoe UI', 10),
                           padding=(10, 8),
                           borderwidth=1,
                           relief='solid')
        else:
            style.configure('Modern.TEntry',
                           fieldbackground=self.colors['surface'],
                           foreground=self.colors['text'],
                           font=('Segoe UI', 10),
                           padding=(10, 8))

        # Modern progress bar
        style.configure('Modern.Horizontal.TProgressbar',
                       background=self.colors['primary'],
                       troughcolor=self.colors['background'])

    def create_button(self, parent, text, style_name, command, **kwargs):
        """Create a button with appropriate styling based on platform."""
        if hasattr(self, 'use_tk_buttons') and self.use_tk_buttons:
            # Use tk.Button for Windows with custom colors
            style_config = self.button_configs.get(style_name, self.button_configs['Primary'])
            button = tk.Button(parent, text=text, command=command, **style_config, **kwargs)
            # Safe print without Unicode issues
            try:
                print(f"Created tk.Button with {style_name} style (bg: {style_config['bg']})")
            except UnicodeEncodeError:
                print(f"Created tk.Button with {style_name} style")
            return button
        else:
            # Use ttk.Button for macOS/Linux
            button = ttk.Button(parent, text=text, style=f'{style_name}.TButton', command=command, **kwargs)
            try:
                print(f"Created ttk.Button with {style_name}.TButton style")
            except UnicodeEncodeError:
                print(f"Created ttk.Button with {style_name} style")
            return button

    def create_modern_widgets(self):
        """Create modern GUI widgets with enhanced styling."""

        # Header section with title and subtitle
        header_frame = ttk.Frame(self.main_container, style='Modern.TFrame')
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        header_frame.columnconfigure(0, weight=1)

        title_label = ttk.Label(header_frame,
                               text="🕵️ Anon - Privacy-First Text Anonymizer",
                               style='Title.TLabel')
        title_label.grid(row=0, column=0, pady=(0, 5))

        subtitle_label = ttk.Label(header_frame,
                                  text="Your sensitive data deserves better than cloud-based anonymization",
                                  style='Subtitle.TLabel')
        subtitle_label.grid(row=1, column=0)

        # Always Redact section with modern design
        self.create_always_redact_section()

        # Main content area with input and output
        self.create_main_content_area()

        # Status bar
        self.create_status_bar()

    def create_always_redact_section(self):
        """Create the always redact section with modern styling - no term display for security."""
        always_redact_frame = ttk.LabelFrame(self.main_container,
                                           text="🔒 Always Redact Words (Secure Management)",
                                           padding="15")
        always_redact_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        always_redact_frame.columnconfigure(1, weight=1)

        # Info label explaining security approach
        info_label = ttk.Label(always_redact_frame,
                              text="📋 Terms are stored securely and not displayed. Use CLI 'anon-web list-redact' to view.",
                              style='Subtitle.TLabel')
        info_label.grid(row=0, column=0, columnspan=4, sticky="ew", pady=(0, 15))

        # Add word section with modern layout
        add_frame = ttk.Frame(always_redact_frame)
        add_frame.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(0, 10))
        add_frame.columnconfigure(1, weight=1)

        ttk.Label(add_frame, text="Add word:", style='Modern.TLabel').grid(row=0, column=0, padx=(0, 10))

        self.add_word_entry = ttk.Entry(add_frame, style='Modern.TEntry')
        self.add_word_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        self.add_word_entry.bind('<Return>', lambda e: self.add_always_redact_word())

        self.add_word_button = self.create_button(add_frame,
                                                "+ Add",
                                                "Primary",
                                                self.add_always_redact_word)
        self.add_word_button.grid(row=0, column=2, padx=(0, 10))

        # Remove word section
        remove_frame = ttk.Frame(always_redact_frame)
        remove_frame.grid(row=2, column=0, columnspan=3, sticky="ew")
        remove_frame.columnconfigure(1, weight=1)

        ttk.Label(remove_frame, text="Remove word:", style='Modern.TLabel').grid(row=0, column=0, padx=(0, 10))

        self.remove_word_entry = ttk.Entry(remove_frame, style='Modern.TEntry')
        self.remove_word_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        self.remove_word_entry.bind('<Return>', lambda e: self.remove_always_redact_word())

        self.remove_word_button = self.create_button(remove_frame,
                                                   "- Remove",
                                                   "Secondary",
                                                   self.remove_always_redact_word)
        self.remove_word_button.grid(row=0, column=2)

    def create_main_content_area(self):
        """Create the main content area with input and output sections."""
        content_frame = ttk.Frame(self.main_container)
        content_frame.grid(row=2, column=0, sticky="nsew", pady=(0, 20))
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=1)
        content_frame.rowconfigure(0, weight=1)
        content_frame.rowconfigure(1, weight=1)

        # Input section
        input_frame = ttk.LabelFrame(content_frame, text="📝 Input Text", padding="15")
        input_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        input_frame.columnconfigure(0, weight=1)
        input_frame.rowconfigure(0, weight=1)

        # Modern input text area
        self.text_input = scrolledtext.ScrolledText(
            input_frame,
            height=12,
            wrap=tk.WORD,
            font=('Consolas', 11),
            bg=self.colors['surface'],
            fg=self.colors['text'],
            insertbackground=self.colors['primary'],
            selectbackground=self.colors['primary'],
            selectforeground='white',
            borderwidth=1,
            relief='solid',
            highlightthickness=0
        )
        self.text_input.grid(row=0, column=0, sticky="nsew")

        # Output section
        output_frame = ttk.LabelFrame(content_frame, text="🛡️ Anonymized Text", padding="15")
        output_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)

        # Modern output text area
        self.text_output = scrolledtext.ScrolledText(
            output_frame,
            height=12,
            wrap=tk.WORD,
            font=('Consolas', 11),
            bg=self.colors['surface'],
            fg=self.colors['text'],
            insertbackground=self.colors['primary'],
            selectbackground=self.colors['primary'],
            selectforeground='white',
            state=tk.DISABLED,  # Read-only by default
            borderwidth=1,
            relief='solid',
            highlightthickness=0
        )
        self.text_output.grid(row=0, column=0, sticky="nsew")

        # Action buttons with modern styling
        self.create_action_buttons()

        # Progress bar with modern styling
        self.progress = ttk.Progressbar(self.main_container,
                                       mode='indeterminate',
                                       style='Modern.Horizontal.TProgressbar')
        self.progress.grid(row=3, column=0, sticky="ew", pady=(0, 10))

    def create_action_buttons(self):
        """Create modern action buttons."""
        button_frame = ttk.Frame(self.main_container)
        button_frame.grid(row=4, column=0, pady=(0, 20))

        # Modern button layout with icons
        self.load_button = self.create_button(button_frame,
                                            "📁 Load File",
                                            "Secondary",
                                            self.load_file)
        self.load_button.pack(side=tk.LEFT, padx=(0, 10))

        self.clear_button = self.create_button(button_frame,
                                             "🗑️ Clear",
                                             "Secondary",
                                             self.clear_text)
        self.clear_button.pack(side=tk.LEFT, padx=(0, 10))

        self.anonymize_button = self.create_button(button_frame,
                                                 "🕵️ Anonymize",
                                                 "Primary",
                                                 self.anonymize_text)
        self.anonymize_button.pack(side=tk.LEFT, padx=(0, 10))

        self.copy_button = self.create_button(button_frame,
                                            "📋 Copy Result",
                                            "Success",
                                            self.copy_result)
        self.copy_button.pack(side=tk.LEFT, padx=(0, 10))

        self.save_button = self.create_button(button_frame,
                                            "💾 Save Result",
                                            "Secondary",
                                            self.save_result)
        self.save_button.pack(side=tk.LEFT)

    def create_status_bar(self):
        """Create a modern status bar."""
        status_frame = ttk.Frame(self.main_container, style='Modern.TFrame')
        status_frame.grid(row=5, column=0, sticky="ew")
        status_frame.columnconfigure(0, weight=1)

        self.status_label = ttk.Label(status_frame,
                                    text="✅ Ready to anonymize",
                                    style='Success.TLabel')
        self.status_label.grid(row=0, column=0, sticky="w")

        # Add timestamp
        timestamp_label = ttk.Label(status_frame,
                                  text=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                  style='Modern.TLabel')
        timestamp_label.grid(row=0, column=1, sticky="e")

    def bind_shortcuts(self):
        """Bind keyboard shortcuts for better UX."""
        self.root.bind('<Control-Return>', lambda e: self.anonymize_text())
        self.root.bind('<Control-o>', lambda e: self.load_file())
        self.root.bind('<Control-s>', lambda e: self.save_result())
        self.root.bind('<Control-c>', lambda e: self.copy_result())
        self.root.bind('<Control-l>', lambda e: self.clear_text())
        self.root.bind('<Control-a>', lambda e: self.select_all_text())

    def select_all_text(self):
        """Select all text in the input area."""
        self.text_input.tag_add(tk.SEL, "1.0", tk.END)
        self.text_input.mark_set(tk.INSERT, "1.0")
        self.text_input.see(tk.INSERT)
        return 'break'

    def add_always_redact_word(self):
        """Add a word to the secure always redact list with modern feedback."""
        word = self.add_word_entry.get().strip()
        if word:
            if add_always_redact_word(word):
                self.add_word_entry.delete(0, tk.END)
                self.show_status_message(f"✅ Added '{word}' to always redact list", 'success')
            else:
                self.show_status_message(f"⚠️ '{word}' is already in the list", 'warning')
        else:
            self.show_status_message("⚠️ Please enter a word to add", 'warning')

    def remove_always_redact_word(self):
        """Remove a word from the secure always redact list with modern feedback."""
        word = self.remove_word_entry.get().strip()
        if word:
            if remove_always_redact_word(word):
                self.remove_word_entry.delete(0, tk.END)
                self.show_status_message(f"🗑️ Removed '{word}' from always redact list", 'success')
            else:
                self.show_status_message(f"⚠️ '{word}' not found in always redact list", 'warning')
        else:
            self.show_status_message("⚠️ Please enter a word to remove", 'warning')

    def show_status_message(self, message, message_type='info'):
        """Show a status message with appropriate styling."""
        if message_type == 'success':
            self.status_label.config(text=message, style='Success.TLabel')
        elif message_type == 'error':
            self.status_label.config(text=message, style='Error.TLabel')
        elif message_type == 'warning':
            self.status_label.config(text=message, style='Error.TLabel')
        else:
            self.status_label.config(text=message, style='Modern.TLabel')

    def load_file(self):
        """Load text from a file with modern error handling."""
        file_path = filedialog.askopenfilename(
            title="📁 Select text file",
            filetypes=[
                ("Text files", "*.txt"),
                ("All files", "*.*"),
                ("Markdown files", "*.md"),
                ("Word documents", "*.docx")
            ]
        )

        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    self.text_input.delete(1.0, tk.END)
                    self.text_input.insert(1.0, content)
                    self.show_status_message(f"📁 Loaded: {os.path.basename(file_path)}", 'success')
            except Exception as e:
                messagebox.showerror("❌ Error", f"Failed to load file:\n{str(e)}")
                self.show_status_message("❌ Failed to load file", 'error')

    def clear_text(self):
        """Clear both input and output text areas with confirmation."""
        if self.text_input.get(1.0, tk.END).strip():
            if messagebox.askyesno("🗑️ Clear Text", "Are you sure you want to clear all text?"):
                self.text_input.delete(1.0, tk.END)
                self.text_output.config(state=tk.NORMAL)
                self.text_output.delete(1.0, tk.END)
                self.text_output.config(state=tk.DISABLED)
                self.copy_button.config(state='disabled')
                self.save_button.config(state='disabled')
                self.show_status_message("🗑️ Text cleared", 'success')
        else:
            self.show_status_message("ℹ️ No text to clear", 'info')

    def anonymize_text(self):
        """Anonymize the input text with modern progress indication."""
        input_text = self.text_input.get(1.0, tk.END).strip()

        if not input_text:
            messagebox.showwarning("⚠️ Warning", "Please enter some text to anonymize.")
            if self.test_mode:
                self.show_status_message("⚠️ Please enter some text to anonymize.", 'warning')
            return

        # Disable buttons during processing
        self.anonymize_button.config(state='disabled')
        self.progress.start()
        self.show_status_message("🔄 Anonymizing text...", 'info')

        if self.test_mode:
            # Run synchronously for tests
            self._process_anonymization(input_text)
        else:
            # Start processing in a separate thread
            thread = threading.Thread(target=self._process_anonymization, args=(input_text,))
            thread.daemon = True
            thread.start()

    def _process_anonymization(self, input_text):
        """Process anonymization in a separate thread or synchronously in test mode."""
        try:
            # Perform redaction (now includes always redact words from secure storage)
            result = redact(input_text)
            result_text = result.text

            # Send result back to main thread
            if self.test_mode:
                self.text_output.config(state=tk.NORMAL)
                self.text_output.delete(1.0, tk.END)
                self.text_output.insert(1.0, result_text)
                self.text_output.config(state=tk.DISABLED)
                self.show_status_message(f"✅ Anonymization complete! {len(result.mapping)} entities redacted", 'success')
                self.anonymize_button.config(state='normal')
                self.progress.stop()
            else:
                self.message_queue.put(('success', result_text, len(result.mapping)))

        except Exception as e:
            if self.test_mode:
                self.show_status_message("❌ Anonymization failed", 'error')
                self.anonymize_button.config(state='normal')
                self.progress.stop()
            else:
                self.message_queue.put(('error', str(e)))

    def check_queue(self):
        """Check for messages from the processing thread."""
        try:
            while True:
                message_type, *args = self.message_queue.get_nowait()

                if message_type == 'success':
                    result_text, entity_count = args
                    self.text_output.config(state=tk.NORMAL)
                    self.text_output.delete(1.0, tk.END)
                    self.text_output.insert(1.0, result_text)
                    self.text_output.config(state=tk.DISABLED)

                elif message_type == 'error':
                    error_msg = args[0]
                    messagebox.showerror("❌ Error", f"Anonymization failed:\n{error_msg}")
                    self.show_status_message("❌ Anonymization failed", 'error')

                # Re-enable buttons
                self.anonymize_button.config(state='normal')
                self.progress.stop()

        except queue.Empty:
            pass

        self.root.after(100, self.check_queue)

    def copy_result(self):
        """Copy the anonymized result to clipboard with modern feedback."""
        result_text = self.text_output.get(1.0, tk.END).strip()
        if result_text:
            self.root.clipboard_clear()
            self.root.clipboard_append(result_text)
            self.show_status_message("📋 Result copied to clipboard", 'success')
        else:
            self.show_status_message("⚠️ No result to copy", 'warning')

    def save_result(self):
        """Save the anonymized result to a file with modern file dialog."""
        result_text = self.text_output.get(1.0, tk.END).strip()
        if not result_text:
            messagebox.showwarning("⚠️ Warning", "No result to save.")
            return

        file_path = filedialog.asksaveasfilename(
            title="💾 Save Anonymized Text",
            defaultextension=".txt",
            filetypes=[
                ("Text files", "*.txt"),
                ("All files", "*.*"),
                ("Markdown files", "*.md")
            ]
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(result_text)
                self.show_status_message(f"💾 Saved to: {os.path.basename(file_path)}", 'success')
            except Exception as e:
                messagebox.showerror("❌ Error", f"Failed to save file:\n{str(e)}")
                self.show_status_message("❌ Failed to save file", 'error')


def main():
    """Main function to launch the modern GUI."""
    root = tk.Tk()

    # Set proper application name for dock/taskbar
    root.wm_title("🕵️ Anon - Privacy-First Text Anonymizer")

    # On macOS, set the application name properly
    try:
        import platform
        if platform.system() == 'Darwin':
            # Set the application name for macOS dock
            root.createcommand('tk::mac::Quit', root.quit)
            root.createcommand('tk::mac::OnHide', lambda: None)
            root.createcommand('tk::mac::ShowPreferences', lambda: None)
            root.createcommand('tk::mac::ShowAbout', lambda: None)
            root.createcommand('tk::mac::ReopenApplication', lambda: None)
    except Exception:
        pass

    ModernAnonymizerGUI(root)

    # Center the window on screen
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")

    root.mainloop()


if __name__ == "__main__":
    main()