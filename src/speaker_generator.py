"""
Speaker page generation module for Hugo Speaker Generator.

Handles creation of speaker markdown files and directory structure.
"""

import os
from typing import Dict
from .config import OUTPUT_DIR
from .utils import format_linkedin_field, format_bio_content, print_progress


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
            print(
                f"   ⚠️  Failed to generate speaker profile for {speaker_name}: {str(e)}"
            )
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

    def generate_all_speaker_profiles(self, speakers: Dict[str, Dict]) -> Dict:
        """
        Generate profiles for all speakers.

        Args:
            speakers: Dictionary of speaker data

        Returns:
            Generation statistics
        """
        print(f"\n📝 Generating speaker profiles...")

        total_speakers = len(speakers)
        current = 0

        for email, speaker_data in speakers.items():
            current += 1
            speaker_name = speaker_data["name"]
            print_progress(current, total_speakers, speaker_name)

            self.generate_speaker_profile(speaker_data)

        print(f"   ✓ Generated {self.generated_count} speaker profiles")
        if self.failed_count > 0:
            print(f"   ⚠️  Failed: {self.failed_count}")

        return self.get_statistics()

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
