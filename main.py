import os
import requests
import time
from canvasapi import Canvas
from canvasapi.exceptions import CanvasException
from dotenv import load_dotenv
from pyfiglet import Figlet
from termcolor import colored
from tqdm import tqdm

# Load environment variables
load_dotenv()

def display_banner():
    """Display animated ASCII art banner."""
    # Clear screen
    os.system('clear' if os.name == 'posix' else 'cls')
    
    # ASCII art for "CanvasWrapper"
    fig = Figlet(font='slant')
    banner = fig.renderText('CanvasWrapper')
    
    # Display banner with animation
    for line in banner.split('\n'):
        print(colored(line, 'cyan', attrs=['bold']))
        time.sleep(0.1)
    
    # Display author information
    author_info = [
        "By Java Jay Bartolome ( Tadashi Jei )",
        "(tadashijei.com)"
    ]
    
    print("\n")
    for line in author_info:
        text = colored(line, 'yellow', attrs=['bold'])
        for char in text:
            print(char, end='', flush=True)
            time.sleep(0.05)
        print()
    
    # Separator line
    print(colored("\n" + "="*50 + "\n", 'blue'))

def show_loading_animation(message):
    """Show a loading animation with a message."""
    with tqdm(total=100, desc=colored(message, 'green'), 
             bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt}', 
             colour='green') as pbar:
        for _ in range(10):
            time.sleep(0.1)
            pbar.update(10)

# Initialize a new Canvas object
API_URL = os.getenv('CANVAS_API_URL', 'https://tip.instructure.com/')
API_KEY = os.getenv('CANVAS_API_KEY')

if not API_KEY:
    raise ValueError("CANVAS_API_KEY environment variable is not set. Please set it before running the script.")

try:
    canvas = Canvas(API_URL, API_KEY)
    # Verify authentication by making a test API call
    user = canvas.get_current_user()
    print(colored(f"Successfully authenticated as: {user.name}", 'green'))
except CanvasException as e:
    print(colored(f"Canvas API Error: {str(e)}", 'red'))
    print(colored("Please verify your API key has the correct permissions and hasn't expired.", 'yellow'))
    raise

# Define the download directory
DOWNLOAD_DIR = "CanvasDownloads"

def sanitize_filename(filename):
    """Remove invalid characters from filename."""
    # Replace invalid characters with underscore
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename

def setup_course_directory(course_name):
    """Create and return course directory path."""
    course_dir = os.path.join(DOWNLOAD_DIR, sanitize_filename(course_name))
    os.makedirs(course_dir, exist_ok=True)
    return course_dir

def setup_assignment_directory(course_dir, assignment_name):
    """Create and return assignment directory path."""
    assignment_dir = os.path.join(course_dir, sanitize_filename(assignment_name))
    os.makedirs(assignment_dir, exist_ok=True)
    return assignment_dir

def download_file(url, local_filename):
    """Download a file from URL to local path."""
    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        return local_filename
    except Exception as e:
        print(colored(f"Error downloading file {local_filename}: {str(e)}", 'red'))
        return None

def create_markdown_file(assignment_dir, assignment_name, submission_text, submission_files):
    """Create markdown file for the submission in the assignment directory."""
    markdown_filename = os.path.join(assignment_dir, "submission.md")
    try:
        with open(markdown_filename, 'w', encoding='utf-8') as f:
            f.write(f"# {assignment_name}\n\n")
            if submission_text:
                f.write(f"## Submission Text\n\n{submission_text}\n\n")
            if submission_files:
                f.write("## Submission Files\n\n")
                for file in submission_files:
                    if file['local_path']:
                        relative_path = os.path.relpath(file['local_path'], assignment_dir)
                        f.write(f"- [{file['filename']}]({relative_path})\n")
        return markdown_filename
    except Exception as e:
        print(colored(f"Error creating markdown file: {str(e)}", 'red'))
        return None

