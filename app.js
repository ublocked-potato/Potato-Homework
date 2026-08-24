/**
 * OmniSearch - Frontend Application
 * Uses the app's same-origin Python API for production requests.
 */

// ============================================================================
// STATE MANAGEMENT
// ============================================================================

const state = {
  currentEngine: localStorage.getItem('searchEngine') || 'duckduckgo',
  proxyHomepage: localStorage.getItem('proxyHomepage') || 'classroom',
  stealthMode: localStorage.getItem('stealthMode') === 'true',
  autoMirror: localStorage.getItem('autoMirror') !== 'false', // default true
  backend: 'server',
  searchCount: parseInt(localStorage.getItem('searchCount')) || 0,
  burnedCount: 0,
  history: [],
  historyIndex: -1,
};

const CORS_PROXIES = [
  'https://corsproxy.io/?url=',
];

let currentProxyIndex = 0;

// ============================================================================
// INITIALIZATION
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
  initializeUI();
  detectBackend();
  setupEventListeners();
  applyDisguise(state.proxyHomepage);
  updateStatistics();
});

function initializeUI() {
  // Set active engine button
  document.querySelectorAll('.engine-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.engine === state.currentEngine);
  });

  // Set active homepage option
  document.querySelectorAll('[data-homepage]').forEach(opt => {
    opt.classList.toggle('active', opt.dataset.homepage === state.proxyHomepage);
  });

  // Set toggle switches
  document.querySelector('[data-setting="stealth"]')?.classList.toggle('active', state.stealthMode);
  document.querySelector('[data-setting="autoMirror"]')?.classList.toggle('active', state.autoMirror);
}

// ============================================================================
// BACKEND DISPLAY
// ============================================================================

async function detectBackend() {
  const modeText = document.getElementById('modeText');
  const modeBadge = document.getElementById('modeBadge');
  const activeBackendSpan = document.getElementById('activeBackend');

  state.backend = 'server';

  const text = 'Server Search Mode • Same-Origin 🔒';
  const badge = '🔒 Server';

  if (modeText) modeText.textContent = text;
  if (modeBadge) {
    modeBadge.textContent = badge;
    modeBadge.style.display = 'block';
  }
  if (activeBackendSpan) activeBackendSpan.textContent = badge;
}

// ============================================================================
// EVENT LISTENERS
// ============================================================================

function setupEventListeners() {
  // Search functionality
  document.getElementById('mainSearch')?.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') performSearch();
  });
  
  document.querySelector('.search-icon')?.addEventListener('click', performSearch);

  // Address bar
  document.getElementById('addressBar')?.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') searchOrNavigate();
  });

  // Engine selection
  document.querySelectorAll('.engine-btn').forEach(btn => {
    btn.addEventListener('click', () => selectEngine(btn.dataset.engine));
  });

  // Settings
  document.getElementById('settingsBtn')?.addEventListener('click', openSettings);
  document.getElementById('closeSettings')?.addEventListener('click', closeSettings);

  // Homepage selection
  document.querySelectorAll('[data-homepage]').forEach(opt => {
    opt.addEventListener('click', () => setHomepage(opt.dataset.homepage));
  });

  // Toggle switches
  document.querySelectorAll('.switch').forEach(toggle => {
    toggle.addEventListener('click', () => toggleSetting(toggle.dataset.setting));
  });

  // Navigation buttons
  document.getElementById('backBtn')?.addEventListener('click', navigateBack);
  document.getElementById('forwardBtn')?.addEventListener('click', navigateForward);
  document.getElementById('refreshBtn')?.addEventListener('click', refreshPage);
  document.querySelector('.add-tab-btn')?.addEventListener('click', addNewTab);
  document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', () => activateTab(tab.dataset.tabId));
  });

  // Keyboard shortcuts
  setupKeyboardShortcuts();
}

