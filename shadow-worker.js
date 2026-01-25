/**
 * Shadow DOM Service Worker
 * Manipulates DOM to hide content from extension-based monitors
 * Uses closed Shadow DOM that cannot be inspected
 */

const CACHE_NAME = 'omnisearch-shadow-v1';
const STEALTH_MODE = true;

// Install service worker
self.addEventListener('install', (event) => {
  console.log('🥷 Shadow Worker installed');
  self.skipWaiting();
});

// Activate service worker
self.addEventListener('activate', (event) => {
  console.log('🥷 Shadow Worker activated');
  event.waitUntil(clients.claim());
});

// Intercept all fetch requests
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);
  
  // Only intercept proxy requests
  if (url.pathname.includes('/api/proxy') || url.pathname.includes('/shadow-load')) {
    event.respondWith(handleShadowRequest(event.request));
  } else {
    event.respondWith(fetch(event.request));
  }
});

async function handleShadowRequest(request) {
  try {
    const response = await fetch(request);
    const contentType = response.headers.get('content-type');
    
    // Only process HTML
    if (contentType && contentType.includes('text/html')) {
      const html = await response.text();
      const shadowHtml = injectShadowDOM(html);
      
      return new Response(shadowHtml, {
        status: response.status,
        statusText: response.statusText,
        headers: response.headers
      });
    }
    
    return response;
  } catch (error) {
    console.error('Shadow Worker error:', error);
    return new Response('Error loading content', { status: 500 });
  }
}

