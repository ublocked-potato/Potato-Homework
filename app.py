#!/usr/bin/env python3
"""
OmniSearch Python Backend - Advanced Bypass Engine 🥔
Implements: Protocol Switching, Proxy Chaining, Header Rotation, DPI Evasion
"""

from flask import Flask, request, jsonify, render_template_string, Response
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re
import random
import time
from urllib.parse import urljoin, urlparse, quote, unquote
import base64
import ssl
import warnings

# Suppress SSL warnings
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Advanced User-Agent Rotation (2026 realistic agents)
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15'
]

# External Proxy List (Fallback for DPI evasion)
PROXY_LIST = [
    None,  # Direct connection first
    {'http': 'http://proxy.server:8080', 'https': 'http://proxy.server:8080'},
    # Add more proxies as needed
]

# Protocol switching function
def fetch_with_protocol_switching(url, timeout=10):
    """Try HTTPS first, fallback to HTTP if blocked"""
    headers = {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0'
    }
    
    # Try HTTPS first
    try:
        response = requests.get(url, headers=headers, timeout=timeout, verify=False, allow_redirects=True)
        if response.status_code == 200:
            return response
    except:
        pass
    
    # Fallback to HTTP (port switching)
    if url.startswith('https://'):
        http_url = url.replace('https://', 'http://')
        try:
            response = requests.get(http_url, headers=headers, timeout=timeout, verify=False, allow_redirects=True)
            if response.status_code == 200:
                return response
        except:
            pass
    
    return None

# Advanced search scraper
def scrape_search_engine(query, engine='duckduckgo'):
    """Scrape search results with advanced bypass techniques"""
    results = []
    
    try:
        if engine == 'duckduckgo':
            url = f'https://html.duckduckgo.com/html/?q={quote(query)}'
            response = fetch_with_protocol_switching(url)
            
            if response:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                for result in soup.select('.result__body'):
                    try:
                        link_elem = result.select_one('.result__a')
                        if not link_elem:
                            continue
                        
                        title = link_elem.get_text(strip=True)
                        href = link_elem.get('href', '')
                        
                        # Clean DDG redirect URLs
                        if 'uddg=' in href:
                            match = re.search(r'uddg=([^&]+)', href)
                            if match:
                                href = unquote(match.group(1))
                        
                        url_elem = result.select_one('.result__url')
                        snippet_elem = result.select_one('.result__snippet')
                        
                        display_url = url_elem.get_text(strip=True) if url_elem else urlparse(href).netloc
                        snippet = snippet_elem.get_text(strip=True) if snippet_elem else ''
                        
                        if title and href:
                            results.append({
                                'title': title,
                                'url': href,
                                'display_url': display_url,
                                'snippet': snippet,
                                'engine': 'duckduckgo'
                            })
                    except:
                        continue
        
        elif engine == 'google':
            url = f'https://www.google.com/search?q={quote(query)}&num=20'
            response = fetch_with_protocol_switching(url)
            
            if response:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                for result in soup.select('.g, div[data-sokoban-container]'):
                    try:
                        link_elem = result.select_one('a')
                        heading = result.select_one('h3')
                        
                        if not link_elem or not heading:
                            continue
                        
                        href = link_elem.get('href', '')
                        
                        # Clean Google redirect
                        if '/url?q=' in href:
                            match = re.search(r'[?&]q=([^&]+)', href)
                            if match:
                                href = unquote(match.group(1))
                        
                        if 'google.com/search' in href:
                            continue
                        
                        title = heading.get_text(strip=True)
                        snippet_elem = result.select_one('.VwiC3b, .IsZvec')
                        snippet = snippet_elem.get_text(strip=True) if snippet_elem else ''
                        
                        if title and href and href.startswith('http'):
                            results.append({
                                'title': title,
                                'url': href,
                                'display_url': urlparse(href).netloc.replace('www.', ''),
                                'snippet': snippet,
                                'engine': 'google'
                            })
                    except:
                        continue
        
        elif engine == 'brave':
            url = f'https://search.brave.com/search?q={quote(query)}'
            response = fetch_with_protocol_switching(url)
            
            if response:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                for result in soup.select('.snippet'):
                    try:
                        link_elem = result.select_one('a.result-header, .title a')
                        if not link_elem:
                            continue
                        
                        title = link_elem.get_text(strip=True)
                        href = link_elem.get('href', '')
                        snippet_elem = result.select_one('.snippet-description')
                        snippet = snippet_elem.get_text(strip=True) if snippet_elem else ''
                        
                        if title and href and href.startswith('http'):
                            results.append({
                                'title': title,
                                'url': href,
                                'display_url': urlparse(href).netloc.replace('www.', ''),
                                'snippet': snippet,
                                'engine': 'brave'
                            })
                    except:
                        continue
        
        elif engine == 'startpage':
            # Startpage is encrypted proxy for Google results (2026 DPI-resistant)
            url = f'https://www.startpage.com/sp/search?query={quote(query)}'
            response = fetch_with_protocol_switching(url)
            
            if response:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                for result in soup.select('.w-gl__result'):
                    try:
                        link_elem = result.select_one('.w-gl__result-url')
                        title_elem = result.select_one('h3')
                        
                        if not link_elem or not title_elem:
                            continue
                        
                        title = title_elem.get_text(strip=True)
                        href = link_elem.get('href', '')
                        snippet_elem = result.select_one('.w-gl__description')
                        snippet = snippet_elem.get_text(strip=True) if snippet_elem else ''
                        
                        if title and href and href.startswith('http'):
                            results.append({
                                'title': title,
                                'url': href,
                                'display_url': urlparse(href).netloc.replace('www.', ''),
                                'snippet': snippet,
                                'engine': 'startpage'
                            })
                    except:
                        continue
    
    except Exception as e:
        print(f"Search error for {engine}: {str(e)}")
    
    return results[:20]  # Limit to 20 results

