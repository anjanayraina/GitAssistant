# GitAssistant/scanner.py

import os
from git import Repo, GitCommandError, InvalidGitRepositoryError, BadName
from utils import COMPILED_FILE_PATTERNS, COMPILED_DATA_PATTERNS

def scan_repository(repo_path):
    """
    Scans the repository for sensitive files and data.

    :param repo_path: Path to the local Git repository
    :return: Tuple containing lists of sensitive files and data found
    """
    try:
        repo = Repo(repo_path)
    except (GitCommandError, InvalidGitRepositoryError):
        print(f"Error: {repo_path} is not a valid Git repository.")
        return [], []

    print(f"Scanning repository at {repo_path}...\n")

    tracked_files = []

    try:
        # Check if the repository has any commits
        if repo.head.is_valid():
            # Get files changed since HEAD
            tracked_files.extend([item.a_path for item in repo.index.diff('HEAD')])
    except BadName:
        # 'HEAD' does not exist because there are no commits yet
        pass

    # Add all tracked files in the repository
    tracked_files.extend(repo.git.ls_files().split('\n'))

    # Remove duplicates and empty strings
    tracked_files = list(set(filter(None, tracked_files)))

    sensitive_files_found = []
    sensitive_data_found = []

    for file_path in tracked_files:
        for pattern in COMPILED_FILE_PATTERNS:
            if pattern.match(file_path):
                sensitive_files_found.append(file_path)
                break

        # Scan the content of the file for sensitive data patterns
        full_path = os.path.join(repo_path, file_path)
        if os.path.isfile(full_path):
            try:
                with open(full_path, 'r', errors='ignore') as file:
                    content = file.read()
                    for pattern in COMPILED_DATA_PATTERNS:
                        if pattern.search(content):
                            sensitive_data_found.append(file_path)
                            break
            except Exception as e:
                print(f"Could not read file {file_path}: {e}")

    return sensitive_files_found, sensitive_data_found
