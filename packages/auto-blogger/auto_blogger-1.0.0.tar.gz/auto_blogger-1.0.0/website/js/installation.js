// Installation Page JavaScript for Tab Functionality

// Initialize tabs when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeTabs();
});

// OS Tab switching functions (for legacy onclick handlers)
function showOSTab(osName) {
    const osTabsContainer = document.querySelector('.os-tabs');
    if (!osTabsContainer) return;
    
    const buttons = osTabsContainer.querySelectorAll('.tab-btn');
    const contents = osTabsContainer.querySelectorAll('.tab-content');
    
    // Remove active class from all
    buttons.forEach(btn => btn.classList.remove('active'));
    contents.forEach(content => content.classList.remove('active'));
    
    // Find and activate the target tab
    buttons.forEach((btn, index) => {
        if (btn.textContent.toLowerCase().includes(osName.toLowerCase())) {
            btn.classList.add('active');
        }
    });
    
    // Show corresponding content
    const targetContent = document.getElementById(osName);
    if (targetContent) {
        targetContent.classList.add('active');
    }
}

function showManualTab(tabName) {
    const manualTabsContainer = document.querySelector('.manual-os-tabs');
    if (!manualTabsContainer) return;
    
    const buttons = manualTabsContainer.querySelectorAll('.tab-btn');
    const contents = manualTabsContainer.querySelectorAll('.tab-content');
    
    // Remove active class from all
    buttons.forEach(btn => btn.classList.remove('active'));
    contents.forEach(content => content.classList.remove('active'));
    
    // Find and activate the target tab
    buttons.forEach(btn => {
        if (btn.onclick && btn.onclick.toString().includes(tabName)) {
            btn.classList.add('active');
        }
    });
    
    const targetContent = document.getElementById(tabName);
    if (targetContent) {
        targetContent.classList.add('active');
    }
}

function showDistroTab(distroName) {
    const distroTabsContainer = document.querySelector('.distro-tabs');
    if (!distroTabsContainer) return;
    
    const buttons = distroTabsContainer.querySelectorAll('.tab-btn');
    const contents = distroTabsContainer.querySelectorAll('.tab-content');
    
    // Remove active class from all
    buttons.forEach(btn => btn.classList.remove('active'));
    contents.forEach(content => content.classList.remove('active'));
    
    // Find and activate the target tab
    buttons.forEach(btn => {
        if (btn.onclick && btn.onclick.toString().includes(distroName)) {
            btn.classList.add('active');
        }
    });
    
    const targetContent = document.getElementById(distroName);
    if (targetContent) {
        targetContent.classList.add('active');
    }
}

function showWindowsTab(tabName) {
    const windowsTabsContainer = document.querySelector('.windows-options .option-tabs');
    if (!windowsTabsContainer) return;
    
    const buttons = windowsTabsContainer.querySelectorAll('.tab-btn');
    const contents = windowsTabsContainer.querySelectorAll('.tab-content');
    
    // Remove active class from all
    buttons.forEach(btn => btn.classList.remove('active'));
    contents.forEach(content => content.classList.remove('active'));
    
    // Find and activate the target tab
    buttons.forEach(btn => {
        if (btn.onclick && btn.onclick.toString().includes(tabName)) {
            btn.classList.add('active');
        }
    });
    
    const targetContent = document.getElementById(tabName);
    if (targetContent) {
        targetContent.classList.add('active');
    }
}

function initializeTabs() {
    // Initialize OS tabs for one-command setup
    initializeTabGroup('os-tabs');
    
    // Initialize manual OS tabs
    initializeTabGroup('manual-os-tabs');
    
    // Initialize distro tabs
    initializeTabGroup('distro-tabs');
    
    // Initialize Windows option tabs
    initializeTabGroup('windows-options');
    
    // Initialize any other tab groups
    initializeTabGroup('option-tabs');
}

