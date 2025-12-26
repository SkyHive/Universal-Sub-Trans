import os
import shutil
import subprocess
import sys
import platform

def run_command(cmd, cwd=None):
    print(f"Executing: {cmd}")
    try:
        subprocess.check_call(cmd, shell=True, cwd=cwd)
    except subprocess.CalledProcessError as e:
        print(f"Error during command: {cmd}")
        sys.exit(e.returncode)

def build_frontend():
    print("--- Building Frontend ---")
    frontend_dir = os.path.abspath("frontend")
    if os.path.exists(os.path.join(frontend_dir, "node_modules")):
        run_command("npm run build", cwd=frontend_dir)
    else:
        print("node_modules not found, running npm install...")
        run_command("npm install && npm run build", cwd=frontend_dir)
    
    # Verification: vite is configured to output to ../backend/dist
    dest_dist = os.path.join(os.getcwd(), "backend", "dist")
    if not os.path.exists(dest_dist):
        print(f"Error: Build completed but {dest_dist} was not found.")
        sys.exit(1)
    
    print(f"Frontend build verified in: {dest_dist}")

def package_app():
    print("--- Packaging with Nuitka ---")
    
    is_windows = platform.system().lower() == "windows"
    
    # Base command
    # We use 'uv run' to ensure Nuitka uses the project's virtual environment
    cmd = [
        "uv run python -m nuitka",
        "--standalone",
        "--show-progress",
        "--plugin-enable=pywebview",
        "--plugin-enable=pyqt6", # Correct plugin name for PyQt6
        "--plugin-enable=gi",    # Helps with GTK/GObject dependencies on Linux
        # Force include packages that Nuitka might miss due to dynamic imports
        "--include-package=appdirs",
        "--include-package=pythonjsonlogger",
        "--include-package=ctranslate2",
        "--include-package=faster_whisper",
        "--include-package=pydantic",
        "--include-package=pydantic_settings",
        "--include-package=openai",
        "--include-package=httpx",
        # Include data files for frontend and resources
        "--include-data-dir=backend/dist=backend/dist",
    ]

    # If resources directory exists and has content (ignoring hidden files)
    if os.path.exists("resources"):
        has_data = any(not f.startswith('.') for f in os.listdir("resources"))
        if has_data:
            cmd.append("--include-data-dir=resources=resources")

    if is_windows:
        cmd.append("--windows-console-mode=disable") # Hide console for GUI
        # cmd.append("--onefile") # Uncomment if you want a single .exe (slower startup)

    cmd.append("main.py")
    
    full_cmd = " ".join(cmd)
    run_command(full_cmd)

if __name__ == "__main__":
    build_frontend()
    package_app()
    print("\n--- Packaging Complete ---")
    if platform.system().lower() == "windows":
        print("Resulting exe can be found in 'main.dist/'")
    else:
        print("Resulting binary can be found in 'main.dist/'")
        print("Tip: To build a Windows .exe, you MUST run this script on a Windows machine.")
