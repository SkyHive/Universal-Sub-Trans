import os
import sys
import platform
import webview
from backend.services.platform_mgr import platform_mgr
from backend.services.logger import logger

def main() -> None:
    """
    Main entry point for the Universal-Sub-Trans application.
    """
    # 1. Platform Flags for stability in packaged environment
    current_os = platform.system().lower()
    
    # Smart detection: Default to false if compiled, or use DEV_MODE env var
    is_compiled = hasattr(sys, "frozen") or "__compiled__" in globals()
    dev_mode = os.environ.get("DEV_MODE", str(not is_compiled)).lower() == "true"
    
    if not dev_mode:
        if current_os == "linux":
            # Force X11 to avoid Wayland/Vulkan segfaults in some environments (WSL/Old distros)
            os.environ["QT_QPA_PLATFORM"] = "xcb"
            # Disable GPU for WebEngine in packaged mode as it's a common cause of crashes
            os.environ["QTWEBENGINE_DISABLE_GPU"] = "1"
        
        # Allow child processes for WebEngine
        os.environ["QTWEBENGINE_DISABLE_SANDBOX"] = "1"

    # 2. Setup cross-platform runtime environment
    platform_mgr.setup_runtime_env()
    logger.info("Application starting...")

    # Initialize bridge
    from backend.api.bridge import ApiBridge
    bridge = ApiBridge()

    # 3. Determine URL with robust resolution
    if dev_mode:
        url = "http://localhost:5173"
    else:
        # Production: Start a local HTTP server to serve static files
        # This fixes 404 errors and protocol restrictions (file://)
        import http.server
        import socketserver
        import threading
        
        # Determine executable directory
        executable_dir = os.path.dirname(os.path.abspath(sys.executable))
        dist_dir = os.path.join(executable_dir, "backend", "dist")
        if not os.path.exists(dist_dir):
            dist_dir = os.path.join(os.getcwd(), "backend", "dist")
        
        if not os.path.exists(dist_dir):
             # Fallback if directory missing
             logger.error(f"frontend_dist_not_found: {dist_dir}")
             url = "about:blank"
        else:
            class Handler(http.server.SimpleHTTPRequestHandler):
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, directory=dist_dir, **kwargs)
                def log_message(self, format, *args):
                    # Suppress standard server logs to avoid cluttering app logs
                    pass

            def start_server():
                # Use port 0 to find a free port
                with socketserver.TCPServer(("127.0.0.1", 0), Handler) as httpd:
                    self_address = httpd.server_address
                    self.server_port = self_address[1]
                    logger.info(f"serving_frontend_at: http://127.0.0.1:{self.server_port}")
                    httpd.serve_forever()

            # We need a way to get the port back to the main thread
            class ServerState:
                server_port = 0
            
            state = ServerState()
            
            def start_server_wrapper(state):
                try:
                    with socketserver.TCPServer(("127.0.0.1", 0), Handler) as httpd:
                        state.server_port = httpd.server_address[1]
                        httpd.serve_forever()
                except Exception as e:
                    logger.error(f"local_server_failed: {e}")

            server_thread = threading.Thread(target=start_server_wrapper, args=(state,), daemon=True)
            server_thread.start()
            
            # Wait for port to be assigned
            import time
            for _ in range(50):
                if state.server_port != 0: break
                time.sleep(0.1)
                
            url = f"http://127.0.0.1:{state.server_port}"
            logger.info(f"loading_production_ui: {url}")

    # 4. Create window
    window = webview.create_window(
        title="UniSub - Universal Subtitle Translator",
        url=url,
        js_api=bridge,
        width=1024,
        height=768,
        min_size=(800, 600),
        background_color="#000000",
        frameless=True,
        resizable=True, # Optimization 2: Enable resizing
        easy_drag=False,
    )

    bridge.set_window(window)
    webview.start(debug=dev_mode)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.critical(f"Unhandled exception in main: {e}", exc_info=True)
        sys.exit(1)
