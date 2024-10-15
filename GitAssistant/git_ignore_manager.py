# GitAssistant/gitignore_manager.py

import os
import re
from utils import COMPILED_FILE_PATTERNS

def update_gitignore(repo_path):
    """
    Suggests updates to the .gitignore file based on detected sensitive files.

    :param repo_path: Path to the local Git repository
    """
    gitignore_path = os.path.join(repo_path, '.gitignore')

    # Read current .gitignore entries
    existing_patterns = []
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r') as gitignore_file:
            existing_patterns = gitignore_file.read().splitlines()

    # Detect files to ignore
    files_to_ignore = []

    for pattern in COMPILED_FILE_PATTERNS:
        regex = pattern
        for root, dirs, files in os.walk(repo_path):
            for file in files:
                relative_path = os.path.relpath(os.path.join(root, file), repo_path)
                if regex.match(relative_path):
                    if relative_path not in existing_patterns and relative_path not in files_to_ignore:
                        files_to_ignore.append(relative_path)

    # Suggest updates to .gitignore
    if files_to_ignore:
        print("\nThe following files are suggested to be added to .gitignore:")
        for file in files_to_ignore:
            print(f" - {file}")

        user_input = input("\nDo you want to add these entries to .gitignore? (y/n): ").lower()
        if user_input == 'y':
            with open(gitignore_path, 'a') as gitignore_file:
                for file in files_to_ignore:
                    gitignore_file.write(f"\n{file}")
            print("Updated .gitignore successfully.")
        else:
            print("No changes made to .gitignore.")
    else:
        print("No new entries to add to .gitignore.")
