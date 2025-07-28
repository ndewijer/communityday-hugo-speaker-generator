#!/usr/bin/env python3
"""
Test script for the enhanced LinkedIn image extractor.

This script demonstrates the new robust LinkedIn profile image extraction capabilities.
"""

from src.linkedin_extractor import LinkedInImageExtractor


def test_linkedin_urls():
    """Test the LinkedIn extractor with sample URLs from the missing_photos.csv file."""

    # Sample LinkedIn URLs from the missing photos CSV
    test_urls = [
        "https://www.linkedin.com/in/matheus-das-merces/",
        "https://www.linkedin.com/in/tpschmidt",
        "https://www.linkedin.com/in/katerinapackova/",
        "https://www.linkedin.com/in/ivica-kolenka%C5%A1-8b333895/",
        "https://www.linkedin.com/in/davidepellegatta/",
        "www.linkedin.com/in/lazarveljovic",
        "https://www.linkedin.com/in/krisgillespie/",
        "https://linkedin.com/in/theburningmonk",
    ]

    print("🔍 Testing Enhanced LinkedIn Image Extractor")
    print("=" * 60)

    # Initialize the extractor
    extractor = LinkedInImageExtractor(request_timeout=15, retry_attempts=2)

    print(
        f"📋 Available extraction strategies: {', '.join(extractor.get_extraction_strategies())}"
    )
    print()

    successful_extractions = 0
    total_tests = len(test_urls)

    for i, url in enumerate(test_urls, 1):
        print(f"[{i}/{total_tests}] Testing: {url}")

        try:
            # Normalize the URL first
            normalized_url = extractor.normalize_linkedin_url(url)
            print(f"   📝 Normalized: {normalized_url}")

            # Extract the image URL
            image_url = extractor.extract_profile_image_url(url)

            if image_url:
                print(f"   ✅ Success: {image_url}")
                successful_extractions += 1
            else:
                print(f"   ❌ Failed: No image URL found")

        except Exception as e:
            print(f"   ⚠️  Error: {str(e)}")

        print()

    # Cleanup
    extractor.close()

    # Summary
    print("=" * 60)
    print(f"📊 RESULTS SUMMARY:")
    print(f"   • Total URLs tested: {total_tests}")
    print(f"   • Successful extractions: {successful_extractions}")
    print(f"   • Success rate: {(successful_extractions/total_tests)*100:.1f}%")

    if successful_extractions > 0:
        print(
            f"   🎉 Improvement detected! The new extractor found {successful_extractions} images."
        )
    else:
        print(
            f"   ⚠️  No images extracted. This may be due to LinkedIn's anti-scraping measures."
        )
        print(
            f"      Consider running with Selenium support or trying at different times."
        )


def test_url_normalization():
    """Test URL normalization functionality."""

    print("\n🔧 Testing URL Normalization")
    print("-" * 40)

    test_cases = [
        "linkedin.com/in/johndoe",
        "www.linkedin.com/in/johndoe",
        "https://www.linkedin.com/in/johndoe",
        "http://linkedin.com/in/johndoe",
        "/in/johndoe",
        "linkedin.com/in/johndoe/",
        "www.linkedin.com/in/lazarveljovic",
    ]

    extractor = LinkedInImageExtractor()

    for test_url in test_cases:
        normalized = extractor.normalize_linkedin_url(test_url)
        print(f"   {test_url:<35} → {normalized}")

    extractor.close()


def main():
    """Main test function."""

    print("🚀 LinkedIn Image Extractor Test Suite")
    print("=" * 60)

    # Test URL normalization
    test_url_normalization()

    # Test actual LinkedIn extraction
    test_linkedin_urls()

    print("\n💡 NOTES:")
    print("   • LinkedIn actively blocks automated scraping attempts")
    print("   • Success rates may vary depending on LinkedIn's current measures")
    print("   • For production use, consider implementing delays between requests")
    print("   • Selenium-based extraction may have higher success rates")
    print("   • Some profiles may have privacy settings that prevent image access")


if __name__ == "__main__":
    main()
