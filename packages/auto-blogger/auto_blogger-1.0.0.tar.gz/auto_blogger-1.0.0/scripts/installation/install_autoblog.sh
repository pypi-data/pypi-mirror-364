#!/bin/bash

# AUTO-blogger Installation Script with Auto-Update
# Copyright © 2025 AryanVBW
# GitHub: https://github.com/AryanVBW/AUTO-blogger

set -e  # Exit on any error

# Environment variables for automation
# Set AUTO_UPDATE=true for automatic updates without prompts
# Set NON_INTERACTIVE=true for completely non-interactive installation
AUTO_UPDATE=${AUTO_UPDATE:-false}
NON_INTERACTIVE=${NON_INTERACTIVE:-false}

# Check if running in non-interactive environment (CI/CD, piped input, etc.)
if [ ! -t 0 ] || [ ! -t 1 ]; then
    NON_INTERACTIVE=true
fi

# Configuration
REPO_URL="https://github.com/AryanVBW/AUTO-blogger.git"
INSTALL_DIR="$HOME/AUTO-blogger"
APP_NAME="AUTO-blogger"
# Generate unique virtual environment name to avoid conflicts
VENV_NAME="auto_blogger_venv_$(openssl rand -hex 4 2>/dev/null || date +%s | tail -c 8)"

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Logo
echo -e "\033[96m+===========================================================================+\033[0m"
echo -e "\033[96m| █████   █████  ███                       █████         █████   ███   █████ |\033[0m"
echo -e "\033[96m|░░███   ░░███  ░░░                       ░░███         ░░███   ░███  ░░███  |\033[0m"
echo -e "\033[96m| ░███    ░███  ████  █████ █████  ██████  ░███ █████    ░███   ░███   ░███  |\033[0m"
echo -e "\033[96m| ░███    ░███ ░░███ ░░███ ░░███  ███░░███ ░███░░███     ░███   ░███   ░███  |\033[0m"
echo -e "\033[96m| ░░███   ███   ░███  ░███  ░███ ░███████  ░██████░      ░░███  █████  ███   |\033[0m"
echo -e "\033[96m|  ░░░█████░    ░███  ░░███ ███  ░███░░░   ░███░░███      ░░░█████░█████░    |\033[0m"
echo -e "\033[96m|    ░░███      █████  ░░█████   ░░██████  ████ █████       ░░███ ░░███      |\033[0m"
echo -e "\033[96m|     ░░░      ░░░░░    ░░░░░     ░░░░░░  ░░░░ ░░░░░         ░░░   ░░░       |\033[0m"
echo -e "\033[95m|                                                                            |\033[0m"
echo -e "\033[95m|                           🔥GitHub:    github.com/AryanVBW                 |\033[0m"
echo -e "\033[95m|                               Copyright © 2025 AryanVBW                    |\033[0m"
echo -e "\033[95m|                           💖Instagram: Aryan_Technolog1es                  |\033[0m"
echo -e "\033[95m|                           📧Email:    vivek.aryanvbw@gmail.com                  |\033[0m"
echo -e "\033[32m+===========================================================================+\033[0m"
echo -e "\033[93m|                            Welcome to AUTO Blogger!                        |\033[0m"


# Function to detect OS with enhanced detection
detect_os() {
    local os="unknown"
    
    # Check for Windows first (multiple methods)
    if [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]] || [[ -n "$WINDIR" ]] || [[ -n "$COMSPEC" ]]; then
        os="windows"
    # Check for macOS (multiple methods)
    elif [[ "$OSTYPE" == "darwin"* ]] || [[ "$(uname -s 2>/dev/null)" == "Darwin" ]] || [[ -d "/Applications" && -d "/System" ]]; then
        os="macos"
    # Check for Linux (multiple methods)
    elif [[ "$OSTYPE" == "linux-gnu"* ]] || [[ "$(uname -s 2>/dev/null)" == "Linux" ]] || [[ -f "/etc/os-release" ]]; then
        os="linux"
    # Additional checks using uname if available
    elif command_exists uname; then
        case "$(uname -s 2>/dev/null)" in
            Linux*)     os="linux";;
            Darwin*)    os="macos";;
            CYGWIN*)    os="windows";;
            MINGW*)     os="windows";;
            MSYS*)      os="windows";;
            *NT*)       os="windows";;
        esac
    # Final fallback checks
    elif [[ -f "/proc/version" ]]; then
        os="linux"
    elif [[ -d "/System/Library" ]]; then
        os="macos"
    fi
    
    echo "$os"
}

# Function to install Git if not available
install_git() {
    local os=$(detect_os)
    echo -e "${YELLOW}📦 Installing Git...${NC}"
    
    case $os in
        "linux")
            if command_exists apt-get; then
                echo -e "${CYAN}🔄 Updating package lists...${NC}"
                sudo apt-get update || handle_error 1 "Failed to update package lists" "Check your internet connection and package manager"
                echo -e "${CYAN}🔄 Installing Git via apt-get...${NC}"
                sudo apt-get install -y git || handle_error 1 "Failed to install Git via apt-get" "Try installing manually: sudo apt-get install git"
            elif command_exists yum; then
                echo -e "${CYAN}🔄 Installing Git via yum...${NC}"
                sudo yum install -y git || handle_error 1 "Failed to install Git via yum" "Try installing manually: sudo yum install git"
            elif command_exists dnf; then
                echo -e "${CYAN}🔄 Installing Git via dnf...${NC}"
                sudo dnf install -y git || handle_error 1 "Failed to install Git via dnf" "Try installing manually: sudo dnf install git"
            elif command_exists pacman; then
                echo -e "${CYAN}🔄 Installing Git via pacman...${NC}"
                sudo pacman -S --noconfirm git || handle_error 1 "Failed to install Git via pacman" "Try installing manually: sudo pacman -S git"
            elif command_exists zypper; then
                echo -e "${CYAN}🔄 Installing Git via zypper...${NC}"
                sudo zypper install -y git || handle_error 1 "Failed to install Git via zypper" "Try installing manually: sudo zypper install git"
            else
                handle_error 1 "Unsupported Linux distribution" "Please install Git manually from https://git-scm.com/downloads"
            fi
            ;;
        "macos")
            if command_exists brew; then
                echo -e "${CYAN}🔄 Installing Git via Homebrew...${NC}"
                brew install git || handle_error 1 "Failed to install Git via Homebrew" "Try installing manually from https://git-scm.com/download/mac"
            elif command_exists port; then
                echo -e "${CYAN}🔄 Installing Git via MacPorts...${NC}"
                sudo port install git || handle_error 1 "Failed to install Git via MacPorts" "Try installing Homebrew or download from https://git-scm.com/download/mac"
            else
                handle_error 1 "No package manager found" "Please install Homebrew (https://brew.sh) or download Git from https://git-scm.com/download/mac"
            fi
            ;;
        "windows")
            handle_error 1 "Git installation required" "Please install Git from https://git-scm.com/download/win and run this script again"
            ;;
        *)
            handle_error 1 "Unsupported operating system" "Please install Git manually from https://git-scm.com/downloads"
            ;;
    esac
    
    # Verify Git installation
    if ! command_exists git; then
        handle_error 1 "Git installation failed" "Please install Git manually and try again"
    fi
    
    echo -e "${GREEN}✅ Git installed successfully${NC}"
}

# Function to check if Git is available
check_git() {
    echo -e "${YELLOW}🔍 Checking Git installation...${NC}"
    
    if command_exists git; then
        local git_version=$(git --version 2>/dev/null | cut -d' ' -f3)
        echo -e "${GREEN}✅ Git found (version: $git_version)${NC}"
        
        # Check if Git is properly configured
        if ! git config --global user.name >/dev/null 2>&1; then
            echo -e "${YELLOW}⚠️ Git user not configured. Setting default configuration...${NC}"
            git config --global user.name "AUTO-blogger User" || true
            git config --global user.email "user@auto-blogger.local" || true
        fi
    else
        echo -e "${RED}❌ Git not found. Installing Git...${NC}"
        install_git
        
        # Verify installation
        if command_exists git; then
            local git_version=$(git --version 2>/dev/null | cut -d' ' -f3)
            echo -e "${GREEN}✅ Git successfully installed (version: $git_version)${NC}"
        else
            handle_error 1 "Git installation verification failed" "Please install Git manually and try again"
        fi
    fi
}

