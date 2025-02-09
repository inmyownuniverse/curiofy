// Cache for translated content
const translationCache = {};

// Loading state tracker
let isTranslating = false;

// Show loading state
function showLoading() {
    const loadingOverlay = document.createElement('div');
    loadingOverlay.id = 'translationLoading';
    loadingOverlay.innerHTML = `
        <div class="loading-spinner"></div>
        <p>Translating...</p>
    `;
    document.body.appendChild(loadingOverlay);
}

// Hide loading state
function hideLoading() {
    const loadingOverlay = document.getElementById('translationLoading');
    if (loadingOverlay) {
        loadingOverlay.remove();
    }
}

async function translateWithGemini(text, targetLang) {
    // Check cache first
    const cacheKey = `${text}_${targetLang}`;
    if (translationCache[cacheKey]) {
        return translationCache[cacheKey];
    }

    try {
        const response = await fetch('/api/translate/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                text: text,
                target_language: targetLang
            })
        });

        if (!response.ok) {
            throw new Error('Translation failed');
        }

        const data = await response.json();
        // Cache the result
        translationCache[cacheKey] = data.translated_text;
        return data.translated_text;
    } catch (error) {
        console.error('Translation error:', error);
        return text;
    }
}

async function setLanguage(lang) {
    if (isTranslating) return; // Prevent multiple translations at once
    isTranslating = true;

    // Update active button state
    document.querySelectorAll('.lang-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.id === lang) {
            btn.classList.add('active');
        }
    });

    try {
        showLoading();
        
        // Get all translatable elements
        const elements = document.querySelectorAll('[data-translate="true"]');
        
        // Translate elements in batches of 5 to prevent overloading
        const batchSize = 5;
        for (let i = 0; i < elements.length; i += batchSize) {
            const batch = Array.from(elements).slice(i, i + batchSize);
            await Promise.all(batch.map(async (element) => {
                const originalText = element.getAttribute('data-original') || element.textContent;
                if (!element.getAttribute('data-original')) {
                    element.setAttribute('data-original', originalText);
                }
                
                if (lang === 'en') {
                    element.textContent = originalText;
                } else {
                    const translatedText = await translateWithGemini(originalText, lang);
                    element.textContent = translatedText;
                }
            }));
        }

        // Save language preference
        localStorage.setItem('preferredLanguage', lang);
        document.documentElement.lang = lang;

    } catch (error) {
        console.error('Translation error:', error);
        alert('Translation failed. Please try again.');
    } finally {
        hideLoading();
        isTranslating = false;
    }
}

// Get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Add loading spinner styles
const style = document.createElement('style');
style.textContent = `
    #translationLoading {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.7);
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        z-index: 9999;
        color: white;
    }

    .loading-spinner {
        width: 50px;
        height: 50px;
        border: 5px solid #FFB84C;
        border-top: 5px solid transparent;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin-bottom: 1rem;
    }

    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    .lang-btn.active {
        background-color: #FFB84C;
        color: black;
    }
`;
document.head.appendChild(style);

// Initialize language switcher
document.addEventListener('DOMContentLoaded', () => {
    const savedLang = localStorage.getItem('preferredLanguage') || 'en';
    
    // Set initial active state
    document.querySelectorAll('.lang-btn').forEach(btn => {
        if (btn.id === savedLang) {
            btn.classList.add('active');
        }
        btn.addEventListener('click', () => setLanguage(btn.id));
    });

    // Apply saved language
    if (savedLang !== 'en') {
        setLanguage(savedLang);
    }
});