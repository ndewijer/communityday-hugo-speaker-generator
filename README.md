# Hugo Speaker Generator

A Python tool to generate Hugo markdown files for AWS Community Day speakers and sessions from Excel data containing Call for Papers responses.

## Features

- **Speaker Profile Generation**: Creates individual speaker pages with bio, headline, and LinkedIn information
- **Session File Generation**: Generates session pages with proper filename conventions (acd{level}{number}.md)
- **Multiple Speakers Per Session**: Supports any number of speakers for a single session
- **Session & Speaker Removal**: Handles removal of sessions and speakers from the datasource
- **Persistent Session IDs**: Maintains stable session filenames even when sessions are added or reordered
- **Content Verification**: Updates existing files when source data changes instead of skipping them
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
├── generated_files/              # Output directory (gitignored)
│   └── content/
│       ├── speakers/             # Generated speaker profiles
│       └── sessions/             # Generated session files
├── data/                         # Input Excel files (gitignored)
│   └── session_id_mapping.json   # Session ID persistence mapping
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
   pip install -r requirements.txt
   ```

   **Option B: Enhanced Installation (Better LinkedIn extraction)**
   For improved LinkedIn image extraction, install Selenium dependencies:
   ```bash
   pip install -r requirements-selenium.txt
   ```
   The system will guide you through a one-time LinkedIn login setup. See [LINKEDIN_SELENIUM_GUIDE.md](LINKEDIN_SELENIUM_GUIDE.md) for detailed instructions.

3. **Prepare Data**:
   - Place your Excel file in the `data/` directory
   - Ensure it's named `responses+votes.xlsx` or update the path in `src/config.py`

## Usage

### Basic Usage
Run the generator:
```bash
source venv/bin/activate  # Activate virtual environment
python main.py
```

### Force Regeneration
To rebuild all files (ignore existing files):
```bash
python main.py --force
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
- Level 5 (Principal): acd501.md, acd502.md, etc.

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
- `Room` - Room number/name for the session
- `Agenda` - Time in HHMM format (e.g., "1100" for 11:00 AM)

## Features in Detail

### Speaker Processing
- Deduplicates speakers by email address
- Generates unique slugs for speaker directories
- Handles name conflicts with numeric suffixes
- Comments out empty LinkedIn fields

### Session Processing
- Sorts sessions by Session_ID for consistent ordering
- Separate counters per level for filename generation
- **Multiple Speakers Support**: Handles any number of speakers per session
- **Persistent Session IDs**: Maintains stable filenames even when sessions are reordered
- **Content Verification**: Updates files when source data changes instead of skipping
- **Session Removal Handling**: Detects and removes sessions no longer in the datasource
- **Speaker Removal Handling**: Updates sessions when speakers are removed
- **Numeric Field Handling**: Properly formats room numbers and agenda times from Excel
- Handles multiple duration options by commenting them out
- Maps durations to standard values (30 or 60 minutes)
- Generates ISO 8601 datetime field from event date and agenda time
- Includes room and agenda information from data source
- Preserves session IDs even after removal to maintain URL stability

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
   ✓ Generated 18 session files
   🔄 Updated 4 session files
   ✓ Skipped: 2 (no changes)

==================================================
✅ GENERATION COMPLETE

📊 SUMMARY STATISTICS:
   • Speakers processed: 17
   • Sessions generated: 18
   • Sessions updated: 4
   • Sessions with multiple speakers: 2
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

The system includes a modern Selenium-based LinkedIn profile image extractor:

- **One-time Interactive Login**: User-friendly browser-based authentication
- **Persistent Sessions**: Login once, use forever (until session expires)
- **Direct DOM Access**: More reliable than regex-based extraction
- **Rate Limiting**: Respects LinkedIn's usage policies
- **Smart Skip Logic**: Avoids re-processing existing files
- **Retry Queue**: Automatically retries previous failures

#### Key Features

- **~90% Success Rate**: Direct DOM access vs regex patterns
- **Automatic Fallback**: Uses basic extraction if Selenium unavailable
- **Skip-if-Exists**: Only processes new or failed speakers
- **Force Regeneration**: `--force` flag to rebuild everything
- **Missing Photos Retry**: Automatically retries speakers from missing_photos.csv

For complete setup and usage instructions, see [LINKEDIN_SELENIUM_GUIDE.md](LINKEDIN_SELENIUM_GUIDE.md).

### Image Processing Notes

- **LinkedIn URL Normalization**: Automatically normalizes LinkedIn URLs missing `https://` protocol
- **Smart Skip Logic**: Skips speakers if both profile and image exist AND not in missing_photos.csv
- **Custom Photos**: Custom photo URLs take priority over LinkedIn extraction
- **Fallback Images**: Default image used when all extraction methods fail
- **Retry System**: Previous LinkedIn failures are automatically retried on next run

## Contributing

For development setup, code quality standards, and contribution guidelines, see [CONTRIBUTING.md](CONTRIBUTING.md).

## License

This project is created for AWS Community Day event management.
