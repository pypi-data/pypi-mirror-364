# AUTO-blogger Installation Script with Auto-Update (PowerShell)
# Copyright © 2025 AryanVBW
# GitHub: https://github.com/AryanVBW/AUTO-blogger

param(
    [switch]$AutoUpdate = $false,
    [switch]$NonInteractive = $false
)

# Set error action preference
$ErrorActionPreference = "Stop"

# Environment variables for automation
# Set -AutoUpdate for automatic updates without prompts
# Set -NonInteractive for completely non-interactive installation
if ($env:AUTO_UPDATE -eq "true") { $AutoUpdate = $true }
if ($env:NON_INTERACTIVE -eq "true") { $NonInteractive = $true }

# Check if running in non-interactive environment
if (-not [Environment]::UserInteractive) {
    $NonInteractive = $true
}

# Configuration
$REPO_URL = "https://github.com/AryanVBW/AUTO-blogger.git"
$INSTALL_DIR = "$env:USERPROFILE\AUTO-blogger"
$APP_NAME = "AUTO-blogger"
# Generate unique virtual environment name to avoid conflicts
$VENV_NAME = "auto_blogger_venv_$(Get-Random -Minimum 1000 -Maximum 9999)"

# Color definitions for console output
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    
    $colorMap = @{
        "Red" = "Red"
        "Green" = "Green"
        "Yellow" = "Yellow"
        "Blue" = "Blue"
        "Cyan" = "Cyan"
        "White" = "White"
    }
    
    Write-Host $Message -ForegroundColor $colorMap[$Color]
}

# Logo function
function Show-Logo {
    Write-ColorOutput "+===========================================================================+" "Cyan"
    Write-ColorOutput "| █████   █████  ███                       █████         █████   ███   █████ |" "Cyan"
    Write-ColorOutput "|░░███   ░░███  ░░░                       ░░███         ░░███   ░███  ░░███  |" "Cyan"
    Write-ColorOutput "| ░███    ░███  ████  █████ █████  ██████  ░███ █████    ░███   ░███   ░███  |" "Cyan"
    Write-ColorOutput "| ░███    ░███ ░░███ ░░███ ░░███  ███░░███ ░███░░███     ░███   ░███   ░███  |" "Cyan"
    Write-ColorOutput "| ░░███   ███   ░███  ░███  ░███ ░███████  ░██████░      ░░███  █████  ███   |" "Cyan"
    Write-ColorOutput "|  ░░░█████░    ░███  ░░███ ███  ░███░░░   ░███░░███      ░░░█████░█████░    |" "Cyan"
    Write-ColorOutput "|    ░░███      █████  ░░█████   ░░██████  ████ █████       ░░███ ░░███      |" "Cyan"
    Write-ColorOutput "|     ░░░      ░░░░░    ░░░░░     ░░░░░░  ░░░░ ░░░░░         ░░░   ░░░       |" "Cyan"
    Write-ColorOutput "|                                                                            |" "Blue"
    Write-ColorOutput "|                           🔥GitHub:    github.com/AryanVBW                 |" "Blue"
    Write-ColorOutput "|                               Copyright © 2025 AryanVBW                    |" "Blue"
    Write-ColorOutput "|                           💖Instagram: Aryan_Technolog1es                  |" "Blue"
    Write-ColorOutput "|                           📧Email:    vivek.aryanvbw@gmail.com                  |" "Blue"
    Write-ColorOutput "+===========================================================================+" "Green"
    Write-ColorOutput "|                            Welcome to AUTO Blogger!                        |" "Yellow"
}

# Function to handle errors with detailed messages
function Handle-Error {
    param(
        [int]$ErrorCode,
        [string]$ErrorMessage,
        [string]$Solution = ""
    )
    
    Write-ColorOutput "❌ ERROR: $ErrorMessage" "Red"
    if ($Solution) {
        Write-ColorOutput "💡 SOLUTION: $Solution" "Yellow"
    }
    Write-ColorOutput "📧 For support, contact: AryanVBW@gmail.com" "Cyan"
    exit $ErrorCode
}

