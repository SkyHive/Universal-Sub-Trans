import os
import platform
import sys

from backend.services.logger import logger


class PlatformManager:
    """
    Handles platform-specific environmental setups and library paths.
    """

    @staticmethod
    def get_app_root() -> str:
        """Returns the absolute path to the application root."""
        if getattr(sys, "frozen", False):
            # If running as a bundled executable (PyInstaller)
            return os.path.dirname(sys.executable)
        return os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )

    @staticmethod
    def setup_runtime_env() -> None:
        """
        Detects the current platform and sets up necessary library search paths.
        """
        from backend.services.dep_mgr import dep_mgr
        from backend.services.hardware_mgr import hardware_mgr

        current_os = platform.system().lower()
        arch = platform.machine().lower()
        if arch == "amd64":
            arch = "x86_64"  # Standardize

        lib_path = dep_mgr.get_lib_dir()

        # 1. Hardware Detection
        vendor = hardware_mgr.detect_gpu_vendor()
        logger.info(f"detected_hardware: OS={current_os}, Arch={arch}, GPU={vendor}")

        # 2. Dependency Check & Initialization (NVIDIA GPUs)
        if vendor == "nvidia":
            if dep_mgr.check_missing_deps():
                logger.warning(
                    f"missing_cuda_dependencies on {current_os}: GPU acceleration might not be available until installed."
                )
            elif os.path.exists(lib_path):
                try:
                    # Convert to absolute path to handle UNC/WSL paths better
                    abs_lib_path = os.path.abspath(lib_path)

                    if current_os == "windows":
                        logger.info(f"attempting_to_load_dlls_from: {abs_lib_path}")

                        # Python 3.8+ requires os.add_dll_directory
                        if hasattr(os, "add_dll_directory"):
                            try:
                                # We store the handle to prevent it from being garbage collected
                                # (though not strictly necessary in most cases, helps in some envs)
                                os.add_dll_directory(abs_lib_path)
                                logger.info("os_add_dll_directory_success")
                            except Exception as dl_err:
                                logger.error(f"os_add_dll_directory_failed: {dl_err}")

                        # Set PATH as fallback and for child processes
                        os.environ["PATH"] = (
                            abs_lib_path + os.pathsep + os.environ["PATH"]
                        )

                        # Special hint for some versions of CTranslate2 / cuDNN
                        # cuDNN 9 is modular, sometimes it needs to be told where its siblings are
                        os.environ["CUDA_PATH"] = abs_lib_path

                    elif current_os == "linux":
                        # Add to LD_LIBRARY_PATH
                        old_ld_path = os.environ.get("LD_LIBRARY_PATH", "")
                        os.environ["LD_LIBRARY_PATH"] = abs_lib_path + (
                            os.pathsep + old_ld_path if old_ld_path else ""
                        )

                    logger.info(f"initialized_cuda_runtime_from: {abs_lib_path}")
                except Exception as e:
                    logger.error(f"failed_to_initialize_gpu_env: {e}")

        # 3. Generic setup (Mac/Other)
        if current_os == "darwin":
            # Add Mac specific setup if needed (e.g., CoreML paths)
            pass

    @staticmethod
    def is_gpu_available() -> bool:
        """
        Placeholder for a unified GPU check.
        """
        # This can be expanded later to check for CUDA (NVIDIA) or CoreML (Mac)
        return False


platform_mgr = PlatformManager()
