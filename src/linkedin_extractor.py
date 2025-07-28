"""
LinkedIn profile image extractor module.

Provides multiple strategies for extracting profile images from LinkedIn profiles.
"""

import requests
import time
import re
import os
from typing import Optional, List
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import json
import logging

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options

    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False


class LinkedInImageExtractor:
    """Handles LinkedIn profile image extraction using multiple strategies."""

    def __init__(
        self,
        request_timeout: int = 15,
        retry_attempts: int = 3,
        cookies: Optional[str] = None,
    ):
        """
        Initialize LinkedIn image extractor.

        Args:
            request_timeout: Timeout for HTTP requests in seconds
            retry_attempts: Number of retry attempts for failed requests
            cookies: LinkedIn session cookies (string or file path)
        """
        self.request_timeout = request_timeout
        self.retry_attempts = retry_attempts
        self.ua = UserAgent()
        self.session = requests.Session()
        self.authenticated = False

        # Setup logging
        self.logger = logging.getLogger(__name__)

        # Load LinkedIn cookies if provided
        self._load_linkedin_cookies(cookies)

        # Common headers for requests
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

    def _load_linkedin_cookies(self, cookies: Optional[str]) -> None:
        """
        Load LinkedIn session cookies for authenticated requests.

        Args:
            cookies: Cookie string or file path containing cookies
        """
        if not cookies:
            return

        try:
            # Check if cookies is a file path
            if os.path.isfile(cookies):
                with open(cookies, "r", encoding="utf-8") as f:
                    cookie_content = f.read().strip()
            else:
                cookie_content = cookies.strip()

            if not cookie_content:
                return

            # Parse cookies and add to session
            self._parse_and_set_cookies(cookie_content)

            if self.authenticated:
                self.logger.info("LinkedIn session cookies loaded successfully")

        except Exception as e:
            self.logger.warning(f"Failed to load LinkedIn cookies: {e}")

    def _parse_and_set_cookies(self, cookie_string: str) -> None:
        """
        Parse cookie string and set them in the session.

        Args:
            cookie_string: Raw cookie string from browser
        """
        try:
            # Handle different cookie formats
            if "; " in cookie_string:
                # Format: "name1=value1; name2=value2"
                cookie_pairs = cookie_string.split("; ")
            elif "\n" in cookie_string:
                # Format: multi-line cookies
                cookie_pairs = [
                    line.strip() for line in cookie_string.split("\n") if "=" in line
                ]
            else:
                # Single cookie
                cookie_pairs = [cookie_string]

            linkedin_cookies = {}
            for pair in cookie_pairs:
                if "=" in pair:
                    name, value = pair.split("=", 1)
                    name = name.strip()
                    value = value.strip()

                    # Only add LinkedIn-related cookies
                    if any(
                        keyword in name.lower()
                        for keyword in [
                            "li_",
                            "linkedin",
                            "jsessionid",
                            "bcookie",
                            "bscookie",
                        ]
                    ):
                        linkedin_cookies[name] = value

            if linkedin_cookies:
                # Set cookies for LinkedIn domain
                for name, value in linkedin_cookies.items():
                    self.session.cookies.set(name, value, domain=".linkedin.com")

                self.authenticated = True
                self.logger.debug(f"Set {len(linkedin_cookies)} LinkedIn cookies")
            else:
                self.logger.warning(
                    "No valid LinkedIn cookies found in provided string"
                )

        except Exception as e:
            self.logger.error(f"Error parsing cookies: {e}")

    def is_authenticated(self) -> bool:
        """
        Check if the extractor has valid LinkedIn authentication.

        Returns:
            True if authenticated, False otherwise
        """
        return self.authenticated

    def test_authentication(self) -> bool:
        """
        Test if the current authentication is working.

        Returns:
            True if authentication is valid, False otherwise
        """
        if not self.authenticated:
            return False

        try:
            # Test with a simple LinkedIn request
            response = self.session.get(
                "https://www.linkedin.com/feed/",
                headers=self.headers,
                timeout=self.request_timeout,
                allow_redirects=False,
            )

            # If we get redirected to login, authentication failed
            if response.status_code == 302 and "login" in response.headers.get(
                "Location", ""
            ):
                self.authenticated = False
                return False

            # If we get a successful response, authentication is working
            return response.status_code == 200

        except Exception as e:
            self.logger.warning(f"Authentication test failed: {e}")
            return False

    def normalize_linkedin_url(self, linkedin_url: str) -> str:
        """
        Normalize LinkedIn URL to ensure it has proper scheme and format.

        Args:
            linkedin_url: Raw LinkedIn URL

        Returns:
            Normalized LinkedIn URL with https:// scheme
        """
        if not linkedin_url:
            return linkedin_url

        # Remove any leading/trailing whitespace
        url = linkedin_url.strip()

        # If URL already has a scheme, return as-is
        if url.startswith(("http://", "https://")):
            return url

        # If URL starts with linkedin.com or www.linkedin.com, add https://
        if url.startswith(("linkedin.com", "www.linkedin.com")):
            return f"https://{url}"

        # If it looks like a LinkedIn profile path, construct full URL
        if "/in/" in url and not url.startswith("http"):
            # Handle cases like "linkedin.com/in/profile" or "www.linkedin.com/in/profile"
            if url.startswith("linkedin.com"):
                return f"https://{url}"
            elif url.startswith("www.linkedin.com"):
                return f"https://{url}"
            else:
                # Assume it's just the path part
                return f'https://www.linkedin.com{url if url.startswith("/") else "/" + url}'

        # If we can't determine the format, assume it needs https://
        return f"https://{url}" if not url.startswith("http") else url

    def extract_profile_image_url(self, linkedin_url: str) -> Optional[str]:
        """
        Extract profile image URL from LinkedIn profile using multiple strategies.

        Args:
            linkedin_url: LinkedIn profile URL

        Returns:
            Image URL if found, None otherwise
        """
        normalized_url = self.normalize_linkedin_url(linkedin_url)

        if not normalized_url:
            return None

        # Strategy 1: Try requests with BeautifulSoup
        image_url = self._extract_with_requests(normalized_url)
        if image_url:
            return image_url

        # Strategy 2: Try with different user agents
        image_url = self._extract_with_rotating_agents(normalized_url)
        if image_url:
            return image_url

        # Strategy 3: Try Selenium if available
        if SELENIUM_AVAILABLE:
            image_url = self._extract_with_selenium(normalized_url)
            if image_url:
                return image_url

        # Strategy 4: Try to construct image URL from profile ID
        image_url = self._construct_image_url_from_profile(normalized_url)
        if image_url:
            return image_url

        return None

    def _extract_with_requests(self, url: str) -> Optional[str]:
        """
        Extract image URL using requests and BeautifulSoup.

        Args:
            url: LinkedIn profile URL

        Returns:
            Image URL if found, None otherwise
        """
        try:
            headers = self.headers.copy()
            headers["User-Agent"] = self.ua.random

            for attempt in range(self.retry_attempts):
                try:
                    response = self.session.get(
                        url,
                        headers=headers,
                        timeout=self.request_timeout,
                        allow_redirects=True,
                    )

                    if response.status_code == 200:
                        return self._parse_html_for_image(response.text)
                    elif response.status_code == 429:
                        # Rate limited, wait and retry
                        time.sleep(2**attempt)
                        continue
                    elif response.status_code == 999:
                        # LinkedIn's "Request denied" - expected anti-scraping response
                        self.logger.debug(
                            f"LinkedIn blocked request (HTTP 999) for {url}"
                        )
                        break  # No point retrying, LinkedIn is actively blocking
                    else:
                        self.logger.debug(f"HTTP {response.status_code} for {url}")

                except requests.exceptions.Timeout:
                    self.logger.warning(f"Timeout on attempt {attempt + 1} for {url}")
                    if attempt < self.retry_attempts - 1:
                        time.sleep(1)
                        continue
                except requests.exceptions.RequestException as e:
                    self.logger.warning(
                        f"Request error on attempt {attempt + 1} for {url}: {e}"
                    )
                    if attempt < self.retry_attempts - 1:
                        time.sleep(1)
                        continue

        except Exception as e:
            self.logger.error(f"Error in _extract_with_requests for {url}: {e}")

        return None

    def _extract_with_rotating_agents(self, url: str) -> Optional[str]:
        """
        Extract image URL using different user agents.

        Args:
            url: LinkedIn profile URL

        Returns:
            Image URL if found, None otherwise
        """
        user_agents = [
            (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
            (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
            (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
        ]

        for user_agent in user_agents:
            try:
                headers = self.headers.copy()
                headers["User-Agent"] = user_agent

                response = self.session.get(
                    url,
                    headers=headers,
                    timeout=self.request_timeout,
                    allow_redirects=True,
                )

                if response.status_code == 200:
                    image_url = self._parse_html_for_image(response.text)
                    if image_url:
                        return image_url

                # Small delay between attempts
                time.sleep(0.5)

            except Exception as e:
                self.logger.warning(f"Error with user agent {user_agent}: {e}")
                continue

        return None

    def _extract_with_selenium(self, url: str) -> Optional[str]:
        """
        Extract image URL using Selenium WebDriver.

        Args:
            url: LinkedIn profile URL

        Returns:
            Image URL if found, None otherwise
        """
        if not SELENIUM_AVAILABLE:
            return None

        driver = None
        try:
            # Setup Chrome options
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument(f"--user-agent={self.ua.random}")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option(
                "excludeSwitches", ["enable-automation"]
            )
            chrome_options.add_experimental_option("useAutomationExtension", False)

            # Initialize driver
            driver = webdriver.Chrome(options=chrome_options)
            driver.execute_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )

            # First, navigate to LinkedIn to set the domain context
            driver.get("https://www.linkedin.com")
            
            # Transfer cookies from requests session to Selenium
            if self.authenticated and self.session.cookies:
                self.logger.debug("Transferring cookies from requests session to Selenium")
                for cookie in self.session.cookies:
                    if 'linkedin.com' in cookie.domain:
                        try:
                            # Convert requests cookie to Selenium cookie format
                            selenium_cookie = {
                                'name': cookie.name,
                                'value': cookie.value,
                                'domain': cookie.domain,
                                'path': cookie.path or '/',
                                'secure': cookie.secure or False,
                            }
                            # Only add expiry if it exists and is valid
                            if cookie.expires:
                                selenium_cookie['expiry'] = int(cookie.expires)
                            
                            driver.add_cookie(selenium_cookie)
                            self.logger.debug(f"Added cookie: {cookie.name}")
                        except Exception as e:
                            self.logger.warning(f"Failed to add cookie {cookie.name}: {e}")

            # Now load the actual profile page with cookies
            driver.get(url)

            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # Try multiple selectors for profile images
            selectors = [
                'img[data-ghost-classes*="profile-photo"]',
                "img.profile-photo-edit__preview",
                "img.pv-top-card-profile-picture__image",
                "img.profile-photo",
                'img[alt*="profile photo"]',
                'img[alt*="Profile photo"]',
                ".pv-top-card__photo img",
                ".profile-photo-edit__preview",
                "button.profile-photo-edit__edit-btn img",
            ]

            for selector in selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        src = element.get_attribute("src")
                        if src and self._is_valid_profile_image_url(src):
                            return src
                except Exception:
                    continue

            # Try to find images in the page source
            page_source = driver.page_source
            return self._parse_html_for_image(page_source)

        except Exception as e:
            self.logger.error(f"Selenium error for {url}: {e}")
            return None
        finally:
            if driver:
                try:
                    driver.quit()
                except Exception:
                    pass

    def _parse_html_for_image(self, html_content: str) -> Optional[str]:
        """
        Parse HTML content to find profile image URLs.

        Args:
            html_content: HTML content to parse

        Returns:
            Image URL if found, None otherwise
        """
        try:
            soup = BeautifulSoup(html_content, "lxml")

            # Strategy 1: Look for JSON-LD structured data
            json_scripts = soup.find_all("script", type="application/ld+json")
            for script in json_scripts:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict) and "image" in data:
                        image_url = data["image"]
                        if isinstance(
                            image_url, str
                        ) and self._is_valid_profile_image_url(image_url):
                            return image_url
                except (json.JSONDecodeError, TypeError):
                    continue

            # Strategy 2: Look for meta tags
            meta_selectors = [
                'meta[property="og:image"]',
                'meta[name="twitter:image"]',
                'meta[property="og:image:secure_url"]',
            ]

            for selector in meta_selectors:
                meta_tag = soup.select_one(selector)
                if meta_tag and meta_tag.get("content"):
                    image_url = meta_tag["content"]
                    if self._is_valid_profile_image_url(image_url):
                        return image_url

            # Strategy 3: Look for profile image elements
            img_selectors = [
                'img[data-ghost-classes*="profile-photo"]',
                "img.profile-photo-edit__preview",
                "img.pv-top-card-profile-picture__image",
                "img.profile-photo",
                'img[alt*="profile photo" i]',
                'img[alt*="Profile photo" i]',
                ".pv-top-card__photo img",
                ".profile-photo-edit__preview",
            ]

            for selector in img_selectors:
                img_elements = soup.select(selector)
                for img in img_elements:
                    src = img.get("src") or img.get("data-src")
                    if src and self._is_valid_profile_image_url(src):
                        return src

            # Strategy 4: Regex patterns for image URLs in script tags
            script_tags = soup.find_all("script")
            for script in script_tags:
                if script.string:
                    image_url = self._extract_image_from_script(script.string)
                    if image_url:
                        return image_url

        except Exception as e:
            self.logger.error(f"Error parsing HTML: {e}")

        return None

    def _extract_image_from_script(self, script_content: str) -> Optional[str]:
        """
        Extract image URL from script content using regex patterns.

        Args:
            script_content: JavaScript content to search

        Returns:
            Image URL if found, None otherwise
        """
        patterns = [
            r'"profilePicture":"([^"]+)"',
            r'"profile_picture":"([^"]+)"',
            r'"profilePhoto":"([^"]+)"',
            r'"profile_photo":"([^"]+)"',
            r'"image":"(https://media\.licdn\.com/[^"]+)"',
            r'"picture":"(https://media\.licdn\.com/[^"]+)"',
            r'profilePicture:\s*"([^"]+)"',
            r'profile_picture:\s*"([^"]+)"',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, script_content)
            for match in matches:
                if self._is_valid_profile_image_url(match):
                    return match

        return None

    def _construct_image_url_from_profile(self, profile_url: str) -> Optional[str]:
        """
        Try to construct image URL from profile URL patterns.

        Args:
            profile_url: LinkedIn profile URL

        Returns:
            Constructed image URL if possible, None otherwise
        """
        try:
            # Extract profile identifier from URL
            match = re.search(r"/in/([^/?]+)", profile_url)
            if not match:
                return None

            profile_id = match.group(1)

            # Try common LinkedIn image URL patterns
            # Note: These patterns may change over time
            base_url = "https://media.licdn.com/dms/image"
            suffix = "profile-displayphoto-shrink_800_800/0/"
            patterns = [
                f"{base_url}/C4D03AQH{profile_id}/{suffix}",
                f"{base_url}/C5603AQH{profile_id}/{suffix}",
                f"{base_url}/D4D03AQH{profile_id}/{suffix}",
                f"{base_url}/D5603AQH{profile_id}/{suffix}",
            ]

            for pattern in patterns:
                if self._test_image_url(pattern):
                    return pattern

        except Exception as e:
            self.logger.error(f"Error constructing image URL: {e}")

        return None

    def _is_valid_profile_image_url(self, url: str) -> bool:
        """
        Check if URL appears to be a valid LinkedIn profile image.

        Args:
            url: Image URL to validate

        Returns:
            True if URL appears valid, False otherwise
        """
        if not url or not isinstance(url, str):
            return False

        # Must be a valid URL
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return False
        except Exception:
            return False

        # Should be from LinkedIn's media domain
        if "media.licdn.com" not in url and "media-exp" not in url:
            return False

        # Should not be a default/placeholder image
        exclude_patterns = [
            "ghost-person",
            "default-profile",
            "placeholder",
            "anonymous",
            "no-photo",
        ]

        url_lower = url.lower()
        for pattern in exclude_patterns:
            if pattern in url_lower:
                return False

        # Should be an image file
        image_extensions = [".jpg", ".jpeg", ".png", ".webp"]
        if not any(ext in url_lower for ext in image_extensions):
            # LinkedIn images might not have extensions, so this is not a hard requirement
            pass

        return True

    def _test_image_url(self, url: str) -> bool:
        """
        Test if an image URL is accessible.

        Args:
            url: Image URL to test

        Returns:
            True if accessible, False otherwise
        """
        try:
            response = requests.head(url, timeout=5)
            return response.status_code == 200
        except Exception:
            return False

    def get_extraction_strategies(self) -> List[str]:
        """
        Get list of available extraction strategies.

        Returns:
            List of strategy names
        """
        strategies = [
            "requests_beautifulsoup",
            "rotating_user_agents",
            "profile_url_construction",
        ]

        if SELENIUM_AVAILABLE:
            strategies.append("selenium_webdriver")

        return strategies

    def close(self):
        """Close the session and cleanup resources."""
        if hasattr(self, "session"):
            self.session.close()
