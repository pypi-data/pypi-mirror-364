// Homepage JavaScript for OS Installation Tabs

// Initialize homepage functionality when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('Homepage JavaScript loaded');
    initializeHomepageTabs();
    initializeModernOSTabs();
    initializeFeatureAnimations();
    
    // Wait a moment for DOM to be fully ready, then detect and reorder OS tabs
    setTimeout(() => {
        detectAndHighlightOS();
        addOSDetectionStyles();
        updateTabDescriptionVisibility();
    }, 100);
    
    // Add immediate debug test
    setTimeout(() => {
        testOSTabsSetup();
    }, 1000);
});

function initializeHomepageTabs() {
    // Initialize OS installation tabs (legacy)
    const osTabsContainer = document.querySelector('.os-installation-tabs');
    if (osTabsContainer) {
        const buttons = osTabsContainer.querySelectorAll('.tab-btn');
        const contents = osTabsContainer.querySelectorAll('.tab-content');
        
        if (buttons.length > 0 && contents.length > 0) {
            // Set first tab as active by default
            buttons[0].classList.add('active');
            contents[0].classList.add('active');
            
            // Add click event listeners
            buttons.forEach((button, index) => {
                button.addEventListener('click', () => {
                    switchHomepageTab(osTabsContainer, index);
                });
            });
        }
    }
}

function initializeModernOSTabs() {
    console.log('Initializing modern OS tabs...');
    
    // Initialize modern OS tabs
    const modernOSTabs = document.querySelector('.os-tabs-modern');
    if (!modernOSTabs) {
        console.error('Modern OS tabs container not found!');
        return;
    }
    
    const tabs = modernOSTabs.querySelectorAll('.os-tab');
    const installCommand = document.getElementById('install-command');
    
    console.log(`Found ${tabs.length} OS tabs`);
    console.log('Install command element:', installCommand);
    
    if (!installCommand) {
        console.error('Install command element not found!');
        return;
    }
    
    // Just ensure tabs are clickable - onclick handlers are in HTML
    tabs.forEach((tab, index) => {
        tab.style.cursor = 'pointer';
        const osType = tab.getAttribute('data-os');
        console.log(`Tab ${index + 1} ready for OS: ${osType}`);
    });
    
    console.log('Modern OS tabs initialization complete - using HTML onclick handlers');
}

function switchOSTab(tabs, activeTab, installCommand, commands) {
    console.log('Switching OS tab...');
    console.log('Active tab:', activeTab);
    console.log('Install command element:', installCommand);
    
    // Remove active class from all tabs
    tabs.forEach(t => {
        t.classList.remove('active');
        t.style.transform = '';
        console.log('Removed active from:', t.getAttribute('data-os'));
    });
    
    // Add active class to clicked tab
    activeTab.classList.add('active');
    const osType = activeTab.getAttribute('data-os');
    console.log('Set active on:', osType);
    
    // Update install command
    if (installCommand && commands[osType]) {
        const newCommand = commands[osType];
        installCommand.textContent = newCommand;
        console.log(`Updated command for ${osType}:`, newCommand);
        
        // Also update the prompt symbol based on OS
        const prompt = document.querySelector('.prompt');
        if (prompt) {
            if (osType === 'windows') {
                prompt.textContent = 'PS>';
            } else {
                prompt.textContent = '$';
            }
        }
    } else {
        console.error('Could not update command - missing elements or command');
    }
    
    // Add visual feedback with animation
    activeTab.style.transform = 'scale(0.98)';
    activeTab.style.transition = 'transform 0.15s ease';
    setTimeout(() => {
        activeTab.style.transform = 'scale(1)';
    }, 150);
    
    // Update terminal title to show selected OS
    const terminalTitle = document.querySelector('.terminal-title .title-text');
    if (terminalTitle) {
        const osNames = {
            linux: 'Linux Terminal',
            macos: 'macOS Terminal', 
            windows: 'PowerShell'
        };
        terminalTitle.textContent = osNames[osType] || 'Terminal';
        console.log('Updated terminal title:', osNames[osType]);
    }
    
    // Update terminal status
    const statusText = document.querySelector('.title-status span');
    if (statusText) {
        statusText.textContent = `Ready to Install on ${osType.charAt(0).toUpperCase() + osType.slice(1)}`;
        console.log('Updated status text');
    }
    
    console.log('OS tab switch complete');
}

