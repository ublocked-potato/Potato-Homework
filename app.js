// app.js - OmniSearch Application Logic 🥔
let currentTabId = 'home';
let currentEngine = localStorage.getItem('searchEngine') || 'duckduckgo';
let proxyHomepage = localStorage.getItem('proxyHomepage') || 'blank';
let bypassMethod = localStorage.getItem('bypassMethod') || 'cors';
let tabs = {'home': {type: 'home', url: '', title: 'OmniSearch', history: [], historyIndex: -1}};

// CORS Proxy endpoints (multiple fallbacks)
const CORS_PROXIES = [
    'https://api.allorigins.win/raw?url=',
    'https://corsproxy.io/?',
    'https://api.codetabs.com/v1/proxy?quest='
];
let currentProxyIndex = 0;

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    selectEngine(currentEngine, false);
    loadSettings();
});

document.getElementById('addressBar').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') searchOrNavigate();
});

document.getElementById('mainSearch').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') performSearch();
});

// Settings Functions
function openSettings() {
    document.getElementById('settingsModal').classList.add('active');
}

function closeSettings() {
    document.getElementById('settingsModal').classList.remove('active');
}

function loadSettings() {
    // Load homepage setting
    document.querySelectorAll('[data-homepage]').forEach(opt => {
        opt.classList.toggle('active', opt.dataset.homepage === proxyHomepage);
    });
    
    // Load default engine
    document.querySelectorAll('[data-default-engine]').forEach(opt => {
        opt.classList.toggle('active', opt.dataset.defaultEngine === currentEngine);
    });
    
    // Load bypass method
    document.querySelectorAll('[data-method]').forEach(opt => {
        opt.classList.toggle('active', opt.dataset.method === bypassMethod);
    });
}

function setHomepage(homepage) {
    proxyHomepage = homepage;
    localStorage.setItem('proxyHomepage', homepage);
    document.querySelectorAll('[data-homepage]').forEach(opt => {
        opt.classList.toggle('active', opt.dataset.homepage === homepage);
    });
}

function setDefaultEngine(engine) {
    currentEngine = engine;
    localStorage.setItem('searchEngine', engine);
    selectEngine(engine);
    document.querySelectorAll('[data-default-engine]').forEach(opt => {
        opt.classList.toggle('active', opt.dataset.defaultEngine === engine);
    });
}

function setBypassMethod(method) {
    bypassMethod = method;
    localStorage.setItem('bypassMethod', method);
    document.querySelectorAll('[data-method]').forEach(opt => {
        opt.classList.toggle('active', opt.dataset.method === method);
    });
}

function selectEngine(engine, updateUI = true) {
    currentEngine = engine;
    localStorage.setItem('searchEngine', engine);

    if (updateUI) {
        document.querySelectorAll('.engine-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.engine === engine);
        });
    }
}

function addNewTab(url = null) {
    const tabId = 'tab_' + Date.now();
    const tabTitle = url ? new URL(url).hostname.replace('www.', '') : 'New Tab';

    tabs[tabId] = {type: url ? 'proxy' : 'home', url: url || '', title: tabTitle, history: url ? [url] : [], historyIndex: url ? 0 : -1};

    const newTab = document.createElement('div');
    newTab.className = 'tab';
    newTab.dataset.tabId = tabId;
    newTab.innerHTML = `<span style="font-size:20px;">${url ? '🌐' : '🥔'}</span><span class="tab-title">${tabTitle}</span><span class="tab-close" onclick="closeTab(event, '${tabId}')">×</span>`;
    newTab.onclick = function(e) {if (e.target.classList.contains('tab-close')) return; switchTab(tabId);};

    document.getElementById('tabsContainer').appendChild(newTab);

    const contentView = document.createElement('div');
    contentView.className = 'content-view';
    contentView.id = 'view-' + tabId;
    document.getElementById('browserContent').appendChild(contentView);

    switchTab(tabId);
    if (url) loadProxyContent(tabId, url); else showHomeContent(tabId);
}