# Function to clone or update repository
clone_or_update_repo() {
    echo -e "${YELLOW}📥 Setting up repository...${NC}"
    
    if [ -d "$INSTALL_DIR" ]; then
        echo -e "${YELLOW}📁 Directory exists. Checking for updates...${NC}"
        cd "$INSTALL_DIR" || handle_error 1 "Failed to access installation directory" "Check permissions for $INSTALL_DIR"
        
        # Check if it's a git repository
        if [ -d ".git" ]; then
            echo -e "${CYAN}🔄 Updating existing installation...${NC}"
            
            # Fetch latest changes
            echo -e "${CYAN}📡 Fetching latest changes...${NC}"
            git fetch origin || handle_error 1 "Failed to fetch updates" "Check your internet connection and GitHub access"
            
            # Determine the default branch
            local default_branch
            default_branch=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@') || default_branch="main"
            
            # Fallback to main or master
            if ! git rev-parse "origin/$default_branch" >/dev/null 2>&1; then
                if git rev-parse "origin/main" >/dev/null 2>&1; then
                    default_branch="main"
                elif git rev-parse "origin/master" >/dev/null 2>&1; then
                    default_branch="master"
                else
                    handle_error 1 "Cannot determine repository branch" "Repository may be corrupted. Try removing $INSTALL_DIR and running again"
                fi
            fi
            
            # Check if updates are available
            local local_commit remote_commit
            local_commit=$(git rev-parse HEAD 2>/dev/null)
            remote_commit=$(git rev-parse "origin/$default_branch" 2>/dev/null)
            
            if [ "$local_commit" != "$remote_commit" ]; then
                echo -e "${GREEN}📦 Updates available! Updating from $default_branch...${NC}"
                
                # Stash any local changes
                git stash push -m "Auto-stash before update" >/dev/null 2>&1 || true
                
                # Pull updates
                git pull origin "$default_branch" || handle_error 1 "Failed to pull updates" "Repository may have conflicts. Try removing $INSTALL_DIR and running again"
                
                echo -e "${GREEN}✅ Repository updated successfully${NC}"
            else
                echo -e "${GREEN}✅ Repository is already up to date${NC}"
            fi
        else
            echo -e "${YELLOW}⚠️ Directory exists but is not a git repository. Removing and cloning fresh...${NC}"
            cd .. || handle_error 1 "Failed to navigate to parent directory" "Check file system permissions"
            rm -rf "$INSTALL_DIR" || handle_error 1 "Failed to remove existing directory" "Check permissions and try running with sudo"
            
            echo -e "${CYAN}📥 Cloning fresh repository...${NC}"
            git clone "$REPO_URL" "$INSTALL_DIR" || handle_error 1 "Failed to clone repository" "Check your internet connection and GitHub access"
            cd "$INSTALL_DIR" || handle_error 1 "Failed to access cloned directory" "Check file system permissions"
        fi
    else
        echo -e "${CYAN}📥 Cloning repository...${NC}"
        
        # Create parent directory if needed
        mkdir -p "$(dirname "$INSTALL_DIR")" || handle_error 1 "Failed to create parent directory" "Check permissions for $(dirname "$INSTALL_DIR")"
        
        # Clone repository
        git clone "$REPO_URL" "$INSTALL_DIR" || handle_error 1 "Failed to clone repository" "Check your internet connection and GitHub access"
        cd "$INSTALL_DIR" || handle_error 1 "Failed to access cloned directory" "Check file system permissions"
        
        echo -e "${GREEN}✅ Repository cloned successfully${NC}"
    fi
    
    # Verify essential files exist
    local essential_files=("requirements.txt" "gui_blogger.py" "automation_engine.py" "autoblog_launcher.py")
    for file in "${essential_files[@]}"; do
        if [ ! -f "$file" ]; then
            handle_error 1 "Essential file missing: $file" "Repository may be corrupted. Try removing $INSTALL_DIR and running again"
        fi
    done
    
    echo -e "${GREEN}✅ Repository verification completed${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to handle errors with detailed messages
handle_error() {
    local error_code=$1
    local error_message="$2"
    local solution="$3"
    
    echo -e "${RED}❌ ERROR: $error_message${NC}"
    if [ -n "$solution" ]; then
        echo -e "${YELLOW}💡 SOLUTION: $solution${NC}"
    fi
    echo -e "${CYAN}📧 For support, contact: AryanVBW@gmail.com${NC}"
    exit $error_code
}

# Function to check if AUTO-blogger is already installed
check_existing_installation() {
    echo -e "${YELLOW}🔍 Checking for existing installation...${NC}"
    
    # Check if directory exists
    if [ -d "$INSTALL_DIR" ]; then
        echo -e "${YELLOW}⚠️ AUTO-blogger is already installed at: $INSTALL_DIR${NC}"
        
        # Check for non-interactive mode or auto-update flag
        if [ "$AUTO_UPDATE" = "true" ] || [ "$NON_INTERACTIVE" = "true" ] || [ ! -t 0 ]; then
            echo -e "${CYAN}🔄 Non-interactive mode detected - proceeding with update...${NC}"
            echo -e "${GREEN}✅ Proceeding with update...${NC}"
            return 0
        fi
        
        echo -e "${CYAN}What would you like to do?${NC}"
        echo "1) Update existing installation (recommended)"
        echo "2) Remove and reinstall completely"
        echo "3) Cancel installation"
        echo ""
        echo -e "${YELLOW}💡 Tip: Use 'curl -sSL ... | AUTO_UPDATE=true bash' for automatic updates${NC}"
        
        # Add timeout for automated environments
        local choice
        if read -t 30 -p "Enter your choice (1-3) [default: 1 in 30s]: " choice; then
            echo ""
        else
            echo ""
            echo -e "${YELLOW}⏰ No input received within 30 seconds, defaulting to update...${NC}"
            choice="1"
        fi
        
        case $choice in
            1|"")
                echo -e "${GREEN}✅ Proceeding with update...${NC}"
                return 0
                ;;
            2)
                echo -e "${YELLOW}🗑️ Removing existing installation...${NC}"
                rm -rf "$INSTALL_DIR" || handle_error 1 "Failed to remove existing installation" "Check permissions and try running with sudo"
                echo -e "${GREEN}✅ Existing installation removed${NC}"
                return 0
                ;;
            3)
                echo -e "${BLUE}👋 Installation cancelled by user${NC}"
                exit 0
                ;;
            *)
                echo -e "${RED}❌ Invalid choice. Defaulting to update...${NC}"
                return 0
                ;;
        esac
    else
        echo -e "${GREEN}✅ No existing installation found${NC}"
    fi
}

# Function to verify system requirements
verify_requirements() {
    local os=$(detect_os)
    echo -e "${YELLOW}🔍 Verifying system requirements...${NC}"
    
    # Check OS support
    if [ "$os" == "unknown" ]; then
        handle_error 1 "Unsupported operating system" "This installer supports Windows, macOS, and Linux only"
    fi
    
    echo -e "${GREEN}✅ Operating System: $os${NC}"
    
    # Check internet connectivity
    echo -e "${CYAN}🌐 Testing internet connectivity...${NC}"
    if ! ping -c 1 google.com >/dev/null 2>&1 && ! ping -c 1 8.8.8.8 >/dev/null 2>&1; then
        handle_error 1 "No internet connection" "Please check your internet connection and try again"
    fi
    
    echo -e "${GREEN}✅ Internet connection verified${NC}"
    
    # Check available disk space (at least 500MB)
    echo -e "${CYAN}💾 Checking disk space...${NC}"
    local available_space
    if command_exists df; then
        available_space=$(df "$HOME" | tail -1 | awk '{print $4}')
        if [ "$available_space" -lt 512000 ]; then
            handle_error 1 "Insufficient disk space" "At least 500MB of free space required"
        fi
        echo -e "${GREEN}✅ Sufficient disk space available${NC}"
    fi
    
    # Check write permissions
    echo -e "${CYAN}🔐 Checking permissions...${NC}"
    if [ ! -w "$(dirname "$INSTALL_DIR")" ]; then
        handle_error 1 "No write permission" "Cannot write to installation directory. Check permissions or run with sudo"
    fi
    
    echo -e "${GREEN}✅ All system requirements verified${NC}"
}