function initializeTabGroup(groupClass) {
    const tabGroups = document.querySelectorAll(`.${groupClass}`);
    
    tabGroups.forEach(group => {
        const buttons = group.querySelectorAll('.tab-btn');
        const contents = group.querySelectorAll('.tab-content');
        
        if (buttons.length === 0 || contents.length === 0) return;
        
        // Set first tab as active by default
        if (buttons[0] && contents[0]) {
            buttons[0].classList.add('active');
            contents[0].classList.add('active');
        }
        
        // Add click event listeners
        buttons.forEach((button, index) => {
            button.addEventListener('click', () => {
                switchTab(group, index);
            });
        });
    });
}

function switchTab(tabGroup, activeIndex) {
    const buttons = tabGroup.querySelectorAll('.tab-btn');
    const contents = tabGroup.querySelectorAll('.tab-content');
    
    // Remove active class from all buttons and contents
    buttons.forEach(btn => btn.classList.remove('active'));
    contents.forEach(content => content.classList.remove('active'));
    
    // Add active class to selected button and content
    if (buttons[activeIndex] && contents[activeIndex]) {
        buttons[activeIndex].classList.add('active');
        contents[activeIndex].classList.add('active');
    }
}

// Copy to clipboard functionality
function copyToClipboard(text, button) {
    navigator.clipboard.writeText(text).then(() => {
        // Show feedback
        const originalText = button.textContent;
        button.textContent = 'Copied!';
        button.style.background = '#28a745';
        
        setTimeout(() => {
            button.textContent = originalText;
            button.style.background = '';
        }, 2000);
    }).catch(err => {
        console.error('Failed to copy text: ', err);
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        
        const originalText = button.textContent;
        button.textContent = 'Copied!';
        setTimeout(() => {
            button.textContent = originalText;
        }, 2000);
    });
}

function copyCode(button) {
    const codeBlock = button.closest('.code-block, .terminal-block');
    if (codeBlock) {
        const code = codeBlock.querySelector('code, pre');
        if (code) {
            copyToClipboard(code.textContent, button);
        }
    }
}

// Add copy buttons to code blocks
function addCopyButtons() {
    const codeBlocks = document.querySelectorAll('.code-block');
    
    codeBlocks.forEach(block => {
        const header = block.querySelector('.code-header, .terminal-header');
        if (header && !header.querySelector('.copy-btn')) {
            const copyBtn = document.createElement('button');
            copyBtn.className = 'copy-btn';
            copyBtn.textContent = 'Copy';
            copyBtn.onclick = () => {
                const code = block.querySelector('code, .terminal-content');
                if (code) {
                    copyToClipboard(code.textContent, copyBtn);
                }
            };
            header.appendChild(copyBtn);
        }
    });
}

// Initialize copy buttons when page loads
document.addEventListener('DOMContentLoaded', addCopyButtons);

// Smooth scrolling for anchor links
document.addEventListener('DOMContentLoaded', function() {
    const links = document.querySelectorAll('a[href^="#"]');
    
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
});

// Highlight current section in navigation
function highlightCurrentSection() {
    const sections = document.querySelectorAll('section[id], .docs-section[id]');
    const navLinks = document.querySelectorAll('.nav-link');
    
    window.addEventListener('scroll', () => {
        let current = '';
        
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.clientHeight;
            if (window.pageYOffset >= sectionTop - 200) {
                current = section.getAttribute('id');
            }
        });
        
        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === `#${current}`) {
                link.classList.add('active');
            }
        });
    });
}

// Initialize section highlighting
document.addEventListener('DOMContentLoaded', highlightCurrentSection);

// Collapsible sections for mobile
function initializeCollapsibleSections() {
    const headers = document.querySelectorAll('.step-header');
    
    headers.forEach(header => {
        header.style.cursor = 'pointer';
        header.addEventListener('click', () => {
            const content = header.nextElementSibling;
            if (content && content.classList.contains('step-content')) {
                content.style.display = content.style.display === 'none' ? 'block' : 'none';
            }
        });
    });
}

// Initialize collapsible sections on mobile
if (window.innerWidth <= 768) {
    document.addEventListener('DOMContentLoaded', initializeCollapsibleSections);
}

// Handle window resize
window.addEventListener('resize', () => {
    if (window.innerWidth <= 768) {
        initializeCollapsibleSections();
    }
});

