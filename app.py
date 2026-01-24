#!/usr/bin/env python3
"""
OmniSearch Ultimate Backend - Everything Works Edition 🥔
Features: ChatGPT proxy, DuckDuckGo AI, Fixed search engines, Advanced bypass
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
import json
import warnings

warnings.filterwarnings('ignore')

app = Flask(__name__)
CORS(app)

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
]

def fetch_with_retry(url, timeout=15, retries=2):
    """Fetch with protocol switching and retries"""
    headers = {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=timeout, verify=False, allow_redirects=True)
            if response.status_code == 200:
                return response
        except:
            if attempt == 0 and url.startswith('https://'):
                url = url.replace('https://', 'http://')
                continue
        time.sleep(0.5)
    
    return None

def get_duckduckgo_instant_answer(query):
    """Get DuckDuckGo AI instant answer"""
    try:
        api_url = f'https://api.duckduckgo.com/?q={quote(query)}&format=json&no_html=1&skip_disambig=1'
        response = fetch_with_retry(api_url, timeout=8)
        
        if response:
            data = response.json()
            
            # Check for instant answer
            if data.get('AbstractText'):
                return {
                    'has_answer': True,
                    'answer': data['AbstractText'],
                    'title': data.get('Heading', 'Quick Answer'),
                    'source': data.get('AbstractSource', 'DuckDuckGo'),
                    'url': data.get('AbstractURL', ''),
                    'type': 'abstract'
                }
            
            # Check for definition
            if data.get('Definition'):
                return {
                    'has_answer': True,
                    'answer': data['Definition'],
                    'title': data.get('DefinitionSource', 'Definition'),
                    'source': data.get('DefinitionSource', 'Dictionary'),
                    'url': data.get('DefinitionURL', ''),
                    'type': 'definition'
                }
            
            # Check for answer type
            if data.get('Answer'):
                return {
                    'has_answer': True,
                    'answer': data['Answer'],
                    'title': 'Answer',
                    'source': 'DuckDuckGo',
                    'url': '',
                    'type': 'answer'
                }
    except:
        pass
    
    return {'has_answer': False}

def scrape_duckduckgo(query):
    """Enhanced DuckDuckGo scraper"""
    results = []
    
    try:
        url = f'https://html.duckduckgo.com/html/?q={quote(query)}'
        response = fetch_with_retry(url)
        
        if response:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for result in soup.select('.result__body'):
                try:
                    link_elem = result.select_one('.result__a')
                    if not link_elem:
                        continue
                    
                    title = link_elem.get_text(strip=True)
                    href = link_elem.get('href', '')
                    
                    # Clean DDG redirect
                    if 'uddg=' in href:
                        match = re.search(r'uddg=([^&]+)', href)
                        if match:
                            href = unquote(match.group(1))
                    
                    if href.startswith('//'):
                        href = 'https:' + href
                    
                    url_elem = result.select_one('.result__url')
                    snippet_elem = result.select_one('.result__snippet')
                    
                    if title and href and href.startswith('http'):
                        results.append({
                            'title': title,
                            'url': href,
                            'display_url': url_elem.get_text(strip=True) if url_elem else urlparse(href).netloc,
                            'snippet': snippet_elem.get_text(strip=True) if snippet_elem else '',
                            'engine': 'duckduckgo'
                        })
                except:
                    continue
    except:
        pass
    
    return results[:20]

def scrape_google(query):
    """Enhanced Google scraper with better parsing"""
    results = []
    
    try:
        # Use multiple Google endpoints
        urls = [
            f'https://www.google.com/search?q={quote(query)}&num=25&hl=en',
            f'https://www.google.com/search?q={quote(query)}&num=25&gl=us&hl=en'
        ]
        
        for search_url in urls:
            response = fetch_with_retry(search_url)
            
            if response:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Multiple selectors for Google's changing structure
                selectors = ['.g', 'div[data-sokoban-container]', '.tF2Cxc', '.Gx5Zad']
                
                for selector in selectors:
                    for result in soup.select(selector):
                        try:
                            link = result.select_one('a')
                            heading = result.select_one('h3')
                            
                            if not link or not heading:
                                continue
                            
                            href = link.get('href', '')
                            
                            # Clean Google redirect
                            if '/url?q=' in href:
                                match = re.search(r'[?&]q=([^&]+)', href)
                                if match:
                                    href = unquote(match.group(1))
                            
                            # Skip Google internal
                            if 'google.com/search' in href or not href.startswith('http'):
                                continue
                            
                            title = heading.get_text(strip=True)
                            snippet_elem = result.select_one('.VwiC3b, .IsZvec, .lEBKkf')
                            
                            if title and href:
                                results.append({
                                    'title': title,
                                    'url': href,
                                    'display_url': urlparse(href).netloc.replace('www.', ''),
                                    'snippet': snippet_elem.get_text(strip=True) if snippet_elem else '',
                                    'engine': 'google'
                                })
                                
                                if len(results) >= 20:
                                    return results
                        except:
                            continue
                
                if results:
                    break
    except:
        pass
    
    return results[:20]

def scrape_brave(query):
    """Fixed Brave Search scraper"""
    results = []
    
    try:
        url = f'https://search.brave.com/search?q={quote(query)}&source=web'
        response = fetch_with_retry(url)
        
        if response:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Brave uses multiple result types
            selectors = [
                '.snippet',
                'div[data-type="web"]',
                '.result',
                'div.fdb'
            ]
            
            for selector in selectors:
                for result in soup.select(selector):
                    try:
                        # Try multiple link selectors
                        link = (result.select_one('a.result-header') or 
                               result.select_one('.title a') or
                               result.select_one('a[href^="http"]'))
                        
                        if not link:
                            continue
                        
                        href = link.get('href', '')
                        if not href.startswith('http'):
                            continue
                        
                        title = link.get_text(strip=True)
                        
                        # Try multiple snippet selectors
                        snippet_elem = (result.select_one('.snippet-description') or
                                      result.select_one('.description') or
                                      result.select_one('p'))
                        
                        if title and href:
                            results.append({
                                'title': title,
                                'url': href,
                                'display_url': urlparse(href).netloc.replace('www.', ''),
                                'snippet': snippet_elem.get_text(strip=True) if snippet_elem else '',
                                'engine': 'brave'
                            })
                            
                            if len(results) >= 20:
                                return results
                    except:
                        continue
                
                if results:
                    break
    except:
        pass
    
    return results[:20]

def scrape_startpage(query):
    """Startpage (encrypted Google results)"""
    results = []
    
    try:
        url = f'https://www.startpage.com/sp/search?query={quote(query)}'
        response = fetch_with_retry(url)
        
        if response:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for result in soup.select('.w-gl__result, .result'):
                try:
                    link = result.select_one('.w-gl__result-url, a[href^="http"]')
                    title_elem = result.select_one('h3, .w-gl__result-title')
                    
                    if not link or not title_elem:
                        continue
                    
                    href = link.get('href', '')
                    title = title_elem.get_text(strip=True)
                    snippet_elem = result.select_one('.w-gl__description, .description')
                    
                    if title and href and href.startswith('http'):
                        results.append({
                            'title': title,
                            'url': href,
                            'display_url': urlparse(href).netloc.replace('www.', ''),
                            'snippet': snippet_elem.get_text(strip=True) if snippet_elem else '',
                            'engine': 'startpage'
                        })
                except:
                    continue
    except:
        pass
    
    return results[:20]

@app.route('/')
def index():
    """Serve main page"""
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return "OmniSearch Backend Running. Please add index.html"

@app.route('/api/search', methods=['GET'])
def search():
    """Enhanced search with instant answers"""
    query = request.args.get('q', '').strip()
    engine = request.args.get('engine', 'duckduckgo').lower()
    
    if not query:
        return jsonify({'success': False, 'error': 'No query', 'results': []})
    
    # Get instant answer (DuckDuckGo AI)
    instant_answer = get_duckduckgo_instant_answer(query)
    
    # Get search results
    if engine == 'duckduckgo':
        results = scrape_duckduckgo(query)
    elif engine == 'google':
        results = scrape_google(query)
    elif engine == 'brave':
        results = scrape_brave(query)
    elif engine == 'startpage':
        results = scrape_startpage(query)
    else:
        results = scrape_duckduckgo(query)
    
    # Add instant answer to top if available
    if instant_answer['has_answer']:
        instant_result = {
            'title': '🤖 ' + instant_answer['title'],
            'url': instant_answer.get('url', '#'),
            'display_url': instant_answer['source'],
            'snippet': instant_answer['answer'],
            'engine': 'duckduckgo_ai',
            'is_instant': True
        }
        results.insert(0, instant_result)
    
    return jsonify({
        'success': len(results) > 0,
        'query': query,
        'engine': engine,
        'has_instant_answer': instant_answer['has_answer'],
        'instant_answer': instant_answer if instant_answer['has_answer'] else None,
        'results': results,
        'count': len(results)
    })

@app.route('/api/proxy', methods=['GET'])
def proxy():
    """Advanced proxy with ChatGPT support"""
    url_param = request.args.get('url', '')
    
    if not url_param:
        return 'No URL', 400
    
    try:
        target_url = base64.b64decode(url_param).decode('utf-8')
    except:
        return 'Invalid URL', 400
    
    # Special handling for ChatGPT/AI sites
    if any(site in target_url.lower() for site in ['chatgpt.com', 'chat.openai.com']):
        return f'''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>ChatGPT Access</title>
            <style>
                body{{margin:0;padding:0;font-family:system-ui;background:#1a0033;color:white;}}
                .container{{max-width:800px;margin:80px auto;padding:40px;text-align:center;}}
                .chat-embed{{width:100%;height:600px;border:none;border-radius:20px;background:white;box-shadow:0 20px 60px rgba(0,0,0,0.5);}}
                .tip{{margin-top:30px;padding:20px;background:rgba(138,43,226,0.2);border-radius:15px;}}
                .btn{{display:inline-block;margin:10px;padding:15px 30px;background:linear-gradient(135deg,#8a2be2,#9300ea);color:white;text-decoration:none;border-radius:25px;font-weight:600;}}
            </style>
        </head>
        <body>
            <div class="container">
                <h1 style="font-size:48px;margin-bottom:20px;">🤖 ChatGPT Access</h1>
                <p style="font-size:18px;opacity:0.9;margin-bottom:30px;">
                    ChatGPT requires direct access. Choose an option below:
                </p>
                
                <iframe class="chat-embed" src="https://chat.openai.com" 
                        sandbox="allow-same-origin allow-scripts allow-forms allow-popups">
                </iframe>
                
                <div class="tip">
                    <p style="font-size:14px;"><strong>💡 For Best Experience:</strong></p>
                    <a href="https://chat.openai.com" target="_blank" class="btn">🌐 Open ChatGPT in New Tab</a>
                    <a href="/" class="btn">← Back to Search</a>
                </div>
                
                <div style="margin-top:30px;font-size:13px;opacity:0.7;">
                    <p>ChatGPT requires:</p>
                    <p>• WebSocket connections for real-time AI responses</p>
                    <p>• Authentication cookies and session management</p>
                    <p>• Direct API access to OpenAI servers</p>
                </div>
            </div>
        </body>
        </html>
        '''
    
    # Fetch page
    response = fetch_with_retry(target_url)
    
    if not response:
        return f'''<html><body style="text-align:center;padding:50px;background:#1a0033;color:white;">
        <h1>🥔 Cannot Load</h1>
        <p>{target_url}</p>
        <a href="{target_url}" target="_blank" style="color:#8a2be2;">Visit Real Site</a>
        </body></html>''', 502
    
    content_type = response.headers.get('Content-Type', '')
    
    if 'text/html' not in content_type:
        return Response(response.content, content_type=content_type)
    
    # Process HTML
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    
    parsed = urlparse(target_url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    
    # Rewrite URLs
    for tag in soup.find_all(['a', 'link', 'script', 'img', 'iframe']):
        for attr in ['href', 'src', 'action']:
            if tag.has_attr(attr):
                url = tag[attr]
                if url and not url.startswith(('data:', 'javascript:', 'mailto:', '#')):
                    abs_url = urljoin(target_url, url)
                    encoded = base64.b64encode(abs_url.encode()).decode()
                    tag[attr] = f'/api/proxy?url={encoded}'
    
    # Proxy bar
    bar = f'''
    <style>
    #pxbar{{position:fixed;top:0;left:0;right:0;height:50px;background:rgba(0,0,0,0.95);z-index:999999;display:flex;align-items:center;padding:0 10px;border-bottom:2px solid #8a2be2;}}
    #pxbar button{{width:38px;height:38px;background:rgba(255,255,255,0.15);border:none;border-radius:8px;color:#fff;cursor:pointer;margin:0 4px;}}
    #pxvisit{{background:linear-gradient(135deg,#8a2be2,#9300ea)!important;padding:0 15px!important;width:auto!important;border-radius:20px!important;}}
    body{{padding-top:50px!important;}}
    </style>
    <div id="pxbar">
    <button onclick="location.href='/'" title="Home">🥔</button>
    <button onclick="history.back()">←</button>
    <button onclick="history.forward()">→</button>
    <button onclick="location.reload()">⟳</button>
    <button id="pxvisit" onclick="window.open('{target_url}','_blank')">🌐 Visit Real</button>
    <div style="margin-left:auto;font:10px monospace;color:rgba(255,255,255,0.7);">{target_url[:60]}...</div>
    </div>
    '''
    
    if soup.body:
        soup.body.insert(0, BeautifulSoup(bar, 'html.parser'))
    
    return str(soup)

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'version': '4.0-ultimate'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=Fa