# Routes
@app.route('/')
def index():
    """Serve the main HTML page"""
    with open('index.html', 'r') as f:
        return f.read()

@app.route('/api/search', methods=['GET'])
def search():
    """Search API endpoint"""
    query = request.args.get('q', '').strip()
    engine = request.args.get('engine', 'duckduckgo').lower()
    
    if not query:
        return jsonify({'success': False, 'error': 'No query provided', 'results': []})
    
    # Add random delay to avoid rate limiting
    time.sleep(random.uniform(0.1, 0.3))
    
    results = scrape_search_engine(query, engine)
    
    return jsonify({
        'success': len(results) > 0,
        'query': query,
        'engine': engine,
        'results': results,
        'count': len(results)
    })

@app.route('/api/proxy', methods=['GET'])
def proxy():
    """Proxy endpoint for loading websites"""
    url_param = request.args.get('url', '')
    
    if not url_param:
        return 'No URL provided', 400
    
    try:
        # Decode base64 URL
        target_url = base64.b64decode(url_param).decode('utf-8')
    except:
        return 'Invalid URL encoding', 400
    
    if not target_url.startswith('http'):
        return 'Invalid URL', 400
    
    # Check if site is complex (JavaScript-heavy)
    complex_sites = ['chatgpt.com', 'openai.com', 'perplexity.ai', 'poki.com', 'youtube.com', 
                     'netflix.com', 'discord.com', 'spotify.com', 'twitch.tv']
    is_complex = any(site in target_url.lower() for site in complex_sites)
    
    if is_complex:
        # Show warning page with "Visit Real Site" button
        return f'''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Complex Site Detected</title>
            <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        </head>
        <body style="font-family:'Poppins',sans-serif;background:linear-gradient(135deg,#1a0033,#2d1b69,#4a0e6a);color:white;margin:0;padding:0;display:flex;align-items:center;justify-content:center;min-height:100vh;">
            <div style="text-align:center;max-width:600px;padding:40px;">
                <div style="font-size:72px;margin-bottom:20px;">🥔</div>
                <h1 style="font-size:32px;margin-bottom:20px;">Complex Site Detected</h1>
                <p style="font-size:18px;opacity:0.9;margin-bottom:30px;">
                    This site requires JavaScript, WebSockets, or advanced features that don't work well in proxies.
                </p>
                <div style="background:rgba(255,255,255,0.1);padding:20px;border-radius:20px;margin-bottom:30px;">
                    <p style="font-size:14px;opacity:0.8;margin-bottom:10px;">Detected site:</p>
                    <p style="font-family:monospace;font-size:16px;color:#a78bfa;word-break:break-all;">{target_url}</p>
                </div>
                <div style="display:flex;gap:15px;justify-content:center;flex-wrap:wrap;">
                    <a href="{target_url}" target="_blank" rel="noopener noreferrer" 
                       style="background:linear-gradient(135deg,#8a2be2,#9300ea);color:white;text-decoration:none;padding:15px 30px;border-radius:25px;font-weight:600;font-size:16px;display:inline-block;transition:transform 0.2s;"
                       onmouseover="this.style.transform='scale(1.05)'"
                       onmouseout="this.style.transform='scale(1)'">
                        🌐 Visit Real Site
                    </a>
                    <a href="/" 
                       style="background:rgba(255,255,255,0.2);color:white;text-decoration:none;padding:15px 30px;border-radius:25px;font-weight:600;font-size:16px;display:inline-block;transition:transform 0.2s;"
                       onmouseover="this.style.transform='scale(1.05)'"
                       onmouseout="this.style.transform='scale(1)'">
                        ← Back to Search
                    </a>
                </div>
                <div style="margin-top:40px;padding:20px;background:rgba(138,43,226,0.2);border-radius:15px;border:2px solid rgba(138,43,226,0.4);">
                    <p style="font-size:14px;opacity:0.9;margin-bottom:10px;"><strong>💡 Why this happens:</strong></p>
                    <ul style="text-align:left;font-size:13px;opacity:0.8;line-height:1.8;">
                        <li>ChatGPT/Perplexity: Require WebSocket connections & AI API access</li>
                        <li>Poki/Gaming Sites: Use Canvas, WebGL, complex JavaScript</li>
                        <li>Streaming Sites: DRM protection & video streaming APIs</li>
                    </ul>
                </div>
                <p style="font-size:12px;opacity:0.6;margin-top:30px;">
                    🥔 Tip: For these sites, you'll need to visit them directly or use a VPN
                </p>
            </div>
        </body>
        </html>
        ''', 200
    
    # Fetch the page with protocol switching
    response = fetch_with_protocol_switching(target_url, timeout=15)
    
    if not response:
        return f'''
        <html>
        <body style="font-family:Arial;text-align:center;padding:50px;background:#1a0033;color:white;">
        <h1 style="font-size:72px;">🥔</h1>
        <h2>Cannot Load Page</h2>
        <p>The site may be blocking proxies or is unavailable.</p>
        <p style="font-size:14px;opacity:0.7;">{target_url}</p>
        <div style="margin-top:30px;">
            <a href="{target_url}" target="_blank" rel="noopener noreferrer" 
               style="background:#8a2be2;color:white;text-decoration:none;padding:12px 24px;border-radius:20px;font-weight:600;margin:0 10px;">
                🌐 Visit Real Site
            </a>
            <a href="/" style="background:rgba(255,255,255,0.2);color:white;text-decoration:none;padding:12px 24px;border-radius:20px;font-weight:600;margin:0 10px;">
                ← Back
            </a>
        </div>
        </body>
        </html>
        ''', 502
    
    content_type = response.headers.get('Content-Type', 'text/html')
    
    # For non-HTML content, pass through directly
    if 'text/html' not in content_type:
        return Response(response.content, content_type=content_type)
    
    # HTML processing - rewrite URLs
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    
    parsed_url = urlparse(target_url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    
    # Rewrite all URLs in HTML
    for tag in soup.find_all(['a', 'link', 'script', 'img', 'iframe']):
        for attr in ['href', 'src', 'action']:
            if tag.has_attr(attr):
                url = tag[attr]
                if url and not url.startswith(('data:', 'javascript:', 'mailto:', '#')):
                    # Make absolute
                    abs_url = urljoin(target_url, url)
                    # Encode for proxy
                    encoded = base64.b64encode(abs_url.encode()).decode()
                    tag[attr] = f'/api/proxy?url={encoded}'
    
    # Enhanced proxy bar with "Visit Real Site" button
    proxy_bar = f'''
    <style>
    #pxbar{{position:fixed!important;top:0!important;left:0!important;right:0!important;height:50px!important;background:rgba(0,0,0,0.95)!important;z-index:2147483647!important;display:flex!important;align-items:center!important;padding:0 10px!important;border-bottom:2px solid #8a2be2!important;}}
    #pxbar button{{width:38px;height:38px;background:rgba(255,255,255,0.15);border:none;border-radius:8px;color:#fff;cursor:pointer;margin:0 4px;font-size:14px;}}
    #pxbar button:hover{{background:rgba(255,255,255,0.25);}}
    #pxlogo{{width:38px;height:38px;border-radius:50%;background:linear-gradient(135deg,#8a2be2,#9300ea);display:flex;align-items:center;justify-content:center;cursor:pointer;font-size:18px;}}
    #pxvisit{{background:linear-gradient(135deg,#8a2be2,#9300ea)!important;padding:0 15px!important;width:auto!important;font-weight:600;font-size:13px;border-radius:20px!important;}}
    #pxvisit:hover{{background:linear-gradient(135deg,#9300ea,#a020f0)!important;transform:scale(1.05);}}
    body{{padding-top:50px!important;}}
    </style>
    <div id="pxbar">
    <div id="pxlogo" onclick="location.href='/'">🥔</div>
    <button onclick="history.back()" title="Back">←</button>
    <button onclick="history.forward()" title="Forward">→</button>
    <button onclick="location.reload()" title="Reload">⟳</button>
    <button id="pxvisit" onclick="window.open('{target_url}', '_blank')" title="Open real site in new tab">🌐 Visit Real Site</button>
    <div style="margin-left:auto;font:10px monospace;color:rgba(255,255,255,0.7);max-width:40%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{target_url}</div>
    </div>
    '''
    
    if soup.body:
        soup.body.insert(0, BeautifulSoup(proxy_bar, 'html.parser'))
    
    return str(soup)

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'omnisearch-python'})

if __name__ == '__main__':
    # Development server
    app.run(host='0.0.0.0', port=5000, debug=True)