# Function to check if command exists
function Test-CommandExists {
    param([string]$Command)
    
    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

# Function to check if AUTO-blogger is already installed
function Test-ExistingInstallation {
    Write-ColorOutput "🔍 Checking for existing installation..." "Yellow"
    
    if (Test-Path $INSTALL_DIR) {
        Write-ColorOutput "⚠️ AUTO-blogger is already installed at: $INSTALL_DIR" "Yellow"
        
        # Check for non-interactive mode or auto-update flag
        if ($AutoUpdate -or $NonInteractive) {
            Write-ColorOutput "🔄 Non-interactive mode detected - proceeding with update..." "Cyan"
            Write-ColorOutput "✅ Proceeding with update..." "Green"
            return
        }
        
        Write-ColorOutput "What would you like to do?" "Cyan"
        Write-Host "1) Update existing installation (recommended)"
        Write-Host "2) Remove and reinstall completely"
        Write-Host "3) Cancel installation"
        Write-Host ""
        Write-ColorOutput "💡 Tip: Use -AutoUpdate parameter for automatic updates" "Yellow"
        
        $choice = Read-Host "Enter your choice (1-3) [default: 1]"
        if ([string]::IsNullOrEmpty($choice)) { $choice = "1" }
        
        switch ($choice) {
            "1" {
                Write-ColorOutput "✅ Proceeding with update..." "Green"
                return
            }
            "2" {
                Write-ColorOutput "🗑️ Removing existing installation..." "Yellow"
                try {
                    Remove-Item -Path $INSTALL_DIR -Recurse -Force
                    Write-ColorOutput "✅ Existing installation removed" "Green"
                }
                catch {
                    Handle-Error 1 "Failed to remove existing installation" "Check permissions and try running as Administrator"
                }
                return
            }
            "3" {
                Write-ColorOutput "👋 Installation cancelled by user" "Blue"
                exit 0
            }
            default {
                Write-ColorOutput "❌ Invalid choice. Defaulting to update..." "Red"
                return
            }
        }
    }
    else {
        Write-ColorOutput "✅ No existing installation found" "Green"
    }
}

# Function to verify system requirements
function Test-SystemRequirements {
    Write-ColorOutput "🔍 Verifying system requirements..." "Yellow"
    
    # Check OS support
    if ($PSVersionTable.Platform -and $PSVersionTable.Platform -ne "Win32NT") {
        Handle-Error 1 "Unsupported operating system" "This PowerShell installer is designed for Windows only"
    }
    
    Write-ColorOutput "✅ Operating System: Windows" "Green"
    
    # Check internet connectivity
    Write-ColorOutput "🌐 Testing internet connectivity..." "Cyan"
    try {
        $null = Test-NetConnection -ComputerName "google.com" -Port 80 -InformationLevel Quiet -ErrorAction Stop
        Write-ColorOutput "✅ Internet connection verified" "Green"
    }
    catch {
        try {
            $null = Test-NetConnection -ComputerName "8.8.8.8" -Port 53 -InformationLevel Quiet -ErrorAction Stop
            Write-ColorOutput "✅ Internet connection verified" "Green"
        }
        catch {
            Handle-Error 1 "No internet connection" "Please check your internet connection and try again"
        }
    }
    
    # Check available disk space (at least 500MB)
    Write-ColorOutput "💾 Checking disk space..." "Cyan"
    $drive = (Get-Item $env:USERPROFILE).PSDrive
    $freeSpace = (Get-WmiObject -Class Win32_LogicalDisk -Filter "DeviceID='$($drive.Name):'").FreeSpace
    if ($freeSpace -lt 500MB) {
        Handle-Error 1 "Insufficient disk space" "At least 500MB of free space required"
    }
    Write-ColorOutput "✅ Sufficient disk space available" "Green"
    
    # Check write permissions
    Write-ColorOutput "🔐 Checking permissions..." "Cyan"
    $parentDir = Split-Path $INSTALL_DIR -Parent
    if (-not (Test-Path $parentDir)) {
        try {
            New-Item -Path $parentDir -ItemType Directory -Force | Out-Null
        }
        catch {
            Handle-Error 1 "No write permission" "Cannot write to installation directory. Check permissions or run as Administrator"
        }
    }
    
    Write-ColorOutput "✅ All system requirements verified" "Green"
}

# Function to install Git if not available
function Install-Git {
    Write-ColorOutput "📦 Installing Git..." "Yellow"
    
    # Check if Chocolatey is available
    if (Test-CommandExists "choco") {
        Write-ColorOutput "🔄 Installing Git via Chocolatey..." "Cyan"
        try {
            choco install git -y
            Write-ColorOutput "✅ Git installed successfully via Chocolatey" "Green"
            return
        }
        catch {
            Write-ColorOutput "⚠️ Chocolatey installation failed, trying alternative method..." "Yellow"
        }
    }
    
    # Check if Winget is available
    if (Test-CommandExists "winget") {
        Write-ColorOutput "🔄 Installing Git via Winget..." "Cyan"
        try {
            winget install --id Git.Git -e --source winget
            Write-ColorOutput "✅ Git installed successfully via Winget" "Green"
            return
        }
        catch {
            Write-ColorOutput "⚠️ Winget installation failed" "Yellow"
        }
    }
    
    # Manual installation required
    Handle-Error 1 "Git installation required" "Please install Git from https://git-scm.com/download/win and run this script again"
}

# Function to check if Git is available
function Test-Git {
    Write-ColorOutput "🔍 Checking Git installation..." "Yellow"
    
    if (Test-CommandExists "git") {
        $gitVersion = (git --version 2>$null) -replace "git version ", ""
        Write-ColorOutput "✅ Git found (version: $gitVersion)" "Green"
        
        # Check if Git is properly configured
        try {
            $null = git config --global user.name 2>$null
        }
        catch {
            Write-ColorOutput "⚠️ Git user not configured. Setting default configuration..." "Yellow"
            git config --global user.name "AUTO-blogger User" 2>$null
            git config --global user.email "user@auto-blogger.local" 2>$null
        }
    }
    else {
        Write-ColorOutput "❌ Git not found. Installing Git..." "Red"
        Install-Git
        
        # Verify installation
        if (Test-CommandExists "git") {
            $gitVersion = (git --version 2>$null) -replace "git version ", ""
            Write-ColorOutput "✅ Git successfully installed (version: $gitVersion)" "Green"
        }
        else {
            Handle-Error 1 "Git installation verification failed" "Please install Git manually and try again"
        }
    }
}

# Function to clone or update repository
function Update-Repository {
    Write-ColorOutput "📥 Setting up repository..." "Yellow"
    
    if (Test-Path $INSTALL_DIR) {
        Write-ColorOutput "📁 Directory exists. Checking for updates..." "Yellow"
        Set-Location $INSTALL_DIR
        
        # Check if it's a git repository
        if (Test-Path ".git") {
            Write-ColorOutput "🔄 Updating existing installation..." "Cyan"
            
            # Fetch latest changes
            Write-ColorOutput "📡 Fetching latest changes..." "Cyan"
            try {
                git fetch origin
            }
            catch {
                Handle-Error 1 "Failed to fetch updates" "Check your internet connection and GitHub access"
            }
            
            # Determine the default branch
            $defaultBranch = "main"
            try {
                $defaultBranch = (git symbolic-ref refs/remotes/origin/HEAD 2>$null) -replace "refs/remotes/origin/", ""
            }
            catch {
                # Fallback to main or master
                try {
                    git rev-parse "origin/main" 2>$null | Out-Null
                    $defaultBranch = "main"
                }
                catch {
                    try {
                        git rev-parse "origin/master" 2>$null | Out-Null
                        $defaultBranch = "master"
                    }
                    catch {
                        Handle-Error 1 "Cannot determine repository branch" "Repository may be corrupted. Try removing $INSTALL_DIR and running again"
                    }
                }
            }
            
            # Check if updates are available
            $localCommit = git rev-parse HEAD 2>$null
            $remoteCommit = git rev-parse "origin/$defaultBranch" 2>$null
            
            if ($localCommit -ne $remoteCommit) {
                Write-ColorOutput "📦 Updates available! Updating from $defaultBranch..." "Green"
                
                # Stash any local changes
                git stash push -m "Auto-stash before update" 2>$null
                
                # Pull updates
                try {
                    git pull origin $defaultBranch
                    Write-ColorOutput "✅ Repository updated successfully" "Green"
                }
                catch {
                    Handle-Error 1 "Failed to pull updates" "Repository may have conflicts. Try removing $INSTALL_DIR and running again"
                }
            }
            else {
                Write-ColorOutput "✅ Repository is already up to date" "Green"
            }
        }
        else {
            Write-ColorOutput "⚠️ Directory exists but is not a git repository. Removing and cloning fresh..." "Yellow"
            Set-Location (Split-Path $INSTALL_DIR -Parent)
            Remove-Item -Path $INSTALL_DIR -Recurse -Force
            
            Write-ColorOutput "📥 Cloning fresh repository..." "Cyan"
            try {
                git clone $REPO_URL $INSTALL_DIR
                Set-Location $INSTALL_DIR
            }
            catch {
                Handle-Error 1 "Failed to clone repository" "Check your internet connection and GitHub access"
            }
        }
    }
    else {
        Write-ColorOutput "📥 Cloning repository..." "Cyan"
        
        # Create parent directory if needed
        $parentDir = Split-Path $INSTALL_DIR -Parent
        if (-not (Test-Path $parentDir)) {
            New-Item -Path $parentDir -ItemType Directory -Force | Out-Null
        }
        
        # Clone repository
        try {
            git clone $REPO_URL $INSTALL_DIR
            Set-Location $INSTALL_DIR
            Write-ColorOutput "✅ Repository cloned successfully" "Green"
        }
        catch {
            Handle-Error 1 "Failed to clone repository" "Check your internet connection and GitHub access"
        }
    }
    
    # Verify essential files exist
    $essentialFiles = @("requirements.txt", "gui_blogger.py", "automation_engine.py", "autoblog_launcher.py")
    foreach ($file in $essentialFiles) {
        if (-not (Test-Path $file)) {
            Handle-Error 1 "Essential file missing: $file" "Repository may be corrupted. Try removing $INSTALL_DIR and running again"
        }
    }
    
    Write-ColorOutput "✅ Repository verification completed" "Green"
}

# Function to install Python
function Install-Python {
    Write-ColorOutput "📦 Installing Python..." "Yellow"
    
    # Check if Chocolatey is available
    if (Test-CommandExists "choco") {
        Write-ColorOutput "🔄 Installing Python via Chocolatey..." "Cyan"
        try {
            choco install python -y
            Write-ColorOutput "✅ Python installed successfully via Chocolatey" "Green"
            # Refresh environment variables
            $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "User")
            return
        }
        catch {
            Write-ColorOutput "⚠️ Chocolatey installation failed, trying alternative method..." "Yellow"
        }
    }
    
    # Check if Winget is available
    if (Test-CommandExists "winget") {
        Write-ColorOutput "🔄 Installing Python via Winget..." "Cyan"
        try {
            winget install --id Python.Python.3.11 -e --source winget
            Write-ColorOutput "✅ Python installed successfully via Winget" "Green"
            # Refresh environment variables
            $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "User")
            return
        }
        catch {
            Write-ColorOutput "⚠️ Winget installation failed" "Yellow"
        }
    }
    
    # Manual installation required
    Write-ColorOutput "❌ Windows detected - automatic Python installation not supported" "Red"
    Write-ColorOutput "💡 MANUAL INSTALLATION REQUIRED:" "Yellow"
    Write-ColorOutput "   1. Download Python from: https://python.org/downloads/" "Cyan"
    Write-ColorOutput "   2. Run the installer and check 'Add Python to PATH'" "Cyan"
    Write-ColorOutput "   3. Restart your PowerShell/command prompt" "Cyan"
    Write-ColorOutput "   4. Re-run this installer" "Cyan"
    Read-Host "Press Enter after manual installation to continue..."
}

