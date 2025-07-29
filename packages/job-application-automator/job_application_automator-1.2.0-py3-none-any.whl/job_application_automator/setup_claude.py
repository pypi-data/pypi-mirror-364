#!/usr/bin/env python3
"""
Setup script for Form Automation MCP Server
This script installs dependencies and configures the MCP server for use with Claude Desktop
"""

import subprocess
import sys
import os
import json
import shutil
import platform
from pathlib import Path

def run_command(command, description):
    """Run a shell command and handle errors."""
    print(f"📦 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_python():
    """Check Python installation."""
    try:
        python_version = sys.version_info
        if python_version >= (3, 10):
            print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro} - OK")
            return True
        else:
            print(f"❌ Python {python_version.major}.{python_version.minor}.{python_version.micro} - Requires Python 3.10+")
            return False
    except Exception as e:
        print(f"❌ Python check failed: {e}")
        return False

def check_nodejs():
    """Check Node.js and npm/npx installation."""
    print("🔧 Checking Node.js prerequisites...")
    
    # Check Node.js
    node_version = None
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True, check=True)
        node_version = result.stdout.strip()
        print(f"✅ Node.js {node_version} - OK")
        node_ok = True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Node.js - MISSING")
        node_ok = False
    
    # Check npm
    npm_version = None
    if node_ok:
        try:
            result = subprocess.run(["npm", "--version"], capture_output=True, text=True, check=True)
            npm_version = result.stdout.strip()
            print(f"✅ npm {npm_version} - OK")
            npm_ok = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ npm - MISSING")
            npm_ok = False
    else:
        npm_ok = False
    
    # Check npx
    npx_ok = False
    if npm_ok:
        try:
            result = subprocess.run(["npx", "--version"], capture_output=True, text=True, check=True)
            npx_version = result.stdout.strip()
            print(f"✅ npx {npx_version} - OK")
            npx_ok = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ npx - MISSING")
    
    return node_ok and npm_ok and npx_ok

def show_nodejs_installation_guide():
    """Display platform-specific Node.js installation instructions."""
    print("\n" + "="*60)
    print("📋 Node.js Installation Required")
    print("="*60)
    print()
    print("To enable job matching features, please install Node.js:")
    print()
    
    system = platform.system().lower()
    
    if system == "windows":
        print("🪟 Windows Installation:")
        print("  1. Visit https://nodejs.org/")
        print("  2. Download the 'LTS' version (recommended)")
        print("  3. Run the installer with default settings")
        print("  4. Restart your terminal/command prompt")
        print()
        print("Alternative (if you have Chocolatey):")
        print("  choco install nodejs")
        print()
        print("Alternative (if you have winget):")
        print("  winget install OpenJS.NodeJS")
        
    elif system == "darwin":
        print("🍎 macOS Installation:")
        print("  Option 1 (Recommended - if you have Homebrew):")
        print("    brew install node")
        print()
        print("  Option 2 (Manual):")
        print("    1. Visit https://nodejs.org/")
        print("    2. Download the 'LTS' version")
        print("    3. Run the installer")
        print()
        print("  Option 3 (if you have MacPorts):")
        print("    sudo port install nodejs18")
        
    else:  # Linux and others
        print("🐧 Linux Installation:")
        print("  Ubuntu/Debian:")
        print("    sudo apt update && sudo apt install nodejs npm")
        print()
        print("  RHEL/CentOS/Fedora:")
        print("    sudo dnf install nodejs npm")
        print("    # or: sudo yum install nodejs npm")
        print()
        print("  Arch Linux:")
        print("    sudo pacman -S nodejs npm")
        print()
        print("  From official website:")
        print("    1. Visit https://nodejs.org/")
        print("    2. Download the 'LTS' version for Linux")
        print("    3. Follow installation instructions")
    
    print()
    print("📝 After installation, verify with:")
    print("  node --version")
    print("  npm --version")
    print("  npx --version")
    print()
    print("🔄 Then run this setup command again:")
    print("  job-automator-setup")
    print()
    print("="*60)

