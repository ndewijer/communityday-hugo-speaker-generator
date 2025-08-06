"""
Session page generation module for Hugo Speaker Generator.

Handles creation of session markdown files with proper filename generation.
"""

import json
import os
import re
from typing import Dict, List, Tuple

from .config import OUTPUT_DIR, SESSION_ID_MAPPING_FILE
from .utils import extract_session_level, print_progress, process_multiple_durations


class SessionGenerator:
    """Handles generation of session markdown files."""

    def __init__(self):
        """Initialize SessionGenerator with empty statistics."""
        self.generated_count = 0
        self.failed_count = 0
        self.updated_count = 0
        self.session_filenames = {}
        self.mapping_data = self._load_session_id_mapping()

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

    def get_level_statistics(self, sessions: List[Dict]) -> Dict[int, int]:
        """
        Get session count statistics by level.

        Args:
            sessions: List of session data

        Returns:
            Dictionary mapping level to count
        """
        level_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}

        for session in sessions:
            level = extract_session_level(session.get("level", ""))
            if level in level_counts:
                level_counts[level] += 1

        return level_counts

    def _load_session_id_mapping(self) -> Dict:
        """
        Load session ID mapping from JSON file.

        Returns:
            Dictionary with mapping data or default structure if file doesn't exist
        """
        default_mapping = {
            "session_id_mapping": {},
            "level_counters": {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0},
        }

        try:
            if os.path.exists(SESSION_ID_MAPPING_FILE):
                with open(SESSION_ID_MAPPING_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            else:
                # Create directory if it doesn't exist
                os.makedirs(os.path.dirname(SESSION_ID_MAPPING_FILE), exist_ok=True)
                return default_mapping
        except Exception as e:
            print(f"   ⚠️  Failed to load session ID mapping: {str(e)}")
            return default_mapping

    def _save_session_id_mapping(self) -> bool:
        """
        Save session ID mapping to JSON file.

        Returns:
            True if successful, False otherwise
        """
        try:
            with open(SESSION_ID_MAPPING_FILE, "w", encoding="utf-8") as f:
                json.dump(self.mapping_data, f, indent=2)
            return True
        except Exception as e:
            print(f"   ⚠️  Failed to save session ID mapping: {str(e)}")
            return False

    def _extract_session_data_from_file(self, filepath: str) -> Dict:
        """
        Extract session data from an existing markdown file.

        Args:
            filepath: Path to the session markdown file

        Returns:
            Dictionary with extracted session data
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
            session_data = {}

            # Extract session ID
            id_match = re.search(r'id:\s*"([^"]*)"', frontmatter)
            if id_match:
                session_data["id"] = id_match.group(1)

            # Extract room
            room_match = re.search(r'room:\s*"([^"]*)"', frontmatter)
            if room_match:
                session_data["room"] = room_match.group(1)

            # Extract agenda time
            agenda_match = re.search(r'agenda:\s*"([^"]*)"', frontmatter)
            if agenda_match:
                session_data["agenda"] = agenda_match.group(1)

            # Extract title
            title_match = re.search(r'title:\s*"([^"]*)"', frontmatter)
            if title_match:
                session_data["title"] = title_match.group(1)

            # Extract speaker slug
            speaker_match = re.search(r'speakers:\s*\n\s*-\s*"([^"]*)"', frontmatter)
            if speaker_match:
                session_data["speaker_slug"] = speaker_match.group(1)

            # Extract abstract (content after frontmatter)
            abstract_match = re.search(r"---\s+(.*?)\s+---(.*)", content, re.DOTALL)
            if abstract_match:
                session_data["abstract"] = abstract_match.group(2).strip()

            return session_data

        except Exception as e:
            print(f"   ⚠️  Failed to extract data from {filepath}: {str(e)}")
            return {}

    def _session_needs_update(self, session_data: Dict, existing_data: Dict) -> bool:
        """
        Check if session data has changed and needs updating.

        Args:
            session_data: Current session data from source
            existing_data: Existing session data from file

        Returns:
            True if update is needed, False otherwise
        """
        # Check key fields that would require an update
        fields_to_check = ["title", "room", "agenda", "speaker_slug", "abstract"]

        for field in fields_to_check:
            current_value = session_data.get(field, "")
            existing_value = existing_data.get(field, "")

            # If any field is different, update is needed
            if current_value != existing_value:
                return True

        return False

    def generate_session_filenames(self, sessions: List[Dict]) -> Dict[str, str]:
        """
        Generate session filenames based on level and persistent mapping.

        Args:
            sessions: List of session dictionaries

        Returns:
            Dictionary mapping session_id to filename
        """
        session_filenames = {}
        session_id_mapping = self.mapping_data.get("session_id_mapping", {})
        level_counters = {
            1: int(self.mapping_data.get("level_counters", {}).get("1", 0)),
            2: int(self.mapping_data.get("level_counters", {}).get("2", 0)),
            3: int(self.mapping_data.get("level_counters", {}).get("3", 0)),
            4: int(self.mapping_data.get("level_counters", {}).get("4", 0)),
            5: int(self.mapping_data.get("level_counters", {}).get("5", 0)),
        }

        # First, assign filenames to sessions that already have mappings
        for session in sessions:
            session_id = session.get("id", "")
            if not session_id:
                continue

            # If this session already has a mapping, use it
            if session_id in session_id_mapping:
                base_filename = session_id_mapping[session_id]
                # Ensure the filename has the .md extension
                filename = (
                    f"{base_filename}.md" if not base_filename.endswith(".md") else base_filename
                )
                session_filenames[session_id] = filename

        # Then, assign filenames to new sessions
        for session in sessions:
            session_id = session.get("id", "")
            if not session_id or session_id in session_filenames:
                continue

            # This is a new session, assign a new filename
            level = extract_session_level(session.get("level", ""))
            level_counters[level] += 1
            base_filename = f"acd{level}{level_counters[level]:02d}"
            filename = f"{base_filename}.md"

            # Add to mappings
            session_filenames[session_id] = filename
            session_id_mapping[session_id] = base_filename  # Store without extension

        # Update the mapping data
        self.mapping_data["session_id_mapping"] = session_id_mapping
        self.mapping_data["level_counters"] = {
            "1": level_counters[1],
            "2": level_counters[2],
            "3": level_counters[3],
            "4": level_counters[4],
            "5": level_counters[5],
        }

        # Save the updated mapping
        self._save_session_id_mapping()

        self.session_filenames = session_filenames
        return session_filenames

    def should_skip_session_file(
        self, filename: str, session_data: Dict, force_regenerate: bool = False
    ) -> Tuple[bool, bool]:
        """
        Determine if session file generation should be skipped or updated.

        Args:
            filename: Session filename
            session_data: Current session data
            force_regenerate: If True, never skip

        Returns:
            Tuple of (should_skip, should_update)
        """
        if force_regenerate:
            return False, False

        session_path = os.path.join(OUTPUT_DIR, "content", "sessions", filename)

        # If file doesn't exist, don't skip (need to generate)
        if not os.path.exists(session_path):
            return False, False

        # File exists, check if it needs updating
        existing_data = self._extract_session_data_from_file(session_path)
        needs_update = self._session_needs_update(session_data, existing_data)

        # If needs update, don't skip but mark for update
        if needs_update:
            return False, True

        # Otherwise, skip (file exists and doesn't need updating)
        return True, False

    def update_session_file(self, session_data: Dict, filename: str) -> bool:
        """
        Update an existing session file with new data.

        Args:
            session_data: Dictionary containing session information
            filename: Target filename for the session

        Returns:
            True if successful, False otherwise
        """
        try:
            # Generate new markdown content
            session_id = session_data.get("id", "")
            session_title = session_data.get("title", "")
            session_abstract = session_data.get("abstract", "")
            session_duration = session_data.get("duration", "")
            speaker_slug = session_data.get("speaker_slug", "")
            room = session_data.get("room", "")
            agenda = session_data.get("agenda", "")

            markdown_content = self._generate_session_markdown(
                session_id,
                session_title,
                session_abstract,
                session_duration,
                speaker_slug,
                room,
                agenda,
            )

            # Write updated markdown file
            session_path = os.path.join(OUTPUT_DIR, "content", "sessions", filename)
            with open(session_path, "w", encoding="utf-8") as f:
                f.write(markdown_content)

            self.updated_count += 1
            return True

        except Exception as e:
            print(f"   ⚠️  Failed to update session file {filename}: {str(e)}")
            self.failed_count += 1
            return False

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

        # Generate filenames first (using persistent mapping)
        session_filenames = self.generate_session_filenames(sessions)

        total_sessions = len(sessions)
        current = 0
        skipped_count = 0
        updated_count = 0

        for session in sessions:
            current += 1
            session_id = session.get("id", "")
            session_title = session.get("title", "Unknown Session")

            if not session_id or session_id not in session_filenames:
                print_progress(
                    current, total_sessions, f"⚠️ Skipped: Invalid session ID for {session_title}"
                )
                self.failed_count += 1
                continue

            filename = session_filenames[session_id]

            # Check if we should skip or update this session file
            should_skip, should_update = self.should_skip_session_file(
                filename, session, force_regenerate
            )

            if should_skip:
                print_progress(current, total_sessions, f"✓ Skipped: {filename} (no changes)")
                skipped_count += 1
            elif should_update:
                print_progress(
                    current, total_sessions, f"🔄 Updating: {filename} - {session_title}"
                )
                self.update_session_file(session, filename)
                updated_count += 1
            else:
                if force_regenerate:
                    print_progress(
                        current,
                        total_sessions,
                        f"🔄 Force regenerating: {filename} - {session_title}",
                    )
                else:
                    print_progress(
                        current, total_sessions, f"📝 Generating: {filename} - {session_title}"
                    )

                self.generate_session_file(session, filename)

        print(f"   ✓ Generated {self.generated_count} session files")
        if updated_count > 0:
            print(f"   🔄 Updated {updated_count} session files")
        if skipped_count > 0:
            print(f"   ✓ Skipped: {skipped_count} (no changes)")
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
            "updated_count": self.updated_count,
            "failed_count": self.failed_count,
            "session_filenames": self.session_filenames,
        }
