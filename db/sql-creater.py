import os
import sqlite3
import platform
import datetime


def get_drives():
    system = platform.system()
    drives = []
    if system == "Windows":
        import string
        from ctypes import windll

        bitmask = windll.kernel32.GetLogicalDrives()
        for letter in string.ascii_uppercase:
            if bitmask & 1:
                drives.append(f"{letter}:\\")
            bitmask >>= 1
    return drives


def get_file_metadata(file_path):
    try:
        stat = os.stat(file_path)
        file_ext = os.path.splitext(file_path)[1].lower()

        file_types = {".txt": "text", ".pdf": "pdf", ".docx": "docx"}
        

        if file_ext in file_types:
            return {
                "file": os.path.basename(file_path),
                "file_type": file_types[file_ext],
                "location": os.path.abspath(file_path),
                "created_date": datetime.datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S"),
            }
    except Exception as e:
        return None  


def scan_drive(drive, cursor):
    for root, _, files in os.walk(drive):
        for name in files:
            file_path = os.path.join(root, name)
            metadata = get_file_metadata(file_path)
            if metadata:
                cursor.execute(
                    "INSERT INTO file_metadata (file, file_type, location, created_date) VALUES (?, ?, ?, ?)",
                    (metadata["file"], metadata["file_type"], metadata["location"], metadata["created_date"]),
                )


def main():
    db_name = r"db\sqlLite\file_metadata.db"
    
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS file_metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file TEXT,
            file_type TEXT,
            location TEXT,
            created_date TEXT
        )"""
    )

    drives = get_drives()
    for drive in drives:
        print(f"Scanning {drive}...")
        scan_drive(drive, cursor)

    conn.commit()
    conn.close()
    print(f"Metadata saved to {db_name}")


if __name__ == "__main__":
    main()