function switchHomepageTab(tabContainer, activeIndex) {
    const buttons = tabContainer.querySelectorAll('.tab-btn');
    const contents = tabContainer.querySelectorAll('.tab-content');
    
    // Remove active class from all buttons and contents
    buttons.forEach(btn => btn.classList.remove('active'));
    contents.forEach(content => content.classList.remove('active'));
    
    // Add active class to selected button and content
    if (buttons[activeIndex] && contents[activeIndex]) {
        buttons[activeIndex].classList.add('active');
        contents[activeIndex].classList.add('active');
    }
}

// Feature animations on scroll
function initializeFeatureAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, observerOptions);
    
    // Observe feature cards
    const featureCards = document.querySelectorAll('.feature-card');
    featureCards.forEach(card => {
        observer.observe(card);
    });
    
    // Observe installation benefits
    const installationBenefits = document.querySelectorAll('.benefit-item');
    installationBenefits.forEach((benefit, index) => {
        benefit.style.animationDelay = `${index * 0.1}s`;
        observer.observe(benefit);
    });
    
    // Observe support cards
    const supportCards = document.querySelectorAll('.support-card');
    supportCards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        observer.observe(card);
    });
}

// Auto-detect user's OS and reorder + highlight appropriate tab
function detectAndHighlightOS() {
    const userAgent = navigator.userAgent.toLowerCase();
    let detectedOS = 'linux'; // default
    
    // More comprehensive OS detection
    if (userAgent.includes('mac') || userAgent.includes('darwin')) {
        detectedOS = 'macos';
    } else if (userAgent.includes('win')) {
        detectedOS = 'windows';
    } else if (userAgent.includes('linux') || userAgent.includes('x11')) {
        detectedOS = 'linux';
    }
    
    console.log('Detected OS:', detectedOS);
    
    // Find and activate the appropriate tab for legacy tabs
    const osTabsContainer = document.querySelector('.os-installation-tabs');
    if (osTabsContainer) {
        const buttons = osTabsContainer.querySelectorAll('.tab-btn');
        const contents = osTabsContainer.querySelectorAll('.tab-content');
        
        buttons.forEach((button, index) => {
            const buttonOS = button.getAttribute('data-os');
            if (buttonOS === detectedOS) {
                // Remove active from all
                buttons.forEach(btn => btn.classList.remove('active'));
                contents.forEach(content => content.classList.remove('active'));
                
                // Activate detected OS tab
                button.classList.add('active');
                if (contents[index]) {
                    contents[index].classList.add('active');
                }
            }
        });
    }
    
    // Find and reorder + activate the appropriate tab for modern tabs
    const modernOSTabs = document.querySelector('.os-tabs-modern');
    if (modernOSTabs) {
        reorderOSTabsByDetection(modernOSTabs, detectedOS);
        
        const tabs = modernOSTabs.querySelectorAll('.os-tab');
        const installCommand = document.getElementById('install-command');
        
        const commands = {
            linux: 'curl -fsSL https://raw.githubusercontent.com/AryanVBW/AUTO-blogger/main/install_autoblog.sh | bash',
            macos: 'curl -fsSL https://raw.githubusercontent.com/AryanVBW/AUTO-blogger/main/install_autoblog.sh | bash',
            windows: 'iwr -useb https://raw.githubusercontent.com/AryanVBW/AUTO-blogger/main/install_autoblog.ps1 | iex'
        };
        
        // Remove active from all tabs first
        tabs.forEach(t => t.classList.remove('active'));
        
        // Find and activate the detected OS tab (now should be first)
        const detectedTab = modernOSTabs.querySelector(`[data-os="${detectedOS}"]`);
        if (detectedTab) {
            detectedTab.classList.add('active');
            
            // Update command
            if (installCommand && commands[detectedOS]) {
                installCommand.textContent = commands[detectedOS];
                console.log('Set default command for:', detectedOS);
            }
            
            // Update terminal title
            const terminalTitle = document.querySelector('.terminal-title .title-text');
            if (terminalTitle) {
                const osNames = {
                    linux: 'Linux Terminal',
                    macos: 'macOS Terminal', 
                    windows: 'PowerShell'
                };
                terminalTitle.textContent = osNames[detectedOS] || 'Terminal';
            }
            
            // Update prompt symbol
            const prompt = document.querySelector('.prompt');
            if (prompt) {
                prompt.textContent = detectedOS === 'windows' ? 'PS>' : '$';
            }
            
            // Update status text
            const statusText = document.querySelector('.title-status span');
            if (statusText) {
                statusText.textContent = `Ready to Install on ${detectedOS.charAt(0).toUpperCase() + detectedOS.slice(1)}`;
            }
        }
    }
}

