from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import urllib.parse
import re
import base64
from datetime import datetime

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}

def calculate_relevance_score(result, query_keywords):
    """Calculate relevance score based on keyword matches"""
    score = 0
    title_lower = result['title'].lower()
    snippet_lower = result['snippet'].lower()
    url_lower = result['url'].lower()
    
    for keyword in query_keywords:
        keyword_lower = keyword.lower()
        # Title matches are most valuable
        if keyword_lower in title_lower:
            score += 10
            # Exact phrase match bonus
            if keyword_lower == title_lower:
                score += 20
        # Snippet matches
        if keyword_lower in snippet_lower:
            score += 5
        # URL matches
        if keyword_lower in url_lower:
            score += 3
    
    # Bonus for having all keywords
    if all(kw.lower() in (title_lower + ' ' + snippet_lower) for kw in query_keywords):
        score += 15
    
    return score

def rank_results_by_relevance(results, query):
    """Sort results by keyword relevance"""
    query_keywords = [w for w in query.split() if len(w) > 2]
    
    for result in results:
        result['relevance_score'] = calculate_relevance_score(result, query_keywords)
    
    # Sort by relevance score (highest first)
    return sorted(results, key=lambda x: x['relevance_score'], reverse=True)

@app.route('/api/search', methods=['GET', 'POST'])
def search():
    """Search endpoint - returns ~100 results ranked by relevance"""
    try:
        if request.method == 'POST':
            data = request.get_json()
            query = data.get('q', '')
            engine = data.get('engine', 'duckduckgo')
        else:
            query = request.args.get('q', '')
            engine = request.args.get('engine', 'duckduckgo')
        
        if not query:
            return jsonify({"success": False, "error": "No query provided"}), 400
        
        encoded_query = urllib.parse.quote_plus(query)
        all_results = []
        
        # Multi-page search to get ~100 results
        if engine == 'duckduckgo':
            # DDG HTML version - fetch multiple pages
            for page in range(0, 5):  # 5 pages = ~100 results
                search_url = f'https://html.duckduckgo.com/html/?q={encoded_query}'
                if page > 0:
                    search_url += f'&s={page * 30}'
                
                try:
                    response = requests.get(search_url, headers=HEADERS, timeout=8)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    for result in soup.select('.result__body'):
                        link = result.select_one('.result__a')
                        snippet = result.select_one('.result__snippet')
                        
                        if link:
                            url = link.get('href', '')
                            # Extract real URL from DDG redirect
                            if 'uddg=' in url:
                                match = re.search(r'uddg=([^&]+)', url)
                                if match:
                                    url = urllib.parse.unquote(match.group(1))
                            
                            all_results.append({
                                'title': link.get_text(strip=True),
                                'url': url,
                                'display_url': urllib.parse.urlparse(url).netloc.replace('www.', ''),
                                'snippet': snippet.get_text(strip=True) if snippet else '',
                                'is_instant': False
                            })
                except Exception as e:
                    print(f"DDG page {page} error: {e}")
                    continue
        
        elif engine == 'google':
            # Google - multiple result pages
            for page in range(0, 10):  # 10 pages = ~100 results
                search_url = f'https://www.google.com/search?q={encoded_query}&num=10&start={page * 10}'
                
                try:
                    response = requests.get(search_url, headers=HEADERS, timeout=8)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    for result in soup.select('div.g'):
                        title_elem = result.select_one('h3')
                        link_elem = result.select_one('a')
                        snippet_elem = result.select_one('.VwiC3b, .s, .st, span.aCOpRe')
                        
                        if title_elem and link_elem:
                            url = link_elem.get('href', '')
                            if url.startswith('/url?q='):
                                url = urllib.parse.parse_qs(urllib.parse.urlparse(url).query).get('q', [''])[0]
                            
                            if url and not url.startswith('/search'):
                                all_results.append({
                                    'title': title_elem.get_text(strip=True),
                                    'url': url,
                                    'display_url': urllib.parse.urlparse(url).netloc.replace('www.', ''),
                                    'snippet': snippet_elem.get_text(strip=True) if snippet_elem else '',
                                    'is_instant': False
                                })
                except Exception as e:
                    print(f"Google page {page} error: {e}")
                    continue
        
        elif engine == 'brave':
            # Brave search
            for page in range(0, 5):
                search_url = f'https://search.brave.com/search?q={encoded_query}&offset={page}'
                
                try:
                    response = requests.get(search_url, headers=HEADERS, timeout=8)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    for result in soup.select('div.snippet'):
                        title_elem = result.select_one('.snippet-title')
                        link_elem = result.select_one('a.result-header')
                        snippet_elem = result.select_one('.snippet-description')
                        
                        if title_elem and link_elem:
                            all_results.append({
                                'title': title_elem.get_text(strip=True),
                                'url': link_elem.get('href', ''),
                                'display_url': urllib.parse.urlparse(link_elem.get('href', '')).netloc.replace('www.', ''),
                                'snippet': snippet_elem.get_text(strip=True) if snippet_elem else '',
                                'is_instant': False
                            })
                except Exception as e:
                    print(f"Brave page {page} error: {e}")
                    continue
        
        else:  # startpage
            search_url = f'https://www.startpage.com/sp/search?query={encoded_query}'
            
            try:
                response = requests.get(search_url, headers=HEADERS, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                
                for result in soup.select('.w-gl__result'):
                    title_elem = result.select_one('.w-gl__result-title')
                    link_elem = result.select_one('a.w-gl__result-url')
                    snippet_elem = result.select_one('.w-gl__description')
                    
                    if title_elem and link_elem:
                        all_results.append({
                            'title': title_elem.get_text(strip=True),
                            'url': link_elem.get('href', ''),
                            'display_url': urllib.parse.urlparse(link_elem.get('href', '')).netloc.replace('www.', ''),
                            'snippet': snippet_elem.get_text(strip=True) if snippet_elem else '',
                            'is_instant': False
                        })
            except Exception as e:
                print(f"Startpage error: {e}")
        
        # Remove duplicates based on URL
        seen_urls = set()
        unique_results = []
        for result in all_results:
            if result['url'] not in seen_urls and result['url']:
                seen_urls.add(result['url'])
                unique_results.append(result)
        
        # Rank by keyword relevance
        ranked_results = rank_results_by_relevance(unique_results, query)
        
        # Limit to 100 best results
        final_results = ranked_results[:100]
        
        return jsonify({
            "success": True,
            "query": query,
            "engine": engine,
            "results": final_results,
            "total_count": len(final_results),
            "timestamp": datetime.utcnow().isoformat()
        })
    
    except requests.Timeout:
        return jsonify({"success": False, "error": "Search timeout"}), 504
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/proxy', methods=['GET'])
def proxy():
    """Proxy any URL through the server"""
    try:
        url_param = request.args.get('url', '')
        
        if not url_param:
            return jsonify({"error": "No URL provided"}), 400
        
        # Decode base64 URL
        try:
            url = base64.b64decode(url_param).decode('utf-8')
        except:
            url = url_param
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Fetch the URL
        response = requests.get(url, headers=HEADERS, timeout=15, allow_redirects=True)
        
        content_type = response.headers.get('Content-Type', '')
        
        if 'text/html' in content_type:
            html = response.text
            # Basic link rewriting for relative URLs
            base_url = urllib.parse.urljoin(url, '/')
            html = re.sub(r'href="/', f'href="{base_url}', html)
            html = re.sub(r'src="/', f'src="{base_url}', html)
            
            return Response(html, content_type=content_type, headers={
                'Access-Control-Allow-Origin': '*',
                'X-Frame-Options': 'ALLOWALL'
            })
        else:
            return Response(response.content, content_type=content_type, headers={
                'Access-Control-Allow-Origin': '*'
            })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "OmniSearch Proxy",
        "version": "3.0",
        "timestamp": datetime.utcnow().isoformat()
    }), 200

@app.route('/', methods=['GET'])
def home():
    """API info endpoint"""
    return jsonify({
        "name": "OmniSearch Python Backend",
        "version": "3.0",
        "endpoints": {
            "/api/search": "Search with 100 results ranked by relevance",
            "/api/proxy": "Proxy any URL",
            "/api/health": "Health check"
        }
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