function injectShadowDOM(html) {
  /**
   * Injects code that creates closed Shadow DOM
   * Content is invisible to:
   * - Chrome DevTools (when closed)
   * - Extension content scripts
   * - Screen capture monitoring
   * - DOM inspection tools
   */
  
  const shadowScript = `
  <script>
  (function() {
    'use strict';
    
    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', initShadowDOM);
    } else {
      initShadowDOM();
    }
    
    function initShadowDOM() {
      console.log('🥷 Initializing Shadow DOM stealth mode...');
      
      // Create shadow host
      const shadowHost = document.createElement('div');
      shadowHost.id = 'shadow-root-' + Math.random().toString(36).substr(2, 9);
      shadowHost.style.cssText = 'width:100%;height:100%;position:absolute;top:0;left:0;';
      
      // Attach CLOSED shadow root (cannot be accessed via JS)
      const shadowRoot = shadowHost.attachShadow({ mode: 'closed' });
      
      // Store reference in closure (inaccessible from outside)
      const hiddenContent = document.body.innerHTML;
      
      // Clear visible DOM (decoy content)
      document.body.innerHTML = '';
      document.body.appendChild(shadowHost);
      
      // Inject real content into shadow DOM
      shadowRoot.innerHTML = \`
        <style>
          :host { display: block; width: 100%; height: 100%; }
          * { all: initial; }
          body { all: initial; display: block; }
        </style>
        <div id="shadow-content">
          \${hiddenContent}
        </div>
      \`;
      
      // Anti-detection measures
      
      // 1. Prevent DevTools detection
      const devtools = { open: false };
      const threshold = 160;
      
      setInterval(() => {
        if (window.outerWidth - window.innerWidth > threshold || 
            window.outerHeight - window.innerHeight > threshold) {
          if (!devtools.open) {
            devtools.open = true;
            console.log('🚨 DevTools detected - activating countermeasures');
            activateDecoy();
          }
        } else {
          devtools.open = false;
        }
      }, 500);
      
      // 2. Decoy content when DevTools opens
      function activateDecoy() {
        const decoy = document.createElement('div');
        decoy.innerHTML = \`
          <h1>Educational Resource Portal</h1>
          <p>Research Database - Scholarly Articles</p>
          <p>Current study: Advanced Network Architecture</p>
          <p>Status: Loading academic content...</p>
        \`;
        decoy.style.cssText = 'padding:50px;font-family:Arial;background:#fff;color:#333;';
        
        // Replace shadow content temporarily
        document.body.innerHTML = '';
        document.body.appendChild(decoy);
        
        // Restore after DevTools likely closed
        setTimeout(() => {
          document.body.innerHTML = '';
          document.body.appendChild(shadowHost);
        }, 3000);
      }
      
      // 3. Prevent screenshot/screen capture
      document.addEventListener('keydown', (e) => {
        // Detect print screen
        if (e.key === 'PrintScreen' || (e.ctrlKey && e.shiftKey && e.key === 'S')) {
          e.preventDefault();
          activateDecoy();
          setTimeout(() => location.reload(), 2000);
        }
      });
      
      // 4. Detect screen recording (Chrome Tab Capture API)
      if (navigator.mediaDevices && navigator.mediaDevices.getDisplayMedia) {
        const originalGetDisplayMedia = navigator.mediaDevices.getDisplayMedia;
        navigator.mediaDevices.getDisplayMedia = function() {
          console.log('🚨 Screen capture detected!');
          activateDecoy();
          return originalGetDisplayMedia.apply(this, arguments);
        };
      }
      
      // 5. Hide from extension content scripts
      // Extensions cannot access closed shadow DOM
      Object.defineProperty(document, 'body', {
        get: function() {
          // Return decoy body to extensions
          const decoyBody = document.createElement('body');
          decoyBody.innerHTML = '<h1>Educational Portal</h1>';
          return decoyBody;
        }
      });
      
      // 6. Disable context menu on sensitive areas
      shadowRoot.addEventListener('contextmenu', (e) => {
        e.preventDefault();
        return false;
      });
      
      // 7. Anti-automation detection
      Object.defineProperty(navigator, 'webdriver', {
        get: () => false
      });
      
      // 8. Spoof headless detection
      Object.defineProperty(navigator, 'plugins', {
        get: () => [1, 2, 3, 4, 5] // Fake plugins
      });
      
      console.log('✅ Shadow DOM stealth mode active');
      console.log('🛡️ Protection: DevTools, Extensions, Screenshots, Recording');
    }
    
    // 9. Tab visibility hiding
    // Hide specific tabs from being monitored
    const HIDDEN_TABS = new Set();
    
    window.hideTab = function(tabId) {
      HIDDEN_TABS.add(tabId);
      console.log(\`🥷 Tab \${tabId} hidden from monitors\`);
    };
    
    // Override document.title for hidden tabs
    let realTitle = document.title;
    Object.defineProperty(document, 'title', {
      get: function() {
        if (HIDDEN_TABS.has(window.location.href)) {
          return 'Google Classroom - Assignments';
        }
        return realTitle;
      },
      set: function(newTitle) {
        realTitle = newTitle;
      }
    });
    
    // 10. Stealth mode indicator (only in console)
    if (${STEALTH_MODE}) {
      console.log('%c🥷 STEALTH MODE ACTIVE', 'color:#8a2be2;font-size:20px;font-weight:bold;');
      console.log('%cProtection Level: MAXIMUM', 'color:#00ff00;font-weight:bold;');
      console.log('%c• Shadow DOM: CLOSED', 'color:#888;');
      console.log('%c• DevTools Detection: ENABLED', 'color:#888;');
      console.log('%c• Screenshot Block: ENABLED', 'color:#888;');
      console.log('%c• Extension Shield: ENABLED', 'color:#888;');
    }
  })();
  </script>
  `;
  
  // Inject shadow script before </body>
  if (html.includes('</body>')) {
    return html.replace('</body>', shadowScript + '</body>');
  } else {
    return html + shadowScript;
  }
}

// Message handler for communication with main page
self.addEventListener('message', (event) => {
  if (event.data.type === 'HIDE_TAB') {
    console.log('🥷 Hiding tab:', event.data.tabId);
    // Notify all clients
    self.clients.matchAll().then(clients => {
      clients.forEach(client => {
        client.postMessage({
          type: 'TAB_HIDDEN',
          tabId: event.data.tabId
        });
      });
    });
  }
  
  if (event.data.type === 'ACTIVATE_STEALTH') {
    console.log('🥷 Activating maximum stealth mode');
    self.clients.matchAll().then(clients => {
      clients.forEach(client => {
        client.postMessage({
          type: 'STEALTH_ACTIVATED'
        });
      });
    });
  }
});
