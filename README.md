# Backup Management Tool

This is a Python-based backup management tool designed to streamline the process of creating secure and organized backups of important files and folders. The tool allows users to define backup sources, set a backup destination, and create compressed ZIP archives of the selected files and folders. It also logs all actions, warnings, and errors for better tracking and troubleshooting.

## Features

1. **Administrative Privileges Check**: Ensures the script is run with the necessary permissions for secure operations.
2. **Manage Backup Sources**: Lets users view, add, or remove file and folder paths to back up.
3. **Backup Destination Setup**: Prompts the user to choose a backup location or creates a default folder.
4. **Automated Backup**: Compresses selected files and folders into a ZIP file with a timestamp.
5. **Event Logging**: Records all actions, warnings, and errors in a log file for better traceability.
6. **Cross-Platform Compatibility**: Supports Windows and Linux environments.

## Requirements

- Python 3.6+
- `colorama` module (installed automatically if not present)

## Installation

1. Clone or download this repository.
2. Ensure Python 3.6 or higher is installed on your system.
3. Make the script executable:
   ```bash
   chmod +x backup_tool.py
   ```

## Usage

### Running the Script

1. Open a terminal or command prompt.
2. Navigate to the directory containing the script.
3. Run the script with appropriate administrative privileges:
   ```bash
   sudo ./backup_tool.py   # For Unix-like systems
   ./backup_tool.py        # For Windows (Run as Administrator)
   ```

### Features Walkthrough

1. **Manage Backup Sources**:
   - Add, view, or remove file/folder paths to back up.
   - Paths are saved in a text file for persistent management.

2. **Set Backup Destination**:
   - Choose a folder to save the backup ZIP file.
   - If no path is provided, a default `backup` folder is created in the script's directory.

3. **Perform Backup**:
   - Compresses all specified files and folders into a timestamped ZIP archive.
   - Skips inaccessible files and logs any issues.

4. **Logs**:
   - All actions are recorded in a log file named after the script (e.g., `backup_tool.log`).
   - Log files are saved in `C:/logs` (Windows) or `/var/log` (Unix-like systems).

### Example

```bash
sudo python3 backup_tool.py
```

1. Define the sources to back up (e.g., `/home/user/documents`).
2. Specify the destination (e.g., `/home/user/backup`).
3. View progress and log details.

## Logging

- The script logs all events in a file located in the designated log directory:
  - Windows: `C:/logs`
  - Unix-like systems: `/var/log`
- Log entries include timestamps and details about completed actions, warnings, and errors.

## Known Limitations

- Administrative privileges are required to create log directories or access protected files.
- The default log paths (`C:/logs` or `/var/log`) may require elevated permissions.

## Troubleshooting

- Ensure Python is installed and added to your system's PATH.
- Run the script with administrative privileges if encountering permission errors.
- Check the log file for detailed error messages.
- For Windows, use PowerShell to make optimal use of the script.

## License

This tool is distributed under the MIT License. Feel free to modify and share it.

## Contributing

Contributions are welcome! Submit a pull request or open an issue to suggest improvements or report bugs.

---

### Disclaimer
This tool is provided as-is. Use it at your own risk, and always ensure you have appropriate permissions to back up files and folders.

