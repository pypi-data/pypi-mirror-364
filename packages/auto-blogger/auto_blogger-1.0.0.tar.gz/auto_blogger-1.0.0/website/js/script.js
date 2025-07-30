// Dark Mode Theme Toggle Functionality
class ThemeManager {
    constructor() {
        this.currentTheme = this.getStoredTheme() || this.getSystemTheme();
        this.themeToggle = document.getElementById('theme-toggle');
        this.themeIcon = document.getElementById('theme-icon');
        
        this.init();
    }
    
    init() {
        // Apply the current theme
        this.applyTheme(this.currentTheme);
        
        // Add event listener for theme toggle
        if (this.themeToggle) {
            this.themeToggle.addEventListener('click', () => {
                this.toggleTheme();
            });
            
            // Add keyboard support
            this.themeToggle.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    this.toggleTheme();
                }
            });
        }
        
        // Add keyboard shortcut (Ctrl/Cmd + Shift + D)
        document.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'D') {
                e.preventDefault();
                this.toggleTheme();
            }
        });
        
        // Listen for system theme changes
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            if (!this.getStoredTheme()) {
                this.currentTheme = e.matches ? 'dark' : 'light';
                this.applyTheme(this.currentTheme);
            }
        });
        
        // Apply theme on page load
        document.addEventListener('DOMContentLoaded', () => {
            this.applyTheme(this.currentTheme);
        });
    }
    
    getSystemTheme() {
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }
    
    getStoredTheme() {
        return localStorage.getItem('theme');
    }
    
    setStoredTheme(theme) {
        localStorage.setItem('theme', theme);
    }
    
    applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        this.updateThemeIcon(theme);
        this.currentTheme = theme;
    }
    
    updateThemeIcon(theme) {
        if (this.themeIcon) {
            // Remove existing feather icon classes
            this.themeIcon.removeAttribute('data-feather');
            
            if (theme === 'dark') {
                this.themeIcon.setAttribute('data-feather', 'moon');
                this.themeToggle.setAttribute('aria-label', 'Switch to light mode');
            } else {
                this.themeIcon.setAttribute('data-feather', 'sun');
                this.themeToggle.setAttribute('aria-label', 'Switch to dark mode');
            }
            
            // Refresh feather icons
            if (typeof feather !== 'undefined') {
                feather.replace();
            }
        }
    }
    
    toggleTheme() {
        const newTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        
        // Add a subtle animation effect
        if (this.themeToggle) {
            this.themeToggle.style.transform = 'scale(0.9) rotate(180deg)';
            
            setTimeout(() => {
                this.applyTheme(newTheme);
                this.setStoredTheme(newTheme);
                
                setTimeout(() => {
                    this.themeToggle.style.transform = 'scale(1) rotate(0deg)';
                }, 100);
            }, 150);
        } else {
            this.applyTheme(newTheme);
            this.setStoredTheme(newTheme);
        }
        
        // Dispatch custom event for other components that might need to know about theme changes
        window.dispatchEvent(new CustomEvent('themechange', { 
            detail: { theme: newTheme } 
        }));
    }
}

// Initialize theme manager
const themeManager = new ThemeManager();

// Enhanced Mobile Navigation Toggle with Smooth Animations
const hamburger = document.querySelector('.hamburger');
const navMenu = document.querySelector('.nav-menu');
const navOverlay = document.createElement('div');
navOverlay.classList.add('nav-overlay');
document.body.appendChild(navOverlay);

if (hamburger && navMenu) {
    // Toggle mobile menu
    hamburger.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        
        hamburger.classList.toggle('active');
        navMenu.classList.toggle('active');
        navOverlay.classList.toggle('active');
        
        // Prevent body scroll when menu is open
        if (navMenu.classList.contains('active')) {
            document.body.style.overflow = 'hidden';
        } else {
            document.body.style.overflow = '';
        }
    });

    // Close mobile menu when clicking overlay
    navOverlay.addEventListener('click', () => {
        hamburger.classList.remove('active');
        navMenu.classList.remove('active');
        navOverlay.classList.remove('active');
        document.body.style.overflow = '';
    });

    // Close mobile menu when clicking on a link
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', () => {
            hamburger.classList.remove('active');
            navMenu.classList.remove('active');
            navOverlay.classList.remove('active');
            document.body.style.overflow = '';
        });
    });

    // Close menu with Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && navMenu.classList.contains('active')) {
            hamburger.classList.remove('active');
            navMenu.classList.remove('active');
            navOverlay.classList.remove('active');
            document.body.style.overflow = '';
        }
    });
}