// Function to reorder OS tabs - puts detected OS first
function reorderOSTabsByDetection(container, detectedOS) {
    console.log('Reordering OS tabs, detected OS:', detectedOS);
    
    // Get all current tabs
    const tabs = Array.from(container.querySelectorAll('.os-tab'));
    console.log('Current tabs order:', tabs.map(tab => tab.getAttribute('data-os')));
    
    if (tabs.length === 0) {
        console.log('No tabs found to reorder');
        return;
    }
    
    // Define the desired order based on detected OS
    const getDesiredOrder = (detectedOS) => {
        switch (detectedOS) {
            case 'macos':
                return ['macos', 'linux', 'windows'];
            case 'windows':
                return ['windows', 'macos', 'linux'];
            case 'linux':
            default:
                return ['linux', 'macos', 'windows'];
        }
    };
    
    const desiredOrder = getDesiredOrder(detectedOS);
    console.log('Desired order:', desiredOrder);
    
    // Create a map of tabs by OS
    const tabMap = {};
    tabs.forEach(tab => {
        const osType = tab.getAttribute('data-os');
        if (osType) {
            tabMap[osType] = tab;
        }
    });
    
    // Clear the container
    container.innerHTML = '';
    
    // Re-append tabs in desired order
    desiredOrder.forEach(osType => {
        if (tabMap[osType]) {
            container.appendChild(tabMap[osType]);
            console.log('Moved', osType, 'tab to position');
        }
    });
    
    // Add any remaining tabs that weren't in our desired order
    tabs.forEach(tab => {
        const osType = tab.getAttribute('data-os');
        if (osType && !desiredOrder.includes(osType)) {
            container.appendChild(tab);
            console.log('Added remaining tab:', osType);
        }
    });
    
    console.log('Tab reordering complete');
    
    // Log helpful message for users
    console.log(`🎯 AUTO-blogger: Detected your OS as ${detectedOS.toUpperCase()}. The ${detectedOS} installation option has been moved to the top and pre-selected for your convenience!`);
    
    // Add visual indicator for detected OS
    setTimeout(() => {
        const detectedTab = container.querySelector(`[data-os="${detectedOS}"]`);
        if (detectedTab) {
            // Add detected OS class for styling
            detectedTab.classList.add('detected-os');
            detectedTab.classList.add('detected-first');
            
            // Add a small badge or indicator
            const existingBadge = detectedTab.querySelector('.detected-os-badge');
            if (!existingBadge) {
                const badge = document.createElement('div');
                badge.className = 'detected-os-badge';
                badge.innerHTML = '●';
                badge.style.cssText = `
                    position: absolute;
                    top: 8px;
                    right: 8px;
                    width: 8px;
                    height: 8px;
                    background: var(--success-color, #28a745);
                    border-radius: 50%;
                    z-index: 10;
                    animation: pulse 2s infinite;
                `;
                
                // Make sure the tab has relative positioning
                detectedTab.style.position = 'relative';
                detectedTab.appendChild(badge);
            }
            
            // Update the tab description to show it's detected
            const tabDesc = detectedTab.querySelector('.tab-desc');
            if (tabDesc && !tabDesc.textContent.includes('(Detected)')) {
                const originalText = tabDesc.textContent;
                tabDesc.textContent = `${originalText} (Detected)`;
                
                // Ensure high contrast colors for visibility
                if (detectedTab.classList.contains('active')) {
                    tabDesc.style.color = 'rgba(255, 255, 255, 0.95)';
                } else {
                    tabDesc.style.color = 'var(--primary-color)';
                }
                tabDesc.style.fontWeight = '600';
                tabDesc.style.textShadow = '0 1px 2px rgba(0, 0, 0, 0.1)';
            }
            
            console.log('Visual indicators added for detected OS:', detectedOS);
        }
    }, 100);
}

