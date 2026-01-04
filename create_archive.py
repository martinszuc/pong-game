#!/usr/bin/env python3
"""
create_archive.py - Package the pong game for sharing

This script creates a clean zip archive of the project, excluding
unnecessary files like logs, AI notes, and Python cache files.
"""

import zipfile
import os
from pathlib import Path
from datetime import datetime

# files and folders to exclude from the archive
EXCLUDE_PATTERNS = [
    'pong_game.log',
    'LINUX_SETUP_NOTES.md',  # technical notes, not needed for teachers
    'create_archive.py',
    'create_archive.py',
    'PROJECT_OVERVIEW.md',
    'PRESENTATION_SLIDES.md',
    'CODEBASE_REFERENCE_FINAL.md',
    '__pycache__',
    '*.pyc',
    '.DS_Store',
    '.git',
    '.gitignore',
    'venv',  # virtual environment is too large
    '*.zip',  # don't include old archives
    'high_scores.json',  # don't share personal high scores
    'settings.json',  # don't share personal settings
]

def should_exclude(path):
    """check if a file/folder should be excluded from the archive"""
    path_str = str(path)
    
    # check each exclude pattern
    for pattern in EXCLUDE_PATTERNS:
        if pattern.startswith('*'):
            # wildcard pattern (e.g., *.pyc)
            if path_str.endswith(pattern[1:]):
                return True
        elif pattern in path_str:
            return True
    
    return False

def create_project_archive():
    """create a zip archive of the project"""
    # get the project root directory
    project_root = Path(__file__).parent
    project_name = project_root.name
    
    # create archive filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d')
    archive_name = f"{project_name}_{timestamp}.zip"
    archive_path = project_root / archive_name
    
    print(f"Creating archive: {archive_name}")
    print(f"Excluding: {', '.join(EXCLUDE_PATTERNS)}")
    print()
    
    # create the zip file
    with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        file_count = 0
        
        # walk through all files in the project
        for root, dirs, files in os.walk(project_root):
            # skip excluded directories
            dirs[:] = [d for d in dirs if not should_exclude(Path(root) / d)]
            
            for file in files:
                file_path = Path(root) / file
                
                # skip excluded files
                if should_exclude(file_path):
                    continue
                
                # calculate relative path for the archive
                relative_path = file_path.relative_to(project_root)
                
                # add file to archive
                zipf.write(file_path, arcname=relative_path)
                print(f"  Added: {relative_path}")
                file_count += 1
    
    # get archive size
    size_mb = archive_path.stat().st_size / (1024 * 1024)
    
    print()
    print(f"✓ Archive created successfully!")
    print(f"  Location: {archive_path}")
    print(f"  Files: {file_count}")
    print(f"  Size: {size_mb:.2f} MB")
    print()
    print("Ready to share with classmates!")

if __name__ == "__main__":
    create_project_archive()

