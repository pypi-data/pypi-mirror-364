#!/bin/bash

# AUTO-blogger Main Installation Script
# This script calls the main installation script from the scripts directory
# 
# Copyright © 2025 AryanVBW
# GitHub: https://github.com/AryanVBW

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Call the main installation script
echo "Starting AUTO-blogger installation..."
bash "$SCRIPT_DIR/scripts/installation/install_auto_blogger.sh" "$@"