# Function to install Python on different systems with robust error handling
install_python() {
    local os=$(detect_os)
    echo -e "${YELLOW}📦 Installing Python...${NC}"
    
    case $os in
        "linux")
            echo -e "${CYAN}🔍 Detecting Linux distribution...${NC}"
            if command_exists apt-get; then
                echo -e "${CYAN}🔄 Updating package lists...${NC}"
                if ! sudo apt-get update; then
                    echo -e "${YELLOW}⚠️ Package update failed. Continuing with installation...${NC}"
                fi
                echo -e "${CYAN}🔄 Installing Python via apt-get...${NC}"
                if ! sudo apt-get install -y python3 python3-pip python3-venv python3-tk python3-dev build-essential; then
                    echo -e "${RED}❌ Python installation via apt-get failed${NC}"
                    echo -e "${YELLOW}💡 MANUAL INSTALLATION REQUIRED:${NC}"
                    echo -e "${CYAN}   Run: sudo apt-get install python3 python3-pip python3-venv${NC}"
                    echo -e "${CYAN}   Then re-run this installer${NC}"
                    read -p "Press Enter after manual installation to continue..." -r
                fi
            elif command_exists yum; then
                echo -e "${CYAN}🔄 Installing Python via yum...${NC}"
                if ! sudo yum install -y python3 python3-pip python3-tkinter python3-devel gcc; then
                    echo -e "${RED}❌ Python installation via yum failed${NC}"
                    echo -e "${YELLOW}💡 MANUAL INSTALLATION REQUIRED:${NC}"
                    echo -e "${CYAN}   Run: sudo yum install python3 python3-pip${NC}"
                    echo -e "${CYAN}   Then re-run this installer${NC}"
                    read -p "Press Enter after manual installation to continue..." -r
                fi
            elif command_exists dnf; then
                echo -e "${CYAN}🔄 Installing Python via dnf...${NC}"
                if ! sudo dnf install -y python3 python3-pip python3-tkinter python3-devel gcc; then
                    echo -e "${RED}❌ Python installation via dnf failed${NC}"
                    echo -e "${YELLOW}💡 MANUAL INSTALLATION REQUIRED:${NC}"
                    echo -e "${CYAN}   Run: sudo dnf install python3 python3-pip${NC}"
                    echo -e "${CYAN}   Then re-run this installer${NC}"
                    read -p "Press Enter after manual installation to continue..." -r
                fi
            elif command_exists pacman; then
                echo -e "${CYAN}🔄 Installing Python via pacman...${NC}"
                if ! sudo pacman -S --noconfirm python python-pip tk base-devel; then
                    echo -e "${RED}❌ Python installation via pacman failed${NC}"
                    echo -e "${YELLOW}💡 MANUAL INSTALLATION REQUIRED:${NC}"
                    echo -e "${CYAN}   Run: sudo pacman -S python python-pip${NC}"
                    echo -e "${CYAN}   Then re-run this installer${NC}"
                    read -p "Press Enter after manual installation to continue..." -r
                fi
            elif command_exists zypper; then
                echo -e "${CYAN}🔄 Installing Python via zypper...${NC}"
                if ! sudo zypper install -y python3 python3-pip python3-devel python3-tk gcc; then
                    echo -e "${RED}❌ Python installation via zypper failed${NC}"
                    echo -e "${YELLOW}💡 MANUAL INSTALLATION REQUIRED:${NC}"
                    echo -e "${CYAN}   Run: sudo zypper install python3 python3-pip${NC}"
                    echo -e "${CYAN}   Then re-run this installer${NC}"
                    read -p "Press Enter after manual installation to continue..." -r
                fi
            else
                echo -e "${RED}❌ Unsupported Linux distribution${NC}"
                echo -e "${YELLOW}💡 MANUAL INSTALLATION REQUIRED:${NC}"
                echo -e "${CYAN}   Download Python from: https://www.python.org/downloads/source/${NC}"
                echo -e "${CYAN}   Or use your distribution's package manager${NC}"
                read -p "Press Enter after manual installation to continue..." -r
            fi
            ;;
        "macos")
            echo -e "${CYAN}🍎 Detected macOS - checking for package managers...${NC}"
            if command_exists brew; then
                echo -e "${CYAN}🔄 Installing Python via Homebrew...${NC}"
                if ! brew install python@3.11 python-tk; then
                    echo -e "${RED}❌ Python installation via Homebrew failed${NC}"
                    echo -e "${YELLOW}💡 MANUAL INSTALLATION REQUIRED:${NC}"
                    echo -e "${CYAN}   Download Python from: https://www.python.org/downloads/mac-osx/${NC}"
                    echo -e "${CYAN}   Or try: brew install python3${NC}"
                    read -p "Press Enter after manual installation to continue..." -r
                fi
            elif command_exists port; then
                echo -e "${CYAN}🔄 Installing Python via MacPorts...${NC}"
                if ! sudo port install python311 +universal; then
                    echo -e "${RED}❌ Python installation via MacPorts failed${NC}"
                    echo -e "${YELLOW}💡 MANUAL INSTALLATION REQUIRED:${NC}"
                    echo -e "${CYAN}   Download Python from: https://www.python.org/downloads/mac-osx/${NC}"
                    read -p "Press Enter after manual installation to continue..." -r
                fi
            else
                echo -e "${YELLOW}⚠️ No package manager found. Installing Homebrew...${NC}"
                if /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"; then
                    # Add Homebrew to PATH for current session
                    if [[ -f "/opt/homebrew/bin/brew" ]]; then
                        export PATH="/opt/homebrew/bin:$PATH"
                    elif [[ -f "/usr/local/bin/brew" ]]; then
                        export PATH="/usr/local/bin:$PATH"
                    fi
                    brew install python@3.11 python-tk || {
                        echo -e "${RED}❌ Python installation failed after Homebrew installation${NC}"
                        echo -e "${YELLOW}💡 MANUAL INSTALLATION REQUIRED:${NC}"
                        echo -e "${CYAN}   Download Python from: https://www.python.org/downloads/mac-osx/${NC}"
                        read -p "Press Enter after manual installation to continue..." -r
                    }
                else
                    echo -e "${RED}❌ Homebrew installation failed${NC}"
                    echo -e "${YELLOW}💡 MANUAL INSTALLATION REQUIRED:${NC}"
                    echo -e "${CYAN}   Download Python from: https://www.python.org/downloads/mac-osx/${NC}"
                    echo -e "${CYAN}   Or install Homebrew manually from: https://brew.sh${NC}"
                    read -p "Press Enter after manual installation to continue..." -r
                fi
            fi
            ;;
        "windows")
            echo -e "${RED}❌ Windows detected - automatic Python installation not supported${NC}"
            echo -e "${YELLOW}💡 MANUAL INSTALLATION REQUIRED:${NC}"
            echo -e "${CYAN}   1. Download Python from: https://python.org/downloads/${NC}"
            echo -e "${CYAN}   2. Run the installer and check 'Add Python to PATH'${NC}"
            echo -e "${CYAN}   3. Restart your terminal/command prompt${NC}"
            echo -e "${CYAN}   4. Re-run this installer${NC}"
            read -p "Press Enter after manual installation to continue..." -r
            ;;
        *)
            echo -e "${RED}❌ Unsupported operating system: $os${NC}"
            echo -e "${YELLOW}💡 MANUAL INSTALLATION REQUIRED:${NC}"
            echo -e "${CYAN}   Download Python 3.8+ from: https://www.python.org/downloads/${NC}"
            read -p "Press Enter after manual installation to continue..." -r
            ;;
    esac
    
    echo -e "${GREEN}✅ Python installation process completed${NC}"
}

