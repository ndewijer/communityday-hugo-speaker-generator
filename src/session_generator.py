"""
Session page generation module for Hugo Speaker Generator.

Handles creation of session markdown files with proper filename generation.
"""

import os
from typing import Dict, List

from .config import OUTPUT_DIR
from .utils import extract_session_level, print_progress, process_multiple_durations


class SessionGenerator:
    """Handles generation of session markdown files."""

    def __init__(self):
        """Initialize SessionGenerator with empty statistics."""
        self.generated_count = 0
        self.failed_count = 0
        self.session_filenames = {}

    def generate_session_filenames(self, sessions: List[Dict]) -> Dict[str, str]:
        """
        Generate session filenames based on level and sorted by Session_ID.

        Args:
            sessions: List of session dictionaries

        Returns:
            Dictionary mapping session_id to filename
        """
        # Sort sessions by Session_ID for consistent ordering
        sessions_sorted = sorted(sessions, key=lambda x: x.get("id", ""))

        # Separate counters for each level
        level_counters = {1: 0, 2: 0, 3: 0, 4: 0}
        session_filenames = {}

        for session in sessions_sorted:
            session_id = session.get("id", "")
            level = extract_session_level(session.get("level", ""))

            level_counters[level] += 1
            filename = f"acd{level}{level_counters[level]:02d}.md"
            session_filenames[session_id] = filename

        self.session_filenames = session_filenames
        return session_filenames

    def generate_session_file(self, session_data: Dict, filename: str) -> bool:
        """
        Generate individual session markdown file.

        Args:
            session_data: Dictionary containing session information
            filename: Target filename for the session

        Returns:
            True if successful, False otherwise
        """
        try:
            session_id = session_data.get("id", "")
            session_title = session_data.get("title", "")
            session_abstract = session_data.get("abstract", "")
            session_duration = session_data.get("duration", "")
            speaker_slug = session_data.get("speaker_slug", "")
            room = session_data.get("room", "")
            agenda = session_data.get("agenda", "")

            # Generate markdown content
            markdown_content = self._generate_session_markdown(
                session_id,
                session_title,
                session_abstract,
                session_duration,
                speaker_slug,
                room,
                agenda,
            )

            # Write markdown file
            sessions_dir = os.path.join(OUTPUT_DIR, "content", "sessions")
            os.makedirs(sessions_dir, exist_ok=True)

            session_path = os.path.join(sessions_dir, filename)
            with open(session_path, "w", encoding="utf-8") as f:
                f.write(markdown_content)

            self.generated_count += 1
            return True

        except Exception as e:
            print(f"   ⚠️  Failed to generate session file {filename}: {str(e)}")
            self.failed_count += 1
            return False

    def _generate_session_markdown(
        self,
        session_id: str,
        title: str,
        abstract: str,
        duration: str,
        speaker_slug: str,
        room: str = "",
        agenda: str = "",
    ) -> str:
        """
        Generate session markdown content.

        Args:
            session_id: Session ID
            title: Session title
            abstract: Session abstract
            duration: Session duration
            speaker_slug: Speaker slug
            room: Room number/name
            agenda: Agenda time in HHMM format

        Returns:
            Formatted markdown content
        """
        # Format fields
        id_field = f'id: "{session_id}"' if session_id else 'id: ""'
        title_field = f'title: "{title}"' if title else 'title: ""'

        # Generate date field from agenda time
        from .utils import format_session_datetime

        formatted_datetime = format_session_datetime(agenda)
        date_field = f'date: "{formatted_datetime}"' if formatted_datetime else 'date: ""'

        # Format room and agenda fields
        room_field = f'room: "{room}"' if room else 'room: ""'
        agenda_field = f'agenda: "{agenda}"' if agenda else 'agenda: ""'

        # Handle speakers field
        if speaker_slug:
            speakers_field = f'speakers:\n    - "{speaker_slug}"'
        else:
            speakers_field = "speakers: []"

        # Handle duration field (may have multiple options)
        duration_lines = process_multiple_durations(duration)
        duration_field = "\n".join(duration_lines)

        # Format abstract
        abstract_content = abstract if abstract else '""'

        # Generate markdown
        markdown = f"""---
{id_field}
{title_field}
{date_field}
{speakers_field}
{room_field}
{agenda_field}
{duration_field}
---

{abstract_content}
"""

        return markdown

    def should_skip_session_file(self, filename: str, force_regenerate: bool = False) -> bool:
        """
        Determine if session file generation should be skipped.

        Args:
            filename: Session filename
            force_regenerate: If True, never skip

        Returns:
            True if should skip, False if should generate
        """
        if force_regenerate:
            return False

        session_path = os.path.join(OUTPUT_DIR, "content", "sessions", filename)
        return os.path.exists(session_path)

    def generate_all_session_files(
        self, sessions: List[Dict], force_regenerate: bool = False
    ) -> Dict:
        """
        Generate files for all sessions with smart skip logic.

        Args:
            sessions: List of session data
            force_regenerate: If True, regenerate all session files

        Returns:
            Generation statistics
        """
        print(f"\n📋 Generating session files...")

        if force_regenerate:
            print("   🔄 Force regeneration enabled - rebuilding all session files")

        # Generate filenames first
        session_filenames = self.generate_session_filenames(sessions)

        total_sessions = len(sessions)
        current = 0
        skipped_count = 0

        for session in sessions:
            current += 1
            session_id = session.get("id", "")
            session_title = session.get("title", "Unknown Session")
            filename = session_filenames.get(session_id, f"unknown-{current}.md")

            # Check if we should skip this session file
            if self.should_skip_session_file(filename, force_regenerate):
                print_progress(current, total_sessions, f"✓ Skipped: {filename} (already exists)")
                skipped_count += 1
            else:
                if force_regenerate:
                    print_progress(
                        current,
                        total_sessions,
                        f"🔄 Force regenerating: {filename} - {session_title}",
                    )
                else:
                    print_progress(current, total_sessions, f"{filename} - {session_title}")

                self.generate_session_file(session, filename)

        print(f"   ✓ Generated {self.generated_count} session files")
        if skipped_count > 0:
            print(f"   ✓ Skipped: {skipped_count}")
        if self.failed_count > 0:
            print(f"   ⚠️  Failed: {self.failed_count}")

        return self.get_statistics()

    def get_level_statistics(self, sessions: List[Dict]) -> Dict[int, int]:
        """
        Get session count statistics by level.

        Args:
            sessions: List of session data

        Returns:
            Dictionary mapping level to count
        """
        level_counts = {1: 0, 2: 0, 3: 0, 4: 0}

        for session in sessions:
            level = extract_session_level(session.get("level", ""))
            level_counts[level] += 1

        return level_counts

    def get_statistics(self) -> Dict:
        """
        Get generation statistics.

        Returns:
            Dictionary with generation statistics
        """
        return {
            "generated_count": self.generated_count,
            "failed_count": self.failed_count,
            "session_filenames": self.session_filenames,
        }
