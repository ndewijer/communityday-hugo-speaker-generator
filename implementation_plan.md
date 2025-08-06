# Hugo Speaker Generator - Implementation Plan

## Project Overview

This project generates Hugo templates for the AWS Community Day website based on Call for Papers responses. The system processes Excel data containing speaker information and session details, then generates markdown files and downloads/processes speaker images.

## Architecture & Requirements

### Input Data
- **Source**: `data/responses+votes.xlsx`
- **Key Columns**:
  - Session_ID (unique identifier)
  - Email Address (speaker unique identifier)
  - Speaker Name, Speaker Headline, Bio
  - Link to your LinkedIn profile
  - Link to photo (Optional, defaults to LinkedIn Profile)
  - Title of Session, Abstract of Session
  - Session Duration, Session Level
  - Room (room number/name)
  - Agenda (time in HHMM format)
  - Voter_1 through Voter_N (future use)

### Output Structure
```
generated_files/
├── content/
│   ├── speakers/
│   │   ├── speaker-slug/
│   │   │   ├── index.md
│   │   │   └── img/photo.jpg
│   └── sessions/
│       ├── acd101.md  # Level 1, session 1
│       ├── acd102.md  # Level 1, session 2
│       ├── acd201.md  # Level 2, session 1
│       └── acd301.md  # Level 3, session 1
└── missing_photos.csv
```

## Technical Specifications

### 1. Speaker Processing Logic

**Deduplication**: Use email address as unique identifier
- One speaker profile per unique email
- Handle multiple sessions per speaker
- Generate unique slugs for name conflicts (john-doe, john-doe-1, john-doe-2)

**Speaker Markdown Template**:
```yaml
---
title: "Speaker Name"
headline: "Speaker Headline or ''"
linkedin: "LinkedIn URL"  # or commented out if empty
---

Bio content or ""
```

**Name Sanitization**:
- Convert to lowercase
- Replace spaces with dashes
- Remove non-unicode characters
- Handle conflicts with numeric suffixes

### 2. Session Processing Logic

**Filename Generation**:
- Sort sessions by Session_ID for consistent ordering
- Extract level number from "Session Level" (e.g., "300 (Advanced)" → 3)
- Separate counters per level: acd{level}{counter:02d}.md
- Examples: acd101.md, acd201.md, acd301.md, acd102.md
- **Persistent Session IDs**: Once assigned, session IDs are preserved between runs using a mapping file
- **Content Verification**: Existing files are checked for changes and updated if needed

**Session Markdown Template**:
```yaml
---
id: "Session_ID"
title: "Title of Session"
date: "2025-09-25T11:00:00"  # Generated from event date and agenda time
speakers:
    - "speaker-slug"
room: "2"  # Room number/name from data source
agenda: "1100"  # Agenda time in HHMM format from data source
duration: "30" or "60"  # Mapped from duration string
---

Abstract content
```

**Duration Mapping**:
- ≤ 30 minutes → "30"
- > 30 and ≤ 60 minutes → "60"
- Multiple durations → Comment all out for manual selection

### 3. Image Processing Logic

**Priority Order**:
1. Custom photo URL (if provided)
2. LinkedIn profile image extraction
3. Default fallback: `samples/unknown.jpg`

**Image Processing**:
- Download images
- Crop to square (center-focused)
- Save as `photo.jpg` in speaker's img directory
- Log failures to `missing_photos.csv`

**Missing Photos CSV Format**:
```csv
Speaker Name,Email,LinkedIn URL,Reason
John Doe,john@example.com,https://linkedin.com/in/johndoe,Download failed
Jane Smith,jane@example.com,,No LinkedIn URL
```

### 4. Configuration Management

**Field Mappings**:
```python
SPEAKER_FIELD_MAPPING = {
    'title': 'Speaker Name',
    'headline': 'Speaker Headline',
    'linkedin': 'Link to your LinkedIn profile',
    'bio': 'Bio'
}

SESSION_FIELD_MAPPING = {
    'id': 'Session_ID',
    'title': 'Title of Session',
    'abstract': 'Abstract of Session',
    'speakers': 'Speaker Name',
    'duration': 'Session Duration',
    'room': 'Room',
    'agenda': 'Agenda'
}

# Event date for session datetime generation
EVENT_DATE = "2025-09-25"

LEVEL_EXTRACTION = {
    '100 (Beginner)': 1,
    '200 (Intermediate)': 2,
    '300 (Advanced)': 3,
    '400 (Expert)': 4,
    '500 (Principal)': 5
}
```

### 5. Session ID Persistence Mechanism

**Purpose**:
- Maintain stable session IDs once assigned
- Prevent duplicate content when sessions are added or reordered
- Allow updates to session content without changing filenames

**Implementation**:
- Store mapping between Session_IDs and assigned filenames in `data/session_id_mapping.json`
- Track the next available number for each level
- When generating sessions:
  1. Check if Session_ID exists in mapping
  2. If yes, use previously assigned filename
  3. If no, assign next available number for that level

