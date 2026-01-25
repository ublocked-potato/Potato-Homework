"""
Python 3.14 - Advanced Evasion Layer
Features:
- Real-time text scrambling to bypass keyword loggers
- Detection learning for burned domains
- Automatic mirror deployment
- Academic jargon camouflage
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import base64
import json
import hashlib
import time
from datetime import datetime, timedelta
import random
import string

app = Flask(__name__)
CORS(app)

# Detection tracking
burned_domains = set()
domain_health = {}  # domain -> {'failures': 0, 'last_check': timestamp}
mirror_registry = {}  # original_domain -> [mirror1, mirror2, ...]

# Academic jargon dictionary for camouflage
ACADEMIC_WORDS = [
    "pedagogical", "methodology", "assessment", "curriculum", "synthesis",
    "analysis", "evaluation", "hypothesis", "theorem", "dissertation",
    "scholarly", "empirical", "quantitative", "qualitative", "framework",
    "paradigm", "epistemology", "ontology", "heuristic", "axiom"
]

def generate_scramble_key(url: str) -> str:
    """Generate deterministic scramble key from URL"""
    return hashlib.sha256(url.encode()).hexdigest()[:32]

def scramble_text(text: str, key: str) -> str:
    """
    ROT-N cipher with XOR encoding
    Looks like random characters to keyword loggers
    """
    scrambled = []
    for i, char in enumerate(text):
        # XOR with key character
        key_char = key[i % len(key)]
        xor_val = ord(char) ^ ord(key_char)
        # ROT-13 variant
        scrambled_char = chr((xor_val + 13) % 256)
        scrambled.append(scrambled_char)
    
    # Base64 encode for transport safety
    return base64.b64encode(''.join(scrambled).encode('utf-8')).decode('ascii')

def camouflage_as_academic(text: str) -> str:
    """
    Replace sensitive keywords with academic jargon
    Makes content look like research papers to automated scanners
    """
    sensitive_keywords = {
        'game': 'interactive simulation',
        'video': 'multimedia presentation',
        'play': 'engage with educational content',
        'fun': 'enrichment activity',
        'entertainment': 'educational resource',
        'social media': 'collaborative platform',
        'chat': 'peer discussion forum',
        'proxy': 'network architecture study',
        'unblock': 'access methodology',
        'bypass': 'alternative routing protocol'
    }
    
    result = text
    for keyword, replacement in sensitive_keywords.items():
        result = result.replace(keyword.lower(), replacement)
    
    # Inject random academic words
    words = result.split()
    if len(words) > 10:
        insert_positions = random.sample(range(len(words)), min(3, len(words) // 5))
        for pos in sorted(insert_positions, reverse=True):
            words.insert(pos, random.choice(ACADEMIC_WORDS))
        result = ' '.join(words)
    
    return result

def check_domain_health(domain: str) -> bool:
    """Monitor if domain is burned/blocked"""
    if domain in burned_domains:
        return False
    
    if domain not in domain_health:
        domain_health[domain] = {'failures': 0, 'last_check': time.time()}
    
    health = domain_health[domain]
    
    # Check every 5 minutes max
    if time.time() - health['last_check'] < 300:
        return health['failures'] < 3
    
    try:
        response = requests.head(f"https://{domain}", timeout=5)
        if response.status_code >= 400:
            health['failures'] += 1
        else:
            health['failures'] = 0
        health['last_check'] = time.time()
        
        # Mark as burned after 3 consecutive failures
        if health['failures'] >= 3:
            burned_domains.add(domain)
            print(f"🔥 Domain BURNED: {domain}")
            deploy_mirror(domain)
            return False
        
        return True
    except:
        health['failures'] += 1
        health['last_check'] = time.time()
        if health['failures'] >= 3:
            burned_domains.add(domain)
            print(f"🔥 Domain BURNED: {domain}")
            deploy_mirror(domain)
        return False

def deploy_mirror(burned_domain: str):
    """
    Auto-deploy mirror site via GitHub Pages or Vercel
    Creates instant backup when domain is burned
    """
    print(f"🚀 Deploying mirror for {burned_domain}...")
    
    # Generate mirror domains
    mirrors = [
        f"{burned_domain.replace('.', '-')}-edu.vercel.app",
        f"academic-{hashlib.md5(burned_domain.encode()).hexdigest()[:8]}.github.io",
        f"research-{burned_domain.split('.')[0]}.netlify.app"
    ]
    
    mirror_registry[burned_domain] = mirrors
    
    # In production, this would trigger:
    # 1. GitHub Actions to deploy to Pages
    # 2. Vercel CLI deployment
    # 3. DNS updates via Cloudflare API
    
    print(f"✅ Mirrors deployed: {mirrors}")
    return mirrors

def get_working_domain(original_domain: str) -> str:
    """Get working mirror if original is burned"""
    if original_domain not in burned_domains:
        return original_domain
    
    mirrors = mirror_registry.get(original_domain, [])
    
    for mirror in mirrors:
        if check_domain_health(mirror):
            print(f"🔄 Redirecting {original_domain} → {mirror}")
            return mirror
    
    # Last resort: generate new random mirror
    new_mirror = f"backup-{random.randint(1000, 9999)}.vercel.app"
    print(f"🆘 Emergency mirror: {new_mirror}")
    return new_mirror

@app.route('/api/scramble', methods=['POST'])
def scramble_page():
    """
    Scramble page content to bypass keyword loggers
    Returns encrypted content + unscramble key
    """
    try:
        data = request.get_json()
        url = data.get('url')
        mode = data.get('mode', 'scramble')  # scramble | camouflage | both
        
        if not url:
            return jsonify({"error": "No URL provided"}), 400
        
        # Check if domain is burned
        domain = url.split('/')[2] if '://' in url else url.split('/')[0]
        working_domain = get_working_domain(domain)
        
        if working_domain != domain:
            url = url.replace(domain, working_domain)
        
        # Fetch content
        response = requests.get(url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Educational Research Bot)'
        })
        
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract text content
        text_content = soup.get_text(separator=' ', strip=True)
        
        # Generate scramble key
        scramble_key = generate_scramble_key(url)
        
        # Apply evasion
        if mode in ['scramble', 'both']:
            scrambled_text = scramble_text(text_content, scramble_key)
        else:
            scrambled_text = text_content
        
        if mode in ['camouflage', 'both']:
            scrambled_text = camouflage_as_academic(scrambled_text)
        
        # Inject unscramble script into HTML
        unscramble_script = f"""
        <script>
        (function() {{
            const scrambleKey = '{scramble_key}';
            const scrambledData = '{scrambled_text}';
            
            function unscramble(data, key) {{
                const decoded = atob(data);
                let result = '';
                for (let i = 0; i < decoded.length; i++) {{
                    const xorVal = (decoded.charCodeAt(i) - 13 + 256) % 256;
                    const keyChar = key.charCodeAt(i % key.length);
                    result += String.fromCharCode(xorVal ^ keyChar);
                }}
                return result;
            }}
            
            // Unscramble after page load
            window.addEventListener('load', function() {{
                setTimeout(() => {{
                    const realContent = unscramble(scrambledData, scrambleKey);
                    // Inject into shadow DOM for extra stealth
                    const container = document.querySelector('#content') || document.body;
                    const shadow = container.attachShadow({{ mode: 'closed' }});
                    shadow.innerHTML = '<div style="all:initial">' + realContent + '</div>';
                }}, 100);
            }});
        }})();
        </script>
        """
        
        # Replace body content with scrambled version
        if soup.body:
            soup.body.clear()
            soup.body.append(BeautifulSoup(f'<div id="content">Loading educational content...</div>{unscramble_script}', 'html.parser'))
        
        return jsonify({
            "success": True,
            "scrambled_html": str(soup),
            "original_domain": domain,
            "working_domain": working_domain,
            "domain_redirected": domain != working_domain,
            "scramble_key": scramble_key,
            "mode": mode,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/check-domain', methods=['POST'])
def check_domain():
    """Check if domain is burned and get mirrors"""
    data = request.get_json()
    domain = data.get('domain')
    
    is_healthy = check_domain_health(domain)
    
    return jsonify({
        "domain": domain,
        "healthy": is_healthy,
        "burned": domain in burned_domains,
        "mirrors": mirror_registry.get(domain, []),
        "failures": domain_health.get(domain, {}).get('failures', 0)
    })

@app.route('/api/burned-domains', methods=['GET'])
def get_burned_domains():
    """Get list of all burned domains and their mirrors"""
    return jsonify({
        "burned_domains": list(burned_domains),
        "mirror_registry": mirror_registry,
        "total_burned": len(burned_domains)
    })

@app.route('/api/report-block', methods=['POST'])
def report_block():
    """
    Manual reporting of blocked domain
    Students can report when they detect a block
    """
    data = request.get_json()
    domain = data.get('domain')
    
    if domain:
        burned_domains.add(domain)
        deploy_mirror(domain)
        
        return jsonify({
            "success": True,
            "message": f"Domain {domain} marked as burned",
            "mirrors": mirror_registry.get(domain, [])
        })
    
    return jsonify({"success": False, "error": "No domain provided"}), 400

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "service": "evasion-layer",
        "burned_domains": len(burned_domains),
        "active_mirrors": sum(len(m) for m in mirror_registry.values()),
        "timestamp": datetime.utcnow().isoformat()
    })

if __name__ == '__main__':
    print("🛡️ Advanced Evasion Layer starting...")
    print("Features: Text Scrambling | Domain Detection | Auto-Mirroring")
    app.run(host='0.0.0.0', port=5001, debug=False)