// Terminal opening functionality
function getCurrentOS() {
    // Get the active OS tab
    const activeTabs = document.querySelectorAll('.os-tabs .tab-btn.active');
    if (activeTabs.length > 0) {
        const activeTabText = activeTabs[0].textContent.trim();
        if (activeTabText.includes('Linux')) return 'linux';
        if (activeTabText.includes('macOS')) return 'macos';
        if (activeTabText.includes('Windows')) return 'windows';
    }
    
    // Fallback: detect user's OS
    const userAgent = navigator.userAgent;
    if (userAgent.includes('Mac')) return 'macos';
    if (userAgent.includes('Win')) return 'windows';
    return 'linux';
}

function getInstallCommand(os) {
    const baseCommand = 'curl -fsSL https://raw.githubusercontent.com/AryanVBW/AUTO-blogger/main/install_autoblog.sh | bash';
    
    switch (os) {
        case 'windows':
            return `wsl ${baseCommand}`;
        case 'macos':
        case 'linux':
        default:
            return baseCommand;
    }
}

function openTerminalWithCommand() {
    const currentOS = getCurrentOS();
    const command = getInstallCommand(currentOS);
    
    // Show loading state
    const button = document.getElementById('openTerminalBtn');
    const originalText = button.innerHTML;
    button.innerHTML = '<i data-feather="loader" style="width: 18px; height: 18px; vertical-align: middle; margin-right: 8px; animation: spin 1s linear infinite;"></i>Preparing Installation...';
    button.disabled = true;
    
    try {
        if (currentOS === 'macos') {
            openMacOSTerminal(command);
            // For macOS, show success immediately since we're downloading files
            setTimeout(() => {
                button.innerHTML = '<i data-feather="download" style="width: 18px; height: 18px; vertical-align: middle; margin-right: 8px;"></i>Files Downloaded!';
                button.style.background = 'linear-gradient(135deg, #28a745, #20c997)';
                
                setTimeout(() => {
                    button.innerHTML = originalText;
                    button.style.background = '';
                    button.disabled = false;
                    feather.replace();
                }, 3000);
            }, 800);
        } else if (currentOS === 'windows') {
            openWindowsTerminal(command);
            setTimeout(() => {
                button.innerHTML = '<i data-feather="download" style="width: 18px; height: 18px; vertical-align: middle; margin-right: 8px;"></i>Script Created!';
                button.style.background = 'linear-gradient(135deg, #28a745, #20c997)';
                
                setTimeout(() => {
                    button.innerHTML = originalText;
                    button.style.background = '';
                    button.disabled = false;
                    feather.replace();
                }, 3000);
            }, 800);
        } else {
            openLinuxTerminal(command);
            setTimeout(() => {
                button.innerHTML = '<i data-feather="download" style="width: 18px; height: 18px; vertical-align: middle; margin-right: 8px;"></i>Script Ready!';
                button.style.background = 'linear-gradient(135deg, #28a745, #20c997)';
                
                setTimeout(() => {
                    button.innerHTML = originalText;
                    button.style.background = '';
                    button.disabled = false;
                    feather.replace();
                }, 3000);
            }, 800);
        }
        
    } catch (error) {
        console.error('Failed to prepare installation:', error);
        
        // Show error state
        setTimeout(() => {
            button.innerHTML = '<i data-feather="x" style="width: 18px; height: 18px; vertical-align: middle; margin-right: 8px;"></i>Command Copied Instead';
            button.style.background = 'linear-gradient(135deg, #dc3545, #fd7e14)';
            
            // Fallback to copying command
            copyToClipboard(command, button);
            
            setTimeout(() => {
                button.innerHTML = originalText;
                button.style.background = '';
                button.disabled = false;
                feather.replace();
            }, 3000);
        }, 800);
    }
}

