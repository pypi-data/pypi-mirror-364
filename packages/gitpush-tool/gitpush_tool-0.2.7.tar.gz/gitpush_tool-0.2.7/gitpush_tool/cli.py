import os
import argparse
import sys
import subprocess
import platform
import urllib.request
import tempfile
import shutil

def check_gh_installed():
    """Check if GitHub CLI is installed, attempt installation if not"""
    if shutil.which("gh"):
        return True

    print("📦 GitHub CLI not found. Attempting installation...")
    system = platform.system()
    
    try:
        if system == "Windows":
            return install_gh_cli_windows()
        elif system == "Darwin":
            subprocess.run(["brew", "install", "gh"], check=True)
        elif system == "Linux":
            subprocess.run(["sudo", "apt", "install", "-y", "gh"], check=True)
        else:
            print("❌ Unsupported OS.")
            return False
            
        return shutil.which("gh") is not None
    except Exception as e:
        print(f"❌ Failed to install GitHub CLI: {e}")
        return False

def install_gh_cli_windows():
    """Install GitHub CLI on Windows using winget or direct download"""
    # Try winget first
    if shutil.which("winget"):
        try:
            subprocess.run(["winget", "install", "--id", "GitHub.cli", "--silent"], check=True)
            return True
        except subprocess.CalledProcessError:
            print("⚠️ winget installation failed.")
    
    # Fallback to direct download
    try:
        print("⬇️ Downloading GitHub CLI installer...")
        url = "https://github.com/cli/cli/releases/latest/download/gh_2.46.0_windows_amd64.msi"
        msi_path = os.path.join(tempfile.gettempdir(), "gh_installer.msi")
        urllib.request.urlretrieve(url, msi_path)
        
        print("🛠 Installing GitHub CLI...")
        subprocess.run(["msiexec", "/i", msi_path, "/quiet", "/norestart"], check=True)
        os.remove(msi_path)  # Clean up
        return True
    except Exception as e:
        print(f"❌ Direct installation failed: {e}")
        return False

def gh_authenticated():
    """Check if user is authenticated with GitHub CLI"""
    try:
        result = subprocess.run(["gh", "auth", "status"], capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False

def authenticate_with_gh():
    """Authenticate user with GitHub CLI"""
    print("\n🔑 GitHub authentication required")
    print("We'll use the GitHub CLI (gh) for authentication")
    print("This will open your browser for secure login")
    
    try:
        subprocess.run(["gh", "auth", "login", "--web", "-h", "github.com"], check=True)
        return True
    except subprocess.CalledProcessError:
        print("❌ Authentication failed")
        return False

def initialize_git_repository():
    """Initialize git repository if not already initialized"""
    if os.path.exists(".git"):
        return False
        
    print("🛠 Initializing git repository")
    try:
        subprocess.run(["git", "init"], check=True)
        subprocess.run(["git", "branch", "-M", "main"], check=True)
        
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
        print(f"❌ Failed to initialize Git repository: {e}")
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
        print(f"❌ Failed to create initial commit: {e}")
        return False

def create_with_gh_cli(repo_name, private=False, description="", commit_message="Initial commit"):
    """Create and push to new repository using GitHub CLI"""
    try:
        if not os.path.exists(".git") and not initialize_git_repository():
            return False
        
        if not create_initial_commit(commit_message):
            print("ℹ️ Using existing commits")

        private_flag = "--private" if private else "--public"
        cmd = ["gh", "repo", "create", repo_name, private_flag,
               "--source=.", "--remote=origin", "--push"]
        
        if description:
            cmd.extend(["--description", description])
        
        print("🚀 Creating repository and pushing code...")
        subprocess.run(cmd, check=True)
        
        url_result = subprocess.run(
            ["gh", "repo", "view", "--json", "url", "--jq", ".url"],
            capture_output=True, text=True, check=True
        )
        repo_url = url_result.stdout.strip()
        print(f"✅ Successfully created repository: {repo_url}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create repository: {e.stderr if e.stderr else 'Unknown error'}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

def standard_git_push(commit_message, branch, remote, force=False, tags=False):
    """Handle standard git push operations"""
    try:
        subprocess.run(["git", "add", "."], check=True)
        
        if commit_message:
            print(f"📦 Committing: '{commit_message}'")
            subprocess.run(["git", "commit", "-m", commit_message], check=True)
        else:
            print("ℹ️ No commit message provided - skipping commit")
        
        push_cmd = ["git", "push"]
        if force:
            push_cmd.append("--force-with-lease")
        if tags:
            push_cmd.append("--tags")
        if remote and branch:
            push_cmd.extend([remote, branch])
        
        print(f"🚀 Executing: {' '.join(push_cmd)}")
        subprocess.run(push_cmd, check=True)
        print("✅ Successfully pushed changes")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Push failed: {e}")
        return False

def run():
    parser = argparse.ArgumentParser(
        description="🚀 Supercharged Git push tool with GitHub repo creation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  Standard push:         gitpush_tool "Commit message"
  Create new repo:       gitpush_tool "Initial commit" --new-repo project-name
  Private repository:    gitpush_tool --new-repo private-project --private
  Force push:            gitpush_tool "Fix critical bug" --force
"""
    )
    parser.add_argument("commit", nargs="?", help="Commit message")
    parser.add_argument("branch", nargs="?", default="main", help="Branch name (default: main)")
    parser.add_argument("remote", nargs="?", default="origin", help="Remote name (default: origin)")
    parser.add_argument("--force", action="store_true", help="Force push with --force-with-lease")
    parser.add_argument("--tags", action="store_true", help="Push tags")
    parser.add_argument("--init", action="store_true", help="Initialize git repo")
    parser.add_argument("--new-repo", metavar="NAME", help="Create new GitHub repository")
    parser.add_argument("--private", action="store_true", help="Make repository private")
    parser.add_argument("--description", help="Repository description")

    args = parser.parse_args()

    if args.new_repo:
        print(f"🆕 Creating repository: {args.new_repo}")
        
        if not check_gh_installed():
            print("❌ GitHub CLI (gh) is not installed")
            print("Please install it first:")
            print("  Mac (Homebrew): brew install gh")
            print("  Windows (Winget): winget install --id GitHub.cli")
            print("  Linux: See https://github.com/cli/cli#installation")
            sys.exit(1)
        
        if not gh_authenticated() and not authenticate_with_gh():
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
            create_initial_commit(args.commit or "Initial commit")
    else:
        if not standard_git_push(
            args.commit,
            args.branch,
            args.remote,
            args.force,
            args.tags
        ):
            sys.exit(1)

if __name__ == "__main__":
    run()