// Enhanced OS detection that also handles mobile devices
function getDetailedOSInfo() {
    const userAgent = navigator.userAgent;
    const platform = navigator.platform;
    
    let osInfo = {
        type: 'linux', // default
        name: 'Linux',
        variant: '',
        isMobile: false
    };
    
    // Check for mobile first
    if (/Android/i.test(userAgent)) {
        osInfo = { type: 'linux', name: 'Android', variant: 'mobile', isMobile: true };
    } else if (/iPad|iPhone|iPod/.test(userAgent)) {
        osInfo = { type: 'macos', name: 'iOS', variant: 'mobile', isMobile: true };
    }
    // Desktop OS detection
    else if (/Mac/.test(platform) || /Darwin/.test(userAgent)) {
        const isMacSilicon = /Apple/.test(navigator.userAgent) && 'ontouchend' in document;
        osInfo = { 
            type: 'macos', 
            name: 'macOS', 
            variant: isMacSilicon ? 'Apple Silicon' : 'Intel',
            isMobile: false 
        };
    } else if (/Win/.test(platform)) {
        let variant = 'Windows';
        if (/Windows NT 10/.test(userAgent)) variant = 'Windows 10/11';
        else if (/Windows NT 6\.3/.test(userAgent)) variant = 'Windows 8.1';
        else if (/Windows NT 6\.2/.test(userAgent)) variant = 'Windows 8';
        else if (/Windows NT 6\.1/.test(userAgent)) variant = 'Windows 7';
        
        osInfo = { type: 'windows', name: 'Windows', variant, isMobile: false };
    } else if (/Linux/.test(platform) || /X11/.test(platform)) {
        let variant = 'Linux';
        if (/Ubuntu/i.test(userAgent)) variant = 'Ubuntu';
        else if (/Debian/i.test(userAgent)) variant = 'Debian';
        else if (/CentOS/i.test(userAgent)) variant = 'CentOS';
        else if (/Fedora/i.test(userAgent)) variant = 'Fedora';
        
        osInfo = { type: 'linux', name: 'Linux', variant, isMobile: false };
    }
    
    console.log('Detailed OS info:', osInfo);
    return osInfo;
}