// Enhanced Navbar Scroll Effect with Smooth Transitions
const header = document.querySelector('.header');
let lastScrollTop = 0;
let scrollTimeout;

function handleNavbarScroll() {
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    
    // Clear previous timeout
    if (scrollTimeout) {
        clearTimeout(scrollTimeout);
    }
    
    // Add scrolled class with delay for smooth transition
    if (scrollTop > 50) {
        header.classList.add('scrolled');
    } else {
        // Delay removing scrolled class to prevent flickering
        scrollTimeout = setTimeout(() => {
            if (window.pageYOffset <= 50) {
                header.classList.remove('scrolled');
            }
        }, 100);
    }
    
    lastScrollTop = scrollTop;
}

// Throttled scroll handler for better performance
let navbarTicking = false;
function requestNavbarTick() {
    if (!navbarTicking) {
        requestAnimationFrame(() => {
            handleNavbarScroll();
            navbarTicking = false;
        });
        navbarTicking = true;
    }
}

window.addEventListener('scroll', requestNavbarTick);

// Active Navigation Link Management
function updateActiveNavLink() {
    const currentPath = window.location.pathname;
    const currentHash = window.location.hash;
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        link.classList.remove('active');
        
        const href = link.getAttribute('href');
        
        // Handle different types of links
        if (href) {
            // Exact page match
            if (href === currentPath || href === currentPath.split('/').pop()) {
                link.classList.add('active');
            }
            // Hash link match
            else if (href.startsWith('#') && href === currentHash) {
                link.classList.add('active');
            }
            // Home page special case
            else if ((currentPath === '/' || currentPath === '/index.html' || currentPath.endsWith('index.html')) && 
                     (href === 'index.html' || href === '/' || href === '#home' || href === './index.html')) {
                link.classList.add('active');
            }
        }
    });
}

// Update active link on page load and hash change
document.addEventListener('DOMContentLoaded', updateActiveNavLink);
window.addEventListener('hashchange', updateActiveNavLink);

// Smooth Scrolling with Enhanced Animation
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        
        const targetId = this.getAttribute('href');
        const target = document.querySelector(targetId);
        
        if (target) {
            // Close mobile menu if open
            if (navMenu && navMenu.classList.contains('active')) {
                hamburger.classList.remove('active');
                navMenu.classList.remove('active');
                navOverlay.classList.remove('active');
                document.body.style.overflow = '';
            }
            
            // Calculate offset for fixed header
            const headerHeight = header ? header.offsetHeight : 0;
            const targetPosition = target.getBoundingClientRect().top + window.pageYOffset - headerHeight - 20;
            
            // Smooth scroll with custom easing
            window.scrollTo({
                top: targetPosition,
                behavior: 'smooth'
            });
            
            // Update active link
            setTimeout(updateActiveNavLink, 300);
        }
    });
});

// Navigation Link Hover Effects
document.querySelectorAll('.nav-link').forEach(link => {
    // Add ripple effect on click (for touch devices)
    link.addEventListener('click', function(e) {
        if (!this.querySelector('.ripple')) {
            const ripple = document.createElement('span');
            ripple.classList.add('ripple');
            ripple.style.cssText = `
                position: absolute;
                border-radius: 50%;
                background: rgba(255, 255, 255, 0.6);
                transform: scale(0);
                animation: ripple-animation 0.6s linear;
                pointer-events: none;
            `;
            
            this.style.position = 'relative';
            this.style.overflow = 'hidden';
            
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            
            this.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        }
    });
});

