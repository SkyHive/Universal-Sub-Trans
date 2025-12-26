import subprocess
import platform
import os
from backend.services.logger import logger

class HardwareManager:
    """
    Service for detecting system hardware capabilities, specifically GPUs.
    """

    def detect_gpu_vendor(self) -> str:
        """
        Detects the GPU vendor.
        Returns: 'nvidia', 'amd', 'intel', or 'unknown'.
        """
        system = platform.system().lower()
        
        try:
            if system == "windows":
                return self._detect_windows_gpu()
            elif system == "linux":
                return self._detect_linux_gpu()
            elif system == "darwin":
                return "apple"  # Metal / M-series
        except Exception as e:
            logger.error(f"gpu_detection_failed: {e}")
            
        return "unknown"

    def _detect_windows_gpu(self) -> str:
        """Helper to detect GPU on Windows using wmic."""
        # Use a list to avoid shell=True, and set cwd to a safe path if we are on a UNC path
        cmd = ["wmic", "path", "win32_videocontroller", "get", "name"]
        try:
            startupinfo = None
            if platform.system().lower() == "windows":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE

            # We explicitly set cwd to a safe local directory to avoid CMD UNC path warnings
            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, cwd="C:\\", startupinfo=startupinfo).decode("utf-8").lower()
            
            if "nvidia" in output:
                return "nvidia"
            if "amd" in output or "radeon" in output:
                return "amd"
            if "intel" in output:
                return "intel"
        except Exception as e:
            logger.error(f"windows_gpu_detection_subprocess_failed: {e}")
        return "unknown"

    def _detect_linux_gpu(self) -> str:
        """Helper to detect GPU on Linux using lspci."""
        try:
            output = subprocess.check_output("lspci | grep -i vga", shell=True).decode("utf-8").lower()
            if "nvidia" in output:
                return "nvidia"
            if "amd" in output or "ati" in output:
                return "amd"
            if "intel" in output:
                return "intel"
        except subprocess.CalledProcessError:
            pass
        return "unknown"

    def is_cuda_available(self) -> bool:
        """Quick check if there is an NVIDIA GPU."""
        return self.detect_gpu_vendor() == "nvidia"

hardware_mgr = HardwareManager()
