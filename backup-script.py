import os
import shutil

# Log-Funktion
def log(message):
    print(message)
    with open("backup_log.txt", "a") as log_file:
        log_file.write(message + "\n")

# Backup-Quellen verwalten
def manage_backup_sources():
    sources_file = "backup_sources.txt"
    if not os.path.exists(sources_file):
        open(sources_file, "w").close()
        log("Backup sources file created.")

    while True:
        print("\nCurrent backup sources:")
        with open(sources_file, "r") as file:
            sources = file.readlines()
            for i, source in enumerate(sources, start=1):
                print(f"{i}: {source.strip()}")

        action = input("Add (a), Remove (r), or Finish (f): ").lower()
        if action == 'a':
            path = input("Enter the path to add: ")
            if os.path.exists(path):
                with open(sources_file, "a") as file:
                    file.write(path + "\n")
                log(f"Added source: {path}")
            else:
                log("Invalid path.")
        elif action == 'r':
            index = int(input("Enter the number of the source to remove: "))
            if 0 < index <= len(sources):
                removed = sources.pop(index - 1)
                with open(sources_file, "w") as file:
                    file.writelines(sources)
                log(f"Removed source: {removed.strip()}")
            else:
                log("Invalid selection.")
        elif action == 'f':
            break

# Backup-Ziel prüfen und setzen
def get_backup_destination():
    while True:
        destination = input("Enter backup destination path: ")
        if os.path.exists(destination) and os.access(destination, os.W_OK):
            print(f"Destination accepted: {destination}")
            return destination
        else:
            log("Invalid destination path.")
            retry = input("Retry? (y/n): ").lower()
            if retry != 'y':
                return None

# Backup durchführen
def perform_backup(sources, destination):
    for source in sources:
        source = source.strip()
        if not os.path.exists(source):
            log(f"Source not found: {source}")
            continue

        try:
            base_name = os.path.basename(source.rstrip(os.sep))
            backup_path = os.path.join(destination, base_name)

            if os.path.isdir(source):
                shutil.copytree(source, backup_path, dirs_exist_ok=True)
            else:
                shutil.copy2(source, backup_path)

            log(f"Backup successful: {source} to {backup_path}")
        except Exception as e:
            log(f"Error during backup of {source}: {e}")

# Hauptprogramm
def main():
    log("Backup process started.")

    manage_backup_sources()

    with open("backup_sources.txt", "r") as file:
        sources = file.readlines()

    if not sources:
        log("No backup sources defined. Exiting.")
        return

    destination = get_backup_destination()
    if not destination:
        log("No valid destination defined. Exiting.")
        return

    perform_backup(sources, destination)
    log("Backup process completed.")

if __name__ == "__main__":
    main()
