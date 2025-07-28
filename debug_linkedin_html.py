#!/usr/bin/env python3
"""
Debug script to examine LinkedIn HTML content and find image URLs.
"""

from src.linkedin_extractor import LinkedInImageExtractor
import os
import re


def debug_linkedin_html():
    print("🔍 Debugging LinkedIn HTML Content...")
    print()

    # Get cookies
    cookies = None
    if os.path.exists("linkedin_cookies.txt"):
        cookies = "linkedin_cookies.txt"
    elif os.environ.get("LINKEDIN_COOKIES"):
        cookies = os.environ.get("LINKEDIN_COOKIES")

    if not cookies:
        print("❌ No cookies found")
        return

    # Test with a sample URL
    extractor = LinkedInImageExtractor(cookies=cookies)
    test_url = "https://www.linkedin.com/in/tpschmidt"

    print(f"🔍 Fetching: {test_url}")

    # Get the HTML content
    headers = extractor.headers.copy()
    headers["User-Agent"] = extractor.ua.random

    response = extractor.session.get(
        test_url, headers=headers, timeout=15, allow_redirects=True
    )
    print(f"📄 HTTP Status: {response.status_code}")

    if response.status_code != 200:
        print("❌ Failed to get LinkedIn page")
        return

    html_content = response.text
    print(f"📄 HTML Length: {len(html_content)} characters")

    # Search for various image URL patterns
    patterns_to_test = [
        # LinkedIn media URLs (broad search)
        (r'https://media\.licdn\.com/[^"\s]+', "All LinkedIn media URLs"),
        (r'https://media\.licdn\.com/dms/image/[^"\s]+', "DMS image URLs"),
        (r'https://media\.licdn\.com/dms/image/v2/[^"\s]+', "DMS v2 image URLs"),
        (r'profile-displayphoto[^"\s]*', "Profile displayphoto references"),
        # Meta tags
        (r'<meta[^>]+property="og:image"[^>]+content="([^"]+)"', "OpenGraph image"),
        (r'<meta[^>]+name="twitter:image"[^>]+content="([^"]+)"', "Twitter image"),
        # Image elements
        (r'<img[^>]+src="([^"]*media\.licdn\.com[^"]*)"', "IMG src attributes"),
        # JSON data
        (r'"profilePicture":"([^"]+)"', "JSON profilePicture"),
        (r'"image":"([^"]*media\.licdn\.com[^"]*)"', "JSON image field"),
    ]

    print("\n🔍 Searching for image URL patterns...")
    for pattern, description in patterns_to_test:
        matches = re.findall(pattern, html_content, re.IGNORECASE)
        print(f"\n📋 {description}: {len(matches)} matches")

        if matches:
            # Show first few matches
            for i, match in enumerate(matches[:3]):
                if len(match) > 100:
                    print(f"   {i+1}. {match[:100]}...")
                else:
                    print(f"   {i+1}. {match}")

            if len(matches) > 3:
                print(f"   ... and {len(matches) - 3} more")

    # Look for any references to profile photos
    print("\n🔍 Searching for profile photo references...")
    photo_keywords = ["profile-photo", "profilePhoto", "profile_photo", "displayphoto"]
    for keyword in photo_keywords:
        count = html_content.lower().count(keyword.lower())
        print(f'   "{keyword}": {count} occurrences')

    # Save HTML for manual inspection
    with open("debug_linkedin.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"\n💾 HTML saved to debug_linkedin.html for manual inspection")

    extractor.close()


if __name__ == "__main__":
    debug_linkedin_html()
