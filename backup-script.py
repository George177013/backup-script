#!/bin/env python3
"""
This script is a backup management tool that:

1. Checks Administrative Privileges: Ensures the script is run with the necessary permissions for secure operations.
2. Manages Backup Sources: Lets users view and add or remove file and folder paths to back up.
3. Sets Backup Destination: Prompts the user to choose a backup location or creates a default folder.
4. Performs Backup: Compresses selected files and folders into a ZIP file with a timestamp.
5. Logs Events: Records all actions, warnings, and errors in a log file.
"""

# Import Python Modules
import os
import sys
import platform
import re
import sqlite3
import logging
import subprocess
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from datetime import datetime


def initialize_database():
    """
    Initializes the SQLite database and creates the table if it doesn't exist.
    """
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(f"""CREATE TABLE IF NOT EXISTS {DB_TABLE} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT NOT NULL
            );""")
        conn.commit()

def validate_path(path):
    """
    Validates the given path against a regex pattern.

    Args:
        path (str): The path to verify.
    """
    return bool(re.match(VALID_PATH_REGEX, path))

def handle_error(error_message):
    """
    Handles errors by matching known patterns and providing appropriate feedback.

    Args:
        error_message (str): The error message.
    """
    for error_type, pattern in ERROR_PATTERNS.items():
        if re.search(pattern, error_message):
            if error_type == "permission_denied":
                logging.error("Permission Denied")
                print(f"{Fore.RED}Error:{Style.RESET_ALL} You don't have the necessary permissions. Please check and try again.")
            elif error_type == "file_not_found":
                logging.error("File not found")
                print(f"{Fore.RED}Error:{Style.RESET_ALL} File or directory not found. Ensure the path exists.")
            elif error_type == "invalid_path":
                logging.error("Invalid path")
                print(f"{Fore.RED}Error:{Style.RESET_ALL} The path is invalid. Please enter a valid path.")
            return
    print(f"An unexpected error occurred: {error_message}")

