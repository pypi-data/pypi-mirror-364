# Enhanced AUTO-blogger Launcher

## Overview

The `autoblog` script has been enhanced with integrated automatic update checking and streamlined application launching. This eliminates the need for a separate GUI launcher and provides a more efficient startup process.

## Features

### 🔄 Automatic Update Checking
- **Smart Update Detection**: Compares local and remote Git commit hashes
- **GitHub API Integration**: Fetches latest commit information from the repository
- **Branch Fallback**: Tries `main` branch first, then falls back to `master`
- **Graceful Degradation**: Continues without updates if Git or network is unavailable

### 🛡️ Robust Error Handling
- **Git Availability Check**: Verifies Git is installed before attempting updates
- **Repository Validation**: Confirms the directory is a valid Git repository
- **Network Resilience**: Handles network failures gracefully
- **Local Changes Protection**: Automatically stashes uncommitted changes before updating

### 🚀 Direct Application Launch
- **Smart Script Detection**: Automatically finds and launches the correct Python script
- **Priority Order**: Tries `gui_blogger.py` first, then `launch_blogger.py`
- **Virtual Environment Integration**: Properly activates and deactivates the virtual environment
- **Clear Status Messages**: Provides informative feedback throughout the process

## Usage

### Basic Launch
```bash
./autoblog
```

### What Happens
1. **Environment Setup**: Locates and validates the virtual environment
2. **Update Check**: Checks for available updates from the GitHub repository
3. **Update Application**: Downloads and applies updates if available
4. **Launch Application**: Starts the main AUTO-blogger application
5. **Cleanup**: Properly deactivates the virtual environment

## Update Process Flow

```
🔧 Using virtual environment: auto_blogger_venv_xxxxx
🔍 Checking for updates...

[If updates available:]
📥 Updates available! Downloading...
💾 Stashing local changes... (if needed)
🔄 Fetching updates...
📦 Applying updates...
✅ Update completed successfully!

[If up to date:]
✅ Application is up to date!

🚀 Launching AUTO-blogger...
```

## Error Scenarios

### Git Not Available
```
⚠️  Git not available, skipping update check
🚀 Launching AUTO-blogger...
```

### Not a Git Repository
```
⚠️  Not a git repository, skipping update check
🚀 Launching AUTO-blogger...
```

### Network Issues
```
⚠️  Could not check remote updates
🚀 Launching AUTO-blogger...
```

### No Launcher Script Found
```
❌ No launcher script found (gui_blogger.py or launch_blogger.py)
💡 Please check your installation
```

## Technical Details

### Update Mechanism
- **Local Commit**: `git rev-parse HEAD`
- **Remote Commit**: GitHub API `/repos/AryanVBW/AUTO-blogger/commits/{branch}`
- **Update Strategy**: `git pull` with fallback to `git reset --hard`
- **Change Protection**: `git stash` for uncommitted changes

### Virtual Environment Detection
- **Pattern Matching**: Searches for `auto_blogger_venv_*` directories
- **Validation**: Confirms `bin/activate` script exists
- **Dynamic Path**: No hardcoded virtual environment names

### Application Launch Priority
1. `gui_blogger.py` (Primary GUI interface)
2. `launch_blogger.py` (Alternative launcher)
3. Error if neither found

## Benefits

### For Users
- **Seamless Updates**: Automatic update checking and application
- **Single Command**: One script handles everything
- **Clear Feedback**: Informative status messages
- **Reliable Operation**: Robust error handling

### For Developers
- **Simplified Maintenance**: One script to maintain instead of multiple
- **Better Integration**: Direct virtual environment and Git integration
- **Flexible Architecture**: Easy to extend and modify
- **Comprehensive Logging**: Clear status reporting for debugging

## Compatibility

- **Operating System**: macOS, Linux (Windows support via WSL)
- **Git**: Any modern Git version
- **Python**: Python 3.6+
- **Network**: Works offline (skips updates gracefully)

## Migration from Previous Version

The enhanced launcher is backward compatible and requires no user action. The previous `autoblog_launcher.py` is still available but no longer used by default. Users can continue using `./autoblog` as before with enhanced functionality.

## Troubleshooting

### Virtual Environment Issues
```bash
# Recreate virtual environment if needed
python3 -m venv auto_blogger_venv_$(date +%s)
```

### Git Repository Issues
```bash
# Reinitialize Git repository if needed
git init
git remote add origin https://github.com/AryanVBW/AUTO-blogger.git
git fetch origin
git checkout main
```

### Permission Issues
```bash
# Make script executable
chmod +x autoblog
```