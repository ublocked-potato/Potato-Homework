# 🥔 OmniSearch - Site Compatibility Guide

## What Works & What Doesn't

This guide explains which websites work well through the proxy and which require the "Visit Real Site" button.

---

## ✅ **Works Great in Proxy**

These sites work perfectly through the Python proxy:

### News & Information
- ✅ **Wikipedia** - Full functionality
- ✅ **Reddit** - Reading posts (commenting needs real site)
- ✅ **BBC News** - Articles load perfectly
- ✅ **CNN, Fox News** - News sites work well
- ✅ **Medium** - Articles readable
- ✅ **Stack Overflow** - Reading Q&A works

### Educational
- ✅ **Khan Academy** - Most content (videos may lag)
- ✅ **Coursera** - Reading materials
- ✅ **Quizlet** - Flash cards work
- ✅ **Archive.org** - Full text archives

### Shopping/Reference
- ✅ **Amazon** - Browsing products (can't checkout)
- ✅ **eBay** - Product viewing
- ✅ **IMDB** - Movie information
- ✅ **Yelp** - Restaurant reviews

### Simple Web Tools
- ✅ **Pastebin** - Text sharing
- ✅ **GitHub** (viewing) - Code repositories
- ✅ **Wolfram Alpha** - Calculations

---

## ⚠️ **Partial Functionality**

These sites load but with limitations:

### Social Media
- ⚠️ **Twitter/X** - Can read, but posting doesn't work
- ⚠️ **Instagram** - View public profiles, can't interact
- ⚠️ **Facebook** - View public pages only
- ⚠️ **LinkedIn** - Profile viewing only

**Why Limited:** Need real-time APIs, authentication, and WebSocket connections

### Video Sites
- ⚠️ **YouTube** - Page loads but videos often don't play
- ⚠️ **Vimeo** - Similar issues
- ⚠️ **Dailymotion** - Video player may fail

**Why Limited:** DRM protection, streaming protocols, embedded players

**Solution:** Use "Visit Real Site" button for full experience

---

## ❌ **Doesn't Work (Use "Visit Real Site")**

These sites require the real site due to technical limitations:

### AI & Chat Services
- ❌ **ChatGPT** - Requires WebSocket & OpenAI API
- ❌ **Perplexity AI** - Real-time AI responses need direct connection
- ❌ **Claude.ai** - Same websocket requirement
- ❌ **Bing Chat** - Integrated AI features

**Why:** WebSocket connections for real-time AI responses can't be proxied

**Auto-Detection:** System shows warning + "Visit Real Site" button

### Gaming Sites
- ❌ **Poki.com** - Games use Canvas/WebGL
- ❌ **CrazyGames** - Similar gaming platform
- ❌ **Miniclip** - Flash/HTML5 games
- ❌ **Roblox** - 3D gaming platform
- ❌ **Krunker.io** - WebGL multiplayer games

**Why:** 
- Canvas/WebGL rendering issues
- Game assets need direct loading
- Multiplayer requires WebSocket
- Performance issues with proxy overhead

**Auto-Detection:** System detects Poki and shows warning

### Streaming & Entertainment
- ❌ **Netflix** - DRM + video streaming
- ❌ **Disney+** - DRM protection
- ❌ **Hulu** - Streaming DRM
- ❌ **Twitch** - Live streaming + WebRTC
- ❌ **Spotify Web** - Audio streaming APIs

**Why:** DRM (Digital Rights Management) + streaming protocols

### Communication
- ❌ **Discord** - WebRTC for voice/video
- ❌ **Zoom** - WebRTC requirements
- ❌ **Google Meet** - Video conferencing
- ❌ **Slack** - Real-time messaging

**Why:** WebRTC, WebSocket, real-time protocols

### Banking & Secure Sites
- ❌ **Any Banking Site** - Security certificates
- ❌ **PayPal** - SSL pinning
- ❌ **Crypto Exchanges** - Security measures

**Why:** SSL certificate pinning, anti-proxy measures

**Note:** Never use proxies for banking/financial sites anyway!

---

## 🔍 **How the Detection Works**

The system automatically detects complex sites:

```python
complex_sites = [
    'chatgpt.com', 'openai.com', 'perplexity.ai',
    'poki.com', 'crazygames.com', 'miniclip.com',
    'youtube.com', 'netflix.com', 'twitch.tv',
    'discord.com', 'spotify.com', 'roblox.com'
]
```

When you try to access these, you'll see:
1. ⚠️ Warning page explaining why
2. 🌐 "Visit Real Site" button (opens in new tab)
3. Option to "Try Proxy Anyway" (usually won't work)
4. ← Back to search button

---

## 💡 **Tips for Best Experience**

### For Sites That Work:
- ✅ Use proxy for: News, Wikipedia, Reddit, research
- ✅ Great for: Avoiding content filters on educational sites
- ✅ Perfect for: Reading articles, viewing information

### For Complex Sites:
- 🌐 Click "Visit Real Site" button
- 🔒 Consider using a VPN for full privacy
- 📱 Use mobile apps when possible (often less restricted)

### For Gaming (Poki, etc.):
**Best Options:**
1. Click "Visit Real Site" - Opens Poki directly
2. Use VPN + Direct access
3. Mobile gaming apps
4. Download games instead of web-based

**Why Proxy Doesn't Work:**
```
Game needs:
- WebGL rendering (3D graphics)
- Canvas API (2D graphics)
- Fast asset loading
- Low latency
- Direct JavaScript execution

Proxy adds:
- Extra latency
- URL rewriting breaks asset paths
- iFrame restrictions
- No WebGL passthrough
```

---

## 🛠️ **Technical Explanation**

### Why Some Sites Work:
```
Simple Site:
HTML → CSS → Images → Text
         ↓
   Proxy rewrites URLs
         ↓
   Everything works!
```

### Why Complex Sites Don't:
```
Complex Site:
HTML → JavaScript → WebSocket → Real-time data
                        ↓
                   Can't proxy!
         
+ WebGL rendering
+ Canvas drawing
+ DRM decryption
+ WebRTC streams
         ↓
    Proxy fails
```

---

## 🎯 **Quick Reference Table**

| Site Type | Works? | Use Case |
|-----------|--------|----------|
| News Sites | ✅ Yes | Reading articles |
| Wikipedia | ✅ Yes | Research |
| Social (view) | ⚠️ Partial | Viewing posts |
| Social (post) | ❌ No | Need real site |
| YouTube | ⚠️ Maybe | Hit or miss |
| Gaming Sites | ❌ No | Use "Visit Real Site" |
| ChatGPT/AI | ❌ No | Use "Visit Real Site" |
| Streaming | ❌ No | DRM protected |
| Banking | ❌ Never | Security risk! |

---

## 🔄 **Workflow for Unknown Sites**

1. **Try searching** - See if it loads
2. **Check proxy** - Click result
3. **Auto-detection:**
   - ✅ Simple site: Loads in proxy
   - ⚠️ Complex site: Warning + "Visit Real Site" button
4. **If broken:** Click "Visit Real Site" button
5. **If works:** Enjoy!

---

## 📝 **Adding More Detections**

To add more auto-detected sites, edit `app.py`:

```python
complex_sites = [
    'chatgpt.com',
    'poki.com',
    'your-new-site.com'  # Add here
]
```

And `index.html`:

```javascript
const complexSites=[
    'chatgpt.com',
    'poki.com',
    'your-new-site.com'  // Add here
];
```

---

## 🥔 **Summary**

**Best Use Cases:**
- ✅ Educational research (Wikipedia, news)
- ✅ Bypassing content filters on simple sites
- ✅ Reading articles and documentation
- ✅ Viewing public social media

**Use "Visit Real Site" For:**
- 🎮 All gaming sites (Poki, etc.)
- 🤖 AI chat (ChatGPT, Perplexity)
- 📺 Video streaming (YouTube, Netflix)
- 💬 Real-time chat (Discord)
- 🎵 Music streaming (Spotify)

**Remember:** The "Visit Real Site" button opens in a new tab, so you're just one click away from the full experience!

---

**Last Updated:** January 2026  
**Version:** 3.1.0

🥔 **Pro Tip:** Bookmark the "Visit Real Site" links for sites you use frequently!