function openMacOSTerminal(command) {
    // Method 1: Try terminal:// protocol (works on some systems)
    try {
        window.open(`terminal://run?command=${encodeURIComponent(command)}`, '_blank');
        return;
    } catch (e) {
        console.log('Terminal protocol not available');
    }

    // Method 2: Create and download an executable script file
    const scriptContent = `#!/bin/bash
# AUTO-blogger Installation Script for macOS
echo "🚀 Starting AUTO-blogger installation..."
echo ""
echo "Running command: ${command}"
echo ""

# Run the installation command
${command}

echo ""
echo "✅ Installation completed!"
echo "Press any key to close this terminal..."
read -n 1
`;

    // Method 3: Create AppleScript that users can double-click
    const appleScript = `tell application "Terminal"
    activate
    do script "cd ~ && echo '🚀 AUTO-blogger Installation' && echo '' && ${command.replace(/"/g, '\\"')} && echo '' && echo '✅ Installation completed! Press any key to close...' && read -n 1"
end tell`;

    // Download both files
    downloadFile(scriptContent, 'auto_blogger_install.sh', 'text/plain');
    downloadFile(appleScript, 'auto_blogger_install.scpt', 'text/plain');
    
    // Copy command to clipboard
    copyToClipboard(command, document.getElementById('openTerminalBtn'));
    
    // Show macOS-specific instructions
    showMacOSInstructions(command);
}

function downloadFile(content, filename, type) {
    const blob = new Blob([content], { type: type });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.style.display = 'none';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

function showMacOSInstructions(command) {
    // Create a macOS-specific modal with detailed instructions
    const modal = document.createElement('div');
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.8);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 10000;
        backdrop-filter: blur(5px);
    `;
    
    modal.innerHTML = `
        <div style="
            background: white;
            padding: 2rem;
            border-radius: 12px;
            max-width: 650px;
            max-height: 80vh;
            overflow-y: auto;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            color: #2d3748;
        ">
            <h3 style="margin-top: 0; color: #2d3748; font-size: 1.5rem;">🍎 macOS Installation Options</h3>
            <p style="color: #718096; margin-bottom: 1.5rem;">Two files have been downloaded to help you install AUTO-blogger. Choose the method that works best for you:</p>
            
            <div style="border: 2px solid #e2e8f0; border-radius: 8px; padding: 1.5rem; margin-bottom: 1.5rem; background: #f7fafc;">
                <h4 style="margin-top: 0; color: #2d3748;">🎯 Method 1: Double-click AppleScript (Easiest)</h4>
                <ol style="color: #4a5568; line-height: 1.6;">
                    <li>Find <strong>auto_blogger_install.scpt</strong> in your Downloads folder</li>
                    <li>Double-click the file to run it automatically</li>
                    <li>Click "Run" if prompted by macOS</li>
                    <li>Terminal will open and run the installation</li>
                </ol>
            </div>
            
            <div style="border: 2px solid #bee3f8; border-radius: 8px; padding: 1.5rem; margin-bottom: 1.5rem; background: #ebf8ff;">
                <h4 style="margin-top: 0; color: #2d3748;">⚡ Method 2: Terminal Command (Advanced)</h4>
                <ol style="color: #4a5568; line-height: 1.6;">
                    <li>Open Terminal (Cmd + Space, type "Terminal")</li>
                    <li>Paste this command (already copied to clipboard):</li>
                </ol>
                <div style="background: #2d3748; padding: 1rem; border-radius: 8px; color: #e2e8f0; font-family: 'Monaco', 'Menlo', monospace; margin: 1rem 0; font-size: 0.875rem; word-break: break-all;">
                    ${command}
                </div>
                <p style="color: #4a5568; margin: 0; font-size: 0.875rem;">Then press Enter to run the command.</p>
            </div>
            
            <div style="border: 2px solid #fed7d7; border-radius: 8px; padding: 1.5rem; margin-bottom: 1.5rem; background: #fffafa;">
                <h4 style="margin-top: 0; color: #2d3748;">🛠️ Method 3: Shell Script</h4>
                <ol style="color: #4a5568; line-height: 1.6;">
                    <li>Find <strong>auto_blogger_install.sh</strong> in Downloads</li>
                    <li>Open Terminal and run:</li>
                </ol>
                <div style="background: #2d3748; padding: 1rem; border-radius: 8px; color: #e2e8f0; font-family: 'Monaco', 'Menlo', monospace; margin: 1rem 0; font-size: 0.875rem;">
                    cd ~/Downloads<br>
                    chmod +x auto_blogger_install.sh<br>
                    ./auto_blogger_install.sh
                </div>
            </div>
            
            <div style="background: #f0fff4; border: 1px solid #9ae6b4; padding: 1rem; border-radius: 8px; margin-bottom: 1.5rem;">
                <p style="margin: 0; color: #22543d; font-weight: 600;">
                    ✅ Command already copied to clipboard! You can paste it anywhere.
                </p>
            </div>
            
            <button onclick="this.parentElement.parentElement.remove()" style="
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                border: none;
                padding: 0.875rem 1.5rem;
                border-radius: 8px;
                cursor: pointer;
                font-weight: 600;
                width: 100%;
                font-size: 1rem;
            ">
                Got it! Close Instructions
            </button>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Auto-remove after 45 seconds
    setTimeout(() => {
        if (modal.parentElement) {
            modal.remove();
        }
    }, 45000);
}