// Add ripple animation CSS
const style = document.createElement('style');
style.textContent = `
    @keyframes ripple-animation {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Navigation Performance Optimization
function addNavigationIndicator() {
    // Create navigation indicator for active tab
    const indicator = document.createElement('div');
    indicator.classList.add('nav-indicator');
    navMenu.appendChild(indicator);
    
    function updateIndicator() {
        const activeLink = document.querySelector('.nav-link.active');
        if (activeLink && window.innerWidth > 768) {
            const rect = activeLink.getBoundingClientRect();
            const menuRect = navMenu.getBoundingClientRect();
            
            indicator.style.width = rect.width + 'px';
            indicator.style.left = (rect.left - menuRect.left) + 'px';
            indicator.style.opacity = '1';
        } else {
            indicator.style.opacity = '0';
        }
    }
    
    // Update indicator on page load and resize
    window.addEventListener('load', updateIndicator);
    window.addEventListener('resize', updateIndicator);
    
    // Update indicator when active link changes
    const observer = new MutationObserver(updateIndicator);
    document.querySelectorAll('.nav-link').forEach(link => {
        observer.observe(link, { attributes: true, attributeFilter: ['class'] });
    });
}

// Initialize navigation indicator
if (navMenu) {
    addNavigationIndicator();
}

// Preload pages for faster navigation
function preloadPages() {
    const pages = ['index.html', 'installation.html', 'documentation.html'];
    pages.forEach(page => {
        const link = document.createElement('link');
        link.rel = 'prefetch';
        link.href = page;
        document.head.appendChild(link);
    });
}

// Initialize preloading after page load
window.addEventListener('load', preloadPages);

// Copy code functionality
function copyCode() {
    const code = document.getElementById('install-code');
    if (code) {
        const text = code.textContent;
        navigator.clipboard.writeText(text).then(() => {
            const copyBtn = document.querySelector('.copy-btn');
            const originalText = copyBtn.textContent;
            copyBtn.textContent = 'Copied!';
            copyBtn.style.background = '#28a745';
            
            setTimeout(() => {
                copyBtn.textContent = originalText;
                copyBtn.style.background = '#667eea';
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
            
            const copyBtn = document.querySelector('.copy-btn');
            const originalText = copyBtn.textContent;
            copyBtn.textContent = 'Copied!';
            copyBtn.style.background = '#28a745';
            
            setTimeout(() => {
                copyBtn.textContent = originalText;
                copyBtn.style.background = '#667eea';
            }, 2000);
        });
    }
}

// Navbar background change on scroll - Enhanced for transparent theme
window.addEventListener('scroll', () => {
    const header = document.querySelector('.header');
    if (window.scrollY > 50) {
        header.classList.add('scrolled');
    } else {
        header.classList.remove('scrolled');
    }
});

// Intersection Observer for animations
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// Observe elements for animation
document.addEventListener('DOMContentLoaded', () => {
    const animateElements = document.querySelectorAll('.feature-card, .support-card, .installation-text, .code-block');
    
    animateElements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });
});

// Form validation (if forms are added later)
function validateForm(form) {
    const inputs = form.querySelectorAll('input[required], textarea[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.classList.add('error');
            isValid = false;
        } else {
            input.classList.remove('error');
        }
    });
    
    return isValid;
}

// Loading state management
function showLoading(element) {
    element.classList.add('loading');
    element.innerHTML = '<div class="spinner"></div> Loading...';
}

function hideLoading(element, originalContent) {
    element.classList.remove('loading');
    element.innerHTML = originalContent;
}

// Utility function for API calls (if needed)
async function fetchData(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Fetch error:', error);
        throw error;
    }
}

// Initialize theme from localStorage
document.addEventListener('DOMContentLoaded', () => {
    // Theme initialization removed - no longer needed
});

// Performance optimization: Lazy loading for images
function lazyLoadImages() {
    const images = document.querySelectorAll('img[data-src]');
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                imageObserver.unobserve(img);
            }
        });
    });
    
    images.forEach(img => imageObserver.observe(img));
}

// Initialize lazy loading when DOM is ready
document.addEventListener('DOMContentLoaded', lazyLoadImages);

// Error handling for missing elements
function safeQuerySelector(selector) {
    const element = document.querySelector(selector);
    if (!element) {
        console.warn(`Element not found: ${selector}`);
    }
    return element;
}

// Debounce function for performance optimization
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Optimized scroll handler - Enhanced for transparent theme
const handleScroll = debounce(() => {
    const header = document.querySelector('.header');
    if (header) {
        if (window.scrollY > 50) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
    }
}, 10);

window.addEventListener('scroll', handleScroll);

// Console welcome message
console.log('%c🤖 AUTO-blogger Documentation Site', 'color: #667eea; font-size: 20px; font-weight: bold;');
console.log('%cWelcome to the AUTO-blogger documentation! Visit https://github.com/AryanVBW/AUTO-blogger for the source code.', 'color: #666; font-size: 14px;');