# Function to check Python version
function Test-Python {
    Write-ColorOutput "🔍 Checking Python installation..." "Yellow"
    
    $pythonCmd = ""
    $pythonVersion = ""
    
    # Check for python first, then python3
    if (Test-CommandExists "python") {
        try {
            $pythonVersion = python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')" 2>$null
            $pythonCmd = "python"
        }
        catch {
            # Python command exists but failed to get version
        }
    }
    
    if (-not $pythonCmd -and (Test-CommandExists "python3")) {
        try {
            $pythonVersion = python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')" 2>$null
            $pythonCmd = "python3"
        }
        catch {
            # Python3 command exists but failed to get version
        }
    }
    
    if ($pythonCmd -and $pythonVersion) {
        $requiredVersion = [Version]"3.8.0"
        $currentVersion = [Version]$pythonVersion
        
        if ($currentVersion -ge $requiredVersion) {
            Write-ColorOutput "✅ Python $pythonVersion found ($pythonCmd)" "Green"
            
            # Set global PYTHON_CMD variable
            $global:PYTHON_CMD = $pythonCmd
            
            # Check if pip is available
            try {
                & $pythonCmd -m pip --version | Out-Null
            }
            catch {
                Write-ColorOutput "⚠️ pip not found. Installing pip..." "Yellow"
                try {
                    & $pythonCmd -m ensurepip --upgrade
                }
                catch {
                    Handle-Error 1 "Failed to install pip" "Please install pip manually"
                }
            }
            
            # Verify pip installation
            $pipVersion = (& $pythonCmd -m pip --version 2>$null) -replace "pip ", "" -replace " from.*", ""
            Write-ColorOutput "✅ pip $pipVersion found" "Green"
        }
        else {
            Write-ColorOutput "❌ Python $pythonVersion found, but version 3.8.0 or higher is required" "Red"
            Install-Python
            
            # Re-verify after installation
            if (Test-CommandExists "python") {
                $global:PYTHON_CMD = "python"
                $pythonVersion = python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')" 2>$null
                Write-ColorOutput "✅ Python $pythonVersion installed successfully" "Green"
            }
            else {
                Handle-Error 1 "Python installation verification failed" "Please install Python 3.8+ manually"
            }
        }
    }
    else {
        Write-ColorOutput "❌ Python not found. Installing Python..." "Red"
        Install-Python
        
        # Verify installation
        if (Test-CommandExists "python") {
            $global:PYTHON_CMD = "python"
            $pythonVersion = python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')" 2>$null
            Write-ColorOutput "✅ Python $pythonVersion installed successfully" "Green"
        }
        else {
            Handle-Error 1 "Python installation verification failed" "Please install Python 3.8+ manually"
        }
    }
}

