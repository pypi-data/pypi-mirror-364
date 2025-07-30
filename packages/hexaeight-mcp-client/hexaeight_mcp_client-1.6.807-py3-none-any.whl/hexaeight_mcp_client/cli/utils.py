"""
Common utilities for HexaEight CLI tools
"""

import os
import sys
import platform
import subprocess
import zipfile
import shutil
import json
import urllib.request
import urllib.error
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple

# FIXED: Use modern importlib.resources instead of deprecated pkg_resources
try:
    from importlib import resources
except ImportError:
    # Fallback for Python < 3.9
    import importlib_resources as resources

def get_platform_info() -> Tuple[str, str]:
    """Get platform information for selecting correct binary"""
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    print(f"🔍 System: {system}, Machine: {machine}")
    
    if system == "windows":
        return "win-x64", "HexaEight-Machine-Tokens-Utility.exe"
    elif system == "darwin":  # macOS
        return "osx-64", "HexaEight-Machine-Tokens-Utility"
    elif system == "linux":
        if machine in ["arm", "aarch64", "arm64"]:
            return "arm-x64", "HexaEight-Machine-Tokens-Utility"
        else:
            return "linux-64", "HexaEight-Machine-Tokens-Utility"
    else:
        raise Exception(f"Unsupported platform: {system} ({machine})")

def check_network_connectivity() -> bool:
    """Check if network is available for downloads"""
    try:
        urllib.request.urlopen('https://github.com', timeout=10)
        return True
    except Exception as e:
        print(f"⚠️  Network check failed: {e}")
        return False

def download_file_with_progress(url: str, filename: str) -> None:
    """Download file with progress indication"""
    def show_progress(block_num, block_size, total_size):
        if total_size > 0:
            downloaded = block_num * block_size
            percent = min(100, (downloaded * 100) // total_size)
            mb_downloaded = downloaded / (1024 * 1024)
            mb_total = total_size / (1024 * 1024)
            print(f"\r📥 Downloading: {percent}% ({mb_downloaded:.1f}/{mb_total:.1f} MB)", end='', flush=True)
        else:
            downloaded = block_num * block_size
            mb_downloaded = downloaded / (1024 * 1024)
            print(f"\r📥 Downloaded: {mb_downloaded:.1f} MB", end='', flush=True)
    
    try:
        urllib.request.urlretrieve(url, filename, show_progress)
        print()  # New line after progress
    except urllib.error.HTTPError as e:
        if e.code == 404:
            raise Exception(f"File not found at URL: {url}")
        elif e.code == 403:
            raise Exception(f"Access denied to URL: {url}")
        else:
            raise Exception(f"HTTP error {e.code} downloading from: {url}")
    except urllib.error.URLError as e:
        raise Exception(f"Network error downloading from {url}: {e.reason}")

def download_machine_token_utility() -> str:
    """Download machine token utility from GitHub releases"""
    platform_name, executable_name = get_platform_info()
    
    print(f"🔍 Detected platform: {platform_name}")
    print(f"🔍 Executable name: {executable_name}")
    
    # Check if already downloaded in current directory
    executable_path = os.path.join('.', executable_name)
    if os.path.exists(executable_path):
        print(f"✅ Machine token utility already exists: {executable_path}")
        # Verify it's executable on Unix systems
        if platform.system() != "Windows":
            os.chmod(executable_path, 0o755)
        return executable_path
    
    # Check network connectivity
    print("🔍 Checking network connectivity...")
    if not check_network_connectivity():
        raise Exception("No network connectivity. Cannot download machine token utility.\n"
                       "Please check your internet connection and try again.")
    
    # GitHub release URL
    zip_filename = f"{platform_name}.zip"
    download_url = f"https://github.com/HexaEightTeam/Machine-Token-Utility/releases/download/prod/{zip_filename}"
    
    print(f"📦 Downloading machine token utility for {platform_name}...")
    print(f"🔗 URL: {download_url}")
    
    temp_zip = f"temp_{zip_filename}"
    
    try:
        # Download the zip file
        download_file_with_progress(download_url, temp_zip)
        
        # Verify the download
        if not os.path.exists(temp_zip):
            raise Exception("Download completed but file not found")
        
        file_size = os.path.getsize(temp_zip)
        print(f"✅ Downloaded {file_size / (1024 * 1024):.1f} MB")
        
        # Extract to current directory
        print(f"📦 Extracting {zip_filename}...")
        with zipfile.ZipFile(temp_zip, 'r') as zip_ref:
            # List contents first for debugging
            file_list = zip_ref.namelist()
            print(f"🔍 Archive contents: {file_list}")
            
            zip_ref.extractall('.')
        
        # Clean up temp zip
        os.remove(temp_zip)
        print(f"🗑️  Removed temporary file: {temp_zip}")
        
        # Handle extracted files - they might be in a subdirectory
        extracted_dir = os.path.join('.', platform_name)
        if os.path.exists(extracted_dir):
            print(f"📁 Moving files from {extracted_dir}/ to current directory...")
            
            # Move all files from subdirectory to current directory
            for filename in os.listdir(extracted_dir):
                source_path = os.path.join(extracted_dir, filename)
                dest_path = os.path.join('.', filename)
                
                # Remove destination if it exists
                if os.path.exists(dest_path):
                    os.remove(dest_path)
                    print(f"🔄 Overwriting existing: {filename}")
                
                # Move file
                shutil.move(source_path, dest_path)
                print(f"📄 Moved: {filename}")
            
            # Remove empty subdirectory
            os.rmdir(extracted_dir)
            print(f"🗑️  Removed empty directory: {extracted_dir}")
        
        # Verify the executable exists
        if not os.path.exists(executable_path):
            # Maybe the executable was extracted directly
            print(f"🔍 Looking for executable in current directory...")
            current_files = os.listdir('.')
            print(f"🔍 Current directory files: {current_files}")
            
            # Try to find the executable with a different name
            possible_names = [
                executable_name,
                "HexaEight-Machine-Tokens-Utility",
                "HexaEight-Machine-Tokens-Utility.exe",
                "machine-token-utility",
                "machine-token-utility.exe"
            ]
            
            found_executable = None
            for possible_name in possible_names:
                if os.path.exists(possible_name):
                    found_executable = possible_name
                    break
            
            if found_executable:
                if found_executable != executable_name:
                    # Rename to expected name
                    os.rename(found_executable, executable_name)
                    print(f"📄 Renamed {found_executable} to {executable_name}")
                executable_path = os.path.join('.', executable_name)
            else:
                raise Exception(f"Executable not found after extraction. Expected: {executable_name}")
        
        # Make executable on Unix systems
        if os.path.exists(executable_path) and platform.system() != "Windows":
            os.chmod(executable_path, 0o755)
            print(f"🔧 Made executable: {executable_path}")
        
        # Final verification
        if not os.path.exists(executable_path):
            raise Exception(f"Failed to create executable: {executable_path}")
        
        print(f"✅ Machine token utility ready: {executable_path}")
        return executable_path
        
    except Exception as e:
        # Cleanup on error
        if os.path.exists(temp_zip):
            try:
                os.remove(temp_zip)
            except:
                pass
        
        # More helpful error messages
        error_msg = str(e)
        if "not found at URL" in error_msg:
            error_msg += f"\n💡 Available platforms: win-x64, osx-64, linux-64, arm-x64"
            error_msg += f"\n💡 Your platform detected as: {platform_name}"
            error_msg += f"\n💡 If this seems wrong, please report this issue"
        
        raise Exception(f"Failed to download machine token utility: {error_msg}")

# Keep the old function name for backward compatibility
def extract_machine_token_utility() -> str:
    """Backward compatibility wrapper - now downloads instead of extracting"""
    return download_machine_token_utility()

def run_command(command: List[str], check: bool = True) -> subprocess.CompletedProcess:
    """Run a command and return the result"""
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=check)
        return result
    except subprocess.CalledProcessError as e:
        raise Exception(f"Command failed: {' '.join(command)}\nError: {e.stderr}")