**JSON Structure**:
```json
{
  "session_id_mapping": {
    "d4610b42-6a84-44f7-841f-564927d6ee55": "acd209",
    "7a8b9c0d-1e2f-3g4h-5i6j-7k8l9m0n1o2p": "acd210"
  },
  "level_counters": {
    "1": 5,  // Next available is acd106
    "2": 10, // Next available is acd211
    "3": 7,  // Next available is acd308
    "4": 2,  // Next available is acd403
    "5": 0   // Next available is acd501
  }
}
```

**Content Verification Process**:
1. Extract key data from existing session files (room, time, title, etc.)
2. Compare with current data from Excel source
3. Update file if differences are detected
4. Preserve the assigned filename

## Project Structure

```
├── src/
│   ├── __init__.py
│   ├── config.py              # Field mappings and configuration
│   ├── data_processor.py      # Excel file processing & validation
│   ├── speaker_generator.py   # Speaker page generation
│   ├── session_generator.py   # Session page generation
│   ├── image_processor.py     # Image downloading & processing
│   └── utils.py              # Utility functions (sanitization, etc.)
├── generated_files/           # Output directory (gitignored)
│   └── content/
│       ├── speakers/
│       └── sessions/
├── data/                     # Input data (gitignored)
│   └── session_id_mapping.json # Session ID persistence mapping (gitignored)
├── samples/
│   └── unknown.jpg           # Default speaker image
├── template/                 # Reference templates
├── requirements.txt          # Python dependencies
├── .gitignore
└── main.py                   # Entry point
```

## Dependencies

```txt
pandas>=2.0.0
openpyxl>=3.1.0
requests>=2.31.0
Pillow>=10.0.0
pyyaml>=6.0
```

## Implementation Flow

### Phase 1: Data Processing
1. Load and validate Excel data
2. Deduplicate speakers by email
3. Generate unique speaker slugs
4. Validate required fields

### Phase 2: Speaker Generation
1. Create speaker directory structure
2. Generate speaker markdown files
3. Process and download speaker images
4. Log missing photos to CSV

### Phase 3: Session Generation
1. Sort sessions by Session_ID
2. Extract session levels and assign filenames
3. Generate session markdown files
4. Handle multiple speakers per session

### Phase 4: Validation & Reporting
1. Validate generated files
2. Generate summary statistics
3. Report missing data and errors

## Console Output Design

```
🚀 Starting Hugo Speaker Generator...
==================================================
📊 Loading Excel data...
   ✓ Loaded 25 submissions

👥 Processing speakers...
   ✓ Found 15 unique speakers

📝 Generating speaker profiles...
   [1/15] John Doe
   [2/15] Jane Smith
   ...

🖼️  Processing speaker images...
   ✓ Downloaded: 12
   ⚠️  Failed: 3 (logged to missing_photos.csv)

📋 Generating session files...
   ✓ Generated 18 session files
   🔄 Updated 5 session files
   ✓ Skipped: 2 (no changes)

==================================================
✅ GENERATION COMPLETE

📊 SUMMARY STATISTICS:
   • Speakers processed: 15
   • Sessions generated: 18
   • Sessions updated: 5
   • Images downloaded: 12
   • Images failed: 3

📈 SESSIONS BY LEVEL:
   • Level 1 (Beginner): 5 sessions
   • Level 2 (Intermediate): 8 sessions
   • Level 3 (Advanced): 10 sessions

⚠️  WARNINGS:
   • 3 speakers missing LinkedIn profiles
   • 2 sessions with multiple durations (commented out)

📁 OUTPUT LOCATION: ./generated_files/
```

## Error Handling

### Missing Data Strategy
- Empty LinkedIn → Comment out linkedin field
- Empty bio/headline → Use empty string with quotes
- Missing images → Use samples/unknown.jpg
- Multiple durations → Comment all options

### Edge Cases
- Duplicate speaker names → Add numeric suffix
- Invalid Session_ID → Log warning, continue
- Malformed URLs → Log to missing_photos.csv
- Network timeouts → Retry once, then fallback

## Git Configuration

### .gitignore
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/

# Data files (personal information)
data/
generated_files/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
```

## Future Enhancements

### Voting Integration
- Current voter columns (Voter_1 through Voter_N) reserved for future use
- Potential features:
  - Session ranking based on votes
  - Automatic session selection thresholds
  - Quality scoring integration

### Additional Features
- Email validation
- LinkedIn profile validation
- Batch image optimization
- Hugo site integration testing
- Automated deployment pipeline

## Testing Strategy

### Unit Tests
- Speaker slug generation
- Duration mapping logic
- Image processing functions
- Data validation routines

### Integration Tests
- End-to-end file generation
- Excel data processing
- Image download workflows
- Error handling scenarios

### Manual Testing
- Generated markdown validation
- Hugo site compatibility
- Image quality verification
- Missing data handling

---

*This implementation plan serves as the complete specification for the Hugo Speaker Generator project. All requirements, edge cases, and technical decisions have been documented for reference during development.*