# Function to install Chrome/Chromium for Selenium
function Install-Chrome {
    # Check if Chrome is already installed
    $chromeInstalled = $false
    $chromePaths = @(
        "${env:ProgramFiles}\Google\Chrome\Application\chrome.exe",
        "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe",
        "${env:LOCALAPPDATA}\Google\Chrome\Application\chrome.exe"
    )
    
    foreach ($path in $chromePaths) {
        if (Test-Path $path) {
            $chromeInstalled = $true
            break
        }
    }
    
    if ($chromeInstalled) {
        Write-ColorOutput "✅ Chrome already installed - skipping installation" "Green"
        return
    }
    
    Write-ColorOutput "🌐 Installing Chrome for web automation..." "Yellow"
    
    # Check if Chocolatey is available
    if (Test-CommandExists "choco") {
        Write-ColorOutput "🔄 Installing Google Chrome via Chocolatey..." "Cyan"
        try {
            choco install googlechrome -y
            Write-ColorOutput "✅ Chrome installed successfully via Chocolatey" "Green"
            return
        }
        catch {
            Write-ColorOutput "⚠️ Chocolatey installation failed, trying alternative method..." "Yellow"
        }
    }
    
    # Check if Winget is available
    if (Test-CommandExists "winget") {
        Write-ColorOutput "🔄 Installing Google Chrome via Winget..." "Cyan"
        try {
            winget install --id Google.Chrome -e --source winget
            Write-ColorOutput "✅ Chrome installed successfully via Winget" "Green"
            return
        }
        catch {
            Write-ColorOutput "⚠️ Winget installation failed" "Yellow"
        }
    }
    
    Write-ColorOutput "⚠️ Please install Chrome from https://www.google.com/chrome/ for web automation features" "Yellow"
    
    # Verify Chrome installation
    $chromeInstalled = $false
    foreach ($path in $chromePaths) {
        if (Test-Path $path) {
            $chromeInstalled = $true
            break
        }
    }
    
    if ($chromeInstalled) {
        Write-ColorOutput "✅ Chrome installed successfully" "Green"
    }
    else {
        Write-ColorOutput "⚠️ Chrome installation could not be verified. Web automation may not work properly." "Yellow"
        Write-ColorOutput "💡 You can install Chrome manually later from https://www.google.com/chrome/" "Cyan"
    }
}

# Function to create virtual environment
function New-VirtualEnvironment {
    Write-ColorOutput "🔧 Creating Python virtual environment: $VENV_NAME..." "Yellow"
    
    # Remove any existing generic virtual environments
    $oldVenvs = @("venv", "auto_blogger_venv", "env", ".venv")
    foreach ($oldVenv in $oldVenvs) {
        if (Test-Path $oldVenv) {
            Write-ColorOutput "⚠️ Removing old virtual environment: $oldVenv" "Yellow"
            try {
                Remove-Item -Path $oldVenv -Recurse -Force
            }
            catch {
                Write-ColorOutput "❌ Failed to remove old virtual environment: $oldVenv" "Red"
                Write-ColorOutput "💡 Please manually remove the directory and re-run installer" "Yellow"
                Read-Host "Press Enter after manual removal to continue..."
            }
        }
    }
    
    # Check if unique virtual environment already exists and is functional
    if (Test-Path $VENV_NAME) {
        Write-ColorOutput "🔍 Checking existing virtual environment: $VENV_NAME..." "Cyan"
        
        $venvPython = "$VENV_NAME\Scripts\python.exe"
        $activateScript = "$VENV_NAME\Scripts\Activate.ps1"
        
        if ((Test-Path $venvPython) -and (Test-Path $activateScript)) {
            try {
                & $venvPython -c "import sys; print('OK')" 2>$null | Out-Null
                Write-ColorOutput "✅ Virtual environment already exists and is functional - skipping creation" "Green"
                return
            }
            catch {
                Write-ColorOutput "⚠️ Virtual environment exists but is not functional. Removing..." "Yellow"
                Remove-Item -Path $VENV_NAME -Recurse -Force
            }
        }
        else {
            Write-ColorOutput "⚠️ Virtual environment exists but is not functional. Removing..." "Yellow"
            Remove-Item -Path $VENV_NAME -Recurse -Force
        }
    }
    
    Write-ColorOutput "🔄 Creating new virtual environment: $VENV_NAME..." "Cyan"
    
    # Try creating virtual environment
    try {
        & $global:PYTHON_CMD -m venv $VENV_NAME
        Write-ColorOutput "✅ Virtual environment created successfully" "Green"
    }
    catch {
        Write-ColorOutput "❌ Failed to create virtual environment" "Red"
        Write-ColorOutput "💡 MANUAL VIRTUAL ENVIRONMENT CREATION REQUIRED:" "Yellow"
        Write-ColorOutput "   Try: $global:PYTHON_CMD -m venv $VENV_NAME" "Cyan"
        Read-Host "Press Enter after manual virtual environment creation to continue..."
        
        # Verify manual creation
        if (-not (Test-Path $VENV_NAME)) {
            Handle-Error 1 "Virtual environment creation failed" "Please create virtual environment manually and re-run installer"
        }
    }
    
    # Activate virtual environment
    Write-ColorOutput "🔄 Activating virtual environment: $VENV_NAME..." "Cyan"
    $activateScript = "$VENV_NAME\Scripts\Activate.ps1"
    
    if (Test-Path $activateScript) {
        try {
            & $activateScript
            Write-ColorOutput "✅ Virtual environment activated successfully" "Green"
        }
        catch {
            Write-ColorOutput "❌ Failed to activate virtual environment" "Red"
            Write-ColorOutput "💡 Virtual environment may be corrupted" "Yellow"
            Read-Host "Press Enter to continue anyway..."
        }
    }
    else {
        Write-ColorOutput "❌ Activation script not found: $activateScript" "Red"
        Write-ColorOutput "💡 Virtual environment may be incomplete" "Yellow"
        Read-Host "Press Enter to continue anyway..."
    }
    
    # Upgrade pip
    Write-ColorOutput "📦 Upgrading pip..." "Yellow"
    try {
        & "$VENV_NAME\Scripts\python.exe" -m pip install --upgrade pip
        $pipVersion = (& "$VENV_NAME\Scripts\python.exe" -m pip --version) -replace "pip ", "" -replace " from.*", ""
        Write-ColorOutput "✅ Virtual environment ready (pip $pipVersion)" "Green"
    }
    catch {
        Write-ColorOutput "⚠️ Pip upgrade failed, but continuing with installation" "Yellow"
        Write-ColorOutput "💡 You may need to upgrade pip manually later" "Cyan"
    }
}

