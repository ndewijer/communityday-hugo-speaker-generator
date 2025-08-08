"""
Speaker page generation module for Hugo Speaker Generator.

Handles creation of speaker markdown files and directory structure.
"""

import os
import re
from typing import Dict, Tuple

from .config import EMOJIS, OUTPUT_DIR
from .utils import format_bio_content, format_linkedin_field, print_progress


class SpeakerGenerator:
    """Handles generation of speaker markdown files."""

    def __init__(
            self,
            debug: bool = False
            ):
        """
        Initialize SpeakerGenerator with empty statistics.
        
        Args:
            debug: Enable debug output for troubleshooting
        """
        self.generated_count = 0
        self.failed_count = 0
        self.updated_count = 0
        self.debug = debug
        

    def generate_speaker_profile(self, speaker_data: Dict) -> bool:
        """
        Generate speaker profile markdown file.

        Args:
            speaker_data: Dictionary containing speaker information

        Returns:
            True if successful, False otherwise
        """
        try:
            speaker_slug = speaker_data["slug"]
            speaker_name = speaker_data["name"]
            speaker_headline = speaker_data.get("headline", "")
            speaker_bio = speaker_data.get("bio", "")
            linkedin_url = speaker_data.get("linkedin", "")

            # Create speaker directory
            speaker_dir = os.path.join(OUTPUT_DIR, "content", "speakers", speaker_slug)
            os.makedirs(speaker_dir, exist_ok=True)

            # Generate markdown content
            markdown_content = self._generate_speaker_markdown(
                speaker_name, speaker_headline, speaker_bio, linkedin_url
            )

            # Write markdown file
            markdown_path = os.path.join(speaker_dir, "index.md")
            with open(markdown_path, "w", encoding="utf-8") as f:
                f.write(markdown_content)

            self.generated_count += 1
            return True

        except Exception as e:
            speaker_name = speaker_data.get("name", "Unknown")
            print(f"   {EMOJIS['warning']}  Failed to generate speaker profile for {speaker_name}: {str(e)}")
            self.failed_count += 1
            return False

    def _generate_speaker_markdown(
        self, name: str, headline: str, bio: str, linkedin_url: str
    ) -> str:
        """
        Generate speaker markdown content.

        Args:
            name: Speaker name
            headline: Speaker headline
            bio: Speaker bio
            linkedin_url: LinkedIn URL

        Returns:
            Formatted markdown content
        """
        # Format fields
        title_field = f'title: "{name}"' if name else 'title: ""'
        headline_field = f'headline: "{headline}"' if headline else 'headline: ""'
        linkedin_field = format_linkedin_field(linkedin_url)
        bio_content = format_bio_content(bio)

        # Generate markdown
        markdown = f"""---
{title_field}
{headline_field}
{linkedin_field}
---

{bio_content}
"""

        return markdown

    def _extract_speaker_data_from_file(self, filepath: str) -> Dict:
        """
        Extract speaker data from an existing markdown file.

        Args:
            filepath: Path to the speaker markdown file

        Returns:
            Dictionary with extracted speaker data
        """
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            # Extract frontmatter between --- markers
            frontmatter_match = re.search(r"---\s+(.*?)\s+---", content, re.DOTALL)
            if not frontmatter_match:
                return {}

            frontmatter = frontmatter_match.group(1)

            # Extract key fields
            speaker_data = {}

            # Extract name (title)
            title_match = re.search(r'title:\s*"([^"]*)"', frontmatter)
            if title_match:
                speaker_data["name"] = title_match.group(1)

            # Extract headline
            headline_match = re.search(r'headline:\s*"([^"]*)"', frontmatter)
            if headline_match:
                speaker_data["headline"] = headline_match.group(1)

            # Extract LinkedIn URL
            linkedin_match = re.search(r'linkedin:\s*"([^"]*)"', frontmatter)
            if linkedin_match:
                speaker_data["linkedin"] = linkedin_match.group(1)

            # Extract bio (content after frontmatter)
            bio_match = re.search(r"---\s+(.*?)\s+---(.*)", content, re.DOTALL)
            if bio_match:
                speaker_data["bio"] = bio_match.group(2).strip()

            return speaker_data

        except Exception as e:
            print(f"   {EMOJIS['warning']}  Failed to extract data from {filepath}: {str(e)}")
            return {}

    def _speaker_needs_update(self, speaker_data: Dict, existing_data: Dict) -> bool:
        """
        Check if speaker data has changed and needs updating.

        Args:
            speaker_data: Current speaker data from source
            existing_data: Existing speaker data from file

        Returns:
            True if update is needed, False otherwise
        """
        # Check key fields that would require an update
        fields_to_check = ["name", "headline", "linkedin", "bio"]

        for field in fields_to_check:
            current_value = speaker_data.get(field, "")
            existing_value = existing_data.get(field, "")

            # If any field is different, update is needed
            if current_value != existing_value:
                return True

        return False

    def update_speaker_profile(self, speaker_data: Dict) -> bool:
        """
        Update an existing speaker profile with new data.

        Args:
            speaker_data: Dictionary containing speaker information

        Returns:
            True if successful, False otherwise
        """
        try:
            speaker_slug = speaker_data["slug"]
            speaker_name = speaker_data["name"]
            speaker_headline = speaker_data.get("headline", "")
            speaker_bio = speaker_data.get("bio", "")
            linkedin_url = speaker_data.get("linkedin", "")

            # Generate markdown content
            markdown_content = self._generate_speaker_markdown(
                speaker_name, speaker_headline, speaker_bio, linkedin_url
            )

            # Write updated markdown file
            speaker_dir = os.path.join(OUTPUT_DIR, "content", "speakers", speaker_slug)
            markdown_path = os.path.join(speaker_dir, "index.md")
            with open(markdown_path, "w", encoding="utf-8") as f:
                f.write(markdown_content)

            self.updated_count += 1
            return True

        except Exception as e:
            print(f"   {EMOJIS['warning']}  Failed to update speaker profile for {speaker_data.get('name', 'Unknown')}: {str(e)}")
            self.failed_count += 1
            return False

    def should_skip_speaker_profile(
        self, speaker_data: Dict, force_regenerate: bool = False
    ) -> Tuple[bool, bool]:
        """
        Determine if speaker profile generation should be skipped or updated.

        Args:
            speaker_data: Dictionary containing speaker information
            force_regenerate: If True, never skip

        Returns:
            Tuple of (should_skip, should_update)
        """
        if force_regenerate:
            return False, False

        speaker_slug = speaker_data["slug"]
        profile_path = os.path.join(OUTPUT_DIR, "content", "speakers", speaker_slug, "index.md")

        # If file doesn't exist, don't skip (need to generate)
        if not os.path.exists(profile_path):
            return False, False

        # File exists, check if it needs updating
        existing_data = self._extract_speaker_data_from_file(profile_path)
        needs_update = self._speaker_needs_update(speaker_data, existing_data)

        # Debug output
        if self.debug:
            print(f"DEBUG: should_skip_speaker_profile checking {profile_path} - exists: True, needs_update: {needs_update}")

        # If needs update, don't skip but mark for update
        if needs_update:
            return False, True

        # Otherwise, skip (file exists and doesn't need updating)
        return True, False

    def generate_all_speaker_profiles(
        self, speakers: Dict[str, Dict], force_regenerate: bool = False
    ) -> Dict:
        """
        Generate profiles for all speakers with smart skip logic.

        Args:
            speakers: Dictionary of speaker data
            force_regenerate: If True, regenerate all profiles

        Returns:
            Generation statistics
        """
        print(f"\n{EMOJIS['document']} Generating speaker profiles...")

        if force_regenerate:
            print(f"   {EMOJIS['update']} Force regeneration enabled - rebuilding all profiles")

        total_speakers = len(speakers)
        current = 0
        skipped_count = 0
        updated_count = 0

        for email, speaker_data in speakers.items():
            current += 1
            speaker_name = speaker_data["name"]

            # Check if we should skip or update this speaker profile
            should_skip, should_update = self.should_skip_speaker_profile(speaker_data, force_regenerate)

            if should_skip:
                print_progress(
                    current,
                    total_speakers,
                    f"{EMOJIS['check']} Skipped: {speaker_name} (no changes)",
                )
                skipped_count += 1
            elif should_update:
                print_progress(
                    current,
                    total_speakers,
                    f"{EMOJIS['update']} Updating: {speaker_name}",
                )
                self.update_speaker_profile(speaker_data)
                updated_count += 1
            else:
                if force_regenerate:
                    print_progress(
                        current,
                        total_speakers,
                        f"{EMOJIS['update']} Force regenerating: {speaker_name}",
                    )
                else:
                    print_progress(current, total_speakers, speaker_name)

                self.generate_speaker_profile(speaker_data)

        print(f"   {EMOJIS['check']} Generated {self.generated_count} speaker profiles")
        if updated_count > 0:
            print(f"   {EMOJIS['update']} Updated {updated_count} speaker profiles")
        if skipped_count > 0:
            print(f"   {EMOJIS['check']} Skipped: {skipped_count} (no changes)")
        if self.failed_count > 0:
            print(f"   {EMOJIS['warning']}  Failed: {self.failed_count}")

        return self.get_statistics()

    def handle_removed_speakers(self, current_speakers: Dict[str, Dict]) -> None:
        """
        Handle speakers that have been removed from the datasource or no longer have sessions.

        Args:
            current_speakers: Dictionary of current speaker data
        """
        # Get all speaker slugs from the current data that have at least one session
        current_speaker_slugs = set()
        for _, speaker_data in current_speakers.items():
            # Only include speakers that have at least one session
            if speaker_data.get("sessions") and len(speaker_data["sessions"]) > 0:
                current_speaker_slugs.add(speaker_data["slug"])
            else:
                print(f"   {EMOJIS['warning']} Speaker {speaker_data['name']} has no sessions")

        # Get all speaker directories in the output directory
        speakers_dir = os.path.join(OUTPUT_DIR, "content", "speakers")
        if not os.path.exists(speakers_dir):
            return

        existing_speaker_dirs = [
            d
            for d in os.listdir(speakers_dir)
            if os.path.isdir(os.path.join(speakers_dir, d)) and d != "_index"
        ]

        # Find speaker directories that are not in the current data or have no sessions
        removed_speaker_slugs = set(existing_speaker_dirs) - current_speaker_slugs

        if removed_speaker_slugs:
            print(f"\n{EMOJIS['trash']} Handling removed speakers...")
            removed_count = 0

            for speaker_slug in removed_speaker_slugs:
                speaker_dir = os.path.join(speakers_dir, speaker_slug)

                # Check if this is a valid speaker directory with an index.md file
                profile_path = os.path.join(speaker_dir, "index.md")
                if os.path.exists(profile_path):
                    print(f"   {EMOJIS['trash']} Removing speaker profile: {speaker_slug}")

                    # Remove the speaker directory and all its contents
                    import shutil

                    shutil.rmtree(speaker_dir)
                    removed_count += 1

            if removed_count > 0:
                print(f"   {EMOJIS['check']} Removed {removed_count} speaker profiles")

    def get_statistics(self) -> Dict:
        """
        Get generation statistics.

        Returns:
            Dictionary with generation statistics
        """
        return {
            "generated_count": self.generated_count,
            "updated_count": self.updated_count,
            "failed_count": self.failed_count,
        }