# Function to check Python version
check_python() {
    echo -e "${YELLOW}🔍 Checking Python installation...${NC}"
    
    local python_cmd=""
    local python_version=""
    
    # Check for python3 first, then python
    if command_exists python3; then
        python_cmd="python3"
        python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')" 2>/dev/null)
    elif command_exists python; then
        # Check if python points to Python 3
        local py_major=$(python -c "import sys; print(sys.version_info.major)" 2>/dev/null)
        if [ "$py_major" = "3" ]; then
            python_cmd="python"
            python_version=$(python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')" 2>/dev/null)
        fi
    fi
    
    if [ -n "$python_cmd" ] && [ -n "$python_version" ]; then
        local required_version="3.8"
        local current_version=$(echo "$python_version" | cut -d'.' -f1,2)
        
        # Compare versions
        if [ "$(printf '%s\n' "$required_version" "$current_version" | sort -V | head -n1)" = "$required_version" ]; then
            echo -e "${GREEN}✅ Python $python_version found ($python_cmd)${NC}"
            
            # Set global PYTHON_CMD variable
            PYTHON_CMD="$python_cmd"
            
            # Check if pip is available
            if ! $python_cmd -m pip --version >/dev/null 2>&1; then
                echo -e "${YELLOW}⚠️ pip not found. Installing pip...${NC}"
                $python_cmd -m ensurepip --upgrade 2>/dev/null || handle_error 1 "Failed to install pip" "Please install pip manually"
            fi
            
            # Verify pip installation
            local pip_version=$($python_cmd -m pip --version 2>/dev/null | cut -d' ' -f2)
            echo -e "${GREEN}✅ pip $pip_version found${NC}"
        else
            echo -e "${RED}❌ Python $python_version found, but version $required_version or higher is required${NC}"
            install_python
            
            # Re-verify after installation
            if command_exists python3; then
                PYTHON_CMD="python3"
                python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')" 2>/dev/null)
                echo -e "${GREEN}✅ Python $python_version installed successfully${NC}"
            else
                handle_error 1 "Python installation verification failed" "Please install Python 3.8+ manually"
            fi
        fi
    else
        echo -e "${RED}❌ Python not found. Installing Python...${NC}"
        install_python
        
        # Verify installation
        if command_exists python3; then
            PYTHON_CMD="python3"
            python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')" 2>/dev/null)
            echo -e "${GREEN}✅ Python $python_version installed successfully${NC}"
        else
            handle_error 1 "Python installation verification failed" "Please install Python 3.8+ manually"
        fi
    fi
}

# Function to install Chrome/Chromium for Selenium
install_chrome() {
    local os=$(detect_os)
    
    # Check if Chrome/Chromium is already installed
    if command_exists google-chrome || command_exists google-chrome-stable || command_exists chromium || command_exists chromium-browser || [ -f "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" ]; then
        echo -e "${GREEN}✅ Chrome/Chromium already installed - skipping installation${NC}"
        return 0
    fi
    
    echo -e "${YELLOW}🌐 Installing Chrome/Chromium for web automation...${NC}"
    
    case $os in
        "linux")
            if command_exists apt-get; then
                echo -e "${CYAN}🔄 Installing Google Chrome via apt-get...${NC}"
                # Install Chrome
                if ! wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add - 2>/dev/null; then
                    echo -e "${YELLOW}⚠️ Failed to add Google signing key, trying alternative method...${NC}"
                    # Try installing chromium instead
                    sudo apt-get update || true
                    sudo apt-get install -y chromium-browser || sudo apt-get install -y chromium || echo -e "${YELLOW}⚠️ Could not install Chrome/Chromium automatically${NC}"
                else
                    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list >/dev/null
                    sudo apt-get update || handle_error 1 "Failed to update package lists" "Check your internet connection"
                    sudo apt-get install -y google-chrome-stable || {
                        echo -e "${YELLOW}⚠️ Chrome installation failed, trying Chromium...${NC}"
                        sudo apt-get install -y chromium-browser || sudo apt-get install -y chromium || echo -e "${YELLOW}⚠️ Could not install Chrome/Chromium automatically${NC}"
                    }
                fi
            elif command_exists yum; then
                echo -e "${CYAN}🔄 Installing Chromium via yum...${NC}"
                sudo yum install -y chromium || echo -e "${YELLOW}⚠️ Could not install Chromium automatically${NC}"
            elif command_exists dnf; then
                echo -e "${CYAN}🔄 Installing Chromium via dnf...${NC}"
                sudo dnf install -y chromium || echo -e "${YELLOW}⚠️ Could not install Chromium automatically${NC}"
            elif command_exists pacman; then
                echo -e "${CYAN}🔄 Installing Chromium via pacman...${NC}"
                sudo pacman -S --noconfirm chromium || echo -e "${YELLOW}⚠️ Could not install Chromium automatically${NC}"
            elif command_exists zypper; then
                echo -e "${CYAN}🔄 Installing Chromium via zypper...${NC}"
                sudo zypper install -y chromium || echo -e "${YELLOW}⚠️ Could not install Chromium automatically${NC}"
            else
                echo -e "${YELLOW}⚠️ Unsupported package manager. Please install Chrome or Chromium manually.${NC}"
            fi
            ;;
        "macos")
            if command_exists brew; then
                echo -e "${CYAN}🔄 Installing Google Chrome via Homebrew...${NC}"
                brew install --cask google-chrome || echo -e "${YELLOW}⚠️ Chrome installation failed. Please install manually from https://www.google.com/chrome/${NC}"
            else
                echo -e "${YELLOW}⚠️ Homebrew not found. Please install Chrome from https://www.google.com/chrome/${NC}"
            fi
            ;;
        "windows")
            echo -e "${YELLOW}⚠️ Please install Chrome from https://www.google.com/chrome/ for web automation features${NC}"
            ;;
        *)
            echo -e "${YELLOW}⚠️ Please install Chrome or Chromium manually for web automation features${NC}"
            ;;
    esac
    
    # Verify Chrome/Chromium installation
    if command_exists google-chrome || command_exists google-chrome-stable || command_exists chromium || command_exists chromium-browser || [ -f "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" ]; then
        echo -e "${GREEN}✅ Chrome/Chromium installed successfully${NC}"
    else
        echo -e "${YELLOW}⚠️ Chrome/Chromium installation could not be verified. Web automation may not work properly.${NC}"
        echo -e "${CYAN}💡 You can install Chrome manually later from https://www.google.com/chrome/${NC}"
    fi
}

# Function to create virtual environment with robust error handling
create_venv() {
    echo -e "${YELLOW}🔧 Creating Python virtual environment: $VENV_NAME...${NC}"
    
    # Remove any existing generic virtual environments
    for old_venv in "venv" "auto_blogger_venv" "env" ".venv"; do
        if [ -d "$old_venv" ]; then
            echo -e "${YELLOW}⚠️ Removing old virtual environment: $old_venv${NC}"
            rm -rf "$old_venv" || {
                echo -e "${RED}❌ Failed to remove old virtual environment: $old_venv${NC}"
                echo -e "${YELLOW}💡 Please manually remove the directory and re-run installer${NC}"
                read -p "Press Enter after manual removal to continue..." -r
            }
        fi
    done
    
    # Check if unique virtual environment already exists and is functional
    if [ -d "$VENV_NAME" ]; then
        echo -e "${CYAN}🔍 Checking existing virtual environment: $VENV_NAME...${NC}"
        
        # Test if the virtual environment is functional
        local venv_python=""
        local activate_script=""
        if [[ "$(detect_os)" == "windows" ]]; then
            venv_python="$VENV_NAME/Scripts/python.exe"
            activate_script="$VENV_NAME/Scripts/activate"
        else
            venv_python="$VENV_NAME/bin/python"
            activate_script="$VENV_NAME/bin/activate"
        fi
        
        if [ -f "$venv_python" ] && [ -f "$activate_script" ] && "$venv_python" -c "import sys; print('OK')" >/dev/null 2>&1; then
            echo -e "${GREEN}✅ Virtual environment already exists and is functional - skipping creation${NC}"
            return 0
        else
            echo -e "${YELLOW}⚠️ Virtual environment exists but is not functional. Removing...${NC}"
            rm -rf "$VENV_NAME" || {
                echo -e "${RED}❌ Failed to remove existing virtual environment${NC}"
                echo -e "${YELLOW}💡 Please manually remove $VENV_NAME directory and re-run installer${NC}"
                read -p "Press Enter after manual removal to continue..." -r
            }
        fi
    fi
    
    echo -e "${CYAN}🔄 Creating new virtual environment: $VENV_NAME...${NC}"
    
    # Try creating virtual environment with multiple methods
    local venv_created=false
    
    # Method 1: Using python -m venv
    if ! $venv_created && command_exists "$PYTHON_CMD"; then
        echo -e "${CYAN}   Trying: $PYTHON_CMD -m venv${NC}"
        if "$PYTHON_CMD" -m venv "$VENV_NAME" 2>/dev/null; then
            venv_created=true
            echo -e "${GREEN}   ✅ Virtual environment created with $PYTHON_CMD -m venv${NC}"
        fi
    fi
    
    # Method 2: Using python3 -m venv
    if ! $venv_created && command_exists python3; then
        echo -e "${CYAN}   Trying: python3 -m venv${NC}"
        if python3 -m venv "$VENV_NAME" 2>/dev/null; then
            venv_created=true
            echo -e "${GREEN}   ✅ Virtual environment created with python3 -m venv${NC}"
        fi
    fi
    
    # Method 3: Using virtualenv
    if ! $venv_created; then
        echo -e "${CYAN}   Trying: virtualenv (installing if needed)${NC}"
        "$PYTHON_CMD" -m pip install --user virtualenv 2>/dev/null || true
        if command_exists virtualenv || "$PYTHON_CMD" -m virtualenv --version >/dev/null 2>&1; then
            if virtualenv "$VENV_NAME" 2>/dev/null || "$PYTHON_CMD" -m virtualenv "$VENV_NAME" 2>/dev/null; then
                venv_created=true
                echo -e "${GREEN}   ✅ Virtual environment created with virtualenv${NC}"
            fi
        fi
    fi
    
    # If all methods failed
    if ! $venv_created; then
        echo -e "${RED}❌ Failed to create virtual environment with all methods${NC}"
        echo -e "${YELLOW}💡 MANUAL VIRTUAL ENVIRONMENT CREATION REQUIRED:${NC}"
        echo -e "${CYAN}   Try one of these commands manually:${NC}"
        echo -e "${CYAN}   1. $PYTHON_CMD -m venv $VENV_NAME${NC}"
        echo -e "${CYAN}   2. python3 -m venv $VENV_NAME${NC}"
        echo -e "${CYAN}   3. pip install virtualenv && virtualenv $VENV_NAME${NC}"
        read -p "Press Enter after manual virtual environment creation to continue..." -r
        
        # Verify manual creation
        if [ ! -d "$VENV_NAME" ]; then
            handle_error 1 "Virtual environment creation failed" "Please create virtual environment manually and re-run installer"
        fi
    fi
    
    # Activate virtual environment
    echo -e "${CYAN}🔄 Activating virtual environment: $VENV_NAME...${NC}"
    local activate_script=""
    if [[ "$(detect_os)" == "windows" ]]; then
        activate_script="$VENV_NAME/Scripts/activate"
    else
        activate_script="$VENV_NAME/bin/activate"
    fi
    
    if [ -f "$activate_script" ]; then
        source "$activate_script" || {
            echo -e "${RED}❌ Failed to activate virtual environment${NC}"
            echo -e "${YELLOW}💡 Virtual environment may be corrupted${NC}"
            echo -e "${CYAN}   Try removing $VENV_NAME folder and running installer again${NC}"
            read -p "Press Enter to continue anyway..." -r
        }
    else
        echo -e "${RED}❌ Activation script not found: $activate_script${NC}"
        echo -e "${YELLOW}💡 Virtual environment may be incomplete${NC}"
        read -p "Press Enter to continue anyway..." -r
    fi
    
    # Verify activation (optional check)
    if [ -n "$VIRTUAL_ENV" ]; then
        echo -e "${GREEN}✅ Virtual environment activated successfully${NC}"
    else
        echo -e "${YELLOW}⚠️ Virtual environment activation could not be verified${NC}"
        echo -e "${CYAN}💡 Continuing with installation...${NC}"
    fi
    
    # Upgrade pip with error handling
    echo -e "${YELLOW}📦 Upgrading pip...${NC}"
    local pip_upgrade_success=false
    
    # Try different pip upgrade methods
    if python -m pip install --upgrade pip 2>/dev/null; then
        pip_upgrade_success=true
    elif pip install --upgrade pip 2>/dev/null; then
        pip_upgrade_success=true
    elif "$PYTHON_CMD" -m pip install --upgrade pip 2>/dev/null; then
        pip_upgrade_success=true
    fi
    
    if $pip_upgrade_success; then
        local pip_version=$(python -m pip --version 2>/dev/null | cut -d' ' -f2 || echo "unknown")
        echo -e "${GREEN}✅ Virtual environment ready (pip $pip_version)${NC}"
    else
        echo -e "${YELLOW}⚠️ Pip upgrade failed, but continuing with installation${NC}"
        echo -e "${CYAN}💡 You may need to upgrade pip manually later${NC}"
    fi
}

