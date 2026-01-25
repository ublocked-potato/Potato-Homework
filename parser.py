"""
Python 3.14 - Advanced HTML Parsing Fallback
Used when Rust hot path is unavailable
Leverages Python's superior BeautifulSoup parsing for complex sites
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import urllib.parse
from datetime import datetime
import re

app = Flask(__name__)
CORS(app)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}

def calculate_relevance(result: dict, keywords: list[str]) -> int:
    """Python's string operations for relevance scoring"""
    score = 0
    title_lower = result['title'].lower()
    snippet_lower = result['snippet'].lower()
    url_lower = result['url'].lower()
    
    for keyword in keywords:
        kw_lower = keyword.lower()
        
        if kw_lower in title_lower:
            score += 10
            if kw_lower == title_lower:
                score += 20
        
        if kw_lower in snippet_lower:
            score += 5
        
        if kw_lower in url_lower:
            score += 3
    
    if all(kw.lower() in (title_lower + ' ' + snippet_lower) for kw in keywords):
        score += 15
    
    return score

def parse_duckduckgo(html: str) -> list[dict]:
    """Advanced DDG parsing with BeautifulSoup"""
    soup = BeautifulSoup(html, 'html.parser')
    results = []
    
    for result in soup.select('.result__body')[:100]:
        link = result.select_one('.result__a')
        snippet = result.select_one('.result__snippet')
        
        if link:
            url = link.get('href', '')
            
            # Advanced URL extraction
            if 'uddg=' in url:
                match = re.search(r'uddg=([^&]+)', url)
                if match:
                    url = urllib.parse.unquote(match.group(1))
            
            results.append({
                'title': link.get_text(strip=True),
                'url': url,
                'display_url': urllib.parse.urlparse(url).netloc.replace('www.', ''),
                'snippet': snippet.get_text(strip=True) if snippet else '',
                'is_instant': False,
            })
    
    return results

def parse_google(html: str) -> list[dict]:
    """Advanced Google parsing - Python excels at this"""
    soup = BeautifulSoup(html, 'html.parser')
    results = []
    
    for result in soup.select('div.g')[:100]:
        title_elem = result.select_one('h3')
        link_elem = result.select_one('a')
        snippet_elem = result.select_one('.VwiC3b, .s, .st, span.aCOpRe, .yXK7lf')
        
        if title_elem and link_elem:
            url = link_elem.get('href', '')
            
            # Clean Google redirect
            if url.startswith('/url?q='):
                parsed = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
                url = parsed.get('q', [''])[0]
            
            if url and not url.startswith('/search'):
                results.append({
                    'title': title_elem.get_text(strip=True),
                    'url': url,
                    'display_url': urllib.parse.urlparse(url).netloc.replace('www.', ''),
                    'snippet': snippet_elem.get_text(strip=True) if snippet_elem else '',
                    'is_instant': False,
                })
    
    return results

def parse_brave(html: str) -> list[dict]:
    """Brave search parsing"""
    soup = BeautifulSoup(html, 'html.parser')
    results = []
    
    for result in soup.select('div.snippet')[:100]:
        title = result.select_one('.snippet-title')
        link = result.select_one('a.result-header')
        snippet = result.select_one('.snippet-description')
        
        if title and link:
            url = link.get('href', '')
            results.append({
                'title': title.get_text(strip=True),
                'url': url,
                'display_url': urllib.parse.urlparse(url).netloc.replace('www.', ''),
                'snippet': snippet.get_text(strip=True) if snippet else '',
                'is_instant': False,
            })
    
    return results

@app.route('/api/search', methods=['GET', 'POST'])
def search():
    """Python fallback search - used when Rust is unavailable"""
    try:
        if request.method == 'POST':
            data = request.get_json()
            query = data.get('q', '')
            engine = data.get('engine', 'duckduckgo')
        else:
            query = request.args.get('q', '')
            engine = request.args.get('engine', 'duckduckgo')
        
        if not query:
            return jsonify({"success": False, "error": "No query"}), 400
        
        print(f"🐍 Python parsing: {query} via {engine}")
        
        all_results = []
        
        # Multi-page scraping
        pages = 5 if engine != 'google' else 10
        
        for page in range(pages):
            try:
                if engine == 'duckduckgo':
                    url = f'https://html.duckduckgo.com/html/?q={urllib.parse.quote_plus(query)}'
                    if page > 0:
                        url += f'&s={page * 30}'
                elif engine == 'google':
                    url = f'https://www.google.com/search?q={urllib.parse.quote_plus(query)}&num=10&start={page * 10}'
                elif engine == 'brave':
                    url = f'https://search.brave.com/search?q={urllib.parse.quote_plus(query)}&offset={page}'
                else:
                    url = f'https://html.duckduckgo.com/html/?q={urllib.parse.quote_plus(query)}'
                
                response = requests.get(url, headers=HEADERS, timeout=8)
                response.raise_for_status()
                
                # Use appropriate parser
                if engine == 'duckduckgo':
                    results = parse_duckduckgo(response.text)
                elif engine == 'google':
                    results = parse_google(response.text)
                elif engine == 'brave':
                    results = parse_brave(response.text)
                else:
                    results = parse_duckduckgo(response.text)
                
                all_results.extend(results)
                
            except Exception as e:
                print(f"⚠️ Page {page} failed: {e}")
                continue
        
        # Remove duplicates
        seen_urls = set()
        unique_results = []
        for result in all_results:
            if result['url'] not in seen_urls and result['url']:
                seen_urls.add(result['url'])
                unique_results.append(result)
        
        # Calculate relevance scores
        keywords = [w for w in query.split() if len(w) > 2]
        for result in unique_results:
            result['relevance_score'] = calculate_relevance(result, keywords)
        
        # Sort by relevance
        unique_results.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        # Top 100
        final_results = unique_results[:100]
        
        return jsonify({
            "success": True,
            "query": query,
            "engine": engine,
            "results": final_results,
            "total_count": len(final_results),
            "method": "python-advanced-parser",
            "timestamp": datetime.utcnow().isoformat()
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "service": "python-parser",
        "version": "3.14.x",
        "timestamp": datetime.utcnow().isoformat()
    })

if __name__ == '__main__':
    print("🐍 Python 3.14 Advanced Parser starting on port 5000...")
    app.run(host='0.0.0.0', port=5000, debug=False)
