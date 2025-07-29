# LinkedIn Selenium Extractor Guide

This guide explains how to use the new Selenium-based LinkedIn profile image extraction system.

## 🚀 Overview

The LinkedIn Selenium Extractor provides reliable LinkedIn profile image extraction using:
- **One-time interactive login** - User-friendly browser-based authentication
- **Persistent sessions** - Login once, use forever (until session expires)
- **Direct DOM access** - More reliable than regex-based extraction
- **Rate limiting** - Respects LinkedIn's usage policies
- **Headless operation** - Runs in background after initial setup

## 📋 Prerequisites

### 1. Install Selenium Dependencies
```bash
pip install -r requirements-selenium.txt
```

### 2. Install ChromeDriver
The system requires ChromeDriver to be installed and available in your PATH.

**macOS (using Homebrew):**
```bash
brew install chromedriver
```

**Ubuntu/Debian:**
```bash
sudo apt-get install chromium-chromedriver
```

**Windows:**
1. Download ChromeDriver from https://chromedriver.chromium.org/
2. Add the executable to your PATH

### 3. Verify Installation
```bash
chromedriver --version
```

## 🔐 First-Time Setup

### 1. Run the Generator
```bash
python main.py
```

### 2. LinkedIn Login Process
When you first run the system, you'll see:

```
🚀 We'll open LinkedIn for you to log in. This is a one-time process. 🔐
Press Enter to continue and come back here once you've logged in... 😊
```

1. **Press Enter** - A Chrome browser window will open
2. **Log in to LinkedIn** - Use your normal LinkedIn credentials
3. **Complete any 2FA** - If you have two-factor authentication enabled
4. **Return to terminal** - Press Enter again when logged in
5. **Verification** - The system will verify your login was successful

```
✅ Credentials saved! You're all set for future use. 🎉
```

### 3. Future Runs
After the initial setup, the system will automatically use your saved session:

```
✅ Existing LinkedIn session found
```

## 🎯 Usage

### Basic Usage
```bash
python main.py
```

### Force Regeneration
```bash
python main.py --force
```

## 🔧 Configuration

The LinkedIn extractor can be configured in `src/config.py`:

```python
# LinkedIn Selenium Configuration
SELENIUM_USER_DATA_DIR = ".selenium"  # Directory for browser session data
LINKEDIN_REQUEST_DELAY = 2.5  # Delay between LinkedIn requests (seconds)
```

### Rate Limiting
The system includes built-in rate limiting to respect LinkedIn's usage policies:
- **2.5 seconds** between profile requests (configurable)
- **Exponential backoff** on errors
- **Session verification** before batch processing

## 🛠️ Troubleshooting

### ChromeDriver Issues
```
❌ Failed to create Chrome driver: Message: 'chromedriver' executable needs to be in PATH
```

**Solution:** Install ChromeDriver (see Prerequisites above)

### Login Verification Failed
```
❌ Login verification failed. Please ensure you're logged in.
```

**Solutions:**
1. Make sure you're fully logged in to LinkedIn
2. Complete any security challenges (2FA, captcha)
3. Try refreshing the LinkedIn page before pressing Enter
4. Check if LinkedIn is asking for additional verification

### Session Expired
```
❌ LinkedIn session expired. Please run login again.
```

**Solution:** The system will automatically prompt for re-login when needed.

### Permission Denied
```
❌ Permission denied: Cannot access .selenium directory
```

**Solution:** Check file permissions or run with appropriate privileges.

## 📊 Performance

### Expected Results
- **Success Rate:** ~90% for public LinkedIn profiles
- **Speed:** ~2.5 seconds per profile (with rate limiting)
- **Reliability:** Direct DOM access vs regex patterns

### Optimization Tips
1. **Batch Processing:** Process multiple speakers at once
2. **Skip Logic:** Use existing files to avoid re-processing
3. **Rate Limiting:** Adjust `LINKEDIN_REQUEST_DELAY` if needed
4. **Session Management:** Login persists across runs

## 🔒 Privacy & Security

### Data Storage
- **Session Data:** Stored in `.selenium/` directory (gitignored)
- **No Passwords:** Only browser session cookies are stored
- **Local Only:** All data remains on your machine

### LinkedIn Compliance
- **Rate Limited:** Respects LinkedIn's usage policies
- **User Agent:** Uses standard browser user agent
- **Session-Based:** Uses normal browser authentication

## 🆘 Fallback Options

### If Selenium Unavailable
The system automatically falls back to basic extraction:

```
⚠️  Selenium LinkedIn extractor not available
💡 Install with: pip install -r requirements-selenium.txt
```

### Manual Image URLs
You can always provide custom photo URLs in your Excel data:
- Add a `custom_photo_url` column
- The system will use custom URLs before trying LinkedIn

## 🔄 Migration from Cookie-Based System

If you were using the old cookie-based system:

1. **Remove old files:**
   - `linkedin_cookies.txt` (if exists)
   - Any manual cookie configurations

2. **Run new system:**
   ```bash
   python main.py
   ```

3. **Complete login setup** as described above

The new system is more reliable and user-friendly than the previous cookie-based approach.

## 📞 Support

### Common Issues
1. **ChromeDriver not found** → Install ChromeDriver
2. **Login fails** → Complete all LinkedIn security steps
3. **Session expires** → System will prompt for re-login
4. **Rate limiting** → Adjust delay in config if needed

### Debug Mode
For detailed debugging, check the debug scripts in the `debug/` folder:
- `debug/test_linkedin_extractor.py` - Test the extractor directly
- `debug/debug_linkedin_html.py` - Analyze LinkedIn HTML content

### Getting Help
If you encounter issues:
1. Check this guide first
2. Verify ChromeDriver installation
3. Try the debug scripts
4. Check the console output for specific error messages