def install_colorama():
    """
    Installs Colorama if it is not already installed. 
    Colorama allows us to use colors in terminal output across different platforms.
    """
    try:
        # Try to import colorama to check if it's already installed
        import colorama
    except ImportError:
        print("colorama not found. Installing colorama...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "colorama"])

def check_admin_privileges():
    """
    Checks if the script is being run with administrative privileges.
    On Unix-like systems, it checks for UID 0.
    On Windows, it checks for administrator privileges.
    Exits the script with a message if not running as admin/sudo.
    """
    if platform.system() == "Windows":
        # Check for administrator privileges on Windows
        try:
            import ctypes
            is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        except:
            is_admin = False
        if not is_admin:
            print(f"{Fore.RED}Error:{Style.RESET_ALL} This script requires administrative privileges. Please run as Administrator.")
            sys.exit(1)
    else:
        # Check for sudo privileges on Unix-like systems
        if os.geteuid() != 0:
            print(f"{Fore.RED}Error:{Style.RESET_ALL} This script requires sudo/root privileges. Please run with 'sudo'.")
            sys.exit(1)

def manage_backup_sources():
    """
    Provides an interactive menu for managing backup sources stored in an SQLite database.
    """
    while True:
        # Get sources from database
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT id, path FROM {DB_TABLE}")
            sources = cursor.fetchall()

        # Display sources
        print("__________")
        print("Current backup sources:")
        if sources:
            for source_id, path in sources:
                print(f"{source_id}: {path}")
        else:
            print("No backup sources defined.")

        # Prompt user for action in this makeshift swich case
        action = input("Add (a), Remove (r), or Finish (f): ").strip().lower()
        if action == 'a':
            path = input("Enter the path to add: ").strip()
            # Regex requirement
            if not validate_path(path):
                print("Invalid path format. Please try again.")
                logging.warning("Invalid path format entered.")
                continue
            path = Path(path).resolve()
            if path.exists():
                with sqlite3.connect(DB_FILE) as conn:
                    cursor = conn.cursor()
                    cursor.execute(f"INSERT INTO {DB_TABLE} (path) VALUES (?)", (str(path),))
                    conn.commit()
                print(f"{Fore.GREEN}Success -{Style.RESET_ALL} Added source: {path}")
                logging.info(f"Added source: {path}")
            else:
                print(f"{Fore.YELLOW}Warning:{Style.RESET_ALL} Path does not exist. Please try again.")
                logging.warning("Invalid path entered.")
        elif action == 'r':
            try:
                source_id = int(input("Enter the ID of the source to remove: "))
                with sqlite3.connect(DB_FILE) as conn:
                    cursor = conn.cursor()
                    cursor.execute(f"DELETE FROM {DB_TABLE} WHERE id = ?", (source_id,))
                    conn.commit()
                print(f"{Fore.GREEN}Success -{Style.RESET_ALL} Removed source with ID: {source_id}")
                logging.info(f"Removed source: {source_id}")
            except ValueError:
                print(f"{Fore.YELLOW}Warning:{Style.RESET_ALL} Invalid input. Please enter a numeric ID.")
                logging.warning("Non-numeric input, try again.")
        elif action == 'f':
            print("Finished managing backup sources.")
            logging.info(f"Finished editing backup sources.")
            break
        else:
            print(f"{Fore.YELLOW}Warning:{Style.RESET_ALL} Invalid action. Please choose 'a', 'r', or 'f'.")
            logging.warning("Invalid action entered.")

def get_backup_sources():
    """
    Retrieves all paths to back up from the database.
    """
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT path FROM {DB_TABLE}")
        return [row[0] for row in cursor.fetchall()]

def get_backup_destination():
    """
    Prompts the user to enter a valid backup destination path or creates a default backup folder.
    
    Returns:
        destination (str): A valid backup destination path.
    """
    default_backup_folder = Path(__file__).parent / "backup"
    while True:
        destination = input("Enter backup destination (or press Enter for default): ").strip()
        if not destination:
            destination = default_backup_folder
            destination.mkdir(parents=True, exist_ok=True)
            print(f"{Fore.GREEN}Success:{Style.RESET_ALL} Default backup folder created at: {destination}")
            logging.info(f"Default backup folder created: {destination}")
            return str(destination)
        else:
            destination = Path(destination).resolve()
            if destination.exists() and os.access(destination, os.W_OK):
                print(f"{Fore.GREEN}Success:{Style.RESET_ALL} Using backup folder at: {destination}")
                logging.info(f"Using backup folder at: {destination}")
                return str(destination)
            print("Invalid destination. Please try again.")

def perform_backup(sources, destination):
    """
    Compresses the specified sources into a zip file at the destination.
    
    Args:
        sources (list): A list of source paths to back up.
        destination (str): Destination for the zip file.

    """
    # Define the zip file path
    timestamp = datetime.now().strftime("%d%m%Y_%H%M%S")
    backup_name = f"backup_{timestamp}.zip"
    backup_zip_path = Path(destination) / backup_name

    skipped_files = [] # Tracking skipped files during the backup


    # Backup process
    try:
        with ZipFile(backup_zip_path, 'w', ZIP_DEFLATED) as zip_file:
            for source in sources:
                source_path = Path(source).resolve()

                if not source_path.exists():
                    logging.warning(f"Source not found: {source_path}")
                    skipped_files.append(str(source_path)) # Adds path to skipped
                    continue

                if source_path.is_dir():
                    for file in source_path.rglob('*'):
                        try:
                            arcname = file.relative_to(source_path.parent)
                            zip_file.write(file, arcname)
                            logging.info(f"Added to backup: {file}")
                        except PermissionError:
                            logging.warning(f"Skipped (permission denied): {file}")
                            skipped_files.append(str(file))
                else:
                    try:
                        arcname = source_path.name
                        zip_file.write(source_path, arcname)
                        logging.info(f"Added to backup: {source_path}")
                    except PermissionError:
                        logging.warning(f"Skipped (permission denied): {source_path}")
                        skipped_files.append(str(source_path))

        if skipped_files:
            print("{Fore.YELLOW}Warning:{Style.RESET_ALL} Some files were skipped. Check logs for details.")

        logging.info(f"Backup completed successfully: {backup_zip_path}")
        print(f"{Fore.GREEN}Success:{Style.RESET_ALL} Backup completed successfully: {backup_name}")
        
        print("\nThank you for using our tool!")

    except Exception as e:
        logging.error(f"Failed to create backup: {e}")
        handle_error(str(e))

def main():
    """
    Main function to orchestrate the backup process.
    
    """
    initialize_database()
    manage_backup_sources()
    
    sources = get_backup_sources()
    if not sources:
        print("No sources to back up. Exiting.")
        return

    destination = get_backup_destination()

    if destination:
        perform_backup(sources, destination)

if __name__ == "__main__":
        # Check if user has admin priviledges
    check_admin_privileges()

    # Call the function to ensure colorama is installed
    install_colorama()

    #Import colorama Module after installation
    from colorama import init, Fore, Style

    # Initialize colorama
    init(autoreset=True)

    # Determine the log directory based on the operating system
    if platform.system() == "Windows":
        LOG_DIR = Path("C:/logs")  # Windows absolute path
    else:
        LOG_DIR = Path("/var/log")  # Linux/Mac absolute path

    # Define the log file name and full path
    SCRIPT_NAME = Path(__file__).stem  # Extracts the script's base name
    LOG_FILE = LOG_DIR / f"{SCRIPT_NAME}.log" # Use SCRIPT_NAME to name the log file

    # Ensure the log directory exists
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
    except PermissionError: # This should never happen, as we check for admin priviledges already.
        print(f"{Fore.RED}Error{Style.RESET_ALL} - Permission denied: Unable to create directory {LOG_DIR}. Please run the script with appropriate permissions.")
        sys.exit(1)

    # Configure Logging Module
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s %(message)s",
        datefmt="[%Y-%m-%d %H:%M:%S]"
    )
    
    # Database Configuration
    DB_FILE = "backup_sources.db"
    DB_TABLE = "sources"

    # Regex for validating paths
    VALID_PATH_REGEX = r"^[a-zA-Z0-9_\-\/\.\\: ]+$"
    ERROR_PATTERNS = {
        "permission_denied": r"Permission denied",
        "file_not_found": r"No such file or directory",
        "invalid_path": r"Invalid path",
    }

    main()