function setupKeyboardShortcuts() {
  document.addEventListener('keydown', (e) => {
    // CTRL+G: Instant Google Classroom disguise
    if (e.ctrlKey && e.key.toLowerCase() === 'g') {
      e.preventDefault();
      applyDisguise('classroom');
      showNotification('✓ CTRL+G: Google Classroom disguise activated');
    }

    // CTRL+SHIFT+S: Toggle stealth mode
    if (e.ctrlKey && e.shiftKey && e.key.toLowerCase() === 's') {
      e.preventDefault();
      toggleSetting('stealth');
      showNotification(state.stealthMode ? '🥷 Stealth Mode ENABLED' : '👁️ Stealth Mode DISABLED');
    }

    // CTRL+SHIFT+R: Report current domain as blocked
    if (e.ctrlKey && e.shiftKey && e.key.toLowerCase() === 'r') {
      e.preventDefault();
      reportCurrentDomain();
    }

    // CTRL+SHIFT+H: Toggle shortcuts help
    if (e.ctrlKey && e.shiftKey && e.key.toLowerCase() === 'h') {
      e.preventDefault();
      const help = document.getElementById('shortcutsHelp');
      if (help) {
        help.style.display = help.style.display === 'none' ? 'block' : 'none';
      }
    }

    // ESC: Close settings
    if (e.key === 'Escape') {
      const modal = document.getElementById('settingsModal');
      if (modal?.classList.contains('active')) {
        closeSettings();
      }
    }
  });
}

// ============================================================================
// SETTINGS MANAGEMENT
// ============================================================================

function selectEngine(engine) {
  state.currentEngine = engine;
  localStorage.setItem('searchEngine', engine);
  
  document.querySelectorAll('.engine-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.engine === engine);
  });
}

function setHomepage(homepage) {
  state.proxyHomepage = homepage;
  localStorage.setItem('proxyHomepage', homepage);
  
  document.querySelectorAll('[data-homepage]').forEach(opt => {
    opt.classList.toggle('active', opt.dataset.homepage === homepage);
  });
  
  applyDisguise(homepage);
  showNotification(`✓ Homepage changed to: ${
    homepage === 'blank' ? 'Blank Page' :
    homepage === 'google' ? 'Google' : 'Google Classroom'
  }`);
}

function toggleSetting(setting) {
  const toggle = document.querySelector(`[data-setting="${setting}"]`);
  if (!toggle) return;

  if (setting === 'stealth') {
    state.stealthMode = !state.stealthMode;
    localStorage.setItem('stealthMode', state.stealthMode);
    toggle.classList.toggle('active', state.stealthMode);
  } else if (setting === 'autoMirror') {
    state.autoMirror = !state.autoMirror;
    localStorage.setItem('autoMirror', state.autoMirror);
    toggle.classList.toggle('active', state.autoMirror);
  }
}

function openSettings() {
  document.getElementById('settingsModal')?.classList.add('active');
  updateStatistics();
}

function closeSettings() {
  document.getElementById('settingsModal')?.classList.remove('active');
}

function updateStatistics() {
  const searchCountEl = document.getElementById('searchCount');
  const burnedCountEl = document.getElementById('burnedCount');
  
  if (searchCountEl) searchCountEl.textContent = state.searchCount;
  if (burnedCountEl) burnedCountEl.textContent = state.burnedCount;
}

// ============================================================================
// DISGUISE SYSTEM
// ============================================================================

function applyDisguise(type) {
  const pageTitle = document.getElementById('pageTitle');
  const favicon = document.getElementById('favicon');
  const addressBar = document.getElementById('addressBar');
  const newTabPage = document.querySelector('.new-tab-page');
  const googleFrame = document.getElementById('googleFrame');
  const classroomFrame = document.getElementById('classroomFrame');

  // Hide all disguise frames
  googleFrame?.classList.remove('active');
  classroomFrame?.classList.remove('active');

  switch (type) {
    case 'blank':
      if (pageTitle) pageTitle.textContent = '';
      if (favicon) favicon.href =
        'data:image/x-icon;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==';
      if (addressBar) addressBar.value = 'about:blank';
      if (newTabPage) newTabPage.style.display = 'flex';
      if (window.history?.pushState) {
        window.history.pushState(null, '', '/about:blank');
      }
      break;

    case 'google':
      if (pageTitle) pageTitle.textContent = 'Google';
      if (favicon) favicon.href = 'https://www.google.com/favicon.ico';
      if (addressBar) addressBar.value = 'https://www.google.com';
      if (newTabPage) newTabPage.style.display = 'none';
      googleFrame?.classList.add('active');
      if (window.history?.pushState) {
        window.history.pushState(null, 'Google', '/google');
      }
      break;

    case 'classroom':
    default:
      if (pageTitle) pageTitle.textContent = 'Google Classroom';
      if (favicon) favicon.href = 'https://ssl.gstatic.com/classroom/favicon.png';
      if (addressBar) addressBar.value = 'https://classroom.google.com';
      if (newTabPage) newTabPage.style.display = 'none';
      classroomFrame?.classList.add('active');
      if (window.history?.pushState) {
        window.history.pushState(null, 'Google Classroom', '/classroom');
      }
      break;
  }
}

