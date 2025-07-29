"""
Image processing module for Hugo Speaker Generator.

Handles downloading, processing, and saving speaker images with enhanced
LinkedIn extraction using Selenium and smart skip logic.
"""

import requests
import os
from PIL import Image
from typing import Dict, Optional
import csv
import logging
from .config import (
    DEFAULT_SPEAKER_IMAGE,
    OUTPUT_DIR,
    MISSING_PHOTOS_CSV,
    IMAGE_SIZE,
    IMAGE_QUALITY,
    REQUEST_TIMEOUT,
    SELENIUM_USER_DATA_DIR,
    LINKEDIN_REQUEST_DELAY,
)

# Try to import the Selenium LinkedIn extractor
try:
    from .linkedin_selenium_extractor import LinkedInSeleniumExtractor

    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    LinkedInSeleniumExtractor = None


class ImageProcessor:
    """Handles speaker image downloading and processing with enhanced LinkedIn support."""

    def __init__(self):
        """Initialize ImageProcessor with empty statistics."""
        self.missing_photos = []
        self.processed_count = 0
        self.failed_count = 0
        self.skipped_count = 0
        self.retry_queue = []  # Queue for speakers that failed in previous runs
        self.missing_photos_emails = set()  # Cache of emails in missing_photos.csv

        # Load previous failures for retry
        self._load_previous_failures()

        # Initialize LinkedIn extractor if available
        if SELENIUM_AVAILABLE and LinkedInSeleniumExtractor.is_selenium_available():
            self.linkedin_extractor = LinkedInSeleniumExtractor(
                user_data_dir=SELENIUM_USER_DATA_DIR,
                request_delay=LINKEDIN_REQUEST_DELAY,
                debug=False,  # Set to True for troubleshooting
            )
            print("   ✓ Selenium LinkedIn extractor available")
        else:
            self.linkedin_extractor = None
            if not SELENIUM_AVAILABLE:
                print("   ⚠️  Selenium LinkedIn extractor not available")
                print("   💡 Install with: pip install -r requirements-selenium.txt")
            else:
                print("   ⚠️  Selenium not installed, using basic extraction")

        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def _load_previous_failures(self):
        """Load previous failures from missing_photos.csv for retry."""
        if not os.path.exists(MISSING_PHOTOS_CSV):
            return

        try:
            with open(MISSING_PHOTOS_CSV, "r", newline="", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    email = row.get("Email", "")
                    if email:
                        self.missing_photos_emails.add(email)

                    # Only queue LinkedIn extraction failures for retry
                    if row.get(
                        "Reason"
                    ) == "LinkedIn image extraction failed" and row.get("LinkedIn URL"):
                        self.retry_queue.append(
                            {
                                "email": email,
                                "name": row.get("Speaker Name", ""),
                                "linkedin_url": row.get("LinkedIn URL", ""),
                            }
                        )

            if self.retry_queue:
                print(
                    f"   📋 Found {len(self.retry_queue)} previous LinkedIn failures to retry"
                )

        except Exception as e:
            print(f"   ⚠️  Could not load previous failures: {str(e)}")

    def should_skip_speaker(
        self, speaker_data: Dict, force_regenerate: bool = False
    ) -> bool:
        """
        Determine if speaker processing should be skipped.

        Args:
            speaker_data: Dictionary containing speaker information
            force_regenerate: If True, never skip

        Returns:
            True if should skip, False if should process
        """
        if force_regenerate:
            return False

        speaker_slug = speaker_data["slug"]
        email = speaker_data.get("email", "")

        # Check if files exist
        profile_path = os.path.join(
            OUTPUT_DIR, "content", "speakers", speaker_slug, "index.md"
        )
        image_path = os.path.join(
            OUTPUT_DIR, "content", "speakers", speaker_slug, "img", "photo.jpg"
        )

        profile_exists = os.path.exists(profile_path)
        image_exists = os.path.exists(image_path)

        # Check if speaker is in missing_photos.csv (needs retry)
        is_in_missing_photos = email in self.missing_photos_emails

        # Only skip if both files exist AND not in missing photos
        return profile_exists and image_exists and not is_in_missing_photos

    def setup_linkedin_login(self) -> bool:
        """
        Setup LinkedIn login if using Selenium extractor.

        Returns:
            True if login successful or not needed, False if failed
        """
        if not self.linkedin_extractor:
            return True  # No LinkedIn extractor, so no login needed

        # Check if we already have a session by looking for session files
        session_dir = os.path.abspath(self.linkedin_extractor.user_data_dir)
        session_exists = os.path.exists(session_dir) and os.listdir(session_dir)

        if session_exists:
            print("   ✅ Existing LinkedIn session found")
            return True
        else:
            print("   🔐 No LinkedIn session found, login required")
            return self.linkedin_extractor.login_to_linkedin()

    def process_speaker_image(
        self, speaker_data: Dict, retry_mode: bool = False
    ) -> str:
        """
        Process and save speaker image.

        Args:
            speaker_data: Dictionary containing speaker information
            retry_mode: If True, only count LinkedIn success as real success

        Returns:
            'success' if got actual image, 'default' if fell back to default,
            'failed' if completely failed
        """
        speaker_slug = speaker_data["slug"]
        speaker_name = speaker_data["name"]
        linkedin_url = speaker_data.get("linkedin", "")
        custom_photo_url = speaker_data.get("custom_photo_url", "")

        # Create speaker image directory
        img_dir = os.path.join(OUTPUT_DIR, "content", "speakers", speaker_slug, "img")
        os.makedirs(img_dir, exist_ok=True)

        output_path = os.path.join(img_dir, "photo.jpg")

        # Try custom photo URL first
        if custom_photo_url:
            if self._download_and_process_image(custom_photo_url, output_path):
                self.processed_count += 1
                return "success"
            else:
                self._log_missing_photo(
                    speaker_name,
                    speaker_data.get("email", ""),
                    linkedin_url,
                    "Custom photo download failed",
                )

        # Try LinkedIn profile image
        if linkedin_url:
            linkedin_image_url = self._extract_linkedin_image_url(linkedin_url)
            if linkedin_image_url and self._download_and_process_image(
                linkedin_image_url, output_path
            ):
                self.processed_count += 1
                return "success"
            else:
                self._log_missing_photo(
                    speaker_name,
                    speaker_data.get("email", ""),
                    linkedin_url,
                    "LinkedIn image extraction failed",
                )

        # Fall back to default image
        if self._copy_default_image(output_path):
            self.processed_count += 1
            if not linkedin_url and not custom_photo_url:
                self._log_missing_photo(
                    speaker_name,
                    speaker_data.get("email", ""),
                    "",
                    "No LinkedIn URL or custom photo provided",
                )
            return "default"
        else:
            self.failed_count += 1
            self._log_missing_photo(
                speaker_name,
                speaker_data.get("email", ""),
                linkedin_url,
                "Default image copy failed",
            )
            return "failed"

    def _extract_linkedin_image_url(self, linkedin_url: str) -> Optional[str]:
        """
        Extract profile image URL from LinkedIn profile.

        Uses Selenium extraction if available, falls back to basic method.

        Args:
            linkedin_url: LinkedIn profile URL

        Returns:
            Image URL if found, None otherwise
        """
        if self.linkedin_extractor:
            # Use Selenium LinkedIn extractor
            try:
                username = LinkedInSeleniumExtractor.extract_username_from_url(
                    linkedin_url
                )
                if username:
                    return self.linkedin_extractor.extract_single_profile_image_url(
                        username
                    )
                else:
                    print(f"   ⚠️  Could not extract username from {linkedin_url}")
                    return None
            except Exception as e:
                self.logger.error(
                    f"Selenium LinkedIn extraction failed for {linkedin_url}: {str(e)}"
                )
                return None
        else:
            # Fall back to basic LinkedIn extraction (original method)
            return self._basic_linkedin_extraction(linkedin_url)

    def _basic_linkedin_extraction(self, linkedin_url: str) -> Optional[str]:
        """
        Basic LinkedIn image extraction using simple regex patterns.

        This is the fallback method when Selenium is not available.

        Args:
            linkedin_url: LinkedIn profile URL

        Returns:
            Image URL if found, None otherwise
        """
        try:
            # Normalize the LinkedIn URL first
            normalized_url = self._normalize_linkedin_url(linkedin_url)

            # Simple approach - try to get the page and extract image
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = requests.get(
                normalized_url, headers=headers, timeout=REQUEST_TIMEOUT
            )

            if response.status_code == 200:
                # Look for profile image patterns in the HTML
                import re

                content = response.text

                # Look for common LinkedIn image patterns
                patterns = [
                    r'<img[^>]+class="[^"]*profile-photo[^"]*"[^>]+src="([^"]+)"',
                    r'<img[^>]+src="([^"]+)"[^>]+class="[^"]*profile-photo[^"]*"',
                    r'"profilePicture":"([^"]+)"',
                ]

                for pattern in patterns:
                    match = re.search(pattern, content)
                    if match:
                        return match.group(1)

            return None

        except Exception as e:
            print(
                f"   ⚠️  Failed to extract LinkedIn image from {linkedin_url}: {str(e)}"
            )
            return None

    def _normalize_linkedin_url(self, linkedin_url: str) -> str:
        """
        Normalize LinkedIn URL to ensure it has proper scheme.

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

    def _download_and_process_image(self, url: str, output_path: str) -> bool:
        """
        Download image from URL and process it.

        Args:
            url: Image URL
            output_path: Path to save processed image

        Returns:
            True if successful, False otherwise
        """
        try:
            # Download image
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()

            # Save temporary file
            temp_path = output_path + ".tmp"
            with open(temp_path, "wb") as f:
                f.write(response.content)

            # Process image
            if self._process_image_to_square(temp_path, output_path):
                os.remove(temp_path)
                return True
            else:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                return False

        except Exception as e:
            print(f"   ⚠️  Failed to download image from {url}: {str(e)}")
            return False

    def _process_image_to_square(self, input_path: str, output_path: str) -> bool:
        """
        Process image to square format.

        Args:
            input_path: Path to input image
            output_path: Path to save processed image

        Returns:
            True if successful, False otherwise
        """
        try:
            with Image.open(input_path) as img:
                # Convert to RGB if necessary
                if img.mode != "RGB":
                    img = img.convert("RGB")

                # Get dimensions
                width, height = img.size

                # Calculate crop box for center square
                if width > height:
                    # Landscape - crop sides
                    left = (width - height) // 2
                    top = 0
                    right = left + height
                    bottom = height
                else:
                    # Portrait or square - crop top/bottom
                    left = 0
                    top = (height - width) // 2
                    right = width
                    bottom = top + width

                # Crop to square
                img_cropped = img.crop((left, top, right, bottom))

                # Resize to target size
                img_resized = img_cropped.resize(IMAGE_SIZE, Image.Resampling.LANCZOS)

                # Save
                img_resized.save(
                    output_path, "JPEG", quality=IMAGE_QUALITY, optimize=True
                )

                return True

        except Exception as e:
            print(f"   ⚠️  Failed to process image {input_path}: {str(e)}")
            return False

    def _copy_default_image(self, output_path: str) -> bool:
        """
        Copy default unknown image to output path.

        Args:
            output_path: Path to save default image

        Returns:
            True if successful, False otherwise
        """
        try:
            if not os.path.exists(DEFAULT_SPEAKER_IMAGE):
                print(f"   ⚠️  Default image not found: {DEFAULT_SPEAKER_IMAGE}")
                return False

            # Process default image to ensure it's square and correct size
            return self._process_image_to_square(DEFAULT_SPEAKER_IMAGE, output_path)

        except Exception as e:
            print(f"   ⚠️  Failed to copy default image: {str(e)}")
            return False

    def _log_missing_photo(
        self, speaker_name: str, email: str, linkedin_url: str, reason: str
    ):
        """
        Log missing photo information.

        Args:
            speaker_name: Speaker name
            email: Speaker email
            linkedin_url: LinkedIn URL
            reason: Reason for failure
        """
        self.missing_photos.append(
            {
                "Speaker Name": speaker_name,
                "Email": email,
                "LinkedIn URL": linkedin_url,
                "Reason": reason,
            }
        )

    def save_missing_photos_report(self) -> bool:
        """
        Save missing photos report to CSV file, or delete if empty.

        Returns:
            True if successful, False otherwise
        """
        if not self.missing_photos:
            # Delete existing missing_photos.csv if it exists and no new issues
            if os.path.exists(MISSING_PHOTOS_CSV):
                try:
                    os.remove(MISSING_PHOTOS_CSV)
                    print(
                        f"   ✓ Removed empty {MISSING_PHOTOS_CSV} "
                        "(all images processed successfully)"
                    )
                except Exception as e:
                    print(f"   ⚠️  Could not remove {MISSING_PHOTOS_CSV}: {str(e)}")
            return True

        try:
            with open(MISSING_PHOTOS_CSV, "w", newline="", encoding="utf-8") as csvfile:
                fieldnames = ["Speaker Name", "Email", "LinkedIn URL", "Reason"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()
                for photo_data in self.missing_photos:
                    writer.writerow(photo_data)

            print(f"   ✓ Missing photos report saved to {MISSING_PHOTOS_CSV}")
            return True

        except Exception as e:
            print(f"   ⚠️  Failed to save missing photos report: {str(e)}")
            return False

    def get_statistics(self) -> Dict:
        """
        Get image processing statistics.

        Returns:
            Dictionary with processing statistics
        """
        return {
            "processed_count": self.processed_count,
            "failed_count": self.failed_count,
            "skipped_count": self.skipped_count,
            "missing_photos_count": len(self.missing_photos),
            "missing_photos": self.missing_photos,
        }

    def process_all_speaker_images(
        self, speakers: Dict[str, Dict], force_regenerate: bool = False
    ) -> Dict:
        """
        Process images for all speakers with smart skip logic.

        Args:
            speakers: Dictionary of speaker data
            force_regenerate: If True, regenerate all images

        Returns:
            Processing statistics
        """
        print(f"\n🖼️  Processing speaker images...")

        if force_regenerate:
            print("   🔄 Force regeneration enabled - rebuilding all images")

        processed_speakers = set()
        retry_successes = 0

        # Phase 1: Process retry queue (high priority)
        if self.retry_queue and not force_regenerate:
            print(
                f"   🔄 Retrying {len(self.retry_queue)} previous LinkedIn failures..."
            )

            for retry_item in self.retry_queue:
                email = retry_item["email"]
                if email in speakers and email not in processed_speakers:
                    speaker_data = speakers[email].copy()
                    speaker_data["email"] = email

                    print(f"   🔄 Retrying: {retry_item['name']}")

                    # Process with retry mode - only count actual LinkedIn success
                    result = self.process_speaker_image(speaker_data, retry_mode=True)
                    if result == "success":
                        print(f"   ✅ Retry successful!")
                        retry_successes += 1
                    elif result == "default":
                        print(f"   ❌ Still failed - using default image")
                    else:
                        print(f"   ❌ Failed completely")

                    processed_speakers.add(email)

            if retry_successes > 0:
                print(
                    f"   🎉 Successfully recovered {retry_successes} images from previous failures!"
                )

        # Phase 2: Process remaining speakers with skip logic
        remaining_speakers = [
            (email, data)
            for email, data in speakers.items()
            if email not in processed_speakers
        ]

        if remaining_speakers:
            print(f"   📋 Processing {len(remaining_speakers)} remaining speakers...")

        for i, (email, speaker_data) in enumerate(remaining_speakers, 1):
            speaker_name = speaker_data["name"]
            total_remaining = len(remaining_speakers)

            # Add email to speaker data for skip logic
            speaker_data_with_email = speaker_data.copy()
            speaker_data_with_email["email"] = email

            # Check if we should skip this speaker
            if self.should_skip_speaker(speaker_data_with_email, force_regenerate):
                print(
                    f"   [{i}/{total_remaining}] ✓ Skipped: {speaker_name} (already exists)"
                )
                self.skipped_count += 1
            else:
                if force_regenerate:
                    print(
                        f"   [{i}/{total_remaining}] 🔄 Force regenerating: {speaker_name}"
                    )
                else:
                    print(f"   [{i}/{total_remaining}] 📝 Processing: {speaker_name}")

                self.process_speaker_image(speaker_data_with_email)

            processed_speakers.add(email)

        # Save missing photos report
        self.save_missing_photos_report()

        # Final statistics
        print(f"   ✓ Total processed: {len(processed_speakers)}")
        if self.skipped_count > 0:
            print(f"   ✓ Skipped: {self.skipped_count}")
        print(f"   ✓ Downloaded: {self.processed_count}")
        if retry_successes > 0:
            print(f"   🔄 Retry successes: {retry_successes}")
        if self.failed_count > 0:
            print(f"   ⚠️  Failed: {self.failed_count}")
        if len(self.missing_photos) > 0:
            print(
                f"   ⚠️  Issues logged: {len(self.missing_photos)} (see {MISSING_PHOTOS_CSV})"
            )

        return self.get_statistics()

    def close(self):
        """Close and cleanup resources."""
        if self.linkedin_extractor:
            self.linkedin_extractor.close()