// Add CSS styles for OS detection indicators
function addOSDetectionStyles() {
    // Check if styles already exist
    if (document.getElementById('os-detection-styles')) {
        return;
    }
    
    const style = document.createElement('style');
    style.id = 'os-detection-styles';
    style.textContent = `
        @keyframes pulse {
            0% {
                opacity: 1;
                transform: scale(1);
            }
            50% {
                opacity: 0.7;
                transform: scale(1.2);
            }
            100% {
                opacity: 1;
                transform: scale(1);
            }
        }
        
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .detected-os-badge {
            animation: pulse 2s infinite !important;
        }
        
        .os-tab.detected-os {
            border: 2px solid var(--primary-color, #007bff) !important;
            box-shadow: 0 4px 12px rgba(0, 123, 255, 0.15) !important;
        }
        
        .os-tab.detected-os::before {
            content: "Your OS";
            position: absolute;
            top: -8px;
            left: 50%;
            transform: translateX(-50%);
            background: var(--primary-color, #007bff);
            color: white;
            font-size: 0.7rem;
            padding: 2px 8px;
            border-radius: 10px;
            z-index: 10;
            font-weight: 500;
        }
        
        .os-tab {
            transition: all 0.3s ease !important;
        }
        
        .copy-hint {
            animation: fadeIn 0.3s ease !important;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateX(-50%) translateY(10px); }
            to { opacity: 1; transform: translateX(-50%) translateY(0); }
        }
        
        /* Enhanced visual feedback for detected OS */
        .os-tab[data-os].detected-first {
            position: relative;
            order: -1; /* Ensure it appears first */
        }
        
        /* Ensure detected OS text is always visible with high contrast */
        .os-tab:not(.active) .tab-desc {
            color: var(--text-color) !important;
            font-weight: 500 !important;
            opacity: 1 !important;
        }
        
        /* Special styling for detected OS description */
        .os-tab.detected-os:not(.active) .tab-desc {
            color: var(--primary-color) !important;
            font-weight: 600 !important;
        }
        
        .os-tab.active.detected-os .tab-desc {
            color: rgba(255, 255, 255, 0.95) !important;
            font-weight: 600 !important;
        }
        
        /* Enhanced text visibility for all tab descriptions */
        .tab-desc {
            text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1) !important;
        }
        
        /* Dark theme text visibility */
        [data-theme="dark"] .os-tab:not(.active) .tab-desc {
            color: var(--text-color) !important;
            text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5) !important;
        }
        
        /* Smooth transition for reordering */
        .os-tabs-modern {
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }
        
        .os-tabs-modern .os-tab {
            transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        }
    `;
    
    document.head.appendChild(style);
    console.log('OS detection styles added');
}

// Enhanced copy functionality for install commands
function copyInstallCommand() {
    const commandElement = document.getElementById('install-command');
    if (!commandElement) {
        console.error('Install command element not found');
        return;
    }
    
    const command = commandElement.textContent;
    console.log('Copying command:', command);
    
    navigator.clipboard.writeText(command).then(() => {
        console.log('Command copied successfully');
        showCopyFeedback();
    }).catch(err => {
        console.error('Failed to copy: ', err);
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = command;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        try {
            document.execCommand('copy');
            console.log('Command copied via fallback method');
            showCopyFeedback();
        } catch (fallbackErr) {
            console.error('Fallback copy failed:', fallbackErr);
        }
        
        document.body.removeChild(textArea);
    });
}

function showCopyFeedback() {
    const button = document.querySelector('.copy-command-btn');
    if (!button) {
        console.error('Copy button not found');
        return;
    }
    
    const originalText = button.innerHTML;
    
    button.innerHTML = `
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M20 6L9 17L4 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        Copied!
    `;
    button.style.background = 'var(--success-color, #28a745)';
    button.style.color = 'white';
    
    // Show terminal animation
    simulateTerminalInstall();
    
    // Reset button after 3 seconds
    setTimeout(() => {
        button.innerHTML = originalText;
        button.style.background = '';
        button.style.color = '';
    }, 3000);
}

function simulateTerminalInstall() {
    const outputLines = document.querySelectorAll('.output-line');
    outputLines.forEach((line, index) => {
        line.style.opacity = '0';
        line.style.animation = 'none';
        
        setTimeout(() => {
            line.style.opacity = '1';
            line.style.animation = `fadeInUp 0.8s ease forwards`;
        }, index * 500 + 1000);
    });
}

