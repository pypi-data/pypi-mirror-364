#!/bin/bash

# AUTO Blogger Launcher for macOS
# This script properly launches the AUTO Blogger application with icon support
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

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Navigate to the project root (two levels up from scripts/launchers/)
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Set the Python script path
PYTHON_SCRIPT="$PROJECT_ROOT/gui_blogger.py"
ICON_PATH="$PROJECT_ROOT/icon.png"

# Check if files exist
if [[ ! -f "$PYTHON_SCRIPT" ]]; then
    echo "❌ Error: gui_blogger.py not found at $PYTHON_SCRIPT"
    exit 1
fi

if [[ ! -f "$ICON_PATH" ]]; then
    echo "⚠️ Warning: icon.png not found at $ICON_PATH"
fi

# Set application name for dock
export CFBundleName="AUTO Blogger"
export CFBundleDisplayName="AUTO Blogger"
export CFBundleIdentifier="com.aryanvbw.autoblogger"

echo "🚀 Launching AUTO Blogger..."
echo "📁 Working directory: $PROJECT_ROOT"
echo "🐍 Python script: $PYTHON_SCRIPT"
echo "🖼️ Icon: $ICON_PATH"

# Change to the project root directory
cd "$PROJECT_ROOT"

# Launch the application
python3 gui_blogger.py

echo "✅ AUTO Blogger closed."
