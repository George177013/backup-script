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
import logging
import subprocess
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from datetime import datetime

# Function to install colorama if it's not already installed
def install_colorama():
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
            print("Error: This script requires administrative privileges. Please run as Administrator.")
            sys.exit(1)
    else:
        # Check for sudo privileges on Unix-like systems
        if os.geteuid() != 0:
            print("Error: This script requires sudo/root privileges. Please run with 'sudo'.")
            sys.exit(1)

def manage_backup_sources():
    """
    Manages a list of backup sources stored in a file.
    Provides user an interactive menu to:
    - View current backup sources.
    - Add new backup source paths.
    - Remove existing backup source paths.

    Returns:
        sources (list): A list of source paths to back up.
    """
    sources_file = Path(f"{SCRIPT_NAME}_sources.txt")
    # If source file doesn't exist, create it.
    if not sources_file.exists():
        try:
            print(f"Creating source file at: {sources_file.resolve()}")
            sources_file.touch(exist_ok=True)
            logging.info(f"Backup sources file created at {sources_file}.")
        except PermissionError:
            logging.error(f"Permission denied: Unable to create the sources file {sources_file}.")
            print(f"{Fore.RED}Error:{Style.RESET_ALL} Permission denied. Cannot create the sources file at {sources_file}.")
            sys.exit(1)
        except Exception as e:
            logging.error(f"Unexpected error while creating the sources file {sources_file}: {e}")
            print(f"{Fore.RED}Error:{Style.RESET_ALL} An unexpected error occurred while creating the sources file: {e}")
            sys.exit(1)

    while True:
        # Load sources into memory
        sources = [line.strip() for line in sources_file.read_text().splitlines()]

        # Display sources
        print("__________")
        print("Current backup sources:")
        if sources:
            for i, source in enumerate(sources, start=1):
                print(f"{i}: {source}")
        else:
            print("No backup sources defined.")

        # Prompt user for action in a makeshift switch case
        action = input("Add (a), Remove (r), or Finish (f): ").strip().lower()
        if action == 'a':
            path = input("Enter the path to add: ").strip()
            path = Path(path).resolve()
            if path.exists():
                sources.append(str(path))
                sources_file.write_text("\n".join(sources) + "\n")
                print(f"{Fore.GREEN}Success:{Style.RESET_ALL} Added source: {path}")
                logging.info(f"Added source: {path}")
            else:
                logging.warning("Invalid path entered.")
                print(f"{Fore.YELLOW}Warning:{Style.RESET_ALL} Invalid path. Please try again.")
        elif action == 'r':
            try:
                index = int(input("Enter the number of the source to remove: "))
                if 0 < index <= len(sources):
                    removed = sources.pop(index - 1)
                    sources_file.write_text("\n".join(sources) + "\n")
                    logging.info(f"Removed source: {removed}")
                    print(f"Removed: {removed}")
                else:
                    logging.warning("Invalid selection for removal.")
                    print(f"{Fore.YELLOW}Warning:{Style.RESET_ALL} Invalid selection. Please try again.")
            except ValueError:
                logging.warning("Non-numeric input for removal index.")
                print(f"{Fore.YELLOW}Warning:{Style.RESET_ALL} Invalid input. Please enter a number.")
        elif action == 'f':
            # Save updated sources to the file
            sources_file.write_text("\n".join(sources) + "\n")
            logging.info(f"Saved changes to {sources_file}, finished editing backup sources.")
            print(f"{Fore.GREEN}Success:{Style.RESET_ALL} Saved changes to {sources_file}, finished editing backup sources.")
            break
        else:
            logging.warning("Invalid action entered.")
            print(f"{Fore.YELLOW}Warning:{Style.RESET_ALL} Invalid action. Please choose 'a', 'r', or 'f'.")
    