// Copy code functionality for homepage (legacy support)
function copyCode(button) {
    const codeBlock = button.closest('.code-block') || button.closest('.terminal-block');
    const code = codeBlock.querySelector('code');
    
    if (code) {
        const text = code.textContent;
        
        navigator.clipboard.writeText(text).then(() => {
            // Show feedback
            const originalText = button.textContent;
            button.textContent = 'Copied!';
            button.style.background = '#28a745';
            button.style.color = 'white';
            
            setTimeout(() => {
                button.textContent = originalText;
                button.style.background = '';
                button.style.color = '';
            }, 2000);
        }).catch(err => {
            console.error('Failed to copy text: ', err);
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = text;
            textArea.style.position = 'fixed';
            textArea.style.left = '-999999px';
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
}

// Smooth scrolling for navigation links
document.addEventListener('DOMContentLoaded', function() {
    const navLinks = document.querySelectorAll('a[href^="#"]');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                e.preventDefault();
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
});

// Enhanced copy functionality with installation simulation
window.copyCode = function(button) {
    const codeBlock = button.closest('.code-block');
    const code = codeBlock.querySelector('code');
    
    if (code) {
        const text = code.textContent;
        
        navigator.clipboard.writeText(text).then(() => {
            // Show feedback
            const originalText = button.textContent;
            button.textContent = 'Copied!';
            button.style.background = '#28a745';
            button.style.color = 'white';
            
            // Add installation hint
            const hint = document.createElement('div');
            hint.className = 'copy-hint';
            hint.textContent = 'Now paste and run in your terminal!';
            hint.style.cssText = `
                position: absolute;
                top: -40px;
                left: 50%;
                transform: translateX(-50%);
                background: var(--primary-color);
                color: white;
                padding: 0.5rem 1rem;
                border-radius: 6px;
                font-size: 0.8rem;
                white-space: nowrap;
                z-index: 1000;
                animation: fadeIn 0.3s ease;
            `;
            
            button.style.position = 'relative';
            button.appendChild(hint);
            
            setTimeout(() => {
                button.textContent = originalText;
                button.style.background = '';
                button.style.color = '';
                if (hint.parentNode) {
                    hint.remove();
                }
            }, 3000);
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
};

// Make functions globally available
window.copyInstallCommand = copyInstallCommand;

// Global function to switch OS tabs (called from HTML onclick)
window.switchToOS = function(osType) {
    console.log('=== switchToOS called with:', osType, '===');
    
    try {
        // Get all tabs and install command element
        const tabs = document.querySelectorAll('.os-tab');
        const installCommand = document.getElementById('install-command');
        const prompt = document.querySelector('.prompt');
        
        console.log('Found tabs:', tabs.length);
        console.log('Install command element:', installCommand);
        console.log('Prompt element:', prompt);
        
        if (!tabs.length) {
            console.error('No OS tabs found!');
            return;
        }
        
        if (!installCommand) {
            console.error('Install command element not found!');
            return;
        }
        
        // Commands for each OS
        const commands = {
            linux: 'curl -fsSL https://raw.githubusercontent.com/AryanVBW/AUTO-blogger/main/install_autoblog.sh | bash',
            macos: 'curl -fsSL https://raw.githubusercontent.com/AryanVBW/AUTO-blogger/main/install_autoblog.sh | bash',
            windows: 'iwr -useb https://raw.githubusercontent.com/AryanVBW/AUTO-blogger/main/install_autoblog.ps1 | iex'
            // Alternative Windows commands:
            // PowerShell (Admin): Set-ExecutionPolicy Bypass -Scope Process -Force; iwr -useb https://raw.githubusercontent.com/AryanVBW/AUTO-blogger/main/install_autoblog.ps1 | iex
            // WSL (Ubuntu): curl -fsSL https://raw.githubusercontent.com/AryanVBW/AUTO-blogger/main/install_autoblog.sh | bash
        };
        
        if (!commands[osType]) {
            console.error('Invalid OS type:', osType);
            return;
        }
        
        // Remove active class from all tabs
        let activeTabFound = false;
        tabs.forEach(tab => {
            const tabOS = tab.getAttribute('data-os');
            if (tab.classList.contains('active')) {
                console.log('Removing active from:', tabOS);
            }
            tab.classList.remove('active');
            
            // Add active to the target tab
            if (tabOS === osType) {
                tab.classList.add('active');
                console.log('Added active to:', osType);
                activeTabFound = true;
            }
        });
        
        if (!activeTabFound) {
            console.error('Target tab not found for OS:', osType);
        }
        
        // Update install command
        const newCommand = commands[osType];
        installCommand.textContent = newCommand;
        console.log('Command updated to:', newCommand);
        
        // Update prompt symbol
        if (prompt) {
            const newPrompt = osType === 'windows' ? 'PS>' : '$';
            prompt.textContent = newPrompt;
            console.log('Prompt updated to:', newPrompt);
        }
        
        // Update terminal title
        const terminalTitle = document.querySelector('.terminal-title .title-text');
        if (terminalTitle) {
            const osNames = {
                linux: 'Linux Terminal',
                macos: 'macOS Terminal', 
                windows: 'PowerShell'
            };
            const newTitle = osNames[osType] || 'Terminal';
            terminalTitle.textContent = newTitle;
            console.log('Terminal title updated to:', newTitle);
        }
        
        // Update status text
        const statusText = document.querySelector('.title-status span');
        if (statusText) {
            const newStatus = `Ready to Install on ${osType.charAt(0).toUpperCase() + osType.slice(1)}`;
            statusText.textContent = newStatus;
            console.log('Status updated to:', newStatus);
        }
        
        // Ensure all tab descriptions are visible after switching
        updateTabDescriptionVisibility();
        
        console.log('=== switchToOS completed successfully ===');
        
    } catch (error) {
        console.error('Error in switchToOS:', error);
    }
};

// Debug function to test OS tabs
window.testOSTabs = function() {
    const tabs = document.querySelectorAll('.os-tab');
    console.log('Available OS tabs:', tabs.length);
    tabs.forEach((tab, index) => {
        console.log(`Tab ${index + 1}:`, {
            os: tab.getAttribute('data-os'),
            active: tab.classList.contains('active'),
            clickable: tab.style.cursor
        });
    });
};

// Debug function to test OS tabs setup
function testOSTabsSetup() {
    console.log('=== DEBUGGING OS TABS SETUP ===');
    
    const modernOSTabs = document.querySelector('.os-tabs-modern');
    console.log('Modern OS tabs container:', modernOSTabs);
    
    if (modernOSTabs) {
        const tabs = modernOSTabs.querySelectorAll('.os-tab');
        console.log('Found tabs:', tabs.length);
        
        tabs.forEach((tab, index) => {
            console.log(`Tab ${index}:`, {
                element: tab,
                dataOs: tab.getAttribute('data-os'),
                isActive: tab.classList.contains('active'),
                hasClickListener: tab.onclick !== null,
                cursor: getComputedStyle(tab).cursor
            });
        });
        
        const installCommand = document.getElementById('install-command');
        console.log('Install command element:', installCommand);
        console.log('Current command:', installCommand ? installCommand.textContent : 'NOT FOUND');
    }
    
    // Test each OS switch
    console.log('Testing OS switches...');
    setTimeout(() => {
        console.log('Testing Linux...');
        window.switchToOS('linux');
    }, 1000);
    
    setTimeout(() => {
        console.log('Testing macOS...');
        window.switchToOS('macos');
    }, 2000);
    
    setTimeout(() => {
        console.log('Testing Windows...');
        window.switchToOS('windows');
    }, 3000);
    
    console.log('=== END DEBUG ===');
}

// Add a test button functionality
window.testOSSwitch = function() {
    console.log('Manual test triggered');
    testOSTabsSetup();
};

// Function to ensure tab descriptions are always visible
function updateTabDescriptionVisibility() {
    const tabs = document.querySelectorAll('.os-tab');
    
    tabs.forEach(tab => {
        const tabDesc = tab.querySelector('.tab-desc');
        if (tabDesc) {
            if (tab.classList.contains('active')) {
                // Active tab - white text
                tabDesc.style.color = 'rgba(255, 255, 255, 0.95)';
                tabDesc.style.textShadow = '0 1px 2px rgba(0, 0, 0, 0.3)';
            } else if (tab.classList.contains('detected-os')) {
                // Detected OS but not active - primary color
                tabDesc.style.color = 'var(--primary-color)';
                tabDesc.style.textShadow = '0 1px 2px rgba(0, 0, 0, 0.1)';
                tabDesc.style.fontWeight = '600';
            } else {
                // Regular inactive tab - main text color
                tabDesc.style.color = 'var(--text-color)';
                tabDesc.style.textShadow = '0 1px 2px rgba(0, 0, 0, 0.1)';
                tabDesc.style.fontWeight = '500';
            }
        }
    });
    
    console.log('Tab description visibility updated');
}

console.log('Homepage JavaScript fully loaded with enhanced OS tab functionality');