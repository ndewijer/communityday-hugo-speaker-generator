# Hugo Speaker Generator

A Python tool to generate Hugo markdown files for AWS Community Day speakers and sessions from Excel data containing Call for Papers responses.

## Features

- **Speaker Profile Generation**: Creates individual speaker pages with bio, headline, and LinkedIn information
- **Session File Generation**: Generates session pages with proper filename conventions (acd{level}{number}.md)
- **Image Processing**: Downloads and processes speaker images from LinkedIn or custom URLs, with fallback to default image
- **Data Validation**: Handles missing data gracefully and provides detailed reporting
- **Duplicate Handling**: Deduplicates speakers by email and handles name conflicts
- **Progress Tracking**: Real-time console output with progress indicators and statistics

## Project Structure

```
├── src/                          # Source code modules
│   ├── config.py                 # Configuration and field mappings
│   ├── data_processor.py         # Excel data processing
│   ├── speaker_generator.py      # Speaker page generation
│   ├── session_generator.py      # Session page generation
│   ├── image_processor.py        # Image downloading and processing
│   └── utils.py                  # Utility functions
├── generated_files/              # Output directory
│   └── content/
│       ├── speakers/             # Generated speaker profiles
│       └── sessions/             # Generated session files
├── data/                         # Input Excel files (gitignored)
├── samples/                      # Default images and samples
├── template/                     # Reference templates
├── main.py                       # Main entry point
├── requirements.txt              # Python dependencies
└── implementation_plan.md        # Detailed implementation documentation
```

## Setup

1. **Create Virtual Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install Dependencies**:

   **Option A: Basic Installation (Recommended for most users)**
   ```bash
   pip install -r requirements-basic.txt
   ```

   **Option B: Enhanced Installation (Better LinkedIn extraction)**
   ```bash
   pip install -r requirements.txt
   ```

3. **Prepare Data**:
   - Place your Excel file in the `data/` directory
   - Ensure it's named `responses+votes.xlsx` or update the path in `src/config.py`

## Usage

Run the generator:
```bash
source venv/bin/activate  # Activate virtual environment
python main.py
```

The tool will:
1. Load and validate Excel data
2. Process and deduplicate speakers
3. Generate speaker profile pages
4. Download and process speaker images
5. Generate session files with proper naming
6. Provide detailed statistics and warnings

## Output

### Speaker Files
Generated in `generated_files/content/speakers/{speaker-slug}/`:
- `index.md` - Speaker profile with YAML frontmatter
- `img/photo.jpg` - Processed square speaker image

### Session Files
Generated in `generated_files/content/sessions/`:
- `acd{level}{number}.md` - Session files with proper naming convention
- Level 1 (Beginner): acd101.md, acd102.md, etc.
- Level 2 (Intermediate): acd201.md, acd202.md, etc.
- Level 3 (Advanced): acd301.md, acd302.md, etc.
- Level 4 (Expert): acd401.md, acd402.md, etc.

### Reports
- `missing_photos.csv` - Log of image processing issues

## Configuration

Edit `src/config.py` to customize:
- Field mappings between Excel columns and output fields
- File paths and naming conventions
- Image processing settings
- Duration mappings

## Data Requirements

Your Excel file should contain these columns:
- `Session_ID` - Unique session identifier
- `Email Address` - Speaker unique identifier
- `Speaker Name` - Speaker's full name
- `Speaker Headline` - Speaker's professional headline
- `Bio` - Speaker biography
- `Link to your LinkedIn profile` - LinkedIn URL (optional)
- `Link to photo (Optional, defaults to LinkedIn Profile)` - Custom photo URL
- `Title of Session` - Session title
- `Abstract of Session` - Session description
- `Session Duration` - Duration (e.g., "20-30 minutes", "40-50 minutes")
- `Session Level` - Level (e.g., "100 (Beginner)", "300 (Advanced)")

## Features in Detail

### Speaker Processing
- Deduplicates speakers by email address
- Generates unique slugs for speaker directories
- Handles name conflicts with numeric suffixes
- Comments out empty LinkedIn fields

### Session Processing
- Sorts sessions by Session_ID for consistent ordering
- Separate counters per level for filename generation
- Handles multiple duration options by commenting them out
- Maps durations to standard values (30 or 60 minutes)

### Image Processing
- Downloads from custom photo URLs first
- Falls back to LinkedIn profile image extraction
- Uses default unknown.jpg for missing images
- Crops images to square format and resizes
- Logs all processing issues to CSV