def process_submission(submission, course_dir, assignment_name):
    """Process a single submission."""
    try:
        # Setup assignment directory
        assignment_dir = setup_assignment_directory(course_dir, assignment_name)
        
        # Get submission text
        submission_text = submission.body if hasattr(submission, 'body') else None
        submission_files = []

        # Debug submission information
        print(colored(f"\nDebug - Submission type: {getattr(submission, 'submission_type', 'unknown')}", 'yellow'))
        print(colored(f"Debug - Has attachments: {hasattr(submission, 'attachments')}", 'yellow'))
        if hasattr(submission, 'attachments'):
            print(colored(f"Debug - Number of attachments: {len(submission.attachments)}", 'yellow'))

        # Process attachments if they exist
        if hasattr(submission, 'submission_type'):
            # Handle online_upload submissions
            if submission.submission_type == 'online_upload' and hasattr(submission, 'attachments'):
                for attachment in submission.attachments:
                    try:
                        # Try both object and dictionary access methods
                        file_url = attachment.url if hasattr(attachment, 'url') else attachment.get('url')
                        file_name = attachment.filename if hasattr(attachment, 'filename') else attachment.get('filename', 'unknown_file')
                        
                        if file_url and file_name:
                            file_name = sanitize_filename(file_name)
                            local_path = os.path.join(assignment_dir, file_name)
                            
                            print(colored(f"Debug - Downloading file: {file_name}", 'yellow'))
                            print(colored(f"Debug - URL: {file_url}", 'yellow'))
                            
                            if download_file(file_url, local_path):
                                submission_files.append({
                                    'filename': file_name,
                                    'local_path': local_path
                                })
                                print(colored(f"Debug - Successfully downloaded: {file_name}", 'green'))
                    except Exception as e:
                        print(colored(f"Debug - Error processing attachment: {str(e)}", 'red'))
            
            # Handle online_text_entry with embedded images
            elif submission.submission_type == 'online_text_entry' and submission_text:
                # Look for image URLs in the text
                import re
                img_urls = re.findall(r'<img[^>]+src="([^">]+)"', submission_text)
                for i, img_url in enumerate(img_urls):
                    try:
                        file_name = f"embedded_image_{i+1}.png"
                        local_path = os.path.join(assignment_dir, file_name)
                        
                        print(colored(f"Debug - Downloading embedded image: {file_name}", 'yellow'))
                        print(colored(f"Debug - URL: {img_url}", 'yellow'))
                        
                        if download_file(img_url, local_path):
                            submission_files.append({
                                'filename': file_name,
                                'local_path': local_path
                            })
                            print(colored(f"Debug - Successfully downloaded embedded image: {file_name}", 'green'))
                    except Exception as e:
                        print(colored(f"Debug - Error downloading embedded image: {str(e)}", 'red'))

        # Create markdown file with submission details
        if create_markdown_file(assignment_dir, assignment_name, submission_text, submission_files):
            print(colored(f"Successfully processed submission for {assignment_name}", 'green'))
            if submission_files:
                print(colored("Files downloaded:", 'green'))
                for file in submission_files:
                    print(colored(f"- {file['filename']}", 'green'))
        
    except Exception as e:
        print(colored(f"Error processing submission for {assignment_name}: {str(e)}", 'red'))

def select_courses():
    """Display and select courses interactively."""
    # Fetch all courses
    courses = list(canvas.get_courses())
    
    if not courses:
        print(colored("No courses found!", 'red'))
        return []

    # Display all courses with numbers
    print("\nAvailable Courses:")
    for i, course in enumerate(courses, 1):
        print(f"{i}. {course.name}")
    
    while True:
        print("\nSelect courses to process:")
        print("1. Process a single course (enter the number)")
        print("2. Process multiple courses (enter numbers separated by commas)")
        print("3. Process all courses")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '4':
            return []
        elif choice == '3':
            return courses
        elif choice == '1':
            try:
                idx = int(input("Enter course number: ").strip()) - 1
                if 0 <= idx < len(courses):
                    return [courses[idx]]
                print(colored("Invalid course number!", 'red'))
            except ValueError:
                print(colored("Please enter a valid number!", 'red'))
        elif choice == '2':
            try:
                indices = [int(x.strip()) - 1 for x in input("Enter course numbers separated by commas: ").split(',')]
                selected_courses = []
                for idx in indices:
                    if 0 <= idx < len(courses):
                        selected_courses.append(courses[idx])
                    else:
                        print(colored(f"Skipping invalid course number: {idx + 1}", 'red'))
                if selected_courses:
                    return selected_courses
                print(colored("No valid courses selected!", 'red'))
            except ValueError:
                print(colored("Please enter valid numbers separated by commas!", 'red'))
        
        print(colored("Invalid choice! Please try again.", 'red'))

def fetch_and_download_data():
    """Main function to fetch and download data."""
    try:
        # Display banner
        display_banner()
        
        # Show authentication loading
        show_loading_animation("Authenticating with Canvas")
        
        selected_courses = select_courses()
        
        if not selected_courses:
            print(colored("\nNo courses selected. Exiting...", 'red'))
            return
        
        # Get current user for filtering submissions
        user = canvas.get_current_user()
        print(colored(f"\nAuthenticated as: {user.name}", 'green'))
        
        for course in selected_courses:
            print(colored(f"\nProcessing course: {course.name}", 'cyan', attrs=['bold']))
            
            # Setup course directory
            course_dir = setup_course_directory(course.name)
            
            try:
                assignments = course.get_assignments()
                for assignment in assignments:
                    print(colored(f"\nProcessing assignment: {assignment.name}", 'yellow'))
                    try:
                        # Get user's own submission directly
                        submission = assignment.get_submission(user.id)
                        if submission and hasattr(submission, 'workflow_state'):
                            if submission.workflow_state != 'unsubmitted':
                                print(colored(f"Found submission for {assignment.name}", 'green'))
                                process_submission(submission, course_dir, assignment.name)
                            else:
                                print(colored(f"No submission found for {assignment.name}", 'red'))
                    except CanvasException as e:
                        if "unauthorized" in str(e).lower():
                            print(colored(f"No access to submission for {assignment.name}", 'red'))
                        else:
                            print(colored(f"Error accessing submission for {assignment.name}: {str(e)}", 'red'))
                            
            except CanvasException as e:
                if "unauthorized" in str(e).lower():
                    print(colored(f"No access to assignments for course {course.name}", 'red'))
                else:
                    print(colored(f"Error accessing assignments for course {course.name}: {str(e)}", 'red'))
                
    except CanvasException as e:
        print(colored(f"Error: {str(e)}", 'red'))
        print(colored("Please verify your API key and permissions.", 'yellow'))

if __name__ == "__main__":
    fetch_and_download_data()