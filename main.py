"""
Main entry point for Hugo Speaker Generator.

Orchestrates the complete generation process from Excel data to Hugo markdown files.
"""

import argparse
import sys

from src.config import EMOJIS
from src.data_processor import DataProcessor
from src.image_processor import ImageProcessor
from src.session_generator import SessionGenerator
from src.speaker_generator import SpeakerGenerator


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description=(
            "Hugo Speaker Generator - Generate speaker profiles and session files from Excel data"
        )
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force regeneration of all files (ignore existing files)",
    )
    return parser.parse_args()


def print_header():
    """Print application header."""
    print(f"{EMOJIS['rocket']} Starting Hugo Speaker Generator...")
    print("=" * 50)


def print_summary(data_stats, speaker_stats, session_stats, image_stats, force_regenerate=False):
    """
    Print final summary statistics.

    Args:
        data_stats: Data processing statistics
        speaker_stats: Speaker generation statistics
        session_stats: Session generation statistics
        image_stats: Image processing statistics
        force_regenerate: Whether force regeneration was used
    """
    print("\n" + "=" * 50)
    print(f"{EMOJIS['check']} GENERATION COMPLETE")
    print()

    # Summary statistics
    print(f"{EMOJIS['chart']} SUMMARY STATISTICS:")
    print(f"   • Speakers processed: {data_stats['unique_speakers']}")
    print(f"   • Speaker profiles generated: {speaker_stats['generated_count']}")
    if not force_regenerate and image_stats.get("skipped_count", 0) > 0:
        print(f"   • Speaker profiles skipped: {image_stats.get('skipped_count', 0)}")
    print(f"   • Sessions generated: {session_stats['generated_count']}")
    if session_stats.get("updated_count", 0) > 0:
        print(f"   • Sessions updated: {session_stats.get('updated_count', 0)}")

    # Count sessions with multiple speakers
    multi_speaker_sessions = 0
    for session in data_stats.get("sessions", []):
        if len(session.get("speaker_slugs", [])) > 1:
            multi_speaker_sessions += 1

    if multi_speaker_sessions > 0:
        print(f"   • Sessions with multiple speakers: {multi_speaker_sessions}")

    print(f"   • Images processed: {image_stats['processed_count']}")
    if image_stats.get("skipped_count", 0) > 0:
        print(f"   • Images skipped: {image_stats.get('skipped_count', 0)}")
    if image_stats["failed_count"] > 0:
        print(f"   • Images failed: {image_stats['failed_count']}")

    # Sessions by level
    print(f"\n{EMOJIS['bar_chart']} SESSIONS BY LEVEL:")
    level_names = {1: "Beginner", 2: "Intermediate", 3: "Advanced", 4: "Expert", 5: "Principal"}

    # Get level statistics from session generator
    session_gen = SessionGenerator()
    level_counts = session_gen.get_level_statistics(data_stats.get("sessions", []))

    for level, count in level_counts.items():
        if count > 0:
            level_name = level_names.get(level, f"Level {level}")
            print(f"   • Level {level} ({level_name}): {count} sessions")

    # Warnings
    warnings = []

    # Missing LinkedIn profiles
    missing_linkedin_count = len(
        [s for s in data_stats.get("speakers", {}).values() if not s.get("linkedin")]
    )
    if missing_linkedin_count > 0:
        warnings.append(f"{missing_linkedin_count} speakers missing LinkedIn profiles")

    # Multiple durations
    multiple_durations_count = len(
        [s for s in data_stats.get("sessions", []) if "," in s.get("duration", "")]
    )
    if multiple_durations_count > 0:
        warnings.append(
            f"{multiple_durations_count} sessions with multiple durations (commented out)"
        )

    # Speakers without sessions
    speakers_without_sessions = []
    for email, speaker_data in data_stats.get("speakers", {}).items():
        if not speaker_data.get("sessions"):
            speakers_without_sessions.append(speaker_data.get("name", "Unknown"))

    if speakers_without_sessions:
        warnings.append(f"{len(speakers_without_sessions)} speakers without session data")

    # Image issues
    if image_stats["missing_photos_count"] > 0:
        warnings.append(
            f"{image_stats['missing_photos_count']} image issues (see missing_photos.csv)"
        )

    # General warnings from data processing
    if data_stats.get("warnings"):
        warnings.extend(data_stats["warnings"][:3])  # Show first 3 warnings

    if warnings:
        print(f"\n{EMOJIS['warning']} WARNINGS:")
        for warning in warnings:
            print(f"   • {warning}")

    print(f"\n{EMOJIS['folder']} OUTPUT LOCATION: ./generated_files/")

    if force_regenerate:
        print(f"\n🔄 Force regeneration was enabled - all files were rebuilt")


def main():
    """Main execution function."""
    try:
        # Parse command line arguments
        args = parse_arguments()
        force_regenerate = args.force

        print_header()

        if force_regenerate:
            print("🔄 Force regeneration enabled - all existing files will be rebuilt")

        # Initialize processors
        data_processor = DataProcessor()
        speaker_generator = SpeakerGenerator()
        session_generator = SessionGenerator()
        image_processor = ImageProcessor()

        # Step 1: Load and process data
        print(f"   {EMOJIS['chart']} Loading Excel data...")
        data_processor.load_excel_data()

        # Validate required columns
        missing_columns = data_processor.validate_required_columns()
        if missing_columns:
            print(f"   {EMOJIS['warning']} Missing required columns: {', '.join(missing_columns)}")
            print("   Please check your Excel file and try again.")
            return 1

        # Step 2: Process speakers
        print(f"\n{EMOJIS['people']} Processing speakers...")
        speakers = data_processor.deduplicate_speakers()

        # Step 3: Prepare sessions data
        sessions = data_processor.prepare_sessions_data()

        # Step 4: Setup LinkedIn login if needed (only if Selenium extractor is available)
        if hasattr(image_processor, "linkedin_extractor") and image_processor.linkedin_extractor:
            print(f"\n🔐 Setting up LinkedIn authentication...")
            if not image_processor.setup_linkedin_login():
                print("❌ LinkedIn login failed. Continuing with basic extraction...")

        # Step 5: Generate speaker profiles
        speaker_stats = speaker_generator.generate_all_speaker_profiles(speakers, force_regenerate)

        # Step 6: Process speaker images
        image_stats = image_processor.process_all_speaker_images(speakers, force_regenerate)

        # Step 7: Generate session files
        session_stats = session_generator.generate_all_session_files(sessions, force_regenerate)

        # Step 7.5: Handle removed speakers (those no longer in the data or without sessions)
        speaker_generator.handle_removed_speakers(speakers)

        # Step 8: Get final statistics
        data_stats = data_processor.get_statistics()
        data_stats["speakers"] = speakers
        data_stats["sessions"] = sessions

        # Step 9: Print summary
        print_summary(data_stats, speaker_stats, session_stats, image_stats, force_regenerate)

        # Cleanup
        image_processor.close()

        return 0

    except FileNotFoundError as e:
        print(f"\n{EMOJIS['warning']} Error: {str(e)}")
        print("Please ensure the Excel file exists in the data/ directory.")
        return 1

    except KeyboardInterrupt:
        print(f"\n\n{EMOJIS['warning']} Process interrupted by user.")
        return 1

    except Exception as e:
        print(f"\n{EMOJIS['warning']} Unexpected error: {str(e)}")
        print("Please check the error details and try again.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