### Error Handling
- Graceful handling of missing data
- Detailed error reporting and warnings
- Continues processing even when individual items fail
- Comprehensive statistics and summary

## Example Output

```
🚀 Starting Hugo Speaker Generator...
==================================================
📊 Loading Excel data...
   ✓ Loaded 22 submissions

👥 Processing speakers...
   ✓ Found 17 unique speakers

📝 Generating speaker profiles...
   [1/17] Sandro Volpciella
   ...
   ✓ Generated 17 speaker profiles

🖼️  Processing speaker images...
   ...
   ✓ Downloaded: 17
   ⚠️  Issues logged: 17 (see missing_photos.csv)

📋 Generating session files...
   ...
   ✓ Generated 22 session files

==================================================
✅ GENERATION COMPLETE

📊 SUMMARY STATISTICS:
   • Speakers processed: 17
   • Sessions generated: 22
   • Images processed: 17

📈 SESSIONS BY LEVEL:
   • Level 1 (Beginner): 2 sessions
   • Level 2 (Intermediate): 9 sessions
   • Level 3 (Advanced): 11 sessions

📁 OUTPUT LOCATION: ./generated_files/
```

## Troubleshooting

### Common Issues

1. **Missing Dependencies**: Ensure virtual environment is activated and dependencies are installed
2. **Excel File Not Found**: Check file path in `src/config.py`
3. **LinkedIn Image Failures**: Expected due to anti-scraping measures, fallback images are used
4. **Permission Errors**: Ensure write permissions for `generated_files/` directory

### Enhanced LinkedIn Image Extraction

The system now includes a robust LinkedIn profile image extractor with multiple strategies:

- **Multiple Extraction Methods**: Uses requests + BeautifulSoup, rotating user agents, and optional Selenium WebDriver
- **Advanced HTML Parsing**: Extracts images from JSON-LD data, meta tags, and JavaScript content
- **Improved Success Rates**: Significantly better than the previous simple approach
- **Automatic Fallback**: Still uses default images when extraction fails

#### Setup Enhanced Extractor

For improved LinkedIn image extraction, install additional dependencies:

```bash
# Install enhanced dependencies
pip install selenium beautifulsoup4 lxml fake-useragent

# Optional: Install ChromeDriver for Selenium support
# macOS: brew install chromedriver
# Ubuntu: sudo apt-get install chromium-chromedriver

# Run setup script
python setup_enhanced_extractor.py
```

#### Testing the Extractor

Test the LinkedIn extractor with sample URLs:

```bash
python test_linkedin_extractor.py
```

For detailed documentation on the enhanced LinkedIn extractor, see [LINKEDIN_EXTRACTOR_README.md](LINKEDIN_EXTRACTOR_README.md).

#### LinkedIn Authentication (Optional)

For significantly improved LinkedIn extraction success rates (70-90% vs ~5%), you can provide LinkedIn session cookies:

**Quick Setup:**
1. Log into LinkedIn in your browser
2. Extract session cookies (see [LINKEDIN_COOKIES_GUIDE.md](LINKEDIN_COOKIES_GUIDE.md) for detailed instructions)
3. Set cookies via environment variable:
   ```bash
   export LINKEDIN_COOKIES="li_at=VALUE1; JSESSIONID=VALUE2; bcookie=VALUE3..."
   ```
4. Or create a `linkedin_cookies.txt` file in the project root

**Security Note:** Keep cookies private and refresh them periodically (they expire every 2-4 weeks).

For complete cookie extraction instructions, see [LINKEDIN_COOKIES_GUIDE.md](LINKEDIN_COOKIES_GUIDE.md).

### Image Processing Notes

- **LinkedIn URL Normalization**: The system automatically normalizes LinkedIn URLs that are missing the `https://` protocol scheme
- **Enhanced Extraction**: New multi-strategy approach significantly improves LinkedIn image extraction success rates
- **Anti-scraping Resilience**: Multiple fallback strategies help overcome LinkedIn's anti-scraping measures
- **Custom Photos**: For guaranteed success, provide custom photo URLs in the Excel data
- **Fallback Images**: All speakers get a default image if all extraction methods fail, ensuring no broken images

## Contributing

For development setup, code quality standards, and contribution guidelines, see [CONTRIBUTING.md](CONTRIBUTING.md).

## License

This project is created for AWS Community Day event management.