function switchTab(tabId) {
    document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
    document.querySelector(`[data-tab-id="${tabId}"]`).classList.add('active');
    document.querySelectorAll('.content-view').forEach(view => view.classList.remove('active'));
    document.getElementById('view-' + tabId).classList.add('active');
    currentTabId = tabId;
    updateAddressBar();
}

function closeTab(event, tabId) {
    event.stopPropagation();
    if (Object.keys(tabs).length <= 1) {alert('Cannot close the last tab!'); return;}
    delete tabs[tabId];
    document.querySelector(`[data-tab-id="${tabId}"]`).remove();
    document.getElementById('view-' + tabId).remove();
    if (currentTabId === tabId) switchTab(Object.keys(tabs)[0]);
}

function updateAddressBar() {
    document.getElementById('addressBar').value = tabs[currentTabId].url || '';
}

function showHomeContent(tabId) {
    const view = document.getElementById('view-' + tabId);
    view.innerHTML = document.getElementById('view-home').innerHTML;
}

function performSearch() {
    const query = document.getElementById('mainSearch').value.trim();
    if (!query) return;
    performSearchInTab(currentTabId, query);
}

async function performSearchInTab(tabId, query) {
    if (!query) return;
    const view = document.getElementById('view-' + tabId);
    view.innerHTML = `<div class="loading-overlay"><div class="loading-spinner"></div><div class="loading-text">🥔 Searching ${currentEngine}...</div></div>`;

    try {
        let searchUrl = '';
        
        // Build search URL based on engine
        switch(currentEngine) {
            case 'duckduckgo':
                searchUrl = `https://html.duckduckgo.com/html/?q=${encodeURIComponent(query)}`;
                break;
            case 'google':
                searchUrl = `https://www.google.com/search?q=${encodeURIComponent(query)}&num=20`;
                break;
            case 'brave':
                searchUrl = `https://search.brave.com/search?q=${encodeURIComponent(query)}`;
                break;
            case 'startpage':
                searchUrl = `https://www.startpage.com/sp/search?query=${encodeURIComponent(query)}`;
                break;
        }

        // Fetch via CORS proxy
        const proxyUrl = CORS_PROXIES[currentProxyIndex] + encodeURIComponent(searchUrl);
        const response = await fetch(proxyUrl);
        
        if (!response.ok) {
            // Try next proxy
            currentProxyIndex = (currentProxyIndex + 1) % CORS_PROXIES.length;
            throw new Error('Proxy failed, trying next...');
        }
        
        const html = await response.text();
        const results = parseSearchResults(html, currentEngine);

        if (results.length === 0) {
            view.innerHTML = `<div style="padding:100px 20px;text-align:center;font-size:20px;">
                <div style="font-size:72px;margin-bottom:20px;">🥔</div>
                <h2>No Results Found</h2>
                <p style="opacity:0.8;margin:20px 0;">Try a different search engine or query.</p>
                <button class="back-btn" onclick="showHomeContent('${tabId}')">← New Search</button>
            </div>`;
            return;
        }

        const resultsHtml = results.map(r => {
            const safeUrl = escapeHtml(r.url);
            const safeTitle = escapeHtml(r.title);
            const safeDisplayUrl = escapeHtml(r.display_url);
            const safeSnippet = escapeHtml(r.snippet);

            return `<div class="result-item" onclick="openProxyInTab('${tabId}', '${safeUrl.replace(/'/g, "\\'")}')">
                <div class="result-title">${safeTitle}</div>
                <div class="result-url">${safeDisplayUrl}</div>
                <div class="result-snippet">${safeSnippet}</div>
            </div>`;
        }).join('');

        view.innerHTML = `<div class="search-results-container">
            <div class="results-header">
                <button class="back-btn" onclick="showHomeContent('${tabId}')">← New Search</button>
                <span style="color:rgba(255,255,255,0.8);margin-left:20px;">${results.length} results • ${currentEngine}</span>
            </div>
            ${resultsHtml}
        </div>`;

        tabs[tabId].type = 'search';
        tabs[tabId].url = `search: ${query}`;
        updateTabTitle(tabId, `Search: ${query.substring(0, 15)}`);

    } catch(e) {
        console.error('Search error:', e);
        view.innerHTML = `<div style="padding:100px 20px;text-align:center;font-size:20px;">
            <div style="font-size:72px;margin-bottom:20px;">🥔</div>
            <h2>Search Error</h2>
            <p style="opacity:0.8;margin:20px 0;">Network issue or engine blocked. Try another engine.</p>
            <button class="back-btn" onclick="showHomeContent('${tabId}')">← Try Again</button>
        </div>`;
    }
}

