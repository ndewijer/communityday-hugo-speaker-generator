"""
Utility functions for Hugo Speaker Generator.

Contains helper functions for string sanitization, data processing, and common operations.
"""

import re
import unicodedata
from typing import Dict, List


def sanitize_speaker_name(name: str) -> str:
    """
    Sanitize speaker name for use as directory/file slug.

    Args:
        name: Original speaker name

    Returns:
        Sanitized slug (lowercase, dashes, no special chars)
    """
    if not name:
        return "unknown-speaker"

    # Convert to lowercase
    slug = name.lower()

    # Remove accents and normalize unicode
    slug = unicodedata.normalize("NFKD", slug)
    slug = "".join(c for c in slug if not unicodedata.combining(c))

    # Replace spaces and special characters with dashes
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[-\s]+", "-", slug)

    # Remove leading/trailing dashes
    slug = slug.strip("-")

    return slug if slug else "unknown-speaker"


def generate_unique_speaker_slug(name: str, existing_slugs: set) -> str:
    """
    Generate a unique speaker slug, handling conflicts with numeric suffixes.

    Args:
        name: Speaker name
        existing_slugs: Set of already used slugs

    Returns:
        Unique slug
    """
    base_slug = sanitize_speaker_name(name)

    if base_slug not in existing_slugs:
        return base_slug

    counter = 1
    while f"{base_slug}-{counter}" in existing_slugs:
        counter += 1

    return f"{base_slug}-{counter}"


def extract_session_level(level_string: str) -> int:
    """
    Extract numeric level from session level string.

    Args:
        level_string: e.g., "300 (Advanced)"

    Returns:
        Numeric level (1-4), defaults to 2 if not found
    """
    if not level_string:
        return 2  # Default to intermediate

    # Extract first number from string
    match = re.search(r"(\d+)", level_string)
    if match:
        level_num = int(match.group(1))
        if level_num >= 400:
            return 4
        elif level_num >= 300:
            return 3
        elif level_num >= 200:
            return 2
        else:
            return 1

    return 2  # Default fallback


def map_duration_to_standard(duration_string: str) -> str:
    """
    Map duration string to standardized duration (30 or 60).

    Args:
        duration_string: e.g., "20-30 minutes", "40-50 minutes"

    Returns:
        "30" or "60"
    """
    if not duration_string:
        return "30"

    # Extract all numbers from the string
    numbers = re.findall(r"\d+", duration_string)

    if not numbers:
        return "30"

    # Get the highest number mentioned
    max_duration = max(int(num) for num in numbers)

    # Map to standard durations
    if max_duration <= 30:
        return "30"
    else:
        return "60"


def process_multiple_durations(duration_string: str) -> List[str]:
    """
    Process duration string that may contain multiple options.

    Args:
        duration_string: e.g., "20-30 minutes, 40-50 minutes"

    Returns:
        List of markdown lines for duration field
    """
    if not duration_string:
        return ['duration: ""']

    # Split by comma to find multiple durations
    durations = [d.strip() for d in duration_string.split(",")]

    if len(durations) == 1:
        # Single duration
        mapped_duration = map_duration_to_standard(durations[0])
        return [f'duration: "{mapped_duration}"']
    else:
        # Multiple durations - comment all out
        lines = ["# Multiple duration options - uncomment one:"]
        for dur in durations:
            mapped_duration = map_duration_to_standard(dur)
            lines.append(f'# duration: "{mapped_duration}"')
        return lines


def safe_get_field(row: Dict, field_name: str, default: str = "") -> str:
    """
    Safely get field value from row, handling missing/empty values.

    Args:
        row: Data row dictionary
        field_name: Field name to retrieve
        default: Default value if field is missing/empty

    Returns:
        Field value or default
    """
    value = row.get(field_name, default)

    # Handle various empty value types
    if value is None or value == "" or str(value).strip() == "" or str(value).lower() == "nan":
        return default

    return str(value).strip()


def format_linkedin_field(linkedin_url: str) -> str:
    """
    Format LinkedIn field for markdown output.

    Args:
        linkedin_url: LinkedIn URL or empty string

    Returns:
        Formatted markdown line
    """
    if linkedin_url and linkedin_url.strip():
        return f'linkedin: "{linkedin_url.strip()}"'
    else:
        return '# linkedin: ""'


def format_bio_content(bio: str) -> str:
    """
    Format bio content for markdown output.

    Args:
        bio: Bio text

    Returns:
        Formatted bio content
    """
    if not bio or bio.strip() == "":
        return '""'

    # Clean up the bio text
    bio = bio.strip()

    # Replace multiple newlines with double newlines for proper markdown
    bio = re.sub(r"\n\s*\n", "\n\n", bio)

    return bio


def validate_session_id(session_id: str) -> bool:
    """
    Validate session ID format.

    Args:
        session_id: Session ID to validate

    Returns:
        True if valid format
    """
    if not session_id:
        return False

    # Check if it looks like a UUID or valid session ID
    uuid_pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    return bool(re.match(uuid_pattern, session_id, re.IGNORECASE))


def print_progress(current: int, total: int, item_name: str) -> None:
    """
    Print progress indicator.

    Args:
        current: Current item number
        total: Total items
        item_name: Name of current item
    """
    print(f"   [{current}/{total}] {item_name}")
