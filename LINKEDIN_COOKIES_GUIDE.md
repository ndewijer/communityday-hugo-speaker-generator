# LinkedIn Session Cookies Guide

This guide explains how to extract LinkedIn session cookies to improve the success rate of profile image extraction.

## ⚠️ Important Security Notes

- **Never share your LinkedIn cookies** - they provide access to your account
- **Cookies expire** - you'll need to refresh them periodically (usually every few weeks)
- **Use at your own risk** - this is for legitimate use cases only
- **Respect LinkedIn's Terms of Service** - only use for appropriate purposes

## Why Use Session Cookies?

LinkedIn heavily blocks anonymous scraping attempts, resulting in ~5% success rates. With valid session cookies, success rates can improve to 70-90% because:

- LinkedIn recognizes you as a logged-in user
- Anti-bot measures are less aggressive
- You can access more profile information
- Rate limiting is more lenient

## Method 1: Extract Cookies from Chrome

### Step 1: Log into LinkedIn
1. Open Chrome and go to [linkedin.com](https://linkedin.com)
2. Log into your LinkedIn account
3. Navigate to any LinkedIn profile to ensure you're fully logged in

### Step 2: Open Developer Tools
1. Press `F12` or right-click and select "Inspect"
2. Go to the **Application** tab
3. In the left sidebar, expand **Cookies**
4. Click on **https://www.linkedin.com**

### Step 3: Copy Important Cookies
Look for and copy these essential cookies (copy the **Value** column):

**Required cookies:**
- `li_at` - Main authentication token
- `JSESSIONID` - Session identifier
- `bcookie` - Browser cookie
- `bscookie` - Browser session cookie

**Optional but helpful:**
- `li_mc` - Member context
- `liap` - LinkedIn application
- `lms_ads` - LinkedIn marketing
- `lms_analytics` - Analytics tracking

### Step 4: Format the Cookie String
Combine all cookies in this format:
```
li_at=VALUE1; JSESSIONID=VALUE2; bcookie=VALUE3; bscookie=VALUE4; li_mc=VALUE5
```

**Example:**
```
li_at=AQEDATEwNzY4NjQwAAABjK...; JSESSIONID="ajax:1234567890"; bcookie="v=2&12345678-1234-1234-1234-123456789012"; bscookie="v=1&202401011200..."; li_mc=MTsyMTs0NjsyMDs...
```

## Method 2: Extract Cookies from Firefox

### Step 1: Log into LinkedIn
1. Open Firefox and go to [linkedin.com](https://linkedin.com)
2. Log into your LinkedIn account

### Step 2: Open Developer Tools
1. Press `F12` or right-click and select "Inspect Element"
2. Go to the **Storage** tab
3. Expand **Cookies** in the left sidebar
4. Click on **https://www.linkedin.com**

### Step 3: Copy Cookies
Follow the same process as Chrome to copy the essential cookies and format them.

## Method 3: Extract Cookies from Safari

### Step 1: Enable Developer Tools
1. Go to Safari → Preferences → Advanced
2. Check "Show Develop menu in menu bar"

### Step 2: Log into LinkedIn and Extract Cookies
1. Log into LinkedIn
2. Go to Develop → Show Web Inspector
3. Go to **Storage** tab → **Cookies** → **linkedin.com**
4. Copy the essential cookies as described above

## Method 4: Using Browser Extensions

### Cookie Editor Extensions
You can use browser extensions like:
- **Cookie Editor** (Chrome/Firefox)
- **EditThisCookie** (Chrome)

These extensions can export cookies in various formats, making it easier to copy them.

## How to Use the Cookies

### Option 1: Environment Variable
Set the cookies as an environment variable:

**Linux/macOS:**
```bash
export LINKEDIN_COOKIES="li_at=VALUE1; JSESSIONID=VALUE2; bcookie=VALUE3..."
```

**Windows:**
```cmd
set LINKEDIN_COOKIES=li_at=VALUE1; JSESSIONID=VALUE2; bcookie=VALUE3...
```

### Option 2: Create a Cookies File
Create a file named `linkedin_cookies.txt` in the project root:

```
li_at=AQEDATEwNzY4NjQwAAABjK...; JSESSIONID="ajax:1234567890"; bcookie="v=2&12345678-1234-1234-1234-123456789012"; bscookie="v=1&202401011200..."; li_mc=MTsyMTs0NjsyMDs...
```

### Option 3: Configuration File
Edit `src/config.py` and set:

```python
LINKEDIN_SESSION_COOKIES = "li_at=VALUE1; JSESSIONID=VALUE2; bcookie=VALUE3..."
```

## Testing Your Cookies

Run the test script to verify your cookies work:

```bash
python test_linkedin_extractor.py
```

If authentication is working, you should see:
```
✓ Enhanced LinkedIn extractor loaded with authentication
```

## Troubleshooting

### Common Issues

**1. "Authentication failed" message**
- Cookies may be expired - extract fresh ones
- Make sure you copied all essential cookies
- Check that cookie format is correct (semicolon-separated)

**2. Still getting HTTP 999 errors**
- LinkedIn may be rate limiting - try with delays
- Your account may be flagged - try from a different account
- Cookies may be invalid - re-extract them

**3. Cookies not being loaded**
- Check file path for `linkedin_cookies.txt`
- Verify environment variable is set correctly
- Ensure no extra spaces or characters in cookie string

### Cookie Expiration

LinkedIn cookies typically expire after:
- **2-4 weeks** for regular sessions
- **Shorter periods** if LinkedIn detects unusual activity
- **Immediately** if you log out or change password

**Signs your cookies have expired:**
- Authentication test fails
- Getting redirected to login pages
- HTTP 302 responses to LinkedIn URLs

### Refreshing Cookies

When cookies expire:
1. Log into LinkedIn again in your browser
2. Extract fresh cookies using the same method
3. Update your configuration with the new cookies
4. Test the authentication again

## Security Best Practices

### Do:
- ✅ Use cookies only for legitimate purposes
- ✅ Keep cookies private and secure
- ✅ Refresh cookies regularly
- ✅ Use a dedicated LinkedIn account if possible
- ✅ Monitor for unusual account activity

### Don't:
- ❌ Share cookies with others
- ❌ Use cookies for spam or harassment
- ❌ Store cookies in version control
- ❌ Use cookies from compromised accounts
- ❌ Violate LinkedIn's Terms of Service

## Legal and Ethical Considerations

- **Respect Privacy**: Only extract images for legitimate purposes
- **Follow Terms of Service**: Ensure compliance with LinkedIn's ToS
- **Rate Limiting**: Don't make excessive requests
- **Data Protection**: Handle extracted data responsibly
- **Professional Use**: Use for conference speakers, team directories, etc.

## Example Usage

Once configured, the system will automatically use authentication:

```bash
# Run with authentication
python main.py

# Expected output:
# ✓ Enhanced LinkedIn extractor loaded with authentication
# 🔄 Retrying 8 previous LinkedIn failures...
# ✅ Retry successful!
# 🎉 Successfully recovered 6 images from previous failures!
```

## Support

If you encounter issues:

1. **Check the troubleshooting section** above
2. **Verify cookie format** - ensure proper semicolon separation
3. **Test with fresh cookies** - extract new ones from browser
4. **Check LinkedIn account status** - ensure account is in good standing

Remember: This feature is designed to improve legitimate use cases like conference speaker directories. Always respect LinkedIn's terms of service and user privacy.
