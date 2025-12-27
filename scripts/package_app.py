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
        "--plugin-enable=gi" if not is_windows else "", # Helps with GTK/GObject dependencies on Linux
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

    # Icon handling
    icon_path = "resources/icon.ico"
    if not os.path.exists(icon_path):
        icon_path = "icon.ico"
    
    if os.path.exists(icon_path) and is_windows:
        cmd.append(f"--windows-icon-from-ico={icon_path}")

    # Optimized Windows-specific flags
    if is_windows:
        cmd.append("--windows-console-mode=disable") # Hide console for GUI
        # cmd.append("--onefile") # Uncomment if you want a single .exe
    else:
        # On Linux, PyQt6 is often needed as a backend for pywebview
        cmd.append("--plugin-enable=pyqt6")

    # If resources directory exists and has content (ignoring hidden files)
    if os.path.exists("resources"):
        has_data = any(not f.startswith('.') for f in os.listdir("resources"))
        if has_data:
            cmd.append("--include-data-dir=resources=resources")

    cmd.append("main.py")
    
    # Filter out empty strings
    cmd = [c for c in cmd if c]
    
    full_cmd = " ".join(cmd)
    run_command(full_cmd)
    
    if is_windows:
        create_windows_installer("main.dist", icon_path if os.path.exists(icon_path) else None)

def create_windows_installer(dist_dir, icon_path=None):
    print("--- Creating Windows Installer ---")
    if not os.path.exists(dist_dir):
        print(f"Error: Distribution directory {dist_dir} not found.")
        return

    setup_icon_line = f"SetupIconFile={icon_path}" if icon_path else ""

    iss_template = f"""
[Setup]
AppName=Universal Subtitle Translator
AppVersion=0.1.0
DefaultDirName={{autopf}}\\UniSub
DefaultGroupName=UniSub
UninstallDisplayIcon={{app}}\\main.exe
Compression=lzma2
SolidCompression=yes
OutputDir=.
OutputBaseFilename=UniSub_Setup_v0.1.0
{setup_icon_line}

[Tasks]
Name: "desktopicon"; Description: "{{cm:CreateDesktopIcon}}"; GroupDescription: "{{cm:AdditionalIcons}}"; Flags: unchecked

[Files]
; IMPORTANT: Permissions: users-modify allows the app to download dependencies to its own folder (libs)
Source: "{dist_dir}\\*"; DestDir: "{{app}}"; Flags: ignoreversion recursesubdirs createallsubdirs; Permissions: users-modify
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{{group}}\\Universal Subtitle Translator"; Filename: "{{app}}\\main.exe"
Name: "{{userdesktop}}\\Universal Subtitle Translator"; Filename: "{{app}}\\main.exe"; Tasks: desktopicon

[Run]
Filename: "{{app}}\\main.exe"; Description: "{{cm:LaunchProgram,Universal Subtitle Translator}}"; Flags: nowait postinstall skipifsilent
"""
    iss_file = "unisub_setup.iss"
    with open(iss_file, "w", encoding="utf-8") as f:
        f.write(iss_template)
    
    print(f"Inno Setup script generated: {iss_file}")
    
    # Try to run ISCC (Inno Setup Compiler)
    # Common paths for ISCC
    iscc_paths = [
        "iscc", # If in PATH
        r"C:\\Program Files (x86)\\Inno Setup 6\\ISCC.exe",
        r"C:\\Program Files\\Inno Setup 6\\ISCC.exe",
    ]
    
    compiler = None
    for path in iscc_paths:
        if shutil.which(path) or os.path.exists(path):
            compiler = path
            break
            
    if compiler:
        print(f"Found Inno Setup Compiler: {compiler}")
        run_command(f'"{compiler}" {iss_file}')
        print("Installer created successfully!")
    else:
        print("Warning: Inno Setup Compiler (ISCC.exe) not found. Please install it to build the installer.")
        print(f"You can still manualy compile {iss_file} using the Inno Setup GUI.")

if __name__ == "__main__":
    build_frontend()
    package_app()
    print("\n--- Packaging Complete ---")
    if platform.system().lower() == "windows":
        print("Resulting exe can be found in 'main.dist/'")
        print("Installer (if compiled) can be found in the current directory.")
    else:
        print("Resulting binary can be found in 'main.dist/'")
        print("Tip: To build a Windows .exe, you MUST run this script on a Windows machine.")
