"""
Data processing module for Hugo Speaker Generator.

Handles Excel file loading, validation, and speaker deduplication.
"""

import os
from typing import Dict, List

import pandas as pd

from .config import EXCEL_FILE_PATH, SESSION_FIELD_MAPPING, SPEAKER_FIELD_MAPPING
from .utils import (
    generate_unique_speaker_slug,
    parse_and_slugify_sponsors,
    safe_get_field,
    validate_session_id,
)


class DataProcessor:
    """Handles loading and processing of Excel data."""

    def __init__(self):
        """Initialize DataProcessor with empty data structures."""
        self.df = None
        self.speakers = {}
        self.sessions = []
        self.warnings = []

    def load_excel_data(self) -> pd.DataFrame:
        """
        Load Excel data from the configured file path.

        Returns:
            DataFrame with loaded data

        Raises:
            FileNotFoundError: If Excel file doesn't exist
            Exception: If file cannot be read
        """
        if not os.path.exists(EXCEL_FILE_PATH):
            raise FileNotFoundError(f"Excel file not found: {EXCEL_FILE_PATH}")

        try:
            self.df = pd.read_excel(EXCEL_FILE_PATH)
            print(f"   ✓ Loaded {len(self.df)} submissions")
            return self.df
        except Exception as e:
            raise Exception(f"Failed to read Excel file: {str(e)}")

    def validate_required_columns(self) -> List[str]:
        """
        Validate that all required columns exist in the DataFrame.

        Returns:
            List of missing columns
        """
        if self.df is None:
            return ["No data loaded"]

        required_columns = set(SPEAKER_FIELD_MAPPING.values()) | set(SESSION_FIELD_MAPPING.values())
        required_columns.add("Email Address")  # Unique identifier

        existing_columns = set(self.df.columns)
        missing_columns = required_columns - existing_columns

        return list(missing_columns)

    def deduplicate_speakers(self) -> Dict[str, Dict]:
        """
        Deduplicate speakers by email address and collect their sessions.

        Returns:
            Dictionary mapping email to speaker data with sessions
        """
        if self.df is None:
            raise ValueError("No data loaded. Call load_excel_data() first.")

        speakers = {}
        existing_slugs = set()

        for _, row in self.df.iterrows():
            email = safe_get_field(row, "Email Address")

            if not email:
                self.warnings.append(f"Row missing email address, skipping")
                continue

            # Get speaker data
            speaker_name = safe_get_field(row, SPEAKER_FIELD_MAPPING["title"])
            speaker_headline = safe_get_field(row, SPEAKER_FIELD_MAPPING["headline"])
            speaker_bio = safe_get_field(row, SPEAKER_FIELD_MAPPING["bio"])
            linkedin_url = safe_get_field(row, SPEAKER_FIELD_MAPPING["linkedin"])
            custom_photo_url = safe_get_field(
                row, "Link to photo (Optional, defaults to LinkedIn Profile)"
            )

            # Get session data
            session_id = safe_get_field(row, SESSION_FIELD_MAPPING["id"])
            session_title = safe_get_field(row, SESSION_FIELD_MAPPING["title"])
            session_abstract = safe_get_field(row, SESSION_FIELD_MAPPING["abstract"])
            session_duration = safe_get_field(row, SESSION_FIELD_MAPPING["duration"])
            session_level = safe_get_field(row, "Session Level")
            session_room = safe_get_field(row, SESSION_FIELD_MAPPING["room"])
            session_agenda = safe_get_field(row, SESSION_FIELD_MAPPING["agenda"])
            session_sponsors = safe_get_field(row, SESSION_FIELD_MAPPING["sponsors"])

            # Validate session ID
            if not validate_session_id(session_id):
                self.warnings.append(f"Invalid session ID format: {session_id}")

            # Create or update speaker entry
            if email not in speakers:
                # Generate unique slug for new speaker
                slug = generate_unique_speaker_slug(speaker_name, existing_slugs)
                existing_slugs.add(slug)

                speakers[email] = {
                    "name": speaker_name,
                    "headline": speaker_headline,
                    "bio": speaker_bio,
                    "linkedin": linkedin_url,
                    "custom_photo_url": custom_photo_url,
                    "slug": slug,
                    "sessions": [],
                }
            else:
                # Update speaker data if we find better information in subsequent rows
                # Prioritize non-empty values
                if custom_photo_url and not speakers[email].get("custom_photo_url"):
                    speakers[email]["custom_photo_url"] = custom_photo_url
                if linkedin_url and not speakers[email].get("linkedin"):
                    speakers[email]["linkedin"] = linkedin_url
                if speaker_headline and not speakers[email].get("headline"):
                    speakers[email]["headline"] = speaker_headline
                if speaker_bio and not speakers[email].get("bio"):
                    speakers[email]["bio"] = speaker_bio

            # Add session to speaker
            session_data = {
                "id": session_id,
                "title": session_title,
                "abstract": session_abstract,
                "duration": session_duration,
                "level": session_level,
                "room": session_room,
                "agenda": session_agenda,
                "sponsors": session_sponsors,
            }

            speakers[email]["sessions"].append(session_data)

        self.speakers = speakers
        print(f"   ✓ Found {len(speakers)} unique speakers")

        return speakers

    def prepare_sessions_data(self) -> List[Dict]:
        """
        Prepare sessions data for filename generation and processing.

        Group by session ID and collect all speakers for each session.

        Returns:
            List of session dictionaries with speaker slugs
        """
        sessions_by_id = {}

        for email, speaker_data in self.speakers.items():
            speaker_slug = speaker_data["slug"]

            for session in speaker_data["sessions"]:
                session_id = session["id"]

                if session_id not in sessions_by_id:
                    # Parse sponsor slugs from sponsor string
                    sponsor_slugs = parse_and_slugify_sponsors(session.get("sponsors", ""))

                    # Create new session entry
                    sessions_by_id[session_id] = {
                        "id": session_id,
                        "title": session["title"],
                        "abstract": session["abstract"],
                        "duration": session["duration"],
                        "level": session["level"],
                        "room": session.get("room", ""),
                        "agenda": session.get("agenda", ""),
                        "speaker_slugs": [speaker_slug],
                        "speaker_names": [speaker_data["name"]],
                        "sponsor_slugs": sponsor_slugs,
                    }
                else:
                    # Add this speaker to existing session
                    if speaker_slug not in sessions_by_id[session_id]["speaker_slugs"]:
                        sessions_by_id[session_id]["speaker_slugs"].append(speaker_slug)
                        sessions_by_id[session_id]["speaker_names"].append(speaker_data["name"])

        # Convert dictionary to list
        sessions = list(sessions_by_id.values())
        self.sessions = sessions
        return sessions

    def get_statistics(self) -> Dict:
        """
        Get processing statistics.

        Returns:
            Dictionary with processing statistics
        """
        stats = {
            "total_submissions": len(self.df) if self.df is not None else 0,
            "unique_speakers": len(self.speakers),
            "total_sessions": len(self.sessions),
            "warnings_count": len(self.warnings),
            "warnings": self.warnings,
        }

        # Count sessions by level
        level_counts = {}
        for session in self.sessions:
            level = session.get("level", "Unknown")
            level_counts[level] = level_counts.get(level, 0) + 1

        stats["sessions_by_level"] = level_counts

        return stats

    def get_speakers_missing_linkedin(self) -> List[Dict]:
        """
        Get list of speakers missing LinkedIn profiles.

        Returns:
            List of speaker data for those missing LinkedIn
        """
        missing_linkedin = []

        for email, speaker_data in self.speakers.items():
            if not speaker_data.get("linkedin"):
                missing_linkedin.append(
                    {
                        "name": speaker_data["name"],
                        "email": email,
                        "slug": speaker_data["slug"],
                    }
                )

        return missing_linkedin

    def get_sessions_with_multiple_durations(self) -> List[Dict]:
        """
        Get sessions that have multiple duration options.

        Returns:
            List of sessions with multiple durations
        """
        multiple_durations = []

        for session in self.sessions:
            duration_str = session.get("duration", "")
            if "," in duration_str:
                multiple_durations.append(
                    {
                        "id": session["id"],
                        "title": session["title"],
                        "duration": duration_str,
                    }
                )

        return multiple_durations
