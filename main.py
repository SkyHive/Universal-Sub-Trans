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

    # 3. Determine URL with robust path resolution
    if dev_mode:
        url = "http://localhost:5173"
    else:
        # Determine executable directory
        executable_dir = os.path.dirname(os.path.abspath(sys.executable))
        
        # For Nuitka standalone, assets are in the same folder as the bin
        url = os.path.join(executable_dir, "backend", "dist", "index.html")
        
        # Fallback if run from dev or different structure
        if not os.path.exists(url):
            url = os.path.join(os.getcwd(), "backend", "dist", "index.html")
        
        # Convert to absolute file:// URL for webview
        url = "file://" + os.path.abspath(url).replace("\\", "/")
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
    )

    bridge.set_window(window)
    webview.start(debug=dev_mode)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.critical(f"Unhandled exception in main: {e}", exc_info=True)
        sys.exit(1)