# Function to install Python dependencies
function Install-Dependencies {
    Write-ColorOutput "📦 Installing Python dependencies..." "Yellow"
    
    $pythonExe = "$VENV_NAME\Scripts\python.exe"
    
    # Check if dependencies are already installed
    Write-ColorOutput "🔍 Checking existing dependencies..." "Cyan"
    $criticalPackages = @("requests", "bs4", "selenium", "openai")
    $allInstalled = $true
    
    foreach ($package in $criticalPackages) {
        try {
            & $pythonExe -c "import $package" 2>$null
        }
        catch {
            $allInstalled = $false
            break
        }
    }
    
    if ($allInstalled -and (Test-Path "requirements.txt")) {
        # Check if all requirements.txt packages are installed
        $missingPackages = 0
        $requirements = Get-Content "requirements.txt" | Where-Object { $_ -notmatch "^#" -and $_ -ne "" }
        
        foreach ($package in $requirements) {
            $pkgName = ($package -split "[>=<]")[0] -replace "\[.*\]", ""
            try {
                & $pythonExe -m pip show $pkgName 2>$null | Out-Null
            }
            catch {
                $missingPackages++
                break
            }
        }
        
        if ($missingPackages -eq 0) {
            Write-ColorOutput "✅ All dependencies already installed - skipping installation" "Green"
            return
        }
    }
    
    # Install from requirements.txt if it exists
    if (Test-Path "requirements.txt") {
        Write-ColorOutput "📋 Installing from requirements.txt..." "Cyan"
        
        # Count total packages for progress indication
        $totalPackages = (Get-Content "requirements.txt" | Where-Object { $_ -notmatch "^#" -and $_ -ne "" }).Count
        Write-ColorOutput "📊 Installing $totalPackages packages..." "Cyan"
        
        # Try bulk install first
        Write-ColorOutput "   Trying bulk installation..." "Cyan"
        try {
            & $pythonExe -m pip install --timeout 300 --retries 3 -r requirements.txt
            Write-ColorOutput "   ✅ Bulk installation successful" "Green"
        }
        catch {
            Write-ColorOutput "   ⚠️ Bulk installation failed. Trying individual installation..." "Yellow"
            $failedPackages = @()
            
            $requirements = Get-Content "requirements.txt" | Where-Object { $_ -notmatch "^#" -and $_ -ne "" }
            foreach ($package in $requirements) {
                Write-ColorOutput "   📦 Installing: $package" "Cyan"
                try {
                    & $pythonExe -m pip install $package
                    Write-ColorOutput "   ✅ Installed: $package" "Green"
                }
                catch {
                    Write-ColorOutput "   ⚠️ Failed to install: $package" "Yellow"
                    $failedPackages += $package
                }
            }
            
            if ($failedPackages.Count -gt 0) {
                Write-ColorOutput "⚠️ Some packages failed to install: $($failedPackages -join ', ')" "Yellow"
                Write-ColorOutput "💡 You may need to install these manually later" "Cyan"
            }
        }
    }
    else {
        Write-ColorOutput "⚠️ requirements.txt not found. Installing essential packages..." "Yellow"
        
        # Install essential packages
        $essentialPackages = @("requests", "beautifulsoup4", "lxml", "selenium", "webdriver-manager", "openai", "google-generativeai", "pillow", "python-dotenv", "colorama", "tqdm", "validators")
        $failedPackages = @()
        
        foreach ($package in $essentialPackages) {
            Write-ColorOutput "📦 Installing: $package" "Cyan"
            try {
                & $pythonExe -m pip install $package
                Write-ColorOutput "   ✅ Installed: $package" "Green"
            }
            catch {
                Write-ColorOutput "   ⚠️ Failed to install: $package" "Yellow"
                $failedPackages += $package
            }
        }
        
        if ($failedPackages.Count -gt 0) {
            Write-ColorOutput "⚠️ Some essential packages failed to install: $($failedPackages -join ', ')" "Yellow"
            Write-ColorOutput "💡 MANUAL INSTALLATION MAY BE REQUIRED:" "Cyan"
            foreach ($pkg in $failedPackages) {
                Write-ColorOutput "   pip install $pkg" "Cyan"
            }
            Read-Host "Press Enter to continue anyway..."
        }
    }
    
    # Verify critical packages are installed
    Write-ColorOutput "🔍 Verifying critical packages..." "Yellow"
    $missingPackages = @()
    
    foreach ($package in $criticalPackages) {
        try {
            & $pythonExe -c "import $package" 2>$null
            Write-ColorOutput "   ✅ $package - OK" "Green"
        }
        catch {
            Write-ColorOutput "   ⚠️ $package - Missing" "Yellow"
            $missingPackages += $package
        }
    }
    
    if ($missingPackages.Count -gt 0) {
        Write-ColorOutput "⚠️ Some critical packages are missing: $($missingPackages -join ', ')" "Yellow"
        Write-ColorOutput "💡 The application may still work, but some features might be limited" "Cyan"
        Write-ColorOutput "💡 You can install missing packages manually later" "Cyan"
    }
    else {
        Write-ColorOutput "✅ All critical packages verified" "Green"
    }
    
    # Show installed packages summary
    try {
        $installedCount = (& $pythonExe -m pip list 2>$null | Measure-Object -Line).Lines
        Write-ColorOutput "✅ Dependencies installation completed ($installedCount packages installed)" "Green"
    }
    catch {
        Write-ColorOutput "✅ Dependencies installation completed" "Green"
    }
}

