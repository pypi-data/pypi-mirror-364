import threading
import webbrowser
import time
import logging
import os
import subprocess
import sys

from flask import Flask, send_from_directory

# Suppress Flask's default startup messages by targeting the 'werkzeug' logger
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

class HtmlRunner:
    """
    A callable class to serve local HTML files and open them in a browser.
    """
    def __init__(self):
        """Initializes the runner with default settings."""
        self.port = 5000
        self.filename = 'index.html'
        self.filepath = '.'

    def __call__(self, port=None, filename=None, filepath=None):
        """
        Starts the Flask server in a background thread and opens the browser.
        """
        run_port = port if port is not None else self.port
        run_filename = filename if filename is not None else self.filename
        run_filepath = filepath if filepath is not None else self.filepath

        abs_filepath = os.path.abspath(run_filepath)
        full_path = os.path.join(abs_filepath, run_filename)

        if not os.path.exists(full_path):
            print(f"❌ Error: The file '{run_filename}' was not found in the directory '{abs_filepath}'.")
            return

        app = Flask(__name__)

        @app.route('/')
        def serve_index():
            return send_from_directory(abs_filepath, run_filename)

        @app.route('/<path:asset_path>')
        def serve_static(asset_path):
            return send_from_directory(abs_filepath, asset_path)

        def run_app():
            # --- WORKAROUND TO HIDE BANNER ---
            original_stdout = sys.stdout
            original_stderr = sys.stderr
            sys.stdout = open(os.devnull, 'w')
            sys.stderr = open(os.devnull, 'w')

            try:
                app.run(host='0.0.0.0', port=run_port)
            finally:
                sys.stdout.close()
                sys.stderr.close()
                sys.stdout = original_stdout
                sys.stderr = original_stderr
            # --- END WORKAROUND ---

        # --- REORDERED LOGIC ---
        # 1. Print messages first
        print(f"code is running on port {run_port} and link is localhost:{run_port}")
        print("opening browser...")

        # 2. Start the server thread
        server_thread = threading.Thread(target=run_app)
        server_thread.daemon = True
        server_thread.start()
        
        # 3. Wait and open the browser
        time.sleep(1)

        if 'TERMUX_VERSION' in os.environ:
            subprocess.run(["termux-open", f"http://localhost:{run_port}"])
        else:
            webbrowser.open(f"http://localhost:{run_port}")
        # --- END REORDERED LOGIC ---
        
        # Keep the main script alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down server.")
