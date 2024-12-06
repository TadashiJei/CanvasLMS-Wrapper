# CanvasWrapper

A powerful Canvas LMS content fetcher and organizer developed by Java Jay Bartolome (Tadashi Jei).

## Features

### 1. Course Management
- List all available Canvas courses
- Select single or multiple courses for processing
- Option to process all courses at once
- Organized course content in dedicated directories

### 2. Assignment Handling
- Fetches all assignments from selected courses
- Downloads submissions and attachments
- Supports multiple submission types:
  - File uploads
  - Text submissions
  - Embedded images
  - Online text entries

### 3. File Organization
- Creates a structured directory hierarchy:
  ```
  CanvasDownloads/
  ├── Course Name/
  │   ├── Assignment 1/
  │   │   ├── submission.md
  │   │   ├── attachment1.pdf
  │   │   └── attachment2.cpp
  │   └── Assignment 2/
  │       ├── submission.md
  │       └── files/
  ```
- Sanitizes filenames for cross-platform compatibility
- Maintains original file organization

### 4. Content Processing
- Creates markdown files for each submission
- Preserves submission text and comments
- Downloads all attached files
- Handles embedded images in text submissions
- Maintains file relationships and links

### 5. User Interface
- Interactive course selection menu
- Colorful terminal output
- Progress indicators for operations
- Clear error messages and status updates
- ASCII art banner and animations

### 6. Error Handling
- Robust error handling for API issues
- Clear feedback for authentication problems
- Graceful handling of missing permissions
- Recovery from network issues

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd CanvasWrapper
   ```

2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure your Canvas API credentials:
   - Create a `.env` file in the project directory
   - Add your Canvas API URL and key:
     ```
     CANVAS_API_URL=https://your-canvas-instance.com/
     CANVAS_API_KEY=your-api-key
     ```

## Usage

1. Run the script:
   ```bash
   python main.py
   ```

2. Select courses to process:
   - Option 1: Process a single course
   - Option 2: Process multiple courses (comma-separated numbers)
   - Option 3: Process all courses
   - Option 4: Exit

3. The script will:
   - Create necessary directories
   - Download submissions and files
   - Organize content by course and assignment
   - Generate markdown files with submission details

## Output Structure

Each assignment's content is organized as follows:
- `submission.md`: Contains submission text and file links
- Original files: Preserved in their uploaded format
- Embedded images: Extracted and saved as separate files
- All content is organized in course-specific directories

## Requirements

- Python 3.6 or higher
- Canvas API access and key
- Required Python packages (see requirements.txt):
  - canvasapi
  - requests
  - python-dotenv
  - pyfiglet (for ASCII art)
  - termcolor (for colored output)
  - tqdm (for progress bars)

## Error Handling

The script handles various error conditions:
- Invalid API credentials
- Network connectivity issues
- Missing permissions
- File download failures
- Invalid course selections

## Notes

- API key must have appropriate permissions
- Some content may be inaccessible due to Canvas permissions
- Large files may take longer to download
- Network connectivity is required throughout the process

## Author

Java Jay Bartolome (Tadashi Jei)
Website: [tadashijei.com](https://tadashijei.com)

## License

This project is licensed under the MIT License - see the LICENSE file for details.