function showWindowsInstructions(command) {
    const modal = document.createElement('div');
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.8);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 10000;
        backdrop-filter: blur(5px);
    `;
    
    modal.innerHTML = `
        <div style="
            background: white;
            padding: 2rem;
            border-radius: 12px;
            max-width: 600px;
            max-height: 80vh;
            overflow-y: auto;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            color: #2d3748;
        ">
            <h3 style="margin-top: 0; color: #2d3748; font-size: 1.5rem;">🪟 Windows Installation</h3>
            <p style="color: #718096; margin-bottom: 1.5rem;">A batch file has been downloaded to help you install AUTO-blogger on Windows:</p>
            
            <div style="border: 2px solid #e2e8f0; border-radius: 8px; padding: 1.5rem; margin-bottom: 1.5rem; background: #f7fafc;">
                <h4 style="margin-top: 0; color: #2d3748;">🎯 Method 1: Run Batch File</h4>
                <ol style="color: #4a5568; line-height: 1.6;">
                    <li>Find <strong>auto_blogger_install.bat</strong> in your Downloads folder</li>
                    <li>Right-click and select <strong>"Run as administrator"</strong></li>
                    <li>Follow the on-screen instructions</li>
                </ol>
            </div>
            
            <div style="border: 2px solid #bee3f8; border-radius: 8px; padding: 1.5rem; margin-bottom: 1.5rem; background: #ebf8ff;">
                <h4 style="margin-top: 0; color: #2d3748;">⚡ Method 2: PowerShell/WSL</h4>
                <ol style="color: #4a5568; line-height: 1.6;">
                    <li>Open PowerShell or WSL</li>
                    <li>Paste this command (already copied to clipboard):</li>
                </ol>
                <div style="background: #2d3748; padding: 1rem; border-radius: 8px; color: #e2e8f0; font-family: 'Consolas', monospace; margin: 1rem 0; font-size: 0.875rem; word-break: break-all;">
                    ${command}
                </div>
            </div>
            
            <div style="background: #f0fff4; border: 1px solid #9ae6b4; padding: 1rem; border-radius: 8px; margin-bottom: 1.5rem;">
                <p style="margin: 0; color: #22543d; font-weight: 600;">
                    ✅ Command copied to clipboard! You can paste it in any terminal.
                </p>
            </div>
            
            <button onclick="this.parentElement.parentElement.remove()" style="
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                border: none;
                padding: 0.875rem 1.5rem;
                border-radius: 8px;
                cursor: pointer;
                font-weight: 600;
                width: 100%;
                font-size: 1rem;
            ">
                Got it! Close Instructions
            </button>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    setTimeout(() => {
        if (modal.parentElement) {
            modal.remove();
        }
    }, 30000);
}

