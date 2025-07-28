"""
Main entry point for Hugo Speaker Generator.

Orchestrates the complete generation process from Excel data to Hugo markdown files.
"""

import sys
from src.data_processor import DataProcessor
from src.speaker_generator import SpeakerGenerator
from src.session_generator import SessionGenerator
from src.image_processor import ImageProcessor
from src.config import EMOJIS


def print_header():
    """Print application header."""
    print(f"{EMOJIS['rocket']} Starting Hugo Speaker Generator...")
    print("=" * 50)


def print_summary(data_stats, speaker_stats, session_stats, image_stats):
    """
    Print final summary statistics.

    Args:
        data_stats: Data processing statistics
        speaker_stats: Speaker generation statistics
        session_stats: Session generation statistics
        image_stats: Image processing statistics
    """
    print("\n" + "=" * 50)
    print(f"{EMOJIS['check']} GENERATION COMPLETE")
    print()

    # Summary statistics
    print(f"{EMOJIS['chart']} SUMMARY STATISTICS:")
    print(f"   • Speakers processed: {data_stats['unique_speakers']}")
    print(f"   • Sessions generated: {session_stats['generated_count']}")
    print(f"   • Images processed: {image_stats['processed_count']}")
    if image_stats["failed_count"] > 0:
        print(f"   • Images failed: {image_stats['failed_count']}")

    # Sessions by level
    print(f"\n{EMOJIS['bar_chart']} SESSIONS BY LEVEL:")
    level_names = {1: "Beginner", 2: "Intermediate", 3: "Advanced", 4: "Expert"}

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


def main():
    """Main execution function."""
    try:
        print_header()

        # Initialize processors
        data_processor = DataProcessor()
        speaker_generator = SpeakerGenerator()
        session_generator = SessionGenerator()
        image_processor = ImageProcessor()

        # Step 1: Load and process data
        print(f"{EMOJIS['chart']} Loading Excel data...")
        data_processor.load_excel_data()

        # Validate required columns
        missing_columns = data_processor.validate_required_columns()
        if missing_columns:
            print(
                f"   {EMOJIS['warning']} Missing required columns: {', '.join(missing_columns)}"
            )
            print("   Please check your Excel file and try again.")
            return 1

        # Step 2: Process speakers
        print(f"\n{EMOJIS['people']} Processing speakers...")
        speakers = data_processor.deduplicate_speakers()

        # Step 3: Prepare sessions data
        sessions = data_processor.prepare_sessions_data()

        # Step 4: Generate speaker profiles
        speaker_stats = speaker_generator.generate_all_speaker_profiles(speakers)

        # Step 5: Process speaker images
        image_stats = image_processor.process_all_speaker_images(speakers)

        # Step 6: Generate session files
        session_stats = session_generator.generate_all_session_files(sessions)

        # Step 7: Get final statistics
        data_stats = data_processor.get_statistics()
        data_stats["speakers"] = speakers
        data_stats["sessions"] = sessions

        # Step 8: Print summary
        print_summary(data_stats, speaker_stats, session_stats, image_stats)

        return 0

    except FileNotFoundError as e:
        print(f"\n{EMOJIS['warning']} Error: {str(e)}")
        print("Please ensure the Excel file exists in the data/ directory.")
        return 1

    except Exception as e:
        print(f"\n{EMOJIS['warning']} Unexpected error: {str(e)}")
        print("Please check the error details and try again.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
