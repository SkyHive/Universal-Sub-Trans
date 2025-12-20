import os
import sys
import webview
from backend.api.bridge import ApiBridge
from backend.services.logger import logger

def main() -> None:
    """
    Main entry point for the Universal-Sub-Trans application.
    """
    logger.info("Application starting...")

    # Initialize bridge
    bridge = ApiBridge()

    # Determine URL
    # In development, use Vite dev server
    # In production, use built index.html
    dev_mode = os.environ.get("DEV_MODE", "true").lower() == "true"
    
    if dev_mode:
        url = "http://localhost:5173"
    else:
        # Path to production build
        base_path = getattr(sys, "_MEIPASS", os.getcwd())
        url = os.path.join(base_path, "backend", "dist", "index.html")

    # Create window
    window = webview.create_window(
        title="Universal Subtitle Translator",
        url=url,
        js_api=bridge,
        width=1024,
        height=768,
        min_size=(800, 600),
        background_color="#000000",
        frameless=True,    # Remove OS title bar
        easy_drag=False    # We will handle drag via CSS/JS
    )

    # Inject window instance into bridge
    bridge.set_window(window)

    # Start webview
    # Note: debug=True allows right-click inspect in dev mode
    webview.start(debug=dev_mode)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.critical(f"Unhandled exception in main: {e}", exc_info=True)
        sys.exit(1)