function showLinuxInstructions(command) {
    const modal = document.createElement('div');
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.8);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 10000;
        backdrop-filter: blur(5px);
    `;
    
    modal.innerHTML = `
        <div style="
            background: white;
            padding: 2rem;
            border-radius: 12px;
            max-width: 600px;
            max-height: 80vh;
            overflow-y: auto;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            color: #2d3748;
        ">
            <h3 style="margin-top: 0; color: #2d3748; font-size: 1.5rem;">🐧 Linux Installation</h3>
            <p style="color: #718096; margin-bottom: 1.5rem;">A shell script has been downloaded to help you install AUTO-blogger on Linux:</p>
            
            <div style="border: 2px solid #e2e8f0; border-radius: 8px; padding: 1.5rem; margin-bottom: 1.5rem; background: #f7fafc;">
                <h4 style="margin-top: 0; color: #2d3748;">🎯 Method 1: Run Script File</h4>
                <ol style="color: #4a5568; line-height: 1.6;">
                    <li>Open terminal and navigate to Downloads:<br><code>cd ~/Downloads</code></li>
                    <li>Make the script executable:<br><code>chmod +x auto_blogger_install.sh</code></li>
                    <li>Run the script:<br><code>./auto_blogger_install.sh</code></li>
                </ol>
            </div>
            
            <div style="border: 2px solid #bee3f8; border-radius: 8px; padding: 1.5rem; margin-bottom: 1.5rem; background: #ebf8ff;">
                <h4 style="margin-top: 0; color: #2d3748;">⚡ Method 2: Direct Command</h4>
                <p style="color: #4a5568; margin-bottom: 1rem;">Paste this command directly in your terminal (already copied to clipboard):</p>
                <div style="background: #2d3748; padding: 1rem; border-radius: 8px; color: #e2e8f0; font-family: 'Ubuntu Mono', monospace; margin: 1rem 0; font-size: 0.875rem; word-break: break-all;">
                    ${command}
                </div>
            </div>
            
            <div style="background: #f0fff4; border: 1px solid #9ae6b4; padding: 1rem; border-radius: 8px; margin-bottom: 1.5rem;">
                <p style="margin: 0; color: #22543d; font-weight: 600;">
                    ✅ Command copied to clipboard! You can paste it in any terminal.
                </p>
            </div>
            
            <button onclick="this.parentElement.parentElement.remove()" style="
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                border: none;
                padding: 0.875rem 1.5rem;
                border-radius: 8px;
                cursor: pointer;
                font-weight: 600;
                width: 100%;
                font-size: 1rem;
            ">
                Got it! Close Instructions
            </button>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    setTimeout(() => {
        if (modal.parentElement) {
            modal.remove();
        }
    }, 30000);
}

function openWindowsTerminal(command) {
    try {
        // Try to open WSL or PowerShell
        const wslCommand = `wsl.exe -e bash -c "${command.replace(/"/g, '\\"')}"`;
        
        // Create a batch file to run the command
        const batchContent = `@echo off
echo Opening WSL to install AUTO-blogger...
echo.
echo If WSL is not available, please install it first:
echo https://docs.microsoft.com/en-us/windows/wsl/install
echo.
pause
${wslCommand}
pause`;
        
        const batchBlob = new Blob([batchContent], { type: 'text/plain' });
        const batchUrl = URL.createObjectURL(batchBlob);
        
        const link = document.createElement('a');
        link.href = batchUrl;
        link.download = 'auto_blogger_install.bat';
        link.click();
        URL.revokeObjectURL(batchUrl);
        
        // Also copy command to clipboard
        copyToClipboard(command, document.getElementById('openTerminalBtn'));
        
        // Show instructions
        showWindowsInstructions(command);
        
    } catch (e) {
        throw new Error('Failed to create Windows terminal launcher');
    }
}