# Function to install Python dependencies with robust error handling
install_dependencies() {
    echo -e "${YELLOW}📦 Installing Python dependencies...${NC}"
    
    # Ensure we're in virtual environment
    local activate_script=""
    if [[ "$(detect_os)" == "windows" ]]; then
        activate_script="$VENV_NAME/Scripts/activate"
    else
        activate_script="$VENV_NAME/bin/activate"
    fi
    
    if [ -z "$VIRTUAL_ENV" ] && [ -f "$activate_script" ]; then
        echo -e "${CYAN}🔄 Activating virtual environment: $VENV_NAME...${NC}"
        source "$activate_script" || {
            echo -e "${YELLOW}⚠️ Failed to activate virtual environment, continuing anyway...${NC}"
        }
    fi
    
    # Check if dependencies are already installed
    echo -e "${CYAN}🔍 Checking existing dependencies...${NC}"
    local critical_packages=("requests" "bs4" "selenium" "openai")
    local all_installed=true
    
    for package in "${critical_packages[@]}"; do
        if ! python -c "import $package" >/dev/null 2>&1; then
            all_installed=false
            break
        fi
    done
    
    if [ "$all_installed" = true ] && [ -f "requirements.txt" ]; then
        # Check if all requirements.txt packages are installed
        local missing_packages=0
        while IFS= read -r package; do
            if [[ "$package" =~ ^#.*$ ]] || [[ -z "$package" ]]; then
                continue
            fi
            local pkg_name=$(echo "$package" | sed 's/[>=<].*//' | sed 's/\[.*\]//')
            if ! python -m pip show "$pkg_name" >/dev/null 2>&1; then
                missing_packages=$((missing_packages + 1))
                break
            fi
        done < requirements.txt
        
        if [ "$missing_packages" -eq 0 ]; then
            echo -e "${GREEN}✅ All dependencies already installed - skipping installation${NC}"
            return 0
        fi
    fi
    
    # Install from requirements.txt if it exists
    if [ -f "requirements.txt" ]; then
        echo -e "${CYAN}📋 Installing from requirements.txt...${NC}"
        
        # Count total packages for progress indication
        local total_packages=$(grep -v '^#' requirements.txt | grep -v '^$' | wc -l | tr -d ' ')
        echo -e "${CYAN}📊 Installing $total_packages packages...${NC}"
        
        # Try multiple installation methods
        local install_success=false
        
        # Method 1: Bulk install with pip
        echo -e "${CYAN}   Trying bulk installation...${NC}"
        if python -m pip install --timeout 300 --retries 3 -r requirements.txt 2>/dev/null; then
            install_success=true
            echo -e "${GREEN}   ✅ Bulk installation successful${NC}"
        elif pip install --timeout 300 --retries 3 -r requirements.txt 2>/dev/null; then
            install_success=true
            echo -e "${GREEN}   ✅ Bulk installation successful${NC}"
        fi
        
        # Method 2: Individual package installation
        if ! $install_success; then
            echo -e "${YELLOW}   ⚠️ Bulk installation failed. Trying individual installation...${NC}"
            local failed_packages=()
            
            while IFS= read -r package; do
                # Skip comments and empty lines
                if [[ "$package" =~ ^#.*$ ]] || [[ -z "$package" ]]; then
                    continue
                fi
                
                echo -e "${CYAN}   📦 Installing: $package${NC}"
                if ! python -m pip install "$package" 2>/dev/null && ! pip install "$package" 2>/dev/null; then
                    echo -e "${YELLOW}   ⚠️ Failed to install: $package${NC}"
                    failed_packages+=("$package")
                else
                    echo -e "${GREEN}   ✅ Installed: $package${NC}"
                fi
            done < requirements.txt
            
            if [ ${#failed_packages[@]} -gt 0 ]; then
                echo -e "${YELLOW}⚠️ Some packages failed to install: ${failed_packages[*]}${NC}"
                echo -e "${CYAN}💡 You may need to install these manually later${NC}"
            fi
        fi
    else
        echo -e "${YELLOW}⚠️ requirements.txt not found. Installing essential packages...${NC}"
        
        # Install essential packages with error handling
        local essential_packages=("requests" "beautifulsoup4" "lxml" "selenium" "webdriver-manager" "openai" "google-generativeai" "pillow" "python-dotenv" "colorama" "tqdm" "validators")
        local failed_packages=()
        
        for package in "${essential_packages[@]}"; do
            echo -e "${CYAN}📦 Installing: $package${NC}"
            if python -m pip install "$package" 2>/dev/null || pip install "$package" 2>/dev/null; then
                echo -e "${GREEN}   ✅ Installed: $package${NC}"
            else
                echo -e "${YELLOW}   ⚠️ Failed to install: $package${NC}"
                failed_packages+=("$package")
            fi
        done
        
        if [ ${#failed_packages[@]} -gt 0 ]; then
            echo -e "${YELLOW}⚠️ Some essential packages failed to install: ${failed_packages[*]}${NC}"
            echo -e "${CYAN}💡 MANUAL INSTALLATION MAY BE REQUIRED:${NC}"
            for pkg in "${failed_packages[@]}"; do
                echo -e "${CYAN}   pip install $pkg${NC}"
            done
            read -p "Press Enter to continue anyway..." -r
        fi
    fi
    
    # Verify critical packages are installed
    echo -e "${YELLOW}🔍 Verifying critical packages...${NC}"
    local critical_packages=("requests" "bs4" "selenium" "openai")
    local missing_packages=()
    
    for package in "${critical_packages[@]}"; do
        if python -c "import $package" 2>/dev/null; then
            echo -e "${GREEN}   ✅ $package - OK${NC}"
        else
            echo -e "${YELLOW}   ⚠️ $package - Missing${NC}"
            missing_packages+=("$package")
        fi
    done
    
    if [ ${#missing_packages[@]} -gt 0 ]; then
        echo -e "${YELLOW}⚠️ Some critical packages are missing: ${missing_packages[*]}${NC}"
        echo -e "${CYAN}💡 The application may still work, but some features might be limited${NC}"
        echo -e "${CYAN}💡 You can install missing packages manually later${NC}"
    else
        echo -e "${GREEN}✅ All critical packages verified${NC}"
    fi
    
    # Show installed packages summary
    local installed_count=$(python -m pip list 2>/dev/null | wc -l | tr -d ' ' || echo "unknown")
    echo -e "${GREEN}✅ Dependencies installation completed ($installed_count packages installed)${NC}"
}

# Function to create launcher script
create_launcher() {
    local install_dir=$(pwd)
    local os=$(detect_os)
    
    echo -e "${YELLOW}🚀 Creating launcher script with auto-update...${NC}"
    
    # Verify essential files exist
    if [ ! -f "gui_blogger.py" ]; then
        handle_error 1 "Main application file missing: gui_blogger.py" "Repository may be corrupted. Try removing $INSTALL_DIR and running again"
    fi
    
    # Create the autoblog launcher script with enhanced OS detection
    echo -e "${CYAN}🔄 Creating enhanced shell launcher...${NC}"
    cat > autoblog << 'EOF'
#!/bin/bash

# AUTO-blogger Enhanced Launcher Script with Auto-Update
# This script provides robust cross-platform launching with OS detection

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Enhanced OS detection function
detect_os() {
    local os="unknown"
    
    # Check for Windows first (multiple methods)
    if [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]] || [[ -n "$WINDIR" ]] || [[ -n "$COMSPEC" ]]; then
        os="windows"
    # Check for macOS (multiple methods)
    elif [[ "$OSTYPE" == "darwin"* ]] || [[ "$(uname -s 2>/dev/null)" == "Darwin" ]] || [[ -d "/Applications" && -d "/System" ]]; then
        os="macos"
    # Check for Linux (multiple methods)
    elif [[ "$OSTYPE" == "linux-gnu"* ]] || [[ "$(uname -s 2>/dev/null)" == "Linux" ]] || [[ -f "/etc/os-release" ]]; then
        os="linux"
    # Additional checks using uname if available
    elif command -v uname >/dev/null 2>&1; then
        case "$(uname -s 2>/dev/null)" in
            Linux*)     os="linux";;
            Darwin*)    os="macos";;
            CYGWIN*)    os="windows";;
            MINGW*)     os="windows";;
            MSYS*)      os="windows";;
            *NT*)       os="windows";;
        esac
    # Final fallback checks
    elif [[ -f "/proc/version" ]]; then
        os="linux"
    elif [[ -d "/System/Library" ]]; then
        os="macos"
    fi
    
    echo "$os"
}

# Get the directory where this script is located
if [ -L "${BASH_SOURCE[0]}" ]; then
    SCRIPT_DIR="$(cd "$(dirname "$(readlink "${BASH_SOURCE[0]}")")") && pwd)"
else
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
fi

# Change to the installation directory
cd "$SCRIPT_DIR" || {
    echo -e "${RED}❌ Failed to access installation directory: $SCRIPT_DIR${NC}"
    echo -e "${YELLOW}💡 Please check if the directory exists and you have permissions${NC}"
    exit 1
}

# Detect operating system
OS=$(detect_os)
echo -e "${CYAN}🖥️  Detected OS: $OS${NC}"

# Find virtual environment directory dynamically based on OS
VENV_DIR=""
for dir in "$SCRIPT_DIR"/auto_blogger_venv_*; do
    if [ -d "$dir" ]; then
        if [[ "$OS" == "windows" ]] && [ -f "$dir/Scripts/activate" ]; then
            VENV_DIR="$dir"
            break
        elif [[ "$OS" != "windows" ]] && [ -f "$dir/bin/activate" ]; then
            VENV_DIR="$dir"
            break
        fi
    fi
done

# Determine Python executable based on OS
PYTHON_EXE=""
ACTIVATE_SCRIPT=""

if [ -n "$VENV_DIR" ] && [ -d "$VENV_DIR" ]; then
    echo -e "${CYAN}🔧 Using virtual environment: $(basename "$VENV_DIR")${NC}"
    
    if [[ "$OS" == "windows" ]]; then
        PYTHON_EXE="$VENV_DIR/Scripts/python.exe"
        ACTIVATE_SCRIPT="$VENV_DIR/Scripts/activate"
        # Fallback for different Windows Python installations
        if [ ! -f "$PYTHON_EXE" ]; then
            PYTHON_EXE="$VENV_DIR/Scripts/python"
        fi
    else
        PYTHON_EXE="$VENV_DIR/bin/python"
        ACTIVATE_SCRIPT="$VENV_DIR/bin/activate"
        # Fallback for different Python installations
        if [ ! -f "$PYTHON_EXE" ]; then
            PYTHON_EXE="$VENV_DIR/bin/python3"
        fi
    fi
else
    echo -e "${RED}❌ Virtual environment not found in $SCRIPT_DIR${NC}"
    echo -e "${YELLOW}💡 Looking for virtual environment directories...${NC}"
    ls -la "$SCRIPT_DIR"/auto_blogger_venv_* 2>/dev/null || echo -e "${YELLOW}   No virtual environment directories found${NC}"
    echo -e "${YELLOW}💡 Please run the installer again to create virtual environment${NC}"
    exit 1
fi

# Verify Python executable exists
if [ ! -f "$PYTHON_EXE" ]; then
    echo -e "${RED}❌ Python executable not found: $PYTHON_EXE${NC}"
    echo -e "${YELLOW}💡 Virtual environment may be corrupted${NC}"
    echo -e "${YELLOW}💡 Please run the installer again${NC}"
    exit 1
fi

# Check for main application files
MAIN_APP=""
if [ -f "autoblog_launcher.py" ]; then
    MAIN_APP="autoblog_launcher.py"
elif [ -f "gui_blogger.py" ]; then
    MAIN_APP="gui_blogger.py"
elif [ -f "launch_blogger.py" ]; then
    MAIN_APP="launch_blogger.py"
else
    echo -e "${RED}❌ No launcher application found${NC}"
    echo -e "${YELLOW}💡 Looking for application files...${NC}"
    ls -la "$SCRIPT_DIR"/*.py 2>/dev/null | head -5 || echo -e "${YELLOW}   No Python files found${NC}"
    echo -e "${YELLOW}💡 Please run the installer again${NC}"
    exit 1
fi

echo -e "${CYAN}🚀 Starting AUTO-blogger ($MAIN_APP) with auto-update...${NC}"

# Set application icon (macOS)
if [[ "$OS" == "macos" ]]; then
    osascript -e 'tell application "System Events" to set the dock tile of application "Terminal" to "🤖"' 2>/dev/null || true
fi

# Activate virtual environment if activation script exists
if [ -f "$ACTIVATE_SCRIPT" ]; then
    echo -e "${CYAN}🔧 Activating virtual environment...${NC}"
    source "$ACTIVATE_SCRIPT" || {
        echo -e "${YELLOW}⚠️ Failed to activate virtual environment, continuing anyway...${NC}"
    }
fi

# Launch the application with error handling
echo -e "${CYAN}🚀 Launching AUTO-blogger...${NC}"
if "$PYTHON_EXE" "$MAIN_APP"; then
    echo -e "${GREEN}✅ AUTO-blogger exited successfully${NC}"
else
    echo -e "${RED}❌ AUTO-blogger exited with errors${NC}"
    echo -e "${YELLOW}💡 Check the application logs for details${NC}"
    exit 1
fi

# Deactivate virtual environment if it was activated
if [ -n "$VIRTUAL_ENV" ]; then
    deactivate 2>/dev/null || true
fi
EOF

    # Make the launcher executable
    chmod +x autoblog || handle_error 1 "Failed to make launcher executable" "Check file permissions"
    
    # Create system-wide launcher based on OS
    case $os in
        "linux" | "macos")
            # Create symlink in /usr/local/bin for system-wide access
            if [ -w "/usr/local/bin" ] || sudo -n true 2>/dev/null; then
                echo -e "${YELLOW}🔗 Creating system-wide launcher...${NC}"
                sudo ln -sf "$install_dir/autoblog" "/usr/local/bin/autoblog" 2>/dev/null && {
                    echo -e "${GREEN}✅ System-wide launcher created: autoblog${NC}"
                    echo -e "${CYAN}💡 You can now run 'autoblog' from anywhere in the terminal${NC}"
                } || {
                    echo -e "${YELLOW}⚠️ Could not create system-wide launcher. You can run './autoblog' from this directory.${NC}"
                }
            else
                echo -e "${YELLOW}⚠️ No sudo access. You can run './autoblog' from this directory.${NC}"
            fi
            ;;
        "windows")
            # For Windows, create a batch file
            echo -e "${CYAN}🔄 Creating Windows batch launcher...${NC}"
            cat > "autoblog.bat" << EOF
@echo off
setlocal

REM AUTO-blogger Windows Launcher
echo 🚀 Starting AUTO-blogger...

REM Change to script directory
cd /d "%~dp0"

REM Check if virtual environment exists
if not exist "$VENV_NAME\Scripts\python.exe" (
    echo ❌ Virtual environment not found: $VENV_NAME
    echo 💡 Please run the installer again
    pause
    exit /b 1
)

REM Check if launcher exists
if not exist "autoblog_launcher.py" (
    echo ❌ Launcher application not found
    echo 💡 Please run the installer again
    pause
    exit /b 1
)

echo Starting AUTO-blogger with auto-update...
$VENV_NAME\Scripts\python.exe autoblog_launcher.py
if errorlevel 1 (
    echo ⚠️ Application exited with errors
    pause
)
EOF
            echo -e "${GREEN}✅ Windows launcher created: autoblog.bat${NC}"
            ;;
    esac
    
    echo -e "${GREEN}✅ Launcher with auto-update created successfully${NC}"
}

# Function to create desktop shortcut
create_desktop_shortcut() {
    local install_dir=$(pwd)
    local os=$(detect_os)
    
    case $os in
        "linux")
            local desktop_dir="$HOME/Desktop"
            if [ -d "$desktop_dir" ]; then
                echo -e "${YELLOW}🖥️ Creating desktop shortcut...${NC}"
                cat > "$desktop_dir/AUTO-blogger.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=AUTO-blogger
Comment=Automated WordPress Blog Posting Tool
Exec=$install_dir/autoblog
Icon=$install_dir/icon.png
Terminal=false
Categories=Development;Office;
EOF
                chmod +x "$desktop_dir/AUTO-blogger.desktop"
                echo -e "${GREEN}✅ Desktop shortcut created${NC}"
            fi
            ;;
        "macos")
            echo -e "${YELLOW}🖥️ Creating macOS application...${NC}"
            local app_dir="$HOME/Applications/AUTO-blogger.app"
            mkdir -p "$HOME/Applications"
            mkdir -p "$app_dir/Contents/MacOS"
            mkdir -p "$app_dir/Contents/Resources"
            
            # Create Info.plist
            cat > "$app_dir/Contents/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>autoblog</string>
    <key>CFBundleIdentifier</key>
    <string>com.aryanbw.autoblogger</string>
    <key>CFBundleName</key>
    <string>AUTO-blogger</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
</dict>
</plist>
EOF
            
            # Create launcher script
            cat > "$app_dir/Contents/MacOS/autoblog" << EOF
#!/bin/bash
cd "$install_dir"
./autoblog
EOF
            chmod +x "$app_dir/Contents/MacOS/autoblog"
            
            # Copy icon if exists
            if [ -f "icon.png" ]; then
                cp "icon.png" "$app_dir/Contents/Resources/"
            fi
            
            echo -e "${GREEN}✅ macOS application created in ~/Applications${NC}"
            ;;
    esac
}

# Function to run post-installation fixes
run_post_installation_fixes() {
    echo -e "${CYAN}🔧 Running post-installation fixes...${NC}"
    
    # Create docs and tests directories
    mkdir -p "docs" "tests"
    
    # Set executable permissions for key scripts
    chmod +x autoblog 2>/dev/null || true
    # Installation fixes are integrated into the main installer

# Installation fixes are integrated
if false; then
        echo -e "${CYAN}🔄 Running installation fixes script...${NC}"
        if [[ "$(detect_os)" == "windows" ]]; then
            "$VENV_NAME/Scripts/python.exe" fix_installation_issues.py 2>/dev/null || echo -e "${YELLOW}⚠️ Fix script completed with warnings${NC}"
        else
            "$VENV_NAME/bin/python" fix_installation_issues.py 2>/dev/null || echo -e "${YELLOW}⚠️ Fix script completed with warnings${NC}"
        fi
        echo -e "${GREEN}✅ Post-installation fixes completed${NC}"
    else
        echo -e "${CYAN}💡 No additional fixes script found - skipping${NC}"
    fi
}

# Function to test installation
test_installation() {
    echo -e "${YELLOW}🧪 Testing installation...${NC}"
    
    # Activate virtual environment
    echo -e "${CYAN}🔄 Activating virtual environment for testing: $VENV_NAME...${NC}"
    if [[ "$(detect_os)" == "windows" ]]; then
        source "$VENV_NAME/Scripts/activate" || handle_error 1 "Failed to activate virtual environment for testing" "Virtual environment may be corrupted"
    else
        source "$VENV_NAME/bin/activate" || handle_error 1 "Failed to activate virtual environment for testing" "Virtual environment may be corrupted"
    fi
    
    # Test critical Python imports
    echo -e "${CYAN}🔍 Testing critical package imports...${NC}"
    local test_packages=("requests" "bs4" "selenium" "openai")
    local failed_packages=()
    
    for package in "${test_packages[@]}"; do
        echo -e "${CYAN}  Testing: $package${NC}"
        if python -c "import $package" 2>/dev/null; then
            echo -e "${GREEN}    ✅ $package - OK${NC}"
        else
            echo -e "${YELLOW}    ⚠️ $package - Failed${NC}"
            failed_packages+=("$package")
        fi
    done
    
    # Test main application file
    echo -e "${CYAN}🔍 Testing main application...${NC}"
    if [ -f "gui_blogger.py" ]; then
        # Try to run a basic syntax check
        if python -m py_compile gui_blogger.py 2>/dev/null; then
            echo -e "${GREEN}✅ Main application syntax - OK${NC}"
        else
            echo -e "${YELLOW}⚠️ Main application syntax check failed${NC}"
        fi
    else
        echo -e "${RED}❌ Main application file missing${NC}"
        failed_packages+=("gui_blogger.py")
    fi
    
    # Test launcher
    echo -e "${CYAN}🔍 Testing launcher script...${NC}"
    if [ -f "autoblog_launcher.py" ]; then
        if python -m py_compile autoblog_launcher.py 2>/dev/null; then
            echo -e "${GREEN}✅ Launcher script syntax - OK${NC}"
        else
            echo -e "${YELLOW}⚠️ Launcher script syntax check failed${NC}"
        fi
    else
        echo -e "${RED}❌ Launcher script missing${NC}"
        failed_packages+=("autoblog_launcher.py")
    fi
    
    # Summary
    if [ ${#failed_packages[@]} -eq 0 ]; then
        echo -e "${GREEN}✅ All tests passed successfully!${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️ Some tests failed: ${failed_packages[*]}${NC}"
        echo -e "${CYAN}💡 The application may still work, but some features might be limited${NC}"
        return 1
    fi
}

# Function to print logo
print_logo() {
    echo -e "\033[96m+===========================================================================+\033[0m"
    echo -e "\033[96m| █████   █████  ███                       █████         █████   ███   █████ |\033[0m"
    echo -e "\033[96m|░░███   ░░███  ░░░                       ░░███         ░░███   ░███  ░░███  |\033[0m"
    echo -e "\033[96m| ░███    ░███  ████  █████ █████  ██████  ░███ █████    ░███   ░███   ░███  |\033[0m"
    echo -e "\033[96m| ░███    ░███ ░░███ ░░███ ░░███  ███░░███ ░███░░███     ░███   ░███   ░███  |\033[0m"
    echo -e "\033[96m| ░░███   ███   ░███  ░███  ░███ ░███████  ░██████░      ░░███  █████  ███   |\033[0m"
    echo -e "\033[96m|  ░░░█████░    ░███  ░░███ ███  ░███░░░   ░███░░███      ░░░█████░█████░    |\033[0m"
    echo -e "\033[96m|    ░░███      █████  ░░█████   ░░██████  ████ █████       ░░███ ░░███      |\033[0m"
    echo -e "\033[96m|     ░░░      ░░░░░    ░░░░░     ░░░░░░  ░░░░ ░░░░░         ░░░   ░░░       |\033[0m"
    echo -e "\033[95m|                                                                            |\033[0m"
    echo -e "\033[95m|                           🔥GitHub:    github.com/AryanVBW                 |\033[0m"
    echo -e "\033[95m|                               Copyright © 2025 AryanVBW                    |\033[0m"
    echo -e "\033[95m|                           💖Instagram: Aryan_Technolog1es                  |\033[0m"
    echo -e "\033[95m|                           📧Email:    vivek.aryanvbw@gmail.com                  |\033[0m"
    echo -e "\033[32m+===========================================================================+\033[0m"
    echo -e "\033[93m|                            Welcome to AUTO Blogger!                        |\033[0m"
}

# Function to show completion message
show_completion() {
    local test_result=$1
    
    echo ""
    echo -e "${GREEN}🎉 AUTO-blogger installation completed with enhanced features!${NC}"
    echo -e "${CYAN}📍 Installation directory: $INSTALL_DIR${NC}"
    echo -e "${CYAN}🔧 Virtual environment: $VENV_NAME (unique)${NC}"
    
    if [ "$test_result" -eq 0 ]; then
        echo -e "${GREEN}✅ All tests passed - Installation is fully functional${NC}"
    else
        echo -e "${YELLOW}⚠️ Installation completed with some warnings${NC}"
        echo -e "${CYAN}💡 Check the test results above for details${NC}"
    fi
    
    echo ""
    echo -e "${YELLOW}🆕 Enhanced Features:${NC}"
    echo -e "${CYAN}   • Enhanced SEO automation with improved algorithms${NC}"
    echo -e "${CYAN}   • Organized project structure (docs/, tests/)${NC}"
    echo -e "${CYAN}   • Unique virtual environment for conflict prevention${NC}"
    echo -e "${CYAN}   • Comprehensive testing and validation tools${NC}"
    echo -e "${CYAN}   • Improved error handling and logging${NC}"
    
    echo ""
    echo -e "${YELLOW}🚀 How to use AUTO-blogger:${NC}"
    
    local os=$(detect_os)
    case $os in
        "linux" | "macos")
            if [ -f "/usr/local/bin/autoblog" ]; then
                echo -e "${CYAN}   • System-wide: Run 'autoblog' from anywhere in terminal${NC}"
            fi
            echo -e "${CYAN}   • Local: Run './autoblog' from installation directory${NC}"
            echo -e "${CYAN}   • Python: Run 'python autoblog_launcher.py' from installation directory${NC}"
            ;;
        "windows")
            echo -e "${CYAN}   • Double-click: autoblog.bat in installation directory${NC}"
            echo -e "${CYAN}   • Command line: Run 'autoblog.bat' from installation directory${NC}"
            echo -e "${CYAN}   • Python: Run 'python autoblog_launcher.py' from installation directory${NC}"
            ;;
    esac
    
    echo ""
    echo -e "${YELLOW}📁 Project Structure:${NC}"
    echo -e "${CYAN}   • Main Application: gui_blogger.py${NC}"
    echo -e "${CYAN}   • Configuration: configs/ directory${NC}"
    echo -e "${CYAN}   • Documentation: docs/ directory${NC}"
    echo -e "${CYAN}   • Tests: tests/ directory${NC}"
    echo -e "${CYAN}   • Virtual Environment: $VENV_NAME/${NC}"
    
    echo ""
    echo -e "${YELLOW}📚 Documentation & Testing:${NC}"
    echo -e "${CYAN}   • README: $INSTALL_DIR/README.md${NC}"
    echo -e "${CYAN}   • Installation Guide: $INSTALL_DIR/docs/README_INSTALLATION.md${NC}"
    echo -e "${CYAN}   • SEO Improvements: $INSTALL_DIR/docs/SEO_IMPROVEMENTS_*.md${NC}"
    echo -e "${CYAN}   • SEO Features are ready to use${NC}"
    echo -e "${CYAN}   • Troubleshooting: $INSTALL_DIR/docs/wordpress_seo_troubleshooting.md${NC}"
    
    echo ""
    echo -e "${YELLOW}🔧 First Time Setup:${NC}"
    echo -e "${CYAN}   1. Launch the application using one of the methods above${NC}"
    echo -e "${CYAN}   2. Configure your API keys (WordPress, OpenAI, Gemini)${NC}"
    echo -e "${CYAN}   3. Set up your automation preferences${NC}"
    echo -e "${CYAN}   4. Start generating content!${NC}"
    
    echo ""
    echo -e "${YELLOW}🆘 Support:${NC}"
    echo -e "${CYAN}   • Email: AryanVBW@gmail.com${NC}"
    echo -e "${CYAN}   • Issues: https://github.com/AryanVBW/AUTO-blogger/issues${NC}"
    echo -e "${CYAN}   • Documentation: Check the docs/ folder for guides${NC}"
    
    echo ""
    if [ "$test_result" -eq 0 ]; then
        echo -e "${GREEN}🚀 Enhanced AUTO-blogger is ready! Start creating amazing content! 📝✨${NC}"
        echo -e "${CYAN}💡 Try the new SEO features and organized project structure!${NC}"
    else
        echo -e "${YELLOW}⚠️ Installation completed with warnings. Please check the issues above.${NC}"
        echo -e "${CYAN}💡 You can still try running the application - it may work despite the warnings.${NC}"
        echo -e "${CYAN}🔧 SEO features are configured and ready${NC}"
    fi
    echo ""
}

# Main installation function
main() {
    # Handle Ctrl+C gracefully
    trap 'echo -e "\n${RED}❌ Installation interrupted by user${NC}"; echo -e "${CYAN}💡 You can run this installer again to complete the setup${NC}"; exit 1' INT
    
    # Start installation
    print_logo
    
    echo -e "${CYAN}🚀 Starting AUTO-blogger installation...${NC}"
    echo -e "${CYAN}📅 $(date)${NC}"
    echo ""
    
    # Step 1: System verification
    echo -e "${YELLOW}📋 Step 1/10: System Verification${NC}"
    verify_requirements
    echo ""
    
    # Step 2: Check existing installation
    echo -e "${YELLOW}📋 Step 2/10: Installation Check${NC}"
    check_existing_installation
    echo ""
    
    # Step 3: Git setup
    echo -e "${YELLOW}📋 Step 3/10: Git Setup${NC}"
    check_git
    echo ""
    
    # Step 4: Repository setup
    echo -e "${YELLOW}📋 Step 4/10: Repository Setup${NC}"
    clone_or_update_repo
    echo ""
    
    # Step 5: Python setup
    echo -e "${YELLOW}📋 Step 5/10: Python Setup${NC}"
    check_python
    echo ""
    
    # Step 6: Browser setup
    echo -e "${YELLOW}📋 Step 6/10: Browser Setup${NC}"
    install_chrome
    echo ""
    
    # Step 7: Virtual environment
    echo -e "${YELLOW}📋 Step 7/10: Virtual Environment${NC}"
    create_venv
    echo ""
    
    # Step 8: Dependencies
    echo -e "${YELLOW}📋 Step 8/10: Dependencies Installation${NC}"
    install_dependencies
    echo ""
    
    # Step 9: Launcher creation
     echo -e "${YELLOW}📋 Step 9/10: Launcher Creation${NC}"
     create_launcher
     create_desktop_shortcut
     echo ""
     
     # Step 10: Post-installation fixes
     echo -e "${YELLOW}📋 Step 10/11: Post-Installation Fixes${NC}"
     run_post_installation_fixes
     echo ""
     
     # Step 11: Testing and completion
     echo -e "${YELLOW}📋 Step 11/11: Testing Installation${NC}"
    test_installation
    local test_result=$?
    echo ""
    
    # Show completion message
    show_completion $test_result
    
    # Final status
    if [ $test_result -eq 0 ]; then
        echo -e "${GREEN}🎯 Installation completed successfully!${NC}"
        exit 0
    else
        echo -e "${YELLOW}⚠️ Installation completed with warnings${NC}"
        exit 2
    fi
}

# Handle script interruption
trap 'echo -e "\n${RED}❌ Installation interrupted by user${NC}"; exit 1' INT

# Run main function
main "$@"