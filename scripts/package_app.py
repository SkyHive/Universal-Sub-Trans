import os
import platform
import shutil
import subprocess
import sys


def run_command(cmd, cwd=None):
    print(f"Executing: {cmd}")
    try:
        subprocess.check_call(cmd, shell=True, cwd=cwd)
    except subprocess.CalledProcessError as e:
        print(f"Error during command: {cmd}")
        sys.exit(e.returncode)


def get_version():
    """Determines the version from GITHUB_REF_NAME or pyproject.toml."""
    # 1. Check CI environment (Targeted for Tags)
    ci_version = os.environ.get("GITHUB_REF_NAME")
    if ci_version and ci_version.startswith("v"):
        version = ci_version[1:]  # v0.1.0 -> 0.1.0
        print(f"Detected version from CI Tag: {version}")
        # Sync to version.py
        update_version_file(version)
        return version

    # 2. Fallback to pyproject.toml
    try:
        with open("pyproject.toml", "r", encoding="utf-8") as f:
            for line in f:
                if line.strip().startswith("version = "):
                    version = line.split("=")[1].strip().strip('"')
                    print(f"Detected version from pyproject.toml: {version}")
                    return version
    except Exception as e:
        print(f"Error reading pyproject.toml: {e}")

    return "0.1.0"


def update_version_file(version):
    """Updates backend/core/version.py with the current build version."""
    version_file = os.path.join("backend", "core", "version.py")
    try:
        with open(version_file, "w", encoding="utf-8") as f:
            f.write(f'VERSION = "{version}"\n')
        print(f"Updated {version_file} to {version}")
    except Exception as e:
        print(f"Error updating version file: {e}")


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


def package_app(version="0.1.0"):
    print(f"--- Packaging with Nuitka (v{version}) ---")

    is_windows = platform.system().lower() == "windows"

    # Base command
    # We use sys.executable to ensure Nuitka uses the current virtual environment's python
    cmd = [
        f'"{sys.executable}" -m nuitka',
        "--standalone",
        "--show-progress",
        "--assume-yes-for-downloads",
        "--plugin-enable=pywebview",
        (
            "--plugin-enable=gi" if not is_windows else ""
        ),  # Helps with GTK/GObject dependencies on Linux
        # Force include packages that Nuitka might miss due to dynamic imports
        "--include-package=appdirs",
        "--include-package=pythonjsonlogger",
        "--include-package=ctranslate2",
        "--include-package=faster_whisper",
        "--include-package=pydantic",
        "--include-package=pydantic_settings",
        "--include-package=openai",
        "--include-package=httpx",
        "--include-package=onnxruntime",  # Critical for VAD
        "--nofollow-import-to=sympy",  # Fixes MSVC out of heap space error
        "--nofollow-import-to=IPython",  # Not needed in runtime, very heavy
        "--nofollow-import-to=setuptools", # Not needed in runtime
        "--plugin-enable=anti-bloat",  # Automatic removal of bloat code (numpy, etc)
        "--low-memory",  # Helpful for CI environments
        # Include data files for frontend and resources
        "--include-data-dir=backend/dist=backend/dist",
    ]

    # VAD Model handling: faster-whisper needs the silero_vad onnx file
    try:
        import faster_whisper

        fw_path = os.path.dirname(faster_whisper.__file__)
        vad_model_path = os.path.join(fw_path, "assets", "silero_vad_v6.onnx")
        if os.path.exists(vad_model_path):
            # Tell Nuitka to put it in faster_whisper/assets/ in the distribution
            cmd.append(
                f'--include-data-file="{vad_model_path}"=faster_whisper/assets/silero_vad_v6.onnx'
            )
            print(f"Including VAD model: {vad_model_path}")
        else:
            print(f"Warning: VAD model not found at {vad_model_path}")
    except ImportError:
        print(
            "Warning: faster_whisper not found in current environment, skipping VAD model inclusion."
        )

    # Icon handling
    icon_path = "resources/icon.ico"
    if not os.path.exists(icon_path):
        icon_path = "icon.ico"

    if os.path.exists(icon_path) and is_windows:
        cmd.append(f"--windows-icon-from-ico={icon_path}")

    # Optimized Windows-specific flags
    if is_windows:
        # Windows metadata requires X.X.X.X format
        win_version = version
        while win_version.count(".") < 3:
            win_version += ".0"

        cmd.append("--windows-console-mode=disable")  # Hide console for GUI
        cmd.append(f"--windows-product-version={win_version}")
        cmd.append(f"--windows-file-version={win_version}")
        cmd.append('--windows-company-name="SkyHive"')
        cmd.append('--windows-product-name="UniSub"')
        # cmd.append("--onefile") # Uncomment if you want a single .exe
    else:
        # On Linux, PyQt6 is often needed as a backend for pywebview
        cmd.append("--plugin-enable=pyqt6")

    # If resources directory exists and has content (ignoring hidden files)
    if os.path.exists("resources"):
        has_data = any(not f.startswith(".") for f in os.listdir("resources"))
        if has_data:
            cmd.append("--include-data-dir=resources=resources")

    cmd.append("main.py")

    # Filter out empty strings
    cmd = [c for c in cmd if c]

    full_cmd = " ".join(cmd)
    run_command(full_cmd)

    if is_windows:
        create_windows_installer(
            "main.dist",
            version,
            icon_path if os.path.exists(icon_path) else None,
        )


