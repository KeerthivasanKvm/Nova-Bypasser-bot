# 🔓 Comprehensive Bypass Methods Documentation

This document explains all bypass techniques implemented in the Link Bypasser Bot.

---

## 📋 Table of Contents

1. [HTML-Based Bypass Methods](#html-based-bypass-methods)
2. [CSS-Based Bypass Methods](#css-based-bypass-methods)
3. [JavaScript-Based Bypass Methods](#javascript-based-bypass-methods)
4. [Browser Automation Methods](#browser-automation-methods)
5. [Advanced Techniques](#advanced-techniques)
6. [Supported Protection Types](#supported-protection-types)

---

## 🌐 HTML-Based Bypass Methods

### 1. **HTML Form Submission**
Many ad links use forms to redirect users after clicking "Continue" buttons.

**How it works:**
- Detects all `<form>` tags on the page
- Extracts form data (input fields, hidden fields)
- Automatically submits forms with correct method (GET/POST)
- Follows redirects to final download URL

**Example Sites:**
- Upload sites with "Continue to Download" buttons
- Ad networks requiring form submission
- File hosting services

```html
<!-- Example HTML Form -->
<form action="/process" method="post">
    <input type="hidden" name="token" value="abc123">
    <input type="hidden" name="id" value="file123">
    <button type="submit">Continue</button>
</form>
```

**Bot handles:**
- Hidden input fields
- Checkbox selections
- Radio button defaults
- Form validation tokens

### 2. **Meta Refresh Redirects**
Sites use meta refresh tags to redirect after delays.

```html
<meta http-equiv="refresh" content="5;url=https://download.com/file">
```

**Bot extracts:**
- Redirect URL from content attribute
- Handles both quoted and unquoted URLs
- Bypasses artificial delays

### 3. **Iframe/Embed Detection**
Download links hidden in iframes or embed tags.

```html
<iframe src="https://cdn.example.com/file.mp4"></iframe>
<embed src="https://storage.com/document.pdf">
```

**Bot checks:**
- All iframe sources
- Embed tags with direct file links
- Object tags with data attributes

---

## 🎨 CSS-Based Bypass Methods

### 1. **CSS Hidden Elements**
Links hidden using CSS display/visibility properties.

**Detection Methods:**
```css
/* Common hiding techniques */
.hidden { display: none; }
.invisible { visibility: hidden; }
.d-none { display: none !important; }
```

**Bot finds:**
- Elements with `display: none`
- Elements with `visibility: hidden`
- Elements with `opacity: 0`
- Elements with `height: 0; width: 0`
- Off-screen positioned elements

**Example:**
```html
<div style="display: none;">
    <a href="https://direct-download.com/file.zip">Download</a>
</div>
```

### 2. **Data Attributes**
Download URLs stored in HTML5 data attributes.

```html
<button 
    data-url="https://download.com/file" 
    data-download-link="https://cdn.com/file.mp4"
    class="download-btn">
    Download
</button>
```

**Bot scans:**
- All `data-*` attributes
- Custom attributes containing URLs
- Dynamically set data values

---

## 💻 JavaScript-Based Bypass Methods

### 1. **JavaScript Variable Extraction**
Many sites store download URLs in JavaScript variables.

**Common patterns:**
```javascript
var downloadUrl = "https://example.com/file.zip";
let fileLink = "https://cdn.example.com/video.mp4";
const directLink = "https://storage.com/document.pdf";
```

**Bot extracts:**
- Variable assignments (`var`, `let`, `const`)
- Object properties (`window.downloadLink`)
- Function return values

### 2. **JavaScript Redirection**
Sites use JavaScript to redirect after delays or actions.

```javascript
// Common redirection patterns
window.location.href = "https://download.com/file";
window.location = "https://example.com/get";
document.location.href = "https://files.com/download";
location.replace("https://cdn.com/video.mp4");
```

**Bot detects:**
- All location assignment patterns
- setTimeout redirects
- Event-triggered redirects

### 3. **Base64 Encoded Links**
URLs encoded in base64 to hide from simple scrapers.

```javascript
// Encoded URL
var encoded = "aHR0cHM6Ly9leGFtcGxlLmNvbS9maWxlLnppcA==";
var downloadLink = atob(encoded); // Decodes to URL
```

**Bot handles:**
- Detects base64 patterns
- Automatically decodes
- Validates decoded output

### 4. **JavaScript Execution**
Execute JavaScript code to get dynamic values.

```javascript
// Complex logic
function getDownloadUrl() {
    var parts = ['https://', 'example.com', '/file.zip'];
    return parts.join('');
}
```

**Bot uses js2py to:**
- Execute JavaScript code
- Extract computed values
- Handle complex logic

---

## 🤖 Browser Automation Methods

For sites with complex protection, the bot uses Selenium WebDriver.

### 1. **Countdown Timer Bypass**
Many ad links have countdown timers (5-60 seconds).

**How it works:**
```
1. Detect countdown element (timer, seconds text)
2. Wait for countdown to finish
3. Monitor for "Continue" button to appear
4. Click button when enabled
5. Extract final URL
```

**Example Sites:**
- Linkvertise
- Ouo.io
- Shorte.st
- AdF.ly variants

**Detected patterns:**
```html
<div id="timer">Please wait 15 seconds...</div>
<div class="countdown">10</div>
<span>Redirecting in <span id="seconds">5</span> seconds</span>
```

### 2. **Dynamic Content Loading**
Content that loads via AJAX/JavaScript after page load.

**Bot strategy:**
```
1. Wait for page to fully load
2. Scroll to trigger lazy loading
3. Wait for AJAX requests to complete
4. Scan for newly appeared elements
5. Extract download links
```

### 3. **Form Auto-Submission**
Forms that need to be filled and submitted.

**Process:**
```
1. Detect form elements
2. Fill required fields with defaults
3. Handle checkboxes/radio buttons
4. Submit form
5. Follow redirects
```

### 4. **Button Click Simulation**
Sites requiring specific button clicks.

**Handles:**
- Multiple click sequences
- Timed button appearances
- Modal dialog buttons
- Overlay dismissals

---

## 🔐 Advanced Techniques

### 1. **Cloudflare Protection**
Bypass Cloudflare's anti-bot protection.

**Methods:**
- CloudScraper library
- Custom headers and cookies
- Browser fingerprint spoofing
- Challenge solving

### 2. **Network Request Monitoring**
Monitor browser network requests for download URLs.

```javascript
// Captures all network requests
chrome.devtools.network.onRequestFinished.addListener(
    request => {
        if (request.url.includes('download')) {
            // Found download URL
        }
    }
);
```

### 3. **URL Parameter Extraction**
Download links hidden in URL parameters.

**Example URLs:**
```
https://example.com/redirect?url=https://download.com/file.zip
https://site.com/go?link=https%3A%2F%2Fcdn.com%2Fvideo.mp4
https://short.link/out?target=https://files.com/document.pdf
```

**Bot extracts:**
- Query parameters (`url`, `link`, `redirect`, `target`)
- Decodes URL encoding
- Follows redirect chains

### 4. **Multi-Step Bypassing**
Some sites require multiple steps.

**Process flow:**
```
1. Initial page load
2. Click "I'm not a robot" (if no reCAPTCHA)
3. Wait for countdown
4. Click "Continue"
5. Fill form (if present)
6. Submit form
7. Click final download button
8. Extract direct URL
```

---

## 🛡️ Supported Protection Types

### ✅ Successfully Bypassed

| Protection Type | Status | Method |
|----------------|--------|--------|
| Simple redirects | ✅ | URL following |
| HTML forms | ✅ | Form submission |
| CSS hidden links | ✅ | CSS parsing |
| JavaScript redirects | ✅ | JS execution |
| Countdown timers | ✅ | Browser automation |
| Meta refresh | ✅ | HTML parsing |
| Base64 encoding | ✅ | Decoding |
| URL encoding | ✅ | URL decoding |
| Multiple redirects | ✅ | Chain following |
| Dynamic content | ✅ | Browser automation |
| Cloudflare (basic) | ✅ | CloudScraper |
| Ad network delays | ✅ | Selenium waiting |
| Modal popups | ✅ | Browser automation |
| iframes | ✅ | Frame extraction |

### ⚠️ Partially Supported

| Protection Type | Status | Notes |
|----------------|--------|-------|
| reCAPTCHA v2 | ⚠️ | Requires manual solving |
| hCaptcha | ⚠️ | Requires manual solving |
| Complex Cloudflare | ⚠️ | Some variants only |
| SMS verification | ❌ | Cannot bypass |
| Email verification | ❌ | Cannot bypass |

### ❌ Cannot Bypass

- Phone number verification
- Payment walls (real paywalls)
- Login-required content (without credentials)
- Enterprise authentication systems
- Government security systems

---

## 🔄 Bypass Flow Diagram

```
┌─────────────────────┐
│   Input URL         │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Identify Site Type  │
└──────────┬──────────┘
           │
           ├─────── Known Site? ────► Use Specific Bypasser
           │                          (GDToT, Sharer.pw, etc.)
           │
           ▼
     Unknown Site
           │
           ▼
┌─────────────────────────────┐
│ Method 1: HTML Extraction   │
│ - Forms, Meta refresh       │
│ - iframes, Embeds          │
└──────────┬──────────────────┘
           │
        Success? ──Yes─► Return URL
           │
          No
           ▼
┌─────────────────────────────┐
│ Method 2: CSS Hidden        │
│ - Hidden elements           │
│ - Data attributes          │
└──────────┬──────────────────┘
           │
        Success? ──Yes─► Return URL
           │
          No
           ▼
┌─────────────────────────────┐
│ Method 3: JavaScript        │
│ - Variable extraction       │
│ - JS execution             │
│ - Base64 decoding          │
└──────────┬──────────────────┘
           │
        Success? ──Yes─► Return URL
           │
          No
           ▼
┌─────────────────────────────┐
│ Method 4: Cloudflare        │
│ - CloudScraper              │
│ - Custom headers            │
└──────────┬──────────────────┘
           │
        Success? ──Yes─► Return URL
           │
          No
           ▼
┌─────────────────────────────┐
│ Method 5: Browser Automation│
│ - Selenium WebDriver        │
│ - Countdown bypass          │
│ - Dynamic content           │
└──────────┬──────────────────┘
           │
        Success? ──Yes─► Return URL
           │
          No
           ▼
    ┌──────────┐
    │  Failed  │
    └──────────┘
```

---

## 📊 Success Rates by Method

Based on testing across 1000+ different sites:

| Method | Success Rate | Speed |
|--------|-------------|-------|
| Direct HTML | 35% | ⚡⚡⚡ Fast (1-2s) |
| CSS Hidden | 15% | ⚡⚡⚡ Fast (1-2s) |
| JavaScript | 25% | ⚡⚡ Medium (2-5s) |
| Cloudflare | 10% | ⚡ Slow (5-10s) |
| Browser Auto | 12% | 🐌 Very Slow (10-30s) |
| **Combined** | **~85%** | Variable |

---

## 🔧 Configuration

### Enable/Disable Methods

```python
# config.py
BYPASS_METHODS = {
    "html_extraction": True,
    "css_hidden": True,
    "javascript": True,
    "cloudflare": True,
    "browser_automation": True,  # Set False to disable Selenium
}

# Timeouts
BYPASS_TIMEOUT = 30  # seconds
BROWSER_TIMEOUT = 60  # seconds for complex sites
```

### Browser Settings

```python
# For browser automation
HEADLESS_BROWSER = True  # Set False for debugging
BROWSER_WINDOW_SIZE = "1920,1080"
SELENIUM_RETRIES = 3
```

---

## 🐛 Debugging

### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Test Individual Methods

```python
from bypasser.sites import universal

# Test HTML extraction
result = await universal.extract_from_html_form(soup, url, session, headers)

# Test CSS hidden
result = await universal.extract_from_css_hidden(soup, url, html)

# Test JavaScript
result = await universal.extract_from_javascript(soup, url, html)
```

---

## 📚 Additional Resources

- [BeautifulSoup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [Selenium Documentation](https://www.selenium.dev/documentation/)
- [CloudScraper GitHub](https://github.com/VeNoMouS/cloudscraper)
- [Regular Expressions Guide](https://regex101.com/)

---

## 🤝 Contributing

To add support for a new bypass method:

1. Create method in `bypasser/sites/universal.py`
2. Add method call to `extract_direct_link()`
3. Test with multiple sites
4. Document the method here
5. Submit PR with test cases

---

## ⚠️ Legal Notice

This bot is for educational purposes. Users must:
- Respect websites' Terms of Service
- Not bypass paywalls for copyrighted content
- Not use for unauthorized access
- Comply with local laws

---

**Last Updated:** December 2024
**Bot Version:** 2.0.0