function showSearchInterface() {
  const newTabPage = document.querySelector('.new-tab-page');
  if (newTabPage) newTabPage.style.display = 'flex';
  document.getElementById('googleFrame')?.classList.remove('active');
  document.getElementById('classroomFrame')?.classList.remove('active');
}

function addNewTab() {
  const tabsContainer = document.getElementById('tabsContainer');
  if (!tabsContainer) return;

  const tabId = `tab-${Date.now()}`;
  const tab = document.createElement('div');
  tab.className = 'tab';
  tab.dataset.tabId = tabId;
  tab.innerHTML = '<span style="font-size:20px;">🥔</span><span class="tab-title">New Tab</span>';
  tab.addEventListener('click', () => activateTab(tabId));
  tabsContainer.querySelectorAll('.tab').forEach(item => item.classList.remove('active'));
  tab.classList.add('active');
  tabsContainer.appendChild(tab);

  const addressBar = document.getElementById('addressBar');
  if (addressBar) addressBar.value = '';
  const mainSearch = document.getElementById('mainSearch');
  if (mainSearch) mainSearch.value = '';
  showSearchInterface();
  applyDisguise('blank');
}

function activateTab(tabId) {
  document.querySelectorAll('.tab').forEach(tab => {
    tab.classList.toggle('active', tab.dataset.tabId === tabId);
  });
  showSearchInterface();
}

// ============================================================================
// SEARCH FUNCTIONALITY
// ============================================================================

async function performSearch() {
  const query = document.getElementById('mainSearch')?.value.trim();
  if (!query) return;

  showSearchInterface();
  const view = document.getElementById('view-home');
  if (!view) return;

  // Increment search count
  state.searchCount++;
  localStorage.setItem('searchCount', state.searchCount);

  // Show loading
  view.innerHTML = `
    <div class="loading-overlay">
      <div class="loading-spinner"></div>
      <div style="margin-top:20px;">
        🔒 Searching securely...
      </div>
    </div>
  `;

  try {
    const results = await serverSearch(query);
    if (!results || results.length === 0) {
      showNoResults(view);
      return;
    }

    displayResults(results, query);
    addToHistory({ type: 'search', query, results: results.length });

  } catch (error) {
    console.error('Search error:', error);
    showError(view, error.message);
  }
}

async function serverSearch(query) {
  const response = await fetch(`/api/search?q=${encodeURIComponent(query)}&engine=${encodeURIComponent(state.currentEngine)}`);
  if (!response.ok) throw new Error(`Search service returned ${response.status}`);

  const payload = await response.json();
  if (!payload.success && (!payload.results || payload.results.length === 0)) {
    throw new Error(payload.error || 'Search service returned no results');
  }
  return payload.results || [];
}