def create_windows_installer(dist_dir, version, icon_path=None):
    print(f"--- Creating Windows Installer (v{version}) ---")
    if not os.path.exists(dist_dir):
        print(f"Error: Distribution directory {dist_dir} not found.")
        return

    setup_icon_line = f"SetupIconFile={icon_path}" if icon_path else ""

    iss_template = f"""
[Setup]
AppName=Universal Subtitle Translator
AppVersion={version}
DefaultDirName={{autopf}}\\UniSub
DefaultGroupName=UniSub
UninstallDisplayIcon={{app}}\\main.exe
Compression=lzma2
SolidCompression=yes
OutputDir=.
OutputBaseFilename=UniSub_Setup_v{version}
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

[Code]
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usPostUninstall then
  begin
    if MsgBox('是否删除本地日志文件 (Logs)?', mbConfirmation, MB_YESNO) = IDYES then
    begin
      DelTree(ExpandConstant('{{localappdata}}\\UniversalSub\\UniversalSub\\Logs'), True, True, True);
    end;
    if MsgBox('是否删除下载的 GPU 依赖包和模型 (Libs)?', mbConfirmation, MB_YESNO) = IDYES then
    begin
      DelTree(ExpandConstant('{{localappdata}}\\UniversalSub\\UniversalSub\\libs'), True, True, True);
    end;
    if MsgBox('是否删除用户配置文件 (Settings)?', mbConfirmation, MB_YESNO) = IDYES then
    begin
      DeleteFile(ExpandConstant('{{localappdata}}\\UniversalSub\\UniversalSub\\config.json'));
      // 尝试清理空目录
      RemoveDir(ExpandConstant('{{localappdata}}\\UniversalSub\\UniversalSub'));
      RemoveDir(ExpandConstant('{{localappdata}}\\UniversalSub'));
    end;
  end;
end;
"""
    iss_file = "unisub_setup.iss"
    with open(iss_file, "w", encoding="utf-8") as f:
        f.write(iss_template)

    print(f"Inno Setup script generated: {iss_file}")

    # Try to run ISCC (Inno Setup Compiler)
    # Common paths for ISCC
    iscc_paths = [
        "iscc",  # If in PATH
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
        print(
            "Warning: Inno Setup Compiler (ISCC.exe) not found. Please install it to build the installer."
        )
        print(f"You can still manualy compile {iss_file} using the Inno Setup GUI.")


if __name__ == "__main__":
    version = get_version()
    build_frontend()
    package_app(version)
    print("\n--- Packaging Complete ---")
    if platform.system().lower() == "windows":
        print("Resulting exe can be found in 'main.dist/'")
        print("Installer (if compiled) can be found in the current directory.")
    else:
        print("Resulting binary can be found in 'main.dist/'")
        print(
            "Tip: To build a Windows .exe, you MUST run this script on a Windows machine."
        )
