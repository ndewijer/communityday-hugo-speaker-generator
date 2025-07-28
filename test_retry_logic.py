#!/usr/bin/env python3
"""Quick test script for the retry logic only."""

from src.image_processor import ImageProcessor
from src.data_processor import DataProcessor


def test_retry_logic():
    """Test the retry logic for LinkedIn image extraction."""
    print("🧪 Testing Retry Logic Only...")
    print()

    # Initialize the image processor (this loads the retry queue)
    processor = ImageProcessor()

    if not processor.retry_queue:
        print(
            "❌ No retry queue found. Make sure missing_photos.csv exists with LinkedIn failures."
        )
        return

    print(f"📋 Found {len(processor.retry_queue)} items in retry queue")
    print()

    # Load speaker data (needed for the retry process)
    data_proc = DataProcessor()
    try:
        data_proc.load_excel_data()
        speakers = data_proc.deduplicate_speakers()
    except Exception as e:
        print(f"❌ Failed to load speaker data: {e}")
        return

    if not speakers:
        print("❌ No speaker data loaded.")
        return

    # Test just the retry logic
    processed_speakers = set()
    retry_successes = 0

    print("🔄 Testing retry logic...")
    for retry_item in processor.retry_queue:
        email = retry_item["email"]
        if email in speakers:
            speaker_data = speakers[email].copy()
            speaker_data["email"] = email

            print(f'   🔄 Testing: {retry_item["name"]}')

            # Test the retry logic
            result = processor.process_speaker_image(speaker_data, retry_mode=True)
            if result == "success":
                print(f"   ✅ Retry successful!")
                retry_successes += 1
            elif result == "default":
                print(f"   ❌ Still failed - using default image")
            else:
                print(f"   ❌ Failed completely")

            processed_speakers.add(email)
        else:
            print(f'   ⚠️  Speaker {retry_item["name"]} not found in current data')

    print()
    print(f"📊 RETRY TEST RESULTS:")
    print(f"   • Total retries attempted: {len(processed_speakers)}")
    print(f"   • Actual successes: {retry_successes}")
    print(
        f"   • Success rate: {(retry_successes/len(processed_speakers)*100):.1f}%"
        if processed_speakers
        else "0%"
    )

    processor.close()


if __name__ == "__main__":
    test_retry_logic()
