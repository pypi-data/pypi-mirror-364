import os
import argparse
import sys
import subprocess
import shutil
import platform

import os
import sys
import json
import platform
import shutil
import tempfile
import urllib.request
import subprocess
from typing import Optional, Tuple

def check_gh_installed() -> bool:
    """Check if GitHub CLI is installed with proper verification"""
    if shutil.which("gh"):
        try:
            # Verify gh is actually working
            subprocess.run(["gh", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
        except:
            # Found but not working - might be PATH issue
            return False
    return False

def install_gh_cli() -> bool:
    """Main installation function with comprehensive error handling"""
    system = platform.system()
    machine = platform.machine().lower()
    
    print("\n🔧 Installing GitHub CLI...")
    print(f"📋 System: {system}, Architecture: {machine}")
    
    try:
        if system == "Windows":
            return install_gh_cli_windows()
        elif system == "Darwin":
            return install_gh_cli_mac()
        elif system == "Linux":
            return install_gh_cli_linux()
        else:
            print(f"❌ Unsupported OS: {system}")
            return False
    except Exception as e:
        print(f"❌ Installation failed: {str(e)}")
        return False

def install_gh_cli_windows() -> bool:
    """Windows installation with multiple fallback methods and PATH management"""
    methods = [
        try_winget_install,
        try_scoop_install,
        try_choco_install,
        try_direct_msi_install,
        try_direct_zip_install
    ]
    
    for method in methods:
        if method():
            if verify_gh_installation():
                return True
        print("⚠️ Trying next installation method...")
    
    print("❌ All installation methods failed")
    return False

def try_winget_install() -> bool:
    """Attempt installation via winget"""
    if not shutil.which("winget"):
        return False
    
    print("\n🔄 Attempting winget installation...")
    try:
        subprocess.run(
            ["winget", "install", "--id", "GitHub.cli", "--silent", "--accept-package-agreements", "--accept-source-agreements"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"⚠️ winget failed: {e.stderr.decode().strip() if e.stderr else 'Unknown error'}")
        return False

def try_scoop_install() -> bool:
    """Attempt installation via scoop"""
    if not shutil.which("scoop"):
        return False
    
    print("\n🔄 Attempting scoop installation...")
    try:
        subprocess.run(
            ["scoop", "install", "gh"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"⚠️ scoop failed: {e.stderr.decode().strip() if e.stderr else 'Unknown error'}")
        return False

def try_choco_install() -> bool:
    """Attempt installation via chocolatey"""
    if not shutil.which("choco"):
        return False
    
    print("\n🔄 Attempting chocolatey installation...")
    try:
        subprocess.run(
            ["choco", "install", "gh", "-y"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"⚠️ chocolatey failed: {e.stderr.decode().strip() if e.stderr else 'Unknown error'}")
        return False

def try_direct_msi_install() -> bool:
    """Direct MSI installation with proper PATH handling"""
    print("\n🔄 Attempting direct MSI installation...")
    try:
        # Get latest release info
        release_info = get_github_release_info()
        if not release_info:
            return False
            
        # Find appropriate MSI
        msi_asset = next(
            (a for a in release_info.get('assets', [])
            if a['name'].endswith('_windows_amd64.msi') or 
               a['name'].endswith('_windows_386.msi')),
            None
        )
        
        if not msi_asset:
            print("❌ Could not find Windows MSI installer")
            return False
            
        # Download MSI
        temp_dir = tempfile.mkdtemp()
        msi_path = os.path.join(temp_dir, msi_asset['name'])
        print(f"⬇️ Downloading {msi_asset['name']}...")
        download_file(msi_asset['browser_download_url'], msi_path)
        
        # Install with appropriate privileges
        print("🛠 Installing...")
        try:
            # Try with admin privileges first
            subprocess.run(
                ["msiexec", "/i", msi_path, "/quiet", "/norestart"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        except subprocess.CalledProcessError:
            # Fallback to user installation
            print("⚠️ Admin install failed, trying user installation...")
            subprocess.run(
                ["msiexec", "/i", msi_path, "/quiet", "/norestart", "ALLUSERS=2"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        
        # Clean up
        shutil.rmtree(temp_dir, ignore_errors=True)
        
        # Add to PATH if needed
        program_files = os.environ.get("ProgramFiles", "C:\\Program Files")
        gh_path = os.path.join(program_files, "GitHub CLI", "gh.exe")
        if os.path.exists(gh_path):
            add_to_path(os.path.dirname(gh_path))
            return True
        
        local_appdata = os.environ.get("LOCALAPPDATA", "")
        gh_path = os.path.join(local_appdata, "GitHub CLI", "gh.exe")
        if os.path.exists(gh_path):
            add_to_path(os.path.dirname(gh_path))
            return True
            
        print("❌ Installation completed but couldn't find gh.exe")
        return False
        
    except Exception as e:
        print(f"❌ MSI installation failed: {str(e)}")
        shutil.rmtree(temp_dir, ignore_errors=True)
        return False

def try_direct_zip_install() -> bool:
    """Fallback ZIP installation for Windows"""
    print("\n🔄 Attempting direct ZIP installation...")
    try:
        # Get latest release info
        release_info = get_github_release_info()
        if not release_info:
            return False
            
        # Find appropriate ZIP
        zip_asset = next(
            (a for a in release_info.get('assets', [])
            if a['name'].endswith('windows_amd64.zip') or 
               a['name'].endswith('windows_386.zip')),
            None
        )
        
        if not zip_asset:
            print("❌ Could not find Windows ZIP package")
            return False
            
        # Download and extract
        temp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(temp_dir, zip_asset['name'])
        print(f"⬇️ Downloading {zip_asset['name']}...")
        download_file(zip_asset['browser_download_url'], zip_path)
        
        print("📦 Extracting...")
        shutil.unpack_archive(zip_path, temp_dir)
        
        # Find the binary
        for root, _, files in os.walk(temp_dir):
            if "gh.exe" in files:
                bin_dir = root
                break
        else:
            print("❌ Could not find gh.exe in extracted files")
            shutil.rmtree(temp_dir, ignore_errors=True)
            return False
        
        # Install to local apps directory
        install_dir = os.path.join(os.environ.get("LOCALAPPDATA", ""), "GitHubCLI")
        os.makedirs(install_dir, exist_ok=True)
        
        # Copy files
        for item in os.listdir(bin_dir):
            src = os.path.join(bin_dir, item)
            dst = os.path.join(install_dir, item)
            if os.path.isdir(src):
                shutil.copytree(src, dst, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dst)
        
        # Add to PATH
        add_to_path(install_dir)
        
        # Clean up
        shutil.rmtree(temp_dir, ignore_errors=True)
        
        return True
        
    except Exception as e:
        print(f"❌ ZIP installation failed: {str(e)}")
        shutil.rmtree(temp_dir, ignore_errors=True)
        return False

def install_gh_cli_mac() -> bool:
    """macOS installation with multiple methods"""
    methods = [
        try_brew_install,
        try_direct_pkg_install,
        try_direct_tar_install
    ]
    
    for method in methods:
        if method():
            if verify_gh_installation():
                return True
        print("⚠️ Trying next installation method...")
    
    print("❌ All installation methods failed")
    return False

def try_brew_install() -> bool:
    """Attempt installation via Homebrew"""
    if not shutil.which("brew"):
        return False
    
    print("\n🔄 Attempting Homebrew installation...")
    try:
        subprocess.run(
            ["brew", "install", "gh"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Homebrew failed: {e.stderr.decode().strip() if e.stderr else 'Unknown error'}")
        return False

def try_direct_pkg_install() -> bool:
    """Direct PKG installation for macOS"""
    print("\n🔄 Attempting direct PKG installation...")
    try:
        release_info = get_github_release_info()
        if not release_info:
            return False
            
        pkg_asset = next(
            (a for a in release_info.get('assets', [])
            if a['name'].endswith('.pkg') and 'macOS' in a['name']),
            None
        )
        
        if not pkg_asset:
            print("❌ Could not find macOS PKG installer")
            return False
            
        temp_dir = tempfile.mkdtemp()
        pkg_path = os.path.join(temp_dir, pkg_asset['name'])
        print(f"⬇️ Downloading {pkg_asset['name']}...")
        download_file(pkg_asset['browser_download_url'], pkg_path)
        
        print("🛠 Installing...")
        subprocess.run(
            ["sudo", "installer", "-pkg", pkg_path, "-target", "/"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        shutil.rmtree(temp_dir, ignore_errors=True)
        return True
        
    except Exception as e:
        print(f"❌ PKG installation failed: {str(e)}")
        shutil.rmtree(temp_dir, ignore_errors=True)
        return False

def try_direct_tar_install() -> bool:
    """Fallback tar.gz installation for macOS"""
    print("\n🔄 Attempting direct tar.gz installation...")
    try:
        release_info = get_github_release_info()
        if not release_info:
            return False
            
        tar_asset = next(
            (a for a in release_info.get('assets', [])
            if a['name'].endswith('macOS_amd64.tar.gz')),
            None
        )
        
        if not tar_asset:
            print("❌ Could not find macOS tar.gz package")
            return False
            
        temp_dir = tempfile.mkdtemp()
        tar_path = os.path.join(temp_dir, tar_asset['name'])
        print(f"⬇️ Downloading {tar_asset['name']}...")
        download_file(tar_asset['browser_download_url'], tar_path)
        
        print("📦 Extracting...")
        subprocess.run(
            ["tar", "-xzf", tar_path, "-C", temp_dir],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Find the binary
        for root, _, files in os.walk(temp_dir):
            if "gh" in files:
                bin_path = os.path.join(root, "gh")
                break
        else:
            print("❌ Could not find gh binary in extracted files")
            shutil.rmtree(temp_dir, ignore_errors=True)
            return False
        
        # Install to /usr/local/bin
        print("🛠 Installing to /usr/local/bin...")
        subprocess.run(
            ["sudo", "install", "-m", "755", bin_path, "/usr/local/bin/gh"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        shutil.rmtree(temp_dir, ignore_errors=True)
        return True
        
    except Exception as e:
        print(f"❌ tar.gz installation failed: {str(e)}")
        shutil.rmtree(temp_dir, ignore_errors=True)
        return False

def install_gh_cli_linux() -> bool:
    """Linux installation with distro detection and multiple methods"""
    methods = []
    
    # Detect distribution
    if os.path.exists("/etc/debian_version"):
        methods.extend([
            try_apt_install,
            try_deb_install
        ])
    elif os.path.exists("/etc/redhat-release"):
        methods.extend([
            try_yum_install,
            try_dnf_install
        ])
    elif os.path.exists("/etc/arch-release"):
        methods.extend([
            try_pacman_install
        ])
    else:
        print("⚠️ Unknown Linux distribution, trying generic methods")
    
    # Add fallback methods
    methods.extend([
        try_tar_install_linux,
        try_script_install
    ])
    
    for method in methods:
        if method():
            if verify_gh_installation():
                return True
        print("⚠️ Trying next installation method...")
    
    print("❌ All installation methods failed")
    return False

def try_apt_install() -> bool:
    """APT installation for Debian/Ubuntu"""
    if not shutil.which("apt"):
        return False
    
    print("\n🔄 Attempting apt installation...")
    try:
        subprocess.run(
            ["sudo", "apt", "update"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        subprocess.run(
            ["sudo", "apt", "install", "-y", "gh"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"⚠️ apt failed: {e.stderr.decode().strip() if e.stderr else 'Unknown error'}")
        return False

def try_deb_install() -> bool:
    """Direct DEB package installation"""
    print("\n🔄 Attempting deb package installation...")
    try:
        release_info = get_github_release_info()
        if not release_info:
            return False
            
        deb_asset = next(
            (a for a in release_info.get('assets', [])
            if a['name'].endswith('linux_amd64.deb') or 
               a['name'].endswith('linux_arm64.deb')),
            None
        )
        
        if not deb_asset:
            print("❌ Could not find DEB package")
            return False
            
        temp_dir = tempfile.mkdtemp()
        deb_path = os.path.join(temp_dir, deb_asset['name'])
        print(f"⬇️ Downloading {deb_asset['name']}...")
        download_file(deb_asset['browser_download_url'], deb_path)
        
        print("🛠 Installing...")
        subprocess.run(
            ["sudo", "dpkg", "-i", deb_path],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Fix potential dependencies
        subprocess.run(
            ["sudo", "apt", "--fix-broken", "install", "-y"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        shutil.rmtree(temp_dir, ignore_errors=True)
        return True
        
    except Exception as e:
        print(f"❌ DEB installation failed: {str(e)}")
        shutil.rmtree(temp_dir, ignore_errors=True)
        return False

def try_yum_install() -> bool:
    """YUM installation for RHEL/CentOS"""
    if not shutil.which("yum"):
        return False
    
    print("\n🔄 Attempting yum installation...")
    try:
        subprocess.run(
            ["sudo", "yum", "install", "-y", "gh"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"⚠️ yum failed: {e.stderr.decode().strip() if e.stderr else 'Unknown error'}")
        return False

def try_dnf_install() -> bool:
    """DNF installation for Fedora"""
    if not shutil.which("dnf"):
        return False
    
    print("\n🔄 Attempting dnf installation...")
    try:
        subprocess.run(
            ["sudo", "dnf", "install", "-y", "gh"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"⚠️ dnf failed: {e.stderr.decode().strip() if e.stderr else 'Unknown error'}")
        return False

def try_pacman_install() -> bool:
    """Pacman installation for Arch"""
    if not shutil.which("pacman"):
        return False
    
    print("\n🔄 Attempting pacman installation...")
    try:
        subprocess.run(
            ["sudo", "pacman", "-Sy", "--noconfirm", "github-cli"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"⚠️ pacman failed: {e.stderr.decode().strip() if e.stderr else 'Unknown error'}")
        return False

def try_tar_install_linux() -> bool:
    """Generic tar.gz installation for Linux"""
    print("\n🔄 Attempting tar.gz installation...")
    try:
        release_info = get_github_release_info()
        if not release_info:
            return False
            
        tar_asset = next(
            (a for a in release_info.get('assets', [])
            if a['name'].endswith('linux_amd64.tar.gz') or 
               a['name'].endswith('linux_arm64.tar.gz')),
            None
        )
        
        if not tar_asset:
            print("❌ Could not find tar.gz package")
            return False
            
        temp_dir = tempfile.mkdtemp()
        tar_path = os.path.join(temp_dir, tar_asset['name'])
        print(f"⬇️ Downloading {tar_asset['name']}...")
        download_file(tar_asset['browser_download_url'], tar_path)
        
        print("📦 Extracting...")
        subprocess.run(
            ["tar", "-xzf", tar_path, "-C", temp_dir],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Find the binary
        for root, _, files in os.walk(temp_dir):
            if "gh" in files:
                bin_path = os.path.join(root, "gh")
                break
        else:
            print("❌ Could not find gh binary in extracted files")
            shutil.rmtree(temp_dir, ignore_errors=True)
            return False
        
        # Install to /usr/local/bin
        print("🛠 Installing to /usr/local/bin...")
        subprocess.run(
            ["sudo", "install", "-m", "755", bin_path, "/usr/local/bin/gh"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        shutil.rmtree(temp_dir, ignore_errors=True)
        return True
        
    except Exception as e:
        print(f"❌ tar.gz installation failed: {str(e)}")
        shutil.rmtree(temp_dir, ignore_errors=True)
        return False

def try_script_install() -> bool:
    """Fallback script installation"""
    print("\n🔄 Attempting script installation...")
    try:
        subprocess.run(
            ["curl", "-fsSL", "https://cli.github.com/packages/githubcli-archive-keyring.gpg", "|", "sudo", "dd", "of=/usr/share/keyrings/githubcli-archive-keyring.gpg"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        subprocess.run(
            ["sudo", "chmod", "go+r", "/usr/share/keyrings/githubcli-archive-keyring.gpg"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        subprocess.run(
            ['echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null'],
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        subprocess.run(
            ["sudo", "apt", "update"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        subprocess.run(
            ["sudo", "apt", "install", "-y", "gh"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Script installation failed: {e.stderr.decode().strip() if e.stderr else 'Unknown error'}")
        return False

def get_github_release_info() -> Optional[dict]:
    """Get latest release info from GitHub API"""
    try:
        with urllib.request.urlopen("https://api.github.com/repos/cli/cli/releases/latest") as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"❌ Failed to get release info: {str(e)}")
        return None

def download_file(url: str, path: str) -> bool:
    """Download a file with progress reporting"""
    try:
        def reporthook(count, block_size, total_size):
            percent = int(count * block_size * 100 / total_size)
            sys.stdout.write(f"\rDownloading... {percent}%")
            sys.stdout.flush()
            
        urllib.request.urlretrieve(url, path, reporthook=reporthook)
        print()  # New line after progress
        return True
    except Exception as e:
        print(f"\n❌ Download failed: {str(e)}")
        return False

def add_to_path(directory: str) -> bool:
    """Add directory to PATH if not already present"""
    try:
        current_path = os.environ.get("PATH", "")
        if directory not in current_path.split(os.pathsep):
            if platform.system() == "Windows":
                # Permanent PATH modification on Windows
                import winreg
                with winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER) as root:
                    with winreg.OpenKey(root, "Environment", 0, winreg.KEY_ALL_ACCESS) as key:
                        path_value, _ = winreg.QueryValueEx(key, "PATH")
                        new_path = f"{path_value};{directory}" if path_value else directory
                        winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, new_path)
                # Notify other processes of PATH change
                import ctypes
                ctypes.windll.user32.SendMessageTimeoutW(
                    0xFFFF, 0x001A, 0, "Environment", 0x02, 5000, None
                )
            else:
                # For Unix-like systems, modify current session PATH
                os.environ["PATH"] = f"{directory}{os.pathsep}{os.environ.get('PATH', '')}"
                # Add to shell profile files
                profile_files = [
                    os.path.expanduser("~/.bashrc"),
                    os.path.expanduser("~/.zshrc"),
                    os.path.expanduser("~/.profile")
                ]
                export_line = f'\nexport PATH="{directory}:$PATH"\n'
                for profile in profile_files:
                    if os.path.exists(profile):
                        with open(profile, "a") as f:
                            f.write(export_line)
            print(f"✅ Added {directory} to PATH")
        return True
    except Exception as e:
        print(f"⚠️ Failed to update PATH: {str(e)}")
        return False

def verify_gh_installation() -> bool:
    """Verify gh is properly installed and in PATH"""
    if not shutil.which("gh"):
        print("❌ GitHub CLI not found in PATH after installation")
        return False
    
    try:
        result = subprocess.run(
            ["gh", "--version"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print(f"✅ GitHub CLI installed: {result.stdout.splitlines()[0]}")
        return True
    except subprocess.CalledProcessError:
        print("❌ GitHub CLI found but not working")
        return False

def check_and_install_gh() -> bool:
    """Main function to check and install GitHub CLI"""
    if check_gh_installed():
        return True
    
    if not install_gh_cli():
        print("\n❌ Failed to install GitHub CLI. Please try manual installation:")
        print("Visit https://github.com/cli/cli#installation for instructions")
        return False
    
    if not check_gh_installed():
        print("\n⚠️ Installation completed but GitHub CLI not detected in PATH")
        print("Please restart your terminal or add the installation directory to your PATH")
        return False
    
    return True

def gh_authenticated():
    """Check if user is authenticated with GitHub CLI"""
    try:
        result = subprocess.run(["gh", "auth", "status"], capture_output=True, text=True, check=True)
        return "Logged in to github.com" in result.stderr
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def authenticate_with_gh():
    """Authenticate user with GitHub CLI"""
    print("\n🔑 GitHub authentication required.")
    print("The tool will use the GitHub CLI (gh) to open a browser for secure login.")
    
    try:
        subprocess.run(["gh", "auth", "login", "--web", "-h", "github.com"], check=True)
        return True
    except subprocess.CalledProcessError:
        print("❌ Authentication failed. Please try running 'gh auth login' manually.", file=sys.stderr)
        return False

def initialize_git_repository():
    """Initialize git repository if not already initialized"""
    if os.path.exists(".git"):
        return False
        
    print("🛠 Initializing git repository")
    try:
        subprocess.run(["git", "init"], check=True, capture_output=True)
        subprocess.run(["git", "branch", "-M", "main"], check=True, capture_output=True)
        
        if not os.path.exists(".gitignore"):
            with open(".gitignore", "w") as f:
                f.write("""# Python
__pycache__/
*.py[cod]
*.so
.Python
env/
venv/
.env

# IDE
.vscode/
.idea/
*.swp
*.swo

# System
.DS_Store
Thumbs.db

# Project specific
*.log
*.tmp
*.bak
""")
            print("📁 Created .gitignore file")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to initialize Git repository: {e.stderr.decode().strip()}", file=sys.stderr)
        return False

def create_initial_commit(commit_message="Initial commit"):
    """Create initial commit if no commits exist"""
    try:
        result = subprocess.run(["git", "rev-list", "--count", "HEAD"], 
                              capture_output=True, text=True)
        commit_count = int(result.stdout.strip()) if result.stdout.strip().isdigit() else 0
        
        if commit_count == 0:
            print("📦 Creating initial commit")
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(["git", "commit", "-m", commit_message], check=True)
            return True
        return False
    except subprocess.CalledProcessError as e:
        if "nothing to commit" in e.stderr.decode():
             print(f"❌ Failed to create initial commit: No files found to commit.", file=sys.stderr)
             print("➡️  Add some files to your project directory before creating a repository.", file=sys.stderr)
        else:
             print(f"❌ Failed to create initial commit: {e.stderr.decode().strip()}", file=sys.stderr)
        return False

def create_with_gh_cli(repo_name, private=False, description="", commit_message="Initial commit"):
    """Create and push to new repository using GitHub CLI"""
    try:
        if not os.path.exists(".git"):
            if not initialize_git_repository():
                return False
        
        if not create_initial_commit(commit_message):
            if subprocess.run(["git", "status"], capture_output=True).returncode != 0:
                 return False
            print("ℹ️ Using existing commits")

        private_flag = "--private" if private else "--public"
        cmd = ["gh", "repo", "create", repo_name, private_flag,
               "--source=.", "--remote=origin", "--push"]
        
        if description:
            cmd.extend(["--description", description])
        
        print("🚀 Creating repository and pushing code...")
        process = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        repo_url = process.stderr.strip()
        print(f"✅ Successfully created repository: {repo_url}")
        return True
        
    except subprocess.CalledProcessError as e:
        error_message = e.stderr.strip()
        if "already exists" in error_message:
            print(f"❌ Failed to create repository: {error_message}", file=sys.stderr)
            print("➡️  Please choose a different repository name.", file=sys.stderr)
        else:
            print(f"❌ Failed to create repository: {error_message}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"❌ An unexpected error occurred: {str(e)}", file=sys.stderr)
        return False

def standard_git_push(commit_message, branch, remote, force=False, tags=False):
    """Handle standard git push operations"""
    try:
        subprocess.run(["git", "add", "."], check=True)
        
        if commit_message:
            print(f"📦 Committing with message: '{commit_message}'")
            subprocess.run(["git", "commit", "-m", commit_message, "--allow-empty-message"], check=True)
        else:
            print("ℹ️ No commit message provided. Pushing only staged changes.")
        
        push_cmd = ["git", "push"]
        if force:
            push_cmd.append("--force-with-lease")
            print("⚠️ Using safe force push (--force-with-lease).")
        if tags:
            push_cmd.append("--tags")
        if remote and branch:
            push_cmd.extend([remote, branch])
        
        print(f"🚀 Executing: {' '.join(push_cmd)}")
        subprocess.run(push_cmd, check=True)
        print("✅ Successfully pushed changes.")
        return True
    except subprocess.CalledProcessError as e:
        error_output = e.stderr.decode().strip() if e.stderr else str(e)
        if "nothing to commit" in error_output:
            print("ℹ️ No changes to commit. Nothing to do.")
            return True
        print(f"❌ Push failed: {error_output}", file=sys.stderr)
        return False

def run():
    parser = argparse.ArgumentParser(
        description="🚀 Supercharged Git push tool with GitHub repo creation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  Standard push:         gitpush_tool "My new feature"
  Create new repo:       gitpush_tool "Initial commit" --new-repo my-awesome-project
  Private repository:    gitpush_tool "Initial commit" --new-repo my-secret-project --private
  Force push (safe):     gitpush_tool "Rebased feature" --force
  Initialize only:       gitpush_tool --init
"""
    )
    parser.add_argument("commit", nargs="?", help="Commit message (optional if just pushing staged changes).")
    parser.add_argument("branch", nargs="?", default=None, help="Branch name (defaults to current branch).")
    parser.add_argument("remote", nargs="?", default="origin", help="Remote name (default: origin).")
    parser.add_argument("--force", action="store_true", help="Force push with --force-with-lease.")
    parser.add_argument("--tags", action="store_true", help="Push all tags.")
    parser.add_argument("--init", action="store_true", help="Initialize a new Git repository and exit.")
    parser.add_argument("--new-repo", metavar="REPO_NAME", help="Create a new GitHub repository with the given name.")
    parser.add_argument("--private", action="store_true", help="Make the new repository private.")
    parser.add_argument("--description", help="Description for the new repository.")

    args = parser.parse_args()
    
    target_branch = args.branch
    if not target_branch:
        try:
            branch_result = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True, check=True)
            target_branch = branch_result.stdout.strip()
        except subprocess.CalledProcessError:
            target_branch = "main"

    if args.new_repo:
        if not check_gh_installed():
            sys.exit(1)
        
        if not gh_authenticated():
            if not authenticate_with_gh():
                sys.exit(1)
        
        if not create_with_gh_cli(
            args.new_repo,
            private=args.private,
            description=args.description or "",
            commit_message=args.commit or "Initial commit"
        ):
            sys.exit(1)

    elif args.init:
        if initialize_git_repository():
             print("✅ Git repository initialized successfully.")
    
    else:
        if not standard_git_push(
            args.commit,
            target_branch,
            args.remote,
            args.force,
            args.tags
        ):
            sys.exit(1)

if __name__ == "__main__":
    run()