# Function to create launcher script
function New-Launcher {
    $installDir = Get-Location
    
    Write-ColorOutput "🚀 Creating launcher script with auto-update..." "Yellow"
    
    # Verify essential files exist
    if (-not (Test-Path "gui_blogger.py")) {
        Handle-Error 1 "Main application file missing: gui_blogger.py" "Repository may be corrupted. Try removing $INSTALL_DIR and running again"
    }
    
    # Create PowerShell launcher script
    Write-ColorOutput "🔄 Creating PowerShell launcher..." "Cyan"
    
    $launcherContent = @"
# AUTO-blogger Enhanced PowerShell Launcher Script with Auto-Update
# This script provides robust launching with auto-update functionality

# Get the directory where this script is located
`$ScriptDir = Split-Path -Parent `$MyInvocation.MyCommand.Path
Set-Location `$ScriptDir

# Colors for output
function Write-ColorOutput {
    param(
        [string]`$Message,
        [string]`$Color = "White"
    )
    
    `$colorMap = @{
        "Red" = "Red"
        "Green" = "Green"
        "Yellow" = "Yellow"
        "Blue" = "Blue"
        "Cyan" = "Cyan"
        "White" = "White"
    }
    
    Write-Host `$Message -ForegroundColor `$colorMap[`$Color]
}

Write-ColorOutput "🖥️  Detected OS: Windows" "Cyan"

# Find virtual environment directory dynamically
`$VenvDir = `$null
`$VenvDirs = Get-ChildItem -Path `$ScriptDir -Directory -Name "auto_blogger_venv_*"
foreach (`$dir in `$VenvDirs) {
    `$fullPath = Join-Path `$ScriptDir `$dir
    if (Test-Path "`$fullPath\Scripts\Activate.ps1") {
        `$VenvDir = `$fullPath
        break
    }
}

if (-not `$VenvDir) {
    Write-ColorOutput "❌ Virtual environment not found in `$ScriptDir" "Red"
    Write-ColorOutput "💡 Looking for virtual environment directories..." "Yellow"
    Get-ChildItem -Path `$ScriptDir -Directory -Name "auto_blogger_venv_*" | ForEach-Object { Write-Host "   Found: `$_" }
    Write-ColorOutput "💡 Please run the installer again to create virtual environment" "Yellow"
    Read-Host "Press Enter to exit..."
    exit 1
}

Write-ColorOutput "🔧 Using virtual environment: `$(Split-Path `$VenvDir -Leaf)" "Cyan"

`$PythonExe = "`$VenvDir\Scripts\python.exe"
`$ActivateScript = "`$VenvDir\Scripts\Activate.ps1"

# Verify Python executable exists
if (-not (Test-Path `$PythonExe)) {
    Write-ColorOutput "❌ Python executable not found: `$PythonExe" "Red"
    Write-ColorOutput "💡 Virtual environment may be corrupted" "Yellow"
    Write-ColorOutput "💡 Please run the installer again" "Yellow"
    Read-Host "Press Enter to exit..."
    exit 1
}

# Check for main application files
`$MainApp = `$null
if (Test-Path "autoblog_launcher.py") {
    `$MainApp = "autoblog_launcher.py"
} elseif (Test-Path "gui_blogger.py") {
    `$MainApp = "gui_blogger.py"
} elseif (Test-Path "launch_blogger.py") {
    `$MainApp = "launch_blogger.py"
} else {
    Write-ColorOutput "❌ No launcher application found" "Red"
    Write-ColorOutput "💡 Looking for application files..." "Yellow"
    Get-ChildItem -Path `$ScriptDir -Name "*.py" | Select-Object -First 5 | ForEach-Object { Write-Host "   Found: `$_" }
    Write-ColorOutput "💡 Please run the installer again" "Yellow"
    Read-Host "Press Enter to exit..."
    exit 1
}

Write-ColorOutput "🚀 Starting AUTO-blogger (`$MainApp) with auto-update..." "Cyan"

# Activate virtual environment if activation script exists
if (Test-Path `$ActivateScript) {
    Write-ColorOutput "🔧 Activating virtual environment..." "Cyan"
    try {
        & `$ActivateScript
    } catch {
        Write-ColorOutput "⚠️ Failed to activate virtual environment, continuing anyway..." "Yellow"
    }
}

# Launch the application with error handling
Write-ColorOutput "🚀 Launching AUTO-blogger..." "Cyan"
try {
    & `$PythonExe `$MainApp
    Write-ColorOutput "✅ AUTO-blogger exited successfully" "Green"
} catch {
    Write-ColorOutput "❌ AUTO-blogger exited with errors" "Red"
    Write-ColorOutput "💡 Check the application logs for details" "Yellow"
    Read-Host "Press Enter to exit..."
    exit 1
}

Read-Host "Press Enter to exit..."
"@
    
    # Write the launcher script
    $launcherContent | Out-File -FilePath "autoblog.ps1" -Encoding UTF8
    
    # Create batch file launcher for easier access
    Write-ColorOutput "🔄 Creating Windows batch launcher..." "Cyan"
    $batchContent = @"
@echo off
setlocal

REM AUTO-blogger Windows Launcher
echo 🚀 Starting AUTO-blogger...

REM Change to script directory
cd /d "%~dp0"

REM Run PowerShell script
powershell.exe -ExecutionPolicy Bypass -File "autoblog.ps1"
if errorlevel 1 (
    echo ⚠️ Application exited with errors
    pause
)
"@
    
    $batchContent | Out-File -FilePath "autoblog.bat" -Encoding ASCII
    
    Write-ColorOutput "✅ Launcher scripts created successfully" "Green"
    Write-ColorOutput "   • PowerShell: autoblog.ps1" "Cyan"
    Write-ColorOutput "   • Batch file: autoblog.bat" "Cyan"
}