def check_command_exists(command: str) -> bool:
    """Check if a command exists in PATH"""
    try:
        subprocess.run([command, "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def find_license_directory() -> Optional[str]:
    """Find directory containing hexaeight.mac license file"""
    # Check current directory first
    if os.path.exists("hexaeight.mac"):
        return os.getcwd()
    
    # Check parent directories
    current = os.getcwd()
    while current != os.path.dirname(current):  # Not root
        parent = os.path.dirname(current)
        license_path = os.path.join(parent, "hexaeight.mac")
        if os.path.exists(license_path):
            return parent
        current = parent
    
    return None

def create_hardlink(source: str, destination: str) -> bool:
    """Create a hardlink, with fallback to copy on Windows"""
    try:
        os.link(source, destination)
        return True
    except OSError:
        # Fallback to copy on systems that don't support hardlinks
        shutil.copy2(source, destination)
        print(f"⚠️  Created copy instead of hardlink: {destination}")
        return False

def get_template_content(template_path: str) -> str:
    """Get content from package template"""
    try:
        # FIXED: Use modern importlib.resources instead of pkg_resources
        import hexaeight_mcp_client
        with resources.files(hexaeight_mcp_client).joinpath(f'templates/{template_path}').open('r', encoding='utf-8') as template_file:
            return template_file.read()
    except Exception as e:
        raise Exception(f"Failed to read template {template_path}: {e}")

def write_template_file(template_path: str, destination: str, replacements: Dict[str, str] = None) -> None:
    """Write template file with optional string replacements"""
    content = get_template_content(template_path)
    
    if replacements:
        for key, value in replacements.items():
            content = content.replace(key, value)
    
    with open(destination, 'w') as f:
        f.write(content)
    
    print(f"✅ Created: {destination}")

def confirm_action(message: str, default: bool = False) -> bool:
    """Ask user for confirmation"""
    default_str = "Y/n" if default else "y/N"
    response = input(f"{message} ({default_str}): ").strip().lower()
    
    if not response:
        return default
    
    return response in ['y', 'yes']

def print_section(title: str, content: str = None):
    """Print a formatted section"""
    print(f"\n{'='*60}")
    print(f"🔧 {title}")
    print(f"{'='*60}")
    if content:
        print(content)

def validate_environment_variables(required_vars: List[str]) -> Dict[str, str]:
    """Validate that required environment variables are set"""
    missing = []
    values = {}
    
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing.append(var)
        else:
            values[var] = value
    
    if missing:
        raise Exception(f"Missing required environment variables: {', '.join(missing)}")
    
    return values

def save_package_state(key: str, value: Any) -> None:
    """Save state information for the package"""
    state_dir = os.path.expanduser("~/.hexaeight-mcp-client")
    os.makedirs(state_dir, exist_ok=True)
    
    state_file = os.path.join(state_dir, "state.json")
    
    # Load existing state
    state = {}
    if os.path.exists(state_file):
        try:
            with open(state_file, 'r') as f:
                state = json.load(f)
        except:
            pass
    
    # Update and save
    state[key] = value
    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)

def load_package_state() -> Dict[str, Any]:
    """Load package state information"""
    state_file = os.path.expanduser("~/.hexaeight-mcp-client/state.json")
    
    if os.path.exists(state_file):
        try:
            with open(state_file, 'r') as f:
                return json.load(f)
        except:
            pass
    
    return {}