def setup_claude_desktop_config():
    """Set up Claude Desktop configuration."""
    print("\n🔧 Configuring Claude Desktop...")
    
    # Claude Desktop config paths
    if os.name == 'nt':  # Windows
        config_dir = Path.home() / "AppData" / "Roaming" / "Claude"
    else:  # macOS/Linux
        config_dir = Path.home() / "Library" / "Application Support" / "Claude"
    
    config_file = config_dir / "claude_desktop_config.json"
    
    # Create config directory if it doesn't exist
    config_dir.mkdir(parents=True, exist_ok=True)
    
    # Find the job-automator-mcp executable
    mcp_command = None
    
    # Method 1: Try to find using shutil.which (works for global installs)
    mcp_command = shutil.which("job-automator-mcp")
    
    if not mcp_command:
        # Method 2: Check in same directory as current Python executable
        python_dir = Path(sys.executable).parent
        if os.name == 'nt':  # Windows
            potential_path = python_dir / "job-automator-mcp.exe"
        else:  # macOS/Linux
            potential_path = python_dir / "job-automator-mcp"
        
        if potential_path.exists():
            mcp_command = str(potential_path)
    
    if not mcp_command:
        # Method 3: Check in Scripts subdirectory (Windows virtual env)
        scripts_dir = Path(sys.executable).parent / "Scripts"
        if scripts_dir.exists():
            if os.name == 'nt':
                potential_path = scripts_dir / "job-automator-mcp.exe"
            else:
                potential_path = scripts_dir / "job-automator-mcp"
            
            if potential_path.exists():
                mcp_command = str(potential_path)
    
    if not mcp_command:
        # Fallback: use just the command name and hope it's in PATH
        mcp_command = "job-automator-mcp"
        print("⚠️  Could not find job-automator-mcp executable, using command name only")
    else:
        print(f"✅ Found job-automator-mcp at: {mcp_command}")
    
    return mcp_command, config_file

def setup_job_automator_server(mcp_command, config_file):
    """Set up the job-automator (local) MCP server."""
    print("🔧 Setting up job-automator MCP server...")
    
    # Read existing config if it exists
    existing_config = {}
    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                existing_config = json.load(f)
        except json.JSONDecodeError:
            print("⚠️  Existing Claude config file is invalid, creating new one")
    
    # Ensure mcpServers section exists
    if "mcpServers" not in existing_config:
        existing_config["mcpServers"] = {}
    
    # Add job-automator server
    existing_config["mcpServers"]["job-automator"] = {
        "command": mcp_command
    }
    
    # Write the updated config
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(existing_config, f, indent=2)
        print("✅ job-automator MCP server configured")
        return True
    except Exception as e:
        print(f"❌ Failed to configure job-automator MCP server: {e}")
        return False

def setup_job_matcher_server(config_file):
    """Set up the job-matcher (remote) MCP server."""
    print("🔧 Setting up job-matcher MCP server...")
    
    # Read existing config
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            existing_config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print("❌ Could not read Claude config file")
        return False
    
    # Add job-matcher server
    existing_config["mcpServers"]["job-matcher"] = {
        "command": "npx",
        "args": [
            "mcp-remote",
            "https://mcp-job-matcher.jobmatcherstmovva.workers.dev"
        ]
    }
    
    # Write the updated config
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(existing_config, f, indent=2)
        print("✅ job-matcher MCP server configured")
        return True
    except Exception as e:
        print(f"❌ Failed to configure job-matcher MCP server: {e}")
        return False