function parseSearchResults(html, engine) {
    const parser = new DOMParser();
    const doc = parser.parseFromString(html, 'text/html');
    const results = [];

    try {
        if (engine === 'duckduckgo') {
            const items = doc.querySelectorAll('.result__body');
            items.forEach(item => {
                const link = item.querySelector('.result__a');
                if (!link) return;
                
                let url = link.href;
                // Clean DDG redirects
                const match = url.match(/uddg=([^&]+)/);
                if (match) url = decodeURIComponent(match[1]);
                
                const title = link.textContent.trim();
                const urlSpan = item.querySelector('.result__url');
                const snippet = item.querySelector('.result__snippet');
                
                if (title && url) {
                    results.push({
                        title: title,
                        url: url,
                        display_url: urlSpan ? urlSpan.textContent.trim() : new URL(url).hostname,
                        snippet: snippet ? snippet.textContent.trim() : ''
                    });
                }
            });
        } else if (engine === 'google') {
            const items = doc.querySelectorAll('.g, div[data-sokoban-container]');
            items.forEach(item => {
                const link = item.querySelector('a');
                const heading = item.querySelector('h3');
                if (!link || !heading) return;
                
                let url = link.href;
                const match = url.match(/[?&]q=([^&]+)/);
                if (match) url = decodeURIComponent(match[1]);
                
                if (url.includes('google.com/search')) return;
                
                const snippet = item.querySelector('.VwiC3b, .IsZvec');
                
                results.push({
                    title: heading.textContent.trim(),
                    url: url,
                    display_url: new URL(url).hostname.replace('www.', ''),
                    snippet: snippet ? snippet.textContent.trim() : ''
                });
            });
        } else if (engine === 'brave') {
            const items = doc.querySelectorAll('.snippet');
            items.forEach(item => {
                const link = item.querySelector('a.result-header, .title a');
                if (!link) return;
                
                const snippet = item.querySelector('.snippet-description');
                
                results.push({
                    title: link.textContent.trim(),
                    url: link.href,
                    display_url: new URL(link.href).hostname.replace('www.', ''),
                    snippet: snippet ? snippet.textContent.trim() : ''
                });
            });
        } else if (engine === 'startpage') {
            const items = doc.querySelectorAll('.w-gl__result');
            items.forEach(item => {
                const link = item.querySelector('.w-gl__result-url');
                const title = item.querySelector('h3');
                if (!link || !title) return;
                
                const snippet = item.querySelector('.w-gl__description');
                
                results.push({
                    title: title.textContent.trim(),
                    url: link.href,
                    display_url: new URL(link.href).hostname.replace('www.', ''),
                    snippet: snippet ? snippet.textContent.trim() : ''
                });
            });
        }
    } catch(e) {
        console.error('Parse error:', e);
    }

    return results.slice(0, 20);
}

