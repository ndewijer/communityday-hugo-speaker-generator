"""
Speaker page generation module for Hugo Speaker Generator.

Handles creation of speaker markdown files and directory structure.
"""

import os
from typing import Dict

from .config import OUTPUT_DIR
from .utils import format_bio_content, format_linkedin_field, print_progress


class SpeakerGenerator:
    """Handles generation of speaker markdown files."""

    def __init__(self):
        """Initialize SpeakerGenerator with empty statistics."""
        self.generated_count = 0
        self.failed_count = 0

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
            print(f"   ⚠️  Failed to generate speaker profile for {speaker_name}: {str(e)}")
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

    def should_skip_speaker_profile(
        self, speaker_data: Dict, force_regenerate: bool = False
    ) -> bool:
        """
        Determine if speaker profile generation should be skipped.

        Args:
            speaker_data: Dictionary containing speaker information
            force_regenerate: If True, never skip

        Returns:
            True if should skip, False if should generate
        """
        if force_regenerate:
            return False

        speaker_slug = speaker_data["slug"]
        profile_path = os.path.join(OUTPUT_DIR, "content", "speakers", speaker_slug, "index.md")

        # Debug output
        exists = os.path.exists(profile_path)
        print(f"DEBUG: should_skip_speaker_profile checking {profile_path} - exists: {exists}")

        return exists

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
        print(f"\n📝 Generating speaker profiles...")

        if force_regenerate:
            print("   🔄 Force regeneration enabled - rebuilding all profiles")

        total_speakers = len(speakers)
        current = 0
        skipped_count = 0

        for email, speaker_data in speakers.items():
            current += 1
            speaker_name = speaker_data["name"]

            # Check if we should skip this speaker profile
            if self.should_skip_speaker_profile(speaker_data, force_regenerate):
                print_progress(
                    current,
                    total_speakers,
                    f"✓ Skipped: {speaker_name} (already exists)",
                )
                skipped_count += 1
            else:
                if force_regenerate:
                    print_progress(
                        current,
                        total_speakers,
                        f"🔄 Force regenerating: {speaker_name}",
                    )
                else:
                    print_progress(current, total_speakers, speaker_name)

                self.generate_speaker_profile(speaker_data)

        print(f"   ✓ Generated {self.generated_count} speaker profiles")
        if skipped_count > 0:
            print(f"   ✓ Skipped: {skipped_count}")
        if self.failed_count > 0:
            print(f"   ⚠️  Failed: {self.failed_count}")

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
                print(f"   ⚠️ Speaker {speaker_data['name']} has no sessions")

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
            print(f"\n🗑️ Handling removed speakers...")
            removed_count = 0

            for speaker_slug in removed_speaker_slugs:
                speaker_dir = os.path.join(speakers_dir, speaker_slug)

                # Check if this is a valid speaker directory with an index.md file
                profile_path = os.path.join(speaker_dir, "index.md")
                if os.path.exists(profile_path):
                    print(f"   🗑️ Removing speaker profile: {speaker_slug}")

                    # Remove the speaker directory and all its contents
                    import shutil

                    shutil.rmtree(speaker_dir)
                    removed_count += 1

            if removed_count > 0:
                print(f"   ✓ Removed {removed_count} speaker profiles")

    def get_statistics(self) -> Dict:
        """
        Get generation statistics.

        Returns:
            Dictionary with generation statistics
        """
        return {
            "generated_count": self.generated_count,
            "failed_count": self.failed_count,
        }
