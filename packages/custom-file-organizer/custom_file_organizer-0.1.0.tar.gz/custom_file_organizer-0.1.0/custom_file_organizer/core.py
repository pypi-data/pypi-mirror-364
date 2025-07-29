import os
import shutil

# Default extension map
extension_map = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg"],
    "Videos": [".mp4", ".mov", ".avi", ".mkv"],
    "Documents": [".pdf", ".docx", ".doc", ".txt", ".pptx"],
    "Spreadsheets": [".xls", ".xlsx", ".csv"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
    "Code": [".py", ".java", ".cpp", ".js", ".html", ".css"]
}

def add_extension(category: str, extension: str):
    """
    Add a new file extension to the extension map.

    Parameters:
    - category: The name of the folder category to add to (e.g., "Images")
    - extension: The extension to associate with the category (e.g., ".webp")
    """
    if category in extension_map:
        if extension not in extension_map[category]:
            extension_map[category].append(extension)
    else:
        extension_map[category] = [extension]

def organize_folder(folder_path):
    """
    Organize files in the specified folder by their extensions.

    Parameters:
    - folder_path: Path to the folder to organize
    """
    if not os.path.isdir(folder_path):
        raise NotADirectoryError(f"{folder_path} is not a valid directory")

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        if os.path.isfile(file_path):
            _, ext = os.path.splitext(filename)

            for folder, extensions in extension_map.items():
                if ext.lower() in extensions:
                    dest_folder = os.path.join(folder_path, folder)
                    os.makedirs(dest_folder, exist_ok=True)
                    shutil.move(file_path, os.path.join(dest_folder, filename))
                    break