function parseSearchResults(html, engine) {
  const parser = new DOMParser();
  const doc = parser.parseFromString(html, 'text/html');
  const results = [];

  if (engine === 'duckduckgo') {
    doc.querySelectorAll('.result__body').forEach(item => {
      const link = item.querySelector('.result__a');
      if (!link) return;

      let url = link.href;
      const match = url.match(/uddg=([^&]+)/);
      if (match) url = decodeURIComponent(match[1]);

      const title = link.textContent.trim();
      const snippet = item.querySelector('.result__snippet')?.textContent.trim() || '';
      const display_url = extractDomain(url);

      if (url && title) {
        results.push({ title, url, display_url, snippet, relevance_score: 0, is_instant: false });
      }
    });
  } else if (engine === 'google') {
    doc.querySelectorAll('.g, div[data-sokoban-container]').forEach(item => {
      const link = item.querySelector('a');
      const h3 = item.querySelector('h3');
      
      if (!link || !h3 || link.href.includes('google.com/search')) return;

      const url = link.href;
      const title = h3.textContent.trim();
      const snippet = item.querySelector('.VwiC3b, .s, .st')?.textContent.trim() || '';
      const display_url = extractDomain(url);

      if (url && title) {
        results.push({ title, url, display_url, snippet, relevance_score: 0, is_instant: false });
      }
    });
  }

  return results.slice(0, 20);
}

function extractDomain(url) {
  try {
    return new URL(url).hostname.replace('www.', '');
  } catch {
    return url;
  }
}

function displayResults(results, query) {
  const view = document.getElementById('view-home');
  if (!view) return;

  let instantAnswerHtml = '';
  let regularResults = results;

  // Check for instant answer
  const instantAnswer = results.find(r => r.is_instant);
  if (instantAnswer) {
    regularResults = results.filter(r => !r.is_instant);
    instantAnswerHtml = `
      <div style="background:linear-gradient(135deg,#8a2be2,#9300ea);border-radius:25px;padding:30px;margin-bottom:30px;border:2px solid rgba(255,255,255,0.3);box-shadow:0 10px 40px rgba(138,43,226,0.4);">
        <div style="display:flex;align-items:center;gap:15px;margin-bottom:15px;">
          <div style="font-size:42px;">🤖</div>
          <div>
            <div style="font-size:20px;font-weight:700;">${escapeHtml(instantAnswer.title)}</div>
            <div style="font-size:13px;opacity:0.9;">${escapeHtml(instantAnswer.display_url)}</div>
          </div>
        </div>
        <div style="font-size:16px;line-height:1.8;background:rgba(255,255,255,0.15);padding:20px;border-radius:15px;">
          ${escapeHtml(instantAnswer.snippet)}
        </div>
      </div>
    `;
  }

  const resultsHtml = regularResults.map(r => `
    <div class="result-item" onclick="handleResultClick('${escapeAttr(r.url)}')">
      <div class="result-title">${escapeHtml(r.title)}</div>
      <div class="result-url">${escapeHtml(r.display_url)}</div>
      <div class="result-snippet">${escapeHtml(r.snippet)}</div>
      ${r.relevance_score ? `<span class="result-score">Relevance: ${r.relevance_score}</span>` : ''}
    </div>
  `).join('');

  view.innerHTML = `
    <div class="search-results-container">
      <div class="results-header">
        <button class="back-btn" onclick="location.reload()">← New Search</button>
        <span style="color:rgba(255,255,255,0.8);">
          ${regularResults.length} results • ${state.currentEngine}
        </span>
      </div>
      ${instantAnswerHtml}
      ${resultsHtml}
    </div>
  `;
}

function showNoResults(view) {
  view.innerHTML = `
    <div style="padding:100px 20px;text-align:center;">
      <div style="font-size:72px;margin-bottom:20px;">🥔</div>
      <h2 style="margin-bottom:15px;">No Results Found</h2>
      <p style="opacity:0.8;margin-bottom:30px;">Try different keywords or search engine</p>
      <button class="back-btn" onclick="location.reload()">← Try Again</button>
    </div>
  `;
}

function showError(view, message) {
  view.innerHTML = `
    <div style="padding:100px 20px;text-align:center;">
      <div style="font-size:72px;margin-bottom:20px;">⚠️</div>
      <h2 style="margin-bottom:15px;">Search Error</h2>
      <p style="opacity:0.8;margin-bottom:15px;">${escapeHtml(message)}</p>
      <button class="back-btn" onclick="location.reload()">← Back</button>
    </div>
  `;
}

// ============================================================================
// PROXY & NAVIGATION
// ============================================================================

