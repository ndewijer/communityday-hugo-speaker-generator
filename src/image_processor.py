"""
Image processing module for Hugo Speaker Generator.

Handles downloading, processing, and saving speaker images.
"""

import requests
import os
from PIL import Image
from typing import Dict, Optional
import csv
import logging
import re
from .config import (
    DEFAULT_SPEAKER_IMAGE,
    OUTPUT_DIR,
    MISSING_PHOTOS_CSV,
    IMAGE_SIZE,
    IMAGE_QUALITY,
    REQUEST_TIMEOUT,
)

# Try to import the enhanced LinkedIn extractor, fall back to basic extraction if not available
try:
    from .linkedin_extractor import LinkedInImageExtractor

    ENHANCED_EXTRACTOR_AVAILABLE = True
except ImportError:
    ENHANCED_EXTRACTOR_AVAILABLE = False
    LinkedInImageExtractor = None


class ImageProcessor:
    """Handles speaker image downloading and processing."""

    def __init__(self):
        """Initialize ImageProcessor with empty statistics."""
        self.missing_photos = []
        self.processed_count = 0
        self.failed_count = 0
        self.retry_queue = []  # Queue for speakers that failed in previous runs

        # Load previous failures for retry
        self._load_previous_failures()

        # Initialize enhanced LinkedIn extractor if available
        if ENHANCED_EXTRACTOR_AVAILABLE:
            self.linkedin_extractor = LinkedInImageExtractor(
                request_timeout=REQUEST_TIMEOUT, retry_attempts=3
            )
            print("   ✓ Enhanced LinkedIn extractor loaded")
        else:
            self.linkedin_extractor = None
            print(
                "   ⚠️  Using basic LinkedIn extraction "
                "(install enhanced dependencies for better results)"
            )

        # Setup logging - set to INFO level to reduce noise from LinkedIn extractor
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # Set LinkedIn extractor logger to INFO level to suppress debug messages
        linkedin_logger = logging.getLogger("src.linkedin_extractor")
        linkedin_logger.setLevel(logging.INFO)

    def _load_previous_failures(self):
        """Load previous failures from missing_photos.csv for retry."""
        if not os.path.exists(MISSING_PHOTOS_CSV):
            return

        try:
            with open(MISSING_PHOTOS_CSV, "r", newline="", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    # Only queue LinkedIn extraction failures for retry
                    if row.get(
                        "Reason"
                    ) == "LinkedIn image extraction failed" and row.get("LinkedIn URL"):
                        self.retry_queue.append(
                            {
                                "email": row.get("Email", ""),
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

    def process_speaker_image(self, speaker_data: Dict) -> bool:
        """
        Process and save speaker image.

        Args:
            speaker_data: Dictionary containing speaker information

        Returns:
            True if successful, False otherwise
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
                return True
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
                return True
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
            return True
        else:
            self.failed_count += 1
            self._log_missing_photo(
                speaker_name,
                speaker_data.get("email", ""),
                linkedin_url,
                "Default image copy failed",
            )
            return False

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

    def _extract_linkedin_image_url(self, linkedin_url: str) -> Optional[str]:
        """
        Extract profile image URL from LinkedIn profile.

        Uses enhanced extraction if available, falls back to basic method.

        Args:
            linkedin_url: LinkedIn profile URL

        Returns:
            Image URL if found, None otherwise
        """
        if ENHANCED_EXTRACTOR_AVAILABLE and self.linkedin_extractor:
            # Use enhanced LinkedIn extractor
            try:
                return self.linkedin_extractor.extract_profile_image_url(linkedin_url)
            except Exception as e:
                self.logger.error(
                    f"Enhanced LinkedIn extraction failed for {linkedin_url}: {str(e)}"
                )
                return None
        else:
            # Fall back to basic LinkedIn extraction
            return self._basic_linkedin_extraction(linkedin_url)

    def _basic_linkedin_extraction(self, linkedin_url: str) -> Optional[str]:
        """
        Basic LinkedIn image extraction using simple regex patterns.

        This is the original method for backward compatibility.

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
                # This is a basic implementation and may not work reliably
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
        Save missing photos report to CSV file.

        Returns:
            True if successful, False otherwise
        """
        if not self.missing_photos:
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
            "missing_photos_count": len(self.missing_photos),
            "missing_photos": self.missing_photos,
        }

    def process_all_speaker_images(self, speakers: Dict[str, Dict]) -> Dict:
        """
        Process images for all speakers.

        Prioritizes retry attempts for speakers that failed in previous runs.

        Args:
            speakers: Dictionary of speaker data

        Returns:
            Processing statistics
        """
        print(f"\n🖼️  Processing speaker images...")

        # First, process retry queue (previous failures)
        retry_successes = 0
        if self.retry_queue:
            print(
                f"   🔄 Retrying {len(self.retry_queue)} previous LinkedIn failures..."
            )

            for retry_item in self.retry_queue:
                email = retry_item["email"]
                if email in speakers:
                    speaker_data = speakers[email].copy()
                    speaker_data["email"] = email

                    print(f"   🔄 Retrying: {retry_item['name']}")

                    # Check if we already have a successful image
                    speaker_slug = speaker_data["slug"]
                    img_path = os.path.join(
                        OUTPUT_DIR,
                        "content",
                        "speakers",
                        speaker_slug,
                        "img",
                        "photo.jpg",
                    )

                    if os.path.exists(img_path) and os.path.getsize(img_path) > 0:
                        # Skip if we already have an image (might be default from previous run)
                        # But only if it's not the default image
                        if not self._is_default_image(img_path):
                            print(f"   ✓ Already has custom image, skipping retry")
                            continue

                    # Try LinkedIn extraction again
                    linkedin_url = speaker_data.get("linkedin", "")
                    if linkedin_url:
                        linkedin_image_url = self._extract_linkedin_image_url(
                            linkedin_url
                        )
                        if linkedin_image_url and self._download_and_process_image(
                            linkedin_image_url, img_path
                        ):
                            print(f"   ✅ Retry successful!")
                            retry_successes += 1
                            self.processed_count += 1
                            continue

                    # If retry failed, it will be logged again in the regular processing

            if retry_successes > 0:
                print(
                    f"   🎉 Successfully recovered {retry_successes} images from previous failures!"
                )

        # Then process all speakers normally
        total_speakers = len(speakers)
        current = 0

        for email, speaker_data in speakers.items():
            current += 1
            speaker_name = speaker_data["name"]
            print(f"   [{current}/{total_speakers}] {speaker_name}")

            # Add email to speaker data for logging
            speaker_data_with_email = speaker_data.copy()
            speaker_data_with_email["email"] = email

            self.process_speaker_image(speaker_data_with_email)

        # Save missing photos report
        self.save_missing_photos_report()

        print(f"   ✓ Downloaded: {self.processed_count}")
        if retry_successes > 0:
            print(f"   🔄 Retry successes: {retry_successes}")
        if self.failed_count > 0:
            print(f"   ⚠️  Failed: {self.failed_count}")
        if len(self.missing_photos) > 0:
            print(
                f"   ⚠️  Issues logged: {len(self.missing_photos)} (see {MISSING_PHOTOS_CSV})"
            )

        # Cleanup resources
        if ENHANCED_EXTRACTOR_AVAILABLE and self.linkedin_extractor:
            self.linkedin_extractor.close()

        return self.get_statistics()

    def _is_default_image(self, image_path: str) -> bool:
        """
        Check if the image at the given path is the default image.

        Args:
            image_path: Path to the image file

        Returns:
            True if it's the default image, False otherwise
        """
        try:
            if not os.path.exists(image_path) or not os.path.exists(
                DEFAULT_SPEAKER_IMAGE
            ):
                return False

            # Compare file sizes first as a quick check
            current_size = os.path.getsize(image_path)
            default_size = os.path.getsize(DEFAULT_SPEAKER_IMAGE)

            # If sizes are different, it's definitely not the default image
            if current_size != default_size:
                return False

            # If sizes are the same, compare file contents to be sure
            with open(image_path, "rb") as f1, open(DEFAULT_SPEAKER_IMAGE, "rb") as f2:
                # Read in chunks to handle large files efficiently
                chunk_size = 8192
                while True:
                    chunk1 = f1.read(chunk_size)
                    chunk2 = f2.read(chunk_size)

                    if chunk1 != chunk2:
                        return False

                    if not chunk1:  # End of file
                        break

            return True

        except Exception:
            return False

    def close(self):
        """Close and cleanup resources."""
        if (
            ENHANCED_EXTRACTOR_AVAILABLE
            and hasattr(self, "linkedin_extractor")
            and self.linkedin_extractor
        ):
            self.linkedin_extractor.close()
