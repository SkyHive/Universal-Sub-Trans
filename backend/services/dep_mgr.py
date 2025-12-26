import os
import zipfile
import urllib.request
import json
import platform
from typing import Callable, Optional, List, Dict
from backend.services.logger import logger
from backend.services.platform_mgr import platform_mgr

class DependencyManager:
    """
    Manages dependencies by "Precision Peeling" from official PyPI wheels.
    This ensures we use official NVIDIA binaries without manual management.
    """

    # Packages and their representative files to check if they are already installed
    # For Windows: .dll, For Linux: .so
    PACKAGE_CHECKS = {
        "nvidia-cudnn-cu12": ["cudnn_ops64_9.dll", "libcudnn_ops.so.9"],
        "nvidia-cublas-cu12": ["cublas64_12.dll", "libcublas.so.12"]
    }
    PYPI_PACKAGES = ["nvidia-cudnn-cu12", "nvidia-cublas-cu12"]

    def get_lib_dir(self) -> str:
        """Returns the platform-specific library directory."""
        current_os = platform.system().lower()
        arch = platform.machine().lower()
        if arch == "amd64": arch = "x86_64"
        
        root = platform_mgr.get_app_root()
        return os.path.join(root, "resources", "libs", f"{current_os}-{arch}")

    def check_missing_deps(self) -> bool:
        """
        Checks if the required cuDNN and cuBLAS libraries exist.
        Checks both the local lib directory and the system environment.
        """
        current_os = platform.system().lower()
        if current_os not in ["windows", "linux"]:
            return False

        lib_dir = self.get_lib_dir()
        
        # 1. Check local lib directory
        missing_locally = False
        ext = ".dll" if current_os == "windows" else ".so"
        
        if not os.path.exists(lib_dir):
            missing_locally = True
        else:
            try:
                local_files = os.listdir(lib_dir)
                for pkg, check_files in self.PACKAGE_CHECKS.items():
                    # Filter check files by extension for the current OS
                    os_files = [f for f in check_files if f.endswith(ext)]
                    for fname in os_files:
                        # For Linux, match prefix (e.g., libcublas.so matches libcublas.so.12)
                        prefix = fname.split('.so')[0] if current_os == "linux" else fname
                        if not any(f.startswith(prefix) for f in local_files):
                            missing_locally = True
                            break
                    if missing_locally: break
            except Exception as e:
                logger.error(f"failed_to_list_local_libs: {e}")
                missing_locally = True

        # If everything is present locally, no need to install
        if not missing_locally:
            return False

        # 2. If missing locally, check system environment
        if current_os == "windows":
            # On Windows, we prefer the local distribution for portability
            return True
        else:
            # For Linux, check system ldconfig
            import subprocess
            try:
                # We use a simple check for common library names in ldconfig output
                output = subprocess.check_output(["ldconfig", "-p"], stderr=subprocess.DEVNULL).decode("utf-8")
                # Look for core libs: libcublas and libcudnn
                # Filter specifically for the versions we expect
                if "libcublas.so.12" in output and "libcudnn.so.9" in output:
                    logger.info("detected_cuda_libs_in_system_ldconfig")
                    return False
            except Exception as e:
                logger.debug(f"ldconfig_check_failed: {e}")
            
            # Additional check for common CUDA paths
            common_paths = ["/usr/local/cuda/lib64", "/usr/lib/x86_64-linux-gnu"]
            for path in common_paths:
                if os.path.exists(path):
                    try:
                        content = os.listdir(path)
                        if any("libcublas.so.12" in f for f in content) and any("libcudnn.so.9" in f for f in content):
                            logger.info(f"detected_cuda_libs_in_system_path: {path}")
                            return False
                    except Exception:
                        continue
            
            return True

    def _get_wheel_url(self, package_name: str) -> Optional[str]:
        """Fetches the Windows/Linux wheel URL from PyPI or Mirror JSON API."""
        from backend.services.config_mgr import config_mgr
        mirror_base = config_mgr.config.app.pypi_mirror.rstrip('/')
        
        current_os = platform.system().lower()
        # Windows uses win_amd64, Linux uses manylinux...x86_64
        platform_tag = "win_amd64" if current_os == "windows" else "manylinux"
        arch_tag = "" if current_os == "windows" else "x86_64"

        def _fetch(base_url: str) -> Optional[str]:
            api_url = f"{base_url}/pypi/{package_name}/json"
            logger.info(f"fetching_package_metadata: {api_url}")
            try:
                # Added timeout to avoid hanging
                with urllib.request.urlopen(api_url, timeout=15) as response:
                    data = json.loads(response.read().decode())
                    for release_file in data["urls"]:
                        filename = release_file["filename"]
                        if (release_file["packagetype"] == "bdist_wheel" and 
                            platform_tag in filename and 
                            (not arch_tag or arch_tag in filename)):
                            logger.info(f"found_matching_wheel: {filename}")
                            return release_file["url"]
            except Exception as e:
                logger.warning(f"metadata_fetch_failed: {api_url}, {e}")
            return None

        # Try mirror first
        url = _fetch(mirror_base)
        if url: return url

        # Fallback to official PyPI
        if "pypi.org" not in mirror_base:
            logger.info("falling_back_to_official_pypi")
            return _fetch("https://pypi.org")
        
        return None

    def download_deps(self, progress_callback: Optional[Callable[[float], None]] = None) -> bool:
        """
        Orchestrates the download and robust extraction of DLLs from PyPI wheels,
        skipping packages that are already present.
        """
        lib_dir = self.get_lib_dir()
        os.makedirs(lib_dir, exist_ok=True)
        
        pkgs = self.PYPI_PACKAGES
        current_os = platform.system().lower()
        
        for idx, package_name in enumerate(pkgs):
            base_overall_progress = (idx / len(pkgs)) * 100
            pkg_weight = 100 / len(pkgs)
            
            # Optimization: Check if this package's core files are already present
            check_files = self.PACKAGE_CHECKS.get(package_name, [])
            ext = ".dll" if current_os == "windows" else ".so"
            os_files = [f for f in check_files if f.endswith(ext)]
            
            already_installed = False
            if os_files and os.path.exists(lib_dir):
                all_found = True
                local_files = os.listdir(lib_dir)
                for f in os_files:
                    prefix = f.split('.so')[0] if current_os == "linux" else f
                    if not any(lf.startswith(prefix) for lf in local_files):
                        all_found = False
                        break
                already_installed = all_found

            if already_installed:
                logger.info(f"package_already_present_skipping: {package_name}")
                if progress_callback:
                    progress_callback((idx + 1) / len(pkgs) * 100)
                continue

            wheel_url = self._get_wheel_url(package_name)
            if not wheel_url:
                logger.error(f"could_not_find_suitable_wheel_for: {package_name}")
                return False

            temp_wheel = os.path.join(lib_dir, f"{package_name}.whl")
            try:
                # 1. Download Phase
                def _report_hook(block_num, block_size, total_size):
                    if total_size > 0 and progress_callback:
                        download_prog = (block_num * block_size / total_size) * 0.8
                        overall = base_overall_progress + (download_prog * pkg_weight)
                        progress_callback(min(99, overall))

                logger.info(f"downloading_from: {wheel_url}")
                urllib.request.urlretrieve(wheel_url, temp_wheel, reporthook=_report_hook)

                # 2. Extraction Phase - Robust Search
                if progress_callback:
                    progress_callback(base_overall_progress + (0.85 * pkg_weight))
                
                logger.info(f"scanning_and_extracting_libs_from: {package_name}")
                extracted_count = 0
                ext = ".dll" if current_os == "windows" else ".so"
                with zipfile.ZipFile(temp_wheel, 'r') as zip_ref:
                    for zip_info in zip_ref.infolist():
                        filename = zip_info.filename
                        lower_name = filename.lower()
                        # Extract .dll for Windows and .so (including .so.X) for Linux
                        if (ext in lower_name) and ('cudnn' in lower_name or 'cublas' in lower_name):
                            target_name = os.path.basename(filename)
                            if 'cache' in lower_name: continue
                            
                            with zip_ref.open(zip_info) as source, \
                                 open(os.path.join(lib_dir, target_name), 'wb') as target_f:
                                target_f.write(source.read())
                            extracted_count += 1
                
                logger.info(f"extracted_files_from_{package_name}: {extracted_count}")
                os.remove(temp_wheel)
                
                if progress_callback:
                    progress_callback((idx + 1) / len(pkgs) * 100)

            except Exception as e:
                logger.error(f"process_failed: {package_name}, {e}", exc_info=True)
                if os.path.exists(temp_wheel): os.remove(temp_wheel)
                return False

        if progress_callback: progress_callback(100)
        return True

dep_mgr = DependencyManager()