# Function to create desktop shortcut
function New-DesktopShortcut {
    $installDir = Get-Location
    $desktopPath = [Environment]::GetFolderPath("Desktop")
    
    Write-ColorOutput "🖥️ Creating desktop shortcut..." "Yellow"
    
    try {
        $WshShell = New-Object -comObject WScript.Shell
        $Shortcut = $WshShell.CreateShortcut("$desktopPath\AUTO-blogger.lnk")
        $Shortcut.TargetPath = "$installDir\autoblog.bat"
        $Shortcut.WorkingDirectory = $installDir
        $Shortcut.Description = "AUTO-blogger - Automated WordPress Blog Posting Tool"
        if (Test-Path "$installDir\icon.ico") {
            $Shortcut.IconLocation = "$installDir\icon.ico"
        }
        $Shortcut.Save()
        
        Write-ColorOutput "✅ Desktop shortcut created" "Green"
    }
    catch {
        Write-ColorOutput "⚠️ Could not create desktop shortcut" "Yellow"
    }
}

# Function to run post-installation fixes
function Invoke-PostInstallationFixes {
    Write-ColorOutput "🔧 Running post-installation fixes..." "Cyan"
    
    # Create docs and tests directories
    if (-not (Test-Path "docs")) { New-Item -Path "docs" -ItemType Directory | Out-Null }
    if (-not (Test-Path "tests")) { New-Item -Path "tests" -ItemType Directory | Out-Null }
    
    # Installation fixes are integrated into the main installer
if ($false) {
        Write-ColorOutput "🔄 Running installation fixes script..." "Cyan"
        try {
            # Installation fixes have been integrated into the main installer
            Write-ColorOutput "✅ Post-installation fixes completed" "Green"
        }
        catch {
            Write-ColorOutput "⚠️ Fix script completed with warnings" "Yellow"
        }
    }
    else {
        Write-ColorOutput "💡 No additional fixes script found - skipping" "Cyan"
    }
}

# Function to test installation
function Test-Installation {
    Write-ColorOutput "🧪 Testing installation..." "Yellow"
    
    $pythonExe = "$VENV_NAME\Scripts\python.exe"
    
    # Test critical Python imports
    Write-ColorOutput "🔍 Testing critical package imports..." "Cyan"
    $testPackages = @("requests", "bs4", "selenium", "openai")
    $failedPackages = @()
    
    foreach ($package in $testPackages) {
        Write-ColorOutput "  Testing: $package" "Cyan"
        try {
            & $pythonExe -c "import $package" 2>$null
            Write-ColorOutput "    ✅ $package - OK" "Green"
        }
        catch {
            Write-ColorOutput "    ⚠️ $package - Failed" "Yellow"
            $failedPackages += $package
        }
    }
    
    # Test main application file
    Write-ColorOutput "🔍 Testing main application..." "Cyan"
    if (Test-Path "gui_blogger.py") {
        try {
            & $pythonExe -m py_compile gui_blogger.py 2>$null
            Write-ColorOutput "✅ Main application syntax - OK" "Green"
        }
        catch {
            Write-ColorOutput "⚠️ Main application syntax check failed" "Yellow"
        }
    }
    else {
        Write-ColorOutput "❌ Main application file missing" "Red"
        $failedPackages += "gui_blogger.py"
    }
    
    # Test launcher
    Write-ColorOutput "🔍 Testing launcher script..." "Cyan"
    if (Test-Path "autoblog_launcher.py") {
        try {
            & $pythonExe -m py_compile autoblog_launcher.py 2>$null
            Write-ColorOutput "✅ Launcher script syntax - OK" "Green"
        }
        catch {
            Write-ColorOutput "⚠️ Launcher script syntax check failed" "Yellow"
        }
    }
    else {
        Write-ColorOutput "❌ Launcher script missing" "Red"
        $failedPackages += "autoblog_launcher.py"
    }
    
    # Summary
    if ($failedPackages.Count -eq 0) {
        Write-ColorOutput "✅ All tests passed successfully!" "Green"
        return 0
    }
    else {
        Write-ColorOutput "⚠️ Some tests failed: $($failedPackages -join ', ')" "Yellow"
        Write-ColorOutput "💡 The application may still work, but some features might be limited" "Cyan"
        return 1
    }
}

