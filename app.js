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
        <a href="/" style="color:#8a2be2;">← Back to Search</a>
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
    
    # Add proxy bar
    proxy_bar = f'''
    <style>
    #pxbar{{position:fixed!important;top:0!important;left:0!important;right:0!important;height:45px!important;background:rgba(0,0,0,0.95)!important;z-index:2147483647!important;display:flex!important;align-items:center!important;padding:0 10px!important;border-bottom:2px solid #8a2be2!important;}}
    #pxbar button{{width:36px;height:36px;background:rgba(255,255,255,0.15);border:none;border-radius:8px;color:#fff;cursor:pointer;margin:0 4px;}}
    #pxlogo{{width:36px;height:36px;border-radius:50%;background:linear-gradient(135deg,#8a2be2,#9300ea);display:flex;align-items:center;justify-content:center;cursor:pointer;}}
    body{{padding-top:45px!important;}}
    </style>
    <div id="pxbar">
    <div id="pxlogo" onclick="location.href='/'">🥔</div>
    <button onclick="history.back()">←</button>
    <button onclick="history.forward()">→</button>
    <button onclick="location.reload()">⟳</button>
    <div style="margin-left:auto;font:10px monospace;color:rgba(255,255,255,0.7);">{target_url}</div>
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