function searchOrNavigate() {
    const input = document.getElementById('addressBar').value.trim();
    if (!input) return;
    if (input.match(/^https?:\/\//i) || input.match(/^[^\s]+\.[^\s]+$/)) {
        openProxyInTab(currentTabId, input.startsWith('http') ? input : 'https://' + input);
    } else {
        performSearchInTab(currentTabId, input);
    }
}

function openProxyInTab(tabId, url) {
    tabs[tabId].type = 'proxy';
    tabs[tabId].url = url;
    if (tabs[tabId].history.length === 0 || tabs[tabId].history[tabs[tabId].historyIndex] !== url) {
        tabs[tabId].history = tabs[tabId].history.slice(0, tabs[tabId].historyIndex + 1);
        tabs[tabId].history.push(url);
        tabs[tabId].historyIndex = tabs[tabId].history.length - 1;
    }
    updateTabTitle(tabId, new URL(url).hostname.replace('www.', ''));
    updateAddressBar();
    loadProxyContent(tabId, url);
}

function loadProxyContent(tabId, url) {
    const view = document.getElementById('view-' + tabId);
    
    if (bypassMethod === 'iframe') {
        // Direct iframe (may be blocked)
        view.innerHTML = `
            <div class="loading-overlay">
                <div class="loading-spinner"></div>
                <div class="loading-text">Loading ${new URL(url).hostname}...</div>
            </div>
            <iframe class="proxy-frame" src="${url}" onload="this.previousElementSibling.remove()"></iframe>
        `;
    } else {
        // CORS proxy method
        let homepageUrl = '';
        switch(proxyHomepage) {
            case 'google':
                homepageUrl = 'https://www.google.com';
                break;
            case 'classroom':
                homepageUrl = 'https://classroom.google.com';
                break;
            default:
                homepageUrl = url;
        }
        
        const proxyUrl = CORS_PROXIES[currentProxyIndex] + encodeURIComponent(homepageUrl);
        
        view.innerHTML = `
            <div class="loading-overlay">
                <div class="loading-spinner"></div>
                <div class="loading-text">Loading via proxy...</div>
            </div>
            <iframe class="proxy-frame" src="${proxyUrl}" onload="this.previousElementSibling.remove()" onerror="handleProxyError('${tabId}')"></iframe>
        `;
    }
}

function handleProxyError(tabId) {
    // Try next proxy
    currentProxyIndex = (currentProxyIndex + 1) % CORS_PROXIES.length;
    const view = document.getElementById('view-' + tabId);
    view.innerHTML = `<div style="padding:100px 20px;text-align:center;font-size:20px;">
        <div style="font-size:72px;margin-bottom:20px;">🥔</div>
        <h2>Cannot Load Site</h2>
        <p style="opacity:0.8;margin:20px 0;">This site may be blocking proxies. Try direct iframe mode in settings.</p>
        <button class="back-btn" onclick="showHomeContent('${tabId}')">← Go Back</button>
    </div>`;
}

function updateTabTitle(tabId, title) {
    tabs[tabId].title = title;
    const tabElement = document.querySelector(`[data-tab-id="${tabId}"] .tab-title`);
    if (tabElement) tabElement.textContent = title.length > 20 ? title.substring(0, 20) + '...' : title;
}

function navigateBack() {
    const tab = tabs[currentTabId];
    if (tab.historyIndex > 0) {
        tab.historyIndex--;
        tab.url = tab.history[tab.historyIndex];
        updateAddressBar();
        loadProxyContent(currentTabId, tab.url);
    }
}

function navigateForward() {
    const tab = tabs[currentTabId];
    if (tab.historyIndex < tab.history.length - 1) {
        tab.historyIndex++;
        tab.url = tab.history[tab.historyIndex];
        updateAddressBar();
        loadProxyContent(currentTabId, tab.url);
    }
}

function reloadCurrentTab() {
    const tab = tabs[currentTabId];
    if (tab.type === 'proxy' && tab.url) loadProxyContent(currentTabId, tab.url);
    else if (tab.type === 'search') location.reload();
    else showHomeContent(currentTabId);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}