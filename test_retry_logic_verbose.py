#!/usr/bin/env python3
"""
Detailed test script for the retry logic with verbose logging to debug failures.
"""

from src.image_processor import ImageProcessor
from src.data_processor import DataProcessor
import logging
import os

def setup_detailed_logging():
    """Setup detailed logging to see what's happening."""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Enable debug logging for LinkedIn extractor
    linkedin_logger = logging.getLogger("src.linkedin_extractor")
    linkedin_logger.setLevel(logging.DEBUG)

def test_retry_logic_verbose():
    print('🧪 Testing Retry Logic with Detailed Logging...')
    print()

    # Setup detailed logging
    setup_detailed_logging()

    # Initialize the image processor (this loads the retry queue)
    processor = ImageProcessor()

    # Check authentication status
    print(f'🔐 LinkedIn Extractor Status:')
    if hasattr(processor, 'linkedin_extractor') and processor.linkedin_extractor:
        print(f'   • Enhanced extractor: ✅ Available')
        print(f'   • Authentication: {"✅ Authenticated" if processor.linkedin_extractor.is_authenticated() else "❌ Not authenticated"}')
        
        # Test authentication
        if processor.linkedin_extractor.is_authenticated():
            auth_test = processor.linkedin_extractor.test_authentication()
            print(f'   • Auth test result: {"✅ Working" if auth_test else "❌ Failed"}')
        
        print(f'   • Available strategies: {processor.linkedin_extractor.get_extraction_strategies()}')
    else:
        print(f'   • Enhanced extractor: ❌ Using basic extraction only')
    
    print()

    if not processor.retry_queue:
        print('❌ No retry queue found. Make sure missing_photos.csv exists with LinkedIn failures.')
        return

    print(f'📋 Found {len(processor.retry_queue)} items in retry queue')
    print()

    # Load speaker data (needed for the retry process)
    data_proc = DataProcessor()
    try:
        data_proc.load_excel_data()
        speakers = data_proc.deduplicate_speakers()
    except Exception as e:
        print(f'❌ Failed to load speaker data: {e}')
        return

    if not speakers:
        print('❌ No speaker data loaded.')
        return

    # Test just the retry logic with detailed logging
    processed_speakers = set()
    retry_successes = 0

    print('🔄 Testing retry logic with detailed logging...')
    for i, retry_item in enumerate(processor.retry_queue, 1):
        email = retry_item['email']
        print(f'\n[{i}/{len(processor.retry_queue)}] Testing: {retry_item["name"]}')
        print(f'   📧 Email: {email}')
        print(f'   🔗 LinkedIn: {retry_item.get("linkedin_url", "N/A")}')
        
        if email in speakers:
            speaker_data = speakers[email].copy()
            speaker_data['email'] = email
            
            # Show what data we're working with
            print(f'   📋 Speaker data:')
            print(f'      • Name: {speaker_data.get("name", "N/A")}')
            print(f'      • LinkedIn: {speaker_data.get("linkedin", "N/A")}')
            print(f'      • Custom photo: {speaker_data.get("custom_photo_url", "N/A")}')
            print(f'      • Slug: {speaker_data.get("slug", "N/A")}')
            
            # Test LinkedIn URL extraction specifically
            linkedin_url = speaker_data.get("linkedin", "")
            if linkedin_url:
                print(f'   🔍 Testing LinkedIn extraction...')
                try:
                    # Test the LinkedIn extraction directly
                    if hasattr(processor, 'linkedin_extractor') and processor.linkedin_extractor:
                        normalized_url = processor.linkedin_extractor.normalize_linkedin_url(linkedin_url)
                        print(f'      • Normalized URL: {normalized_url}')
                        
                        image_url = processor.linkedin_extractor.extract_profile_image_url(linkedin_url)
                        print(f'      • Extracted image URL: {image_url if image_url else "❌ None found"}')
                        
                        if image_url:
                            # Test if the image URL is accessible
                            import requests
                            try:
                                response = requests.head(image_url, timeout=5)
                                print(f'      • Image URL status: {response.status_code}')
                            except Exception as e:
                                print(f'      • Image URL test failed: {str(e)}')
                    else:
                        print(f'      • Using basic extraction method')
                        image_url = processor._extract_linkedin_image_url(linkedin_url)
                        print(f'      • Basic extraction result: {image_url if image_url else "❌ None found"}')
                        
                except Exception as e:
                    print(f'      • ❌ LinkedIn extraction error: {str(e)}')
                    import traceback
                    print(f'      • Full traceback: {traceback.format_exc()}')
            else:
                print(f'   ⚠️  No LinkedIn URL provided')
            
            print(f'   🎯 Running full process_speaker_image...')
            
            # Test the retry logic
            try:
                result = processor.process_speaker_image(speaker_data, retry_mode=True)
                
                if result == 'success':
                    print(f'   ✅ Retry successful!')
                    retry_successes += 1
                elif result == 'default':
                    print(f'   ❌ Still failed - using default image')
                else:
                    print(f'   ❌ Failed completely')
                
                # Check what file was actually created
                img_path = os.path.join('generated_files', 'content', 'speakers', speaker_data.get('slug', ''), 'img', 'photo.jpg')
                if os.path.exists(img_path):
                    file_size = os.path.getsize(img_path)
                    print(f'   📁 Created file: {img_path} ({file_size} bytes)')
                    
                    # Check if it's the default image by comparing with samples/unknown.jpg
                    default_path = 'samples/unknown.jpg'
                    if os.path.exists(default_path):
                        default_size = os.path.getsize(default_path)
                        if file_size == default_size:
                            print(f'   📁 File appears to be default image (same size as {default_path})')
                        else:
                            print(f'   📁 File appears to be custom image (different size from default)')
                else:
                    print(f'   📁 No file created at expected path: {img_path}')
                
            except Exception as e:
                print(f'   ❌ Error during process_speaker_image: {str(e)}')
                import traceback
                print(f'   📋 Full traceback: {traceback.format_exc()}')
            
            processed_speakers.add(email)
        else:
            print(f'   ⚠️  Speaker not found in current data')

    print()
    print(f'📊 RETRY TEST RESULTS:')
    print(f'   • Total retries attempted: {len(processed_speakers)}')
    print(f'   • Actual successes: {retry_successes}')
    print(f'   • Success rate: {(retry_successes/len(processed_speakers)*100):.1f}%' if processed_speakers else '0%')

    processor.close()

if __name__ == "__main__":
    test_retry_logic_verbose()
