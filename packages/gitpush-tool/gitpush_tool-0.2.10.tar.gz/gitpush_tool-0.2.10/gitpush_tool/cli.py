import os
import argparse
import sys
import subprocess
import shutil
import platform

def check_gh_installed():
    """
    Checks if GitHub CLI is installed. If not, it provides a comprehensive list
    of platform-specific installation commands and fallbacks.
    """
    if shutil.which("gh"):
        return True

    print("❌ Error: GitHub CLI (gh) is not installed or not in your system's PATH.", file=sys.stderr)
    print("   The '--new-repo' feature requires the GitHub CLI for all repository operations.", file=sys.stderr)

    system = platform.system()
    install_options = []

    # --- Platform-specific detection with fallbacks ---
    if system == "Windows":
        print("\n➡️ For Windows, we recommend one of the following package managers:", file=sys.stderr)
        if shutil.which("winget"):
            install_options.append(("Winget (Recommended)", "winget install --id GitHub.cli --source winget"))
        if shutil.which("scoop"):
            install_options.append(("Scoop", "scoop install gh"))
        if shutil.which("choco"):
            install_options.append(("Chocolatey", "choco install gh"))
    
    elif system == "Darwin":
        print("\n➡️ For macOS, we recommend using Homebrew:", file=sys.stderr)
        if shutil.which("brew"):
            install_options.append(("Homebrew (Recommended)", "brew install gh"))

    elif system == "Linux":
        print("\n➡️ For Linux, we recommend one of the following package managers:", file=sys.stderr)
        if shutil.which("apt") or shutil.which("apt-get"):
            install_options.append(("Debian/Ubuntu/Mint", "sudo apt update && sudo apt install gh -y"))
        if shutil.which("dnf"):
            install_options.append(("Fedora/RHEL/CentOS", "sudo dnf install gh"))
        if shutil.which("yum"):
            install_options.append(("Older Fedora/RHEL/CentOS", "sudo yum install gh"))
        if shutil.which("pacman"):
            install_options.append(("Arch Linux", "sudo pacman -S github-cli"))
        if shutil.which("zypper"):
            install_options.append(("openSUSE", "sudo zypper install gh"))

    # --- Displaying the options and the ultimate fallback ---
    if install_options:
        print("   Please copy and run one of the commands below in your terminal:\n", file=sys.stderr)
        for name, command in install_options:
            print(f"     # For {name}:\n     {command}\n", file=sys.stderr)
    
    print("   If none of the above are available on your system, please follow the", file=sys.stderr)
    print("   official installation guide for more options (including manual download):", file=sys.stderr)
    print("   https://github.com/cli/cli#installation\n", file=sys.stderr)
    print("‼️  After installation, please open a NEW terminal and run your command again.", file=sys.stderr)

    return False

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