function openLinuxTerminal(command) {
    try {
        // Try various Linux terminal applications
        const terminals = [
            `gnome-terminal -- bash -c "${command}; exec bash"`,
            `konsole -e bash -c "${command}; exec bash"`,
            `xterm -e bash -c "${command}; exec bash"`,
            `x-terminal-emulator -e bash -c "${command}; exec bash"`
        ];
        
        // Create a shell script
        const scriptContent = `#!/bin/bash
# AUTO-blogger Installation Script
echo "Starting AUTO-blogger installation..."
echo "Command: ${command}"
echo ""

# Try to detect and use available terminal
if command -v gnome-terminal >/dev/null 2>&1; then
    gnome-terminal -- bash -c "${command}; echo 'Press any key to close...'; read -n 1"
elif command -v konsole >/dev/null 2>&1; then
    konsole -e bash -c "${command}; echo 'Press any key to close...'; read -n 1"
elif command -v xterm >/dev/null 2>&1; then
    xterm -e bash -c "${command}; echo 'Press any key to close...'; read -n 1"
else
    echo "No suitable terminal found. Please run the following command manually:"
    echo "${command}"
    echo "Press any key to close..."
    read -n 1
fi`;
        
        const scriptBlob = new Blob([scriptContent], { type: 'text/plain' });
        const scriptUrl = URL.createObjectURL(scriptBlob);
        
        const link = document.createElement('a');
        link.href = scriptUrl;
        link.download = 'auto_blogger_install.sh';
        link.click();
        URL.revokeObjectURL(scriptUrl);
        
        // Also copy command to clipboard
        copyToClipboard(command, document.getElementById('openTerminalBtn'));
        
        // Show instructions
        showLinuxInstructions(command);
        
    } catch (e) {
        throw new Error('Failed to create Linux terminal launcher');
    }
}

function showTerminalInstructions(os, command) {
    // Create a modal with instructions
    const modal = document.createElement('div');
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.8);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 10000;
        backdrop-filter: blur(5px);
    `;
    
    let instructions = '';
    switch (os) {
        case 'macOS':
            instructions = `
                <h3>📱 macOS Terminal Instructions</h3>
                <p>A script file has been downloaded. To use it:</p>
                <ol>
                    <li>Open <strong>Terminal</strong> (Cmd + Space, type "Terminal")</li>
                    <li>Navigate to your Downloads folder</li>
                    <li>Run: <code>osascript auto_blogger_install.scpt</code></li>
                </ol>
                <p><strong>Or manually run:</strong></p>
                <div style="background: #2d3748; padding: 1rem; border-radius: 8px; color: #e2e8f0; font-family: monospace; margin: 1rem 0;">
                    ${command}
                </div>
            `;
            break;
        case 'Windows':
            instructions = `
                <h3>🪟 Windows Installation Instructions</h3>
                <p>A batch file has been downloaded. To use it:</p>
                <ol>
                    <li>Find <strong>auto_blogger_install.bat</strong> in your Downloads</li>
                    <li>Right-click and select <strong>"Run as administrator"</strong></li>
                    <li>Or open <strong>PowerShell</strong> and run:</li>
                </ol>
                <div style="background: #2d3748; padding: 1rem; border-radius: 8px; color: #e2e8f0; font-family: monospace; margin: 1rem 0;">
                    ${command}
                </div>
            `;
            break;
        case 'Linux':
            instructions = `
                <h3>🐧 Linux Terminal Instructions</h3>
                <p>A script file has been downloaded. To use it:</p>
                <ol>
                    <li>Open your terminal</li>
                    <li>Navigate to Downloads: <code>cd ~/Downloads</code></li>
                    <li>Make executable: <code>chmod +x auto_blogger_install.sh</code></li>
                    <li>Run: <code>./auto_blogger_install.sh</code></li>
                </ol>
                <p><strong>Or manually run:</strong></p>
                <div style="background: #2d3748; padding: 1rem; border-radius: 8px; color: #e2e8f0; font-family: monospace; margin: 1rem 0;">
                    ${command}
                </div>
            `;
            break;
    }
    
    modal.innerHTML = `
        <div style="
            background: white;
            padding: 2rem;
            border-radius: 12px;
            max-width: 600px;
            max-height: 80vh;
            overflow-y: auto;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            color: #2d3748;
        ">
            ${instructions}
            <p style="margin-top: 1.5rem; padding-top: 1rem; border-top: 1px solid #e2e8f0; color: #718096;">
                ✅ <strong>Command copied to clipboard!</strong> You can paste it directly into your terminal.
            </p>
            <button onclick="this.parentElement.parentElement.remove()" style="
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                border: none;
                padding: 0.75rem 1.5rem;
                border-radius: 8px;
                cursor: pointer;
                font-weight: 600;
                margin-top: 1rem;
                width: 100%;
            ">
                Got it! Close Instructions
            </button>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Auto-remove after 30 seconds
    setTimeout(() => {
        if (modal.parentElement) {
            modal.remove();
        }
    }, 30000);
}