function searchOrNavigate() {
  const input = document.getElementById('addressBar')?.value.trim();
  if (!input) return;

  showSearchInterface();

  // Check if it's a URL
  if (input.match(/^https?:\/\//i) || input.match(/^[^\s]+\.[^\s]+$/)) {
    const url = input.startsWith('http') ? input : 'https://' + input;
    openProxy(url);
  } else {
    // It's a search query
    const mainSearch = document.getElementById('mainSearch');
    if (mainSearch) {
      mainSearch.value = input;
      performSearch();
    }
  }
}

function handleResultClick(url) {
  openProxy(url);
}

async function openProxy(url) {
  const view = document.getElementById('view-home');
  if (!view) return;

  view.innerHTML = `
    <div class="loading-overlay">
      <div class="loading-spinner"></div>
      <div style="margin-top:20px;">Loading site...</div>
    </div>
    <iframe class="proxy-frame" data-url="${escapeAttr(url)}" src="${getProxyUrl(url)}"
      onload="removeProxyLoader(this)"
      onerror="retryProxyFrame(this)"></iframe>
  `;

  addToHistory({ type: 'proxy', url });
}

function getProxyUrl(url) {
  const encodedUrl = btoa(unescape(encodeURIComponent(url)));
  return `/api/proxy?url=${encodeURIComponent(encodedUrl)}`;
}

function removeProxyLoader(frame) {
  frame?.previousElementSibling?.remove();
}

function retryProxyFrame(frame) {
  if (!frame || frame.dataset.retried === 'true') {
    removeProxyLoader(frame);
    return;
  }
  frame.dataset.retried = 'true';
  frame.src = getProxyUrl(frame.dataset.url || frame.src);
}

// (If you want to keep the ChatGPT/complex-site warnings, you can reinsert those helpers here)

// ============================================================================
// HISTORY & NAVIGATION
// ============================================================================

function addToHistory(entry) {
  if (state.historyIndex < state.history.length - 1) {
    state.history = state.history.slice(0, state.historyIndex + 1);
  }

  state.history.push(entry);
  state.historyIndex = state.history.length - 1;

  updateNavigationButtons();
}

function navigateBack() {
  if (state.historyIndex > 0) {
    state.historyIndex--;
    const entry = state.history[state.historyIndex];
    
    if (entry.type === 'search') {
      const mainSearch = document.getElementById('mainSearch');
      if (mainSearch) {
        mainSearch.value = entry.query;
        performSearch();
      }
    } else if (entry.type === 'proxy') {
      openProxy(entry.url);
    }

    updateNavigationButtons();
  }
}

function navigateForward() {
  if (state.historyIndex < state.history.length - 1) {
    state.historyIndex++;
    const entry = state.history[state.historyIndex];
    
    if (entry.type === 'search') {
      const mainSearch = document.getElementById('mainSearch');
      if (mainSearch) {
        mainSearch.value = entry.query;
        performSearch();
      }
    } else if (entry.type === 'proxy') {
      openProxy(entry.url);
    }

    updateNavigationButtons();
  }
}

function refreshPage() {
  location.reload();
}

function updateNavigationButtons() {
  const backBtn = document.getElementById('backBtn');
  const forwardBtn = document.getElementById('forwardBtn');

  if (backBtn) backBtn.disabled = state.historyIndex <= 0;
  if (forwardBtn) forwardBtn.disabled = state.historyIndex >= state.history.length - 1;
}

// ============================================================================
// UTILITIES
// ============================================================================

function showNotification(message) {
  const existing = document.querySelector('.notification');
  if (existing) existing.remove();

  const note = document.createElement('div');
  note.className = 'notification';
  note.textContent = message;
  document.body.appendChild(note);

  setTimeout(() => note.remove(), 3000);
}

function escapeHtml(str = '') {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function escapeAttr(str = '') {
  return escapeHtml(str).replace(/"/g, '&quot;');
}

// Stub for reportCurrentDomain (kept so shortcut doesn’t break)
function reportCurrentDomain() {
  showNotification('Reported current domain as blocked (stub).');
}