def test_mcp_server():
    """Test the MCP server installation."""
    print("🧪 Testing MCP server...")
    
    server_path = Path(__file__).parent / "form_automation_server.py"
    
    # Test that the server can be imported
    try:
        # Add the project directory to Python path for testing
        project_dir = Path(__file__).parent.parent
        sys.path.insert(0, str(project_dir))
        
        # Try to import the server modules
        from simple_form_extractor import SimpleFormExtractor
        from simple_form_filler import SimpleFormFiller
        print("✅ Form automation modules imported successfully")
        
        # Validate server exists
        try:
            import job_application_automator.mcp_server
            print("✅ MCP server module found")
        except ImportError:
            print("❌ MCP server module not found")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return False
    
    # Setup Claude Desktop config
    if not setup_claude_desktop_config():
        print("❌ Claude Desktop configuration failed")
        sys.exit(1)
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Restart Claude Desktop application")
    print("2. Look for the form automation tools in Claude Desktop")
    print("3. Test with: 'Extract form data from [URL]'")
    print("\n🔧 Available tools:")
    print("- simple_form_extraction: Extract form fields from any URL")
    print("- simple_form_filling: Fill forms with provided data")
    print("- health_check: Check server status")
    
    print(f"\n📁 Server location: {Path(__file__).parent / 'form_automation_server.py'}")
    print(f"📁 Config location: {Path.home() / 'Library/Application Support/Claude/claude_desktop_config.json' if os.name != 'nt' else Path.home() / 'AppData/Roaming/Claude/claude_desktop_config.json'}")

def show_next_steps(nodejs_available, config_path):
    """Show user what to do next."""
    print("\n" + "="*60)
    if nodejs_available:
        print("🎉 Setup completed successfully!")
        print("="*60)
        print()
        print("� Next steps:")
        print("1. Restart Claude Desktop application")
        print("2. Look for the job automation tools in Claude Desktop")
        print("3. Test with: 'Extract form data from [job posting URL]'")
        print("4. Test job matching with: 'Find jobs matching my resume'")
        print()
        print("🔧 Available tools:")
        print("- simple_form_extraction: Extract form fields from job posting URLs")
        print("- simple_form_filling: Fill forms with your information")
        print("- create_cover_letter: Generate personalized cover letters")
        print("- get_applied_jobs: View your application dashboard")
        print("- health_check: Check server status")
        print("- job_matcher: Find jobs matching your resume and skills")
    else:
        print("⚠️  Setup completed with core features")
        print("="*60)
        print()
        print("✅ Available now:")
        print("- Form extraction and filling")
        print("- Cover letter generation")
        print("- Application tracking")
        print()
        print("🔄 To enable job matching:")
        print("1. Install Node.js (see instructions above)")
        print("2. Run 'job-automator-setup' again")
        print()
        print("📋 Current next steps:")
        print("1. Restart Claude Desktop application")
        print("2. Look for the job automation tools in Claude Desktop")
        print("3. Test with: 'Extract form data from [job posting URL]'")
    
    print()
    print(f"📁 Config location: {config_path}")
    print("="*60)

def main():
    """Main entry point for Claude Desktop setup."""
    print("� Job Application Automator - Claude Desktop Setup")
    print("=" * 60)
    
    # Phase 1: Check prerequisites
    print("\n🔧 Checking prerequisites...")
    
    python_ok = check_python()
    if not python_ok:
        print("\n❌ Setup cannot continue without Python 3.10+")
        print("Please install Python 3.10 or higher from https://python.org/")
        sys.exit(1)
    
    nodejs_ok = check_nodejs()
    
    # Phase 2: Install playwright browsers if needed
    print("\n🎭 Installing Playwright browsers...")
    try:
        run_command("playwright install chromium", "Installing Playwright browser")
    except:
        print("⚠️  Playwright browser installation skipped (may already be installed)")
    
    # Phase 3: Set up Claude Desktop configuration
    print("\n🔧 Configuring Claude Desktop MCP servers...")
    
    mcp_command, config_file = setup_claude_desktop_config()
    
    # Always set up job-automator (core functionality)
    automator_success = setup_job_automator_server(mcp_command, config_file)
    
    if not automator_success:
        print("\n❌ Failed to set up core job-automator functionality")
        sys.exit(1)
    
    # Conditionally set up job-matcher (enhanced functionality)
    matcher_success = False
    if nodejs_ok:
        matcher_success = setup_job_matcher_server(config_file)
    else:
        print("⚠️  job-matcher MCP server skipped (requires Node.js)")
        show_nodejs_installation_guide()
    
    # Phase 4: Show results and next steps
    config_path = Path.home() / "AppData" / "Roaming" / "Claude" / "claude_desktop_config.json" if os.name == 'nt' else Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
    
    show_next_steps(nodejs_ok and matcher_success, config_path)

if __name__ == "__main__":
    main()
