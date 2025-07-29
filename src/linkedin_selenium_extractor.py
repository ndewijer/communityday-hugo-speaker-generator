"""
Selenium-based LinkedIn image extractor for Hugo Speaker Generator.

Provides reliable LinkedIn profile image extraction using Selenium WebDriver
with persistent session management and one-time interactive login.
"""

import os
import sys
import time
import requests
from typing import List, Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from tqdm import tqdm


class LinkedInSeleniumExtractor:
    """Selenium-based LinkedIn profile image extractor."""

    def __init__(self, user_data_dir: str = ".selenium", request_delay: float = 2.5):
        """
        Initialize the LinkedIn Selenium extractor.

        Args:
            user_data_dir: Directory to store browser session data
            request_delay: Delay between requests to avoid rate limiting
        """
        self.user_data_dir = user_data_dir
        self.request_delay = request_delay
        self.driver = None

    def login_to_linkedin(self) -> bool:
        """
        Interactive one-time LinkedIn login setup.

        Returns:
            True if login successful, False otherwise
        """
        print(
            "🚀 We'll open LinkedIn for you to log in. This is a one-time process. 🔐"
        )
        print(
            "   💡 A Chrome browser window will open. Please log in and then return here."
        )
        input("Press Enter to continue... 😊")

        driver = None
        try:
            print("   🔧 Starting Chrome browser...")
            driver = self._create_driver(headless=False)
            self.driver = driver

            print("   🌐 Navigating to LinkedIn login page...")
            driver.get("https://www.linkedin.com/login")

            # Give the page time to load
            time.sleep(3)

            print("🖥️ LinkedIn login page should now be open in Chrome.")
            print("   📝 Please log in to LinkedIn in the browser window.")
            print("   🔐 Complete any 2FA or security challenges if prompted.")
            print("   ⏳ Take your time - the browser will stay open.")

            input(
                "\n✅ Press Enter here AFTER you have successfully logged in to LinkedIn... 😊"
            )

            print("   🔍 Verifying your login...")
            # Verify login success
            if self._verify_login_success(driver):
                print(
                    "✅ Login verified successfully! Credentials saved for future use. 🎉"
                )
                driver.quit()
                self.driver = None
                return True
            else:
                print("❌ Login verification failed.")
                print("   💡 Please make sure you're fully logged in to LinkedIn.")
                print("   💡 Check if LinkedIn is asking for additional verification.")
                driver.quit()
                self.driver = None
                return False

        except KeyboardInterrupt:
            print("\n❌ Login process cancelled by user.")
            if driver:
                driver.quit()
            sys.exit(1)
        except Exception as e:
            print(f"❌ Login process failed: {str(e)}")
            print("   💡 This might be a Chrome/ChromeDriver compatibility issue.")
            print("   💡 Try updating Chrome and ChromeDriver to the latest versions.")
            if driver:
                driver.quit()
            sys.exit(1)

    def _verify_login_success(self, driver) -> bool:
        """
        Verify that login was successful.

        Args:
            driver: Selenium WebDriver instance

        Returns:
            True if logged in, False otherwise
        """
        try:
            # Navigate to LinkedIn home to check login status
            driver.get("https://www.linkedin.com/feed")
            time.sleep(3)

            # Look for elements that indicate successful login
            login_indicators = [
                "nav-item__profile-member-photo",  # Profile photo in nav
                "global-nav__me",  # Me menu
                "feed-identity-module",  # Feed identity
            ]

            for indicator in login_indicators:
                try:
                    element = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CLASS_NAME, indicator))
                    )
                    if element:
                        return True
                except TimeoutException:
                    continue

            # Check if we're still on login page (indicates failed login)
            current_url = driver.current_url
            if "login" in current_url or "challenge" in current_url:
                return False

            return True

        except Exception as e:
            print(f"   ⚠️  Login verification error: {str(e)}")
            return False

    def _create_driver(self, headless: bool = False) -> webdriver.Chrome:
        """
        Create Chrome WebDriver with persistent session.

        Args:
            headless: Whether to run in headless mode

        Returns:
            Chrome WebDriver instance
        """
        options = Options()

        # Create user data directory if it doesn't exist
        user_data_path = os.path.abspath(self.user_data_dir)
        os.makedirs(user_data_path, exist_ok=True)
        options.add_argument(f"--user-data-dir={user_data_path}")

        if headless:
            options.add_argument("--headless=new")  # Use new headless mode

        # Essential stability options
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1280,720")

        # Reduce resource usage
        options.add_argument("--disable-extensions")
        options.add_argument("--no-first-run")
        options.add_argument("--no-default-browser-check")

        # User agent to appear more like a regular browser
        options.add_argument(
            "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        # Disable logging to reduce noise
        options.add_argument("--log-level=3")
        options.add_argument("--silent")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        options.add_experimental_option("useAutomationExtension", False)

        # Keep browser open for interactive sessions
        if not headless:
            options.add_experimental_option("detach", True)

        try:
            driver = webdriver.Chrome(options=options)
            pid = driver.service.process.pid if driver.service.process else "unknown"
            print(f"   ✅ Chrome driver created successfully (PID: {pid})")

            # Additional setup for stability
            driver.set_page_load_timeout(30)
            driver.implicitly_wait(10)

            print(f"   🌐 Chrome window should be visible (headless: {headless})")
            return driver

        except WebDriverException as e:
            error_msg = str(e)
            print(f"❌ Failed to create Chrome driver: {error_msg}")

            # Provide specific troubleshooting based on error
            if "chromedriver" in error_msg.lower():
                print("💡 ChromeDriver not found. Install with:")
                print("   macOS: brew install chromedriver")
                print("   Ubuntu: sudo apt-get install chromium-chromedriver")
                print("   Or download from: https://chromedriver.chromium.org/")
            elif "chrome" in error_msg.lower():
                print("💡 Chrome browser not found. Please install Google Chrome.")
            elif "permission" in error_msg.lower():
                print(
                    "💡 Permission denied. Try running with sudo or check file permissions."
                )
            else:
                print("💡 Try these troubleshooting steps:")
                print("   1. Update Chrome browser to latest version")
                print("   2. Update ChromeDriver to match Chrome version")
                print("   3. Check that ChromeDriver is in your PATH")
                print("   4. Try running: chromedriver --version")

            sys.exit(1)

    def get_profile_pictures(self, usernames: List[str], output_folder: str) -> dict:
        """
        Download profile pictures for multiple LinkedIn usernames.

        Args:
            usernames: List of LinkedIn usernames (without /in/ prefix)
            output_folder: Folder to save images

        Returns:
            Dictionary with download statistics
        """
        print(f"🔍 Preparing to get profile pictures for {len(usernames)} users...")

        # Create output folder
        os.makedirs(output_folder, exist_ok=True)

        # Initialize driver in headless mode
        driver = self._create_driver(headless=True)
        self.driver = driver

        try:
            # Navigate to LinkedIn and load session
            print("🔐 Loading LinkedIn session...")
            driver.get("https://www.linkedin.com")
            time.sleep(2)

            # Verify we're still logged in
            if not self._verify_login_success(driver):
                print("❌ LinkedIn session expired. Please run login again.")
                driver.quit()
                self.driver = None
                return {"success": 0, "failed": 0, "errors": ["Session expired"]}

            print("✅ LinkedIn session loaded successfully")

            # Process each username
            stats = {"success": 0, "failed": 0, "errors": []}

            for username in tqdm(usernames, desc="Getting profile pictures"):
                try:
                    success = self._download_single_profile_picture(
                        driver, username, output_folder
                    )
                    if success:
                        stats["success"] += 1
                    else:
                        stats["failed"] += 1

                    # Rate limiting delay
                    time.sleep(self.request_delay)

                except Exception as e:
                    error_msg = (
                        f"Error getting profile picture for {username}: {str(e)}"
                    )
                    print(f"   ⚠️  {error_msg}")
                    stats["errors"].append(error_msg)
                    stats["failed"] += 1

            return stats

        finally:
            if self.driver:
                self.driver.quit()
                self.driver = None

    def _download_single_profile_picture(
        self, driver, username: str, output_folder: str
    ) -> bool:
        """
        Download profile picture for a single username.

        Args:
            driver: Selenium WebDriver instance
            username: LinkedIn username
            output_folder: Output folder path

        Returns:
            True if successful, False otherwise
        """
        try:
            # Navigate to profile
            profile_url = f"https://www.linkedin.com/in/{username}/"
            driver.get(profile_url)
            time.sleep(2)  # Wait for page to load

            # Look for profile picture container
            img_selectors = [
                ".pv-top-card-profile-picture__container img",  # Desktop version
                ".profile-photo-edit__preview img",  # Alternative selector
                ".pv-top-card-profile-picture img",  # Another alternative
                "img[data-delayed-url*='profile-displayphoto']",  # Data attribute
                ".artdeco-entity-image",  # Generic LinkedIn image class
            ]

            img_element = None
            img_url = None

            # Try different selectors
            for selector in img_selectors:
                try:
                    img_element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    if img_element:
                        # Try different attributes for image URL
                        for attr in ["src", "data-delayed-url", "data-ghost-url"]:
                            img_url = img_element.get_attribute(attr)
                            if img_url and "media.licdn.com" in img_url:
                                break
                        if img_url:
                            break
                except TimeoutException:
                    continue

            if not img_url:
                print(f"   ⚠️  No profile image found for {username}")
                return False

            # Download the image
            response = requests.get(img_url, timeout=10)
            response.raise_for_status()

            # Determine file extension
            content_type = response.headers.get("content-type", "image/jpeg")
            extension = content_type.split("/")[-1]
            if extension not in ["jpg", "jpeg", "png", "gif"]:
                extension = "jpg"

            # Save the image
            filename = f"{username}.{extension}"
            filepath = os.path.join(output_folder, filename)

            with open(filepath, "wb") as f:
                f.write(response.content)

            return True

        except Exception as e:
            print(f"   ⚠️  Failed to download image for {username}: {str(e)}")
            return False

    def extract_single_profile_image_url(self, username: str) -> Optional[str]:
        """
        Extract profile image URL for a single username.

        Args:
            username: LinkedIn username

        Returns:
            Image URL if found, None otherwise
        """
        if not self.driver:
            driver = self._create_driver(headless=True)
            self.driver = driver
            should_close = True
        else:
            driver = self.driver
            should_close = False

        try:
            # Navigate to profile
            profile_url = f"https://www.linkedin.com/in/{username}/"
            driver.get(profile_url)
            time.sleep(2)

            # Look for profile picture
            img_selectors = [
                ".pv-top-card-profile-picture__container img",
                ".profile-photo-edit__preview img",
                ".pv-top-card-profile-picture img",
                "img[data-delayed-url*='profile-displayphoto']",
                ".artdeco-entity-image",
            ]

            for selector in img_selectors:
                try:
                    img_element = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    if img_element:
                        for attr in ["src", "data-delayed-url", "data-ghost-url"]:
                            img_url = img_element.get_attribute(attr)
                            if img_url and "media.licdn.com" in img_url:
                                return img_url
                except TimeoutException:
                    continue

            return None

        except Exception as e:
            print(f"   ⚠️  Error extracting image URL for {username}: {str(e)}")
            return None

        finally:
            if should_close and self.driver:
                self.driver.quit()
                self.driver = None

    def close(self):
        """Close the WebDriver and cleanup resources."""
        if self.driver:
            self.driver.quit()
            self.driver = None

    @staticmethod
    def is_selenium_available() -> bool:
        """
        Check if Selenium is available.

        Returns:
            True if selenium is available, False otherwise
        """
        try:
            from selenium import webdriver  # noqa: F401

            return True
        except ImportError:
            return False

    @staticmethod
    def extract_username_from_url(linkedin_url: str) -> Optional[str]:
        """
        Extract username from LinkedIn URL.

        Args:
            linkedin_url: Full LinkedIn profile URL

        Returns:
            Username if found, None otherwise
        """
        if not linkedin_url:
            return None

        # Clean up the URL
        url = linkedin_url.strip().rstrip("/")

        # Extract username from various URL formats
        if "/in/" in url:
            parts = url.split("/in/")
            if len(parts) > 1:
                username = parts[1].split("/")[0].split("?")[0]
                return username if username else None

        return None