# Function to show completion message
function Show-Completion {
    param([int]$TestResult)
    
    Write-Host ""
    Write-ColorOutput "🎉 AUTO-blogger installation completed with enhanced features!" "Green"
    Write-ColorOutput "📍 Installation directory: $INSTALL_DIR" "Cyan"
    Write-ColorOutput "🔧 Virtual environment: $VENV_NAME (unique)" "Cyan"
    
    if ($TestResult -eq 0) {
        Write-ColorOutput "✅ All tests passed - Installation is fully functional" "Green"
    }
    else {
        Write-ColorOutput "⚠️ Installation completed with some warnings" "Yellow"
        Write-ColorOutput "💡 Check the test results above for details" "Cyan"
    }
    
    Write-Host ""
    Write-ColorOutput "🆕 Enhanced Features:" "Yellow"
    Write-ColorOutput "   • Enhanced SEO automation with improved algorithms" "Cyan"
    Write-ColorOutput "   • Organized project structure (docs/, tests/)" "Cyan"
    Write-ColorOutput "   • Unique virtual environment for conflict prevention" "Cyan"
    Write-ColorOutput "   • Comprehensive testing and validation tools" "Cyan"
    Write-ColorOutput "   • Improved error handling and logging" "Cyan"
    
    Write-Host ""
    Write-ColorOutput "🚀 How to use AUTO-blogger:" "Yellow"
    Write-ColorOutput "   • Double-click: autoblog.bat in installation directory" "Cyan"
    Write-ColorOutput "   • PowerShell: Run .\autoblog.ps1 from installation directory" "Cyan"
    Write-ColorOutput "   • Command line: Run autoblog.bat from installation directory" "Cyan"
    Write-ColorOutput "   • Python: Run python autoblog_launcher.py from installation directory" "Cyan"
    
    Write-Host ""
    Write-ColorOutput "📁 Project Structure:" "Yellow"
    Write-ColorOutput "   • Main Application: gui_blogger.py" "Cyan"
    Write-ColorOutput "   • Configuration: configs/ directory" "Cyan"
    Write-ColorOutput "   • Documentation: docs/ directory" "Cyan"
    Write-ColorOutput "   • Tests: tests/ directory" "Cyan"
    Write-ColorOutput "   • Virtual Environment: $VENV_NAME/" "Cyan"
    
    Write-Host ""
    Write-ColorOutput "📚 Documentation & Testing:" "Yellow"
    Write-ColorOutput "   • README: $INSTALL_DIR\README.md" "Cyan"
    Write-ColorOutput "   • Installation Guide: $INSTALL_DIR\docs\README_INSTALLATION.md" "Cyan"
    Write-ColorOutput "   • SEO Improvements: $INSTALL_DIR\docs\SEO_IMPROVEMENTS_*.md" "Cyan"
    Write-ColorOutput "   • SEO Features are ready to use" "Cyan"
    Write-ColorOutput "   • Troubleshooting: $INSTALL_DIR\docs\wordpress_seo_troubleshooting.md" "Cyan"
    
    Write-Host ""
    Write-ColorOutput "🔧 First Time Setup:" "Yellow"
    Write-ColorOutput "   1. Launch the application using one of the methods above" "Cyan"
    Write-ColorOutput "   2. Configure your API keys (WordPress, OpenAI, Gemini)" "Cyan"
    Write-ColorOutput "   3. Set up your automation preferences" "Cyan"
    Write-ColorOutput "   4. Start generating content!" "Cyan"
    
    Write-Host ""
    Write-ColorOutput "🆘 Support:" "Yellow"
    Write-ColorOutput "   • Email: AryanVBW@gmail.com" "Cyan"
    Write-ColorOutput "   • Issues: https://github.com/AryanVBW/AUTO-blogger/issues" "Cyan"
    Write-ColorOutput "   • Documentation: Check the docs/ folder for guides" "Cyan"
    
    Write-Host ""
    if ($TestResult -eq 0) {
        Write-ColorOutput "🚀 Enhanced AUTO-blogger is ready! Start creating amazing content! 📝✨" "Green"
        Write-ColorOutput "💡 Try the new SEO features and organized project structure!" "Cyan"
    }
    else {
        Write-ColorOutput "⚠️ Installation completed with warnings. Please check the issues above." "Yellow"
        Write-ColorOutput "💡 You can still try running the application - it may work despite the warnings." "Cyan"
        Write-ColorOutput "🔧 SEO features are configured and ready" "Cyan"
    }
    Write-Host ""
}

# Main installation function
function Start-Installation {
    # Handle Ctrl+C gracefully
    $null = Register-EngineEvent PowerShell.Exiting -Action {
        Write-ColorOutput "`n❌ Installation interrupted by user" "Red"
        Write-ColorOutput "💡 You can run this installer again to complete the setup" "Cyan"
    }
    
    # Start installation
    Show-Logo
    
    Write-ColorOutput "🚀 Starting AUTO-blogger installation..." "Cyan"
    Write-ColorOutput "📅 $(Get-Date)" "Cyan"
    Write-Host ""
    
    try {
        # Step 1: System verification
        Write-ColorOutput "📋 Step 1/10: System Verification" "Yellow"
        Test-SystemRequirements
        Write-Host ""
        
        # Step 2: Check existing installation
        Write-ColorOutput "📋 Step 2/10: Installation Check" "Yellow"
        Test-ExistingInstallation
        Write-Host ""
        
        # Step 3: Git setup
        Write-ColorOutput "📋 Step 3/10: Git Setup" "Yellow"
        Test-Git
        Write-Host ""
        
        # Step 4: Repository setup
        Write-ColorOutput "📋 Step 4/10: Repository Setup" "Yellow"
        Update-Repository
        Write-Host ""
        
        # Step 5: Python setup
        Write-ColorOutput "📋 Step 5/10: Python Setup" "Yellow"
        Test-Python
        Write-Host ""
        
        # Step 6: Browser setup
        Write-ColorOutput "📋 Step 6/10: Browser Setup" "Yellow"
        Install-Chrome
        Write-Host ""
        
        # Step 7: Virtual environment
        Write-ColorOutput "📋 Step 7/10: Virtual Environment" "Yellow"
        New-VirtualEnvironment
        Write-Host ""
        
        # Step 8: Dependencies
        Write-ColorOutput "📋 Step 8/10: Dependencies Installation" "Yellow"
        Install-Dependencies
        Write-Host ""
        
        # Step 9: Launcher creation
        Write-ColorOutput "📋 Step 9/10: Launcher Creation" "Yellow"
        New-Launcher
        New-DesktopShortcut
        Write-Host ""
        
        # Step 10: Post-installation fixes
        Write-ColorOutput "📋 Step 10/11: Post-Installation Fixes" "Yellow"
        Invoke-PostInstallationFixes
        Write-Host ""
        
        # Step 11: Testing and completion
        Write-ColorOutput "📋 Step 11/11: Testing Installation" "Yellow"
        $testResult = Test-Installation
        Write-Host ""
        
        # Show completion message
        Show-Completion -TestResult $testResult
        
        # Final status
        if ($testResult -eq 0) {
            Write-ColorOutput "🎯 Installation completed successfully!" "Green"
            exit 0
        }
        else {
            Write-ColorOutput "⚠️ Installation completed with warnings" "Yellow"
            exit 2
        }
    }
    catch {
        Write-ColorOutput "❌ Installation failed with error: $($_.Exception.Message)" "Red"
        Write-ColorOutput "💡 Please check the error above and try again" "Yellow"
        Write-ColorOutput "📧 For support, contact: AryanVBW@gmail.com" "Cyan"
        Read-Host "Press Enter to exit..."
        exit 1
    }
}

# Run main installation
Start-Installation