def get_backup_destination():
    """
    Prompts the user to enter a valid backup destination path or allows the script
    to create a default backup folder in the same directory as the script.

    Returns:
        destination (str): A valid backup destination path.
    """
    default_backup_folder = Path(__file__).parent / "backup"

    while True:
        print("Where would you like to store your backup?")
        destination = input(f"Enter path, or leave empty to use default folder: ").strip()

        if not destination:
            # Use the default folder, which is /backup in the path of the script
            destination = default_backup_folder
            if not destination.exists():
                try:
                    destination.mkdir(parents=True, exist_ok=True)
                    print(f"{Fore.GREEN}Success:{Style.RESET_ALL} Default backup folder created at: {destination}")
                    logging.info(f"Default backup folder created: {destination}")
                except PermissionError:
                    logging.error(f"Permission denied while creating the default backup folder: {destination}")
                    print(f"{Fore.RED}Error:{Style.RESET_ALL} Permission denied while creating {destination}.")
                    return None
            else:
                print(f"Using existing default backup folder: {destination}")
                logging.info(f"Using existing default backup folder: {destination}")
            return str(destination)

        # Normalize and validate the user-provided destination
        destination = Path(destination).resolve()
        if destination.exists() and os.access(destination, os.W_OK):
            print(f"Destination accepted: {destination}")
            return str(destination)
        else:
            if not destination.exists():
                logging.error(f"Invalid destination path: {destination} (Path does not exist).")
                print(f"{Fore.RED}Error:{Style.RESET_ALL} The specified path does not exist.")
            elif not os.access(destination, os.W_OK):
                logging.error(f"Invalid destination path: {destination} (Path is not writable).")
                print(f"{Fore.RED}Error:{Style.RESET_ALL} The specified path is not writable.")

            retry = input("Retry? (y/n): ").lower().strip()
            if retry != 'y':
                print(f"{Fore.YELLOW}Warning:{Style.RESET_ALL} Backup destination setup aborted.")
                return None

def perform_backup(sources, destination):
    """
    Zips all files and directories in the sources list into a single zip file in the destination directory.

    Args:
        sources (list): A list of source paths to back up.
        destination (str): The directory where the zip file will be created.
    """
    print("\nStarting backup process now.")
    # Normalize and ensure the destination exists
    destination = Path(destination).resolve()
    if not destination.exists():
        try:
            destination.mkdir(parents=True, exist_ok=True)
            logging.info(f"Destination directory created: {destination}")
        except PermissionError:
            logging.error(f"{Fore.RED}Error:{Style.RESET_ALL} Permission denied while creating destination: {destination}")
            return

    # Define the zip file path
    timestamp = datetime.now().strftime("%d%m%Y_%H%M%S")
    backup_name = f"backup_{timestamp}.zip"
    backup_zip_path = destination / backup_name

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
        print(f"{Fore.RED}Error:{Style.RESET_ALL} Failed to create backup: {e}")

def main():
    """
    Main function to orchestrate the backup process:
    - Manage sources (add/remove paths to backup).
    - Set or create a backup destination.
    - Perform the backup (compressing into a zip file).

    Logs all critical steps and errors.
    """
    
    logging.info("Backup process started.")
    print("Starting backup process...")

    try:
        # Step 1: Manage Backup Sources
        logging.info("Managing backup sources.")
        print("Setting backup sources.")
        manage_backup_sources()
        sources_file = Path(f"{SCRIPT_NAME}_sources.txt")

        # Load sources from the file
        sources = [line.strip() for line in sources_file.read_text().splitlines() if line.strip()]

        if not sources:
            logging.warning("No sources found. Exiting backup process.")
            print(f"{Fore.RED}Error:{Style.RESET_ALL} No sources to back up. Exiting.")
            return

        logging.info(f"Sources to backup: {sources}")

        # Step 2: Get Backup Destination
        logging.info("Setting backup destination.")
        print("\nSetting backup destination.")
        destination = get_backup_destination()
        if not destination:
            logging.warning("Backup destination not set. Exiting backup process.")
            print(f"{Fore.RED}Error:{Style.RESET_ALL} No backup destination set. Exiting.")
            return

        logging.info(f"Backup destination: {destination}")

        # Step 3: Perform Backup
        logging.info("Starting backup process.")
        perform_backup(sources, destination)
        logging.info("Backup process completed successfully.")

    except Exception as e:
        logging.error(f"An error occurred during the backup process: {e}")
        print(f"{Fore.RED}Error{Style.RESET_ALL} - An error occurred during the backup process: {e}")

    logging.info("Backup process finished.")

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

    # Ready to go 
    main()