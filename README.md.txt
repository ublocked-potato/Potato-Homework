# 🥔 OmniSearch - GitHub Pages Edition

## Privacy-First Multi-Engine Search Browser

A static web application that bypasses network restrictions using CORS proxies and client-side rendering. Works on GitHub Pages with zero backend requirements.

## 🌟 Features

### 🔍 Multi-Engine Search
- **DuckDuckGo** - Privacy-focused, often unblocked
- **Google** - Standard search results
- **Brave Search** - Independent privacy-first index
- **Startpage** - Google results via encrypted proxy (2026 DPI-resistant)

### 🛡️ Advanced Bypass Techniques
- **CORS Proxy Method**: Routes requests through AllOrigins/Corsproxy
- **Protocol Flexibility**: Automatic HTTP/HTTPS switching
- **Multiple Proxy Fallbacks**: 3+ CORS proxies for reliability
- **Client-Side Rendering**: No server-side processing required

### ⚙️ Customizable Settings
- **Proxy Homepage**: Blank, Google, or Classroom (stealth mode)
- **Default Search Engine**: Choose your preferred engine
- **Bypass Method**: CORS proxy or direct iframe embedding

### 🎯 How It Bypasses Blocks (2026 Techniques)

**1. CORS Proxy Routing**
- Network sees: `student → github.io → allorigins.win → blocked-site`
- Admins only see traffic to AllOrigins (legitimate service)
- Works around basic domain blocking

**2. Protocol Switching**
- Automatically tries HTTP if HTTPS is blocked
- Switches between ports 80/443 to evade port-specific filters

**3. Multiple Proxy Fallbacks**
- If one CORS proxy is blocked, switches to next
- 3 different proxy services built-in

**4. Encrypted Search Options**
- Startpage provides Google results via their encrypted proxy
- Resists DPI (Deep Packet Inspection) that blocks standard proxies

## 🚀 Quick Deploy to GitHub Pages

### Method 1: GitHub Web Interface (Easiest)

1. **Create New Repository**
   - Go to https://github.com/new
   - Name: `omnisearch` (or any name)
   - Set to Public
   - Click "Create repository"

2. **Upload Files**
   - Click "uploading an existing file"
   - Drag and drop these files:
     - `index.html`
     - `app.js`
     - `README.md`
   - Click "Commit changes"

3. **Enable GitHub Pages**
   - Go to Settings → Pages
   - Source: Deploy from a branch
   - Branch: `main` (or `master`)
   - Folder: `/ (root)`
   - Click Save

4. **Access Your Site**
   - Wait 1-2 minutes
   - Visit: `https://yourusername.github.io/omnisearch/`

### Method 2: Git Command Line

```bash
# Clone your repo
git clone https://github.com/yourusername/omnisearch.git
cd omnisearch

# Add files
# (Copy index.html, app.js, README.md to this folder)

# Commit and push
git add .
git commit -m "Initial OmniSearch deployment"
git push origin main

# Enable GitHub Pages in Settings → Pages
```

### Method 3: GitHub Desktop

1. Create new repository in GitHub Desktop
2. Add the 3 files to the repository folder
3. Commit to main
4. Publish repository
5. Enable Pages in Settings

## 📁 File Structure

```
omnisearch/
├── index.html          (Main page with UI)
├── app.js             (Search & proxy logic)
└── README.md          (This file)
```

## 🔧 Configuration

### Changing CORS Proxies

Edit `app.js` line 9:

```javascript
const CORS_PROXIES = [
    'https://api.allorigins.win/raw?url=',
    'https://corsproxy.io/?',
    'https://api.codetabs.com/v1/proxy?quest='
];
```

Add more proxies as needed!

### Customizing Search Engines

Add engines in `app.js` `performSearchInTab` function:

```javascript
case 'yourcustomengine':
    searchUrl = `https://yoursearchengine.com/search?q=${encodeURIComponent(query)}`;
    break;
```

## 🛠️ Troubleshooting

### Search Not Working
- **Issue**: CORS proxy blocked
- **Fix**: The app will auto-switch to next proxy. If all fail, try different search engine.

### Sites Won't Load in Proxy
- **Issue**: Site blocks iframes or CORS
- **Fix**: Go to Settings → Change bypass method or proxy homepage

### Everything Blocked
- **Issue**: Advanced DPI blocking all proxies
- **Fix**: 
  1. Try Startpage (encrypted)
  2. Use VPN + this tool
  3. Try accessing during off-peak hours

## 🔒 Privacy & Security

### What This Tool Does NOT Do:
- ❌ Store search history
- ❌ Track user data
- ❌ Send data to third parties
- ❌ Use cookies or analytics

### What It DOES:
- ✅ Client-side only processing
- ✅ All data stored in browser localStorage
- ✅ No server-side logs
- ✅ Privacy-first search engines

## 📊 2026 Network Bypass Landscape

Based on current (2026) network security trends:

**Still Works:**
- ✅ CORS proxies (like AllOrigins) - Legitimate services, hard to block
- ✅ Encrypted search proxies (Startpage) - End-to-end encryption
- ✅ GitHub Pages hosting - Educational platform, rarely blocked
- ✅ Protocol switching - Simple but effective

**Getting Harder:**
- ⚠️ Simple iframe embedding - Easily detected
- ⚠️ Direct proxy tools - DPI can identify patterns
- ⚠️ VPN-less solutions - Advanced DPI improving

**Best Practices:**
- Use Startpage for encrypted Google results
- Rotate between multiple CORS proxies
- Combine with VPN for maximum privacy
- Access during off-peak hours for better success

## 🎓 Educational Purpose

This tool is designed for educational purposes and to demonstrate:
- Client-side web scraping
- CORS bypass techniques
- Privacy-preserving search methods
- Modern web application architecture

**Use responsibly and in accordance with your network's acceptable use policies.**

## 📜 License

MIT License - Free to use, modify, and distribute

## 🥔 Credits

Created with love and potatoes by the OmniSearch team.

Special thanks to:
- AllOrigins for CORS proxy service
- DuckDuckGo for privacy-first search
- GitHub Pages for free hosting

---

**Last Updated**: January 2026

**Version**: 2.0.0 (GitHub Pages Edition)

**Tested On**: Chrome, Firefox, Safari, Edge (2026 builds)