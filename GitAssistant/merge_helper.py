# GitAssistant/merge_helper.py

import os
from git import Repo, GitCommandError, InvalidGitRepositoryError
from git.exc import GitCommandError, BadName

def merge_branches(repo_path, branch_to_merge):
    """
    Attempts to merge the specified branch into the current branch and handles conflicts.

    :param repo_path: Path to the local Git repository
    :param branch_to_merge: Name of the branch to merge into the current branch
    """
    try:
        repo = Repo(repo_path)
    except (InvalidGitRepositoryError, GitCommandError):
        print(f"Error: {repo_path} is not a valid Git repository.")
        return

    # Ensure the branch to merge exists
    if branch_to_merge not in repo.branches:
        print(f"Branch '{branch_to_merge}' does not exist in this repository.")
        return

    current_branch = repo.active_branch.name
    print(f"Attempting to merge '{branch_to_merge}' into '{current_branch}'...\n")

    try:
        # Perform the merge
        repo.git.merge(branch_to_merge)
        print(f"Branch '{branch_to_merge}' merged successfully into '{current_branch}'.")
    except GitCommandError as e:
        print(f"Merge conflict detected: {e}")
        handle_merge_conflicts(repo)

def handle_merge_conflicts(repo):
    """
    Handles merge conflicts by listing conflicting files and extracting conflicting lines.

    :param repo: Repo object representing the Git repository
    """
    print("\nConflicts detected in the following files:")
    conflicts = repo.index.unmerged_blobs()
    for file_path in conflicts.keys():
        if file_path:
            print(f" - {file_path}")
            full_file_path = os.path.join(repo.working_tree_dir, file_path)
            if os.path.isfile(full_file_path):
                extract_conflicting_lines(full_file_path)
            else:
                print(f"Error: '{full_file_path}' is not a valid file.")
        else:
            print("Warning: Encountered an empty file path in conflicts.")

def extract_conflicting_lines(file_path):
    """
    Extracts and displays conflicting lines from a file with merge conflicts.

    :param file_path: Path to the conflicting file
    """
    conflict_start = '<<<<<<<'
    conflict_mid = '======='
    conflict_end = '>>>>>>>'

    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()

        in_conflict = False
        conflict_blocks = []
        current_conflict = {'ours': [], 'theirs': []}
        section = None

        for index, line in enumerate(lines):
            stripped_line = line.strip()
            if stripped_line.startswith(conflict_start):
                in_conflict = True
                section = 'ours'
                continue
            elif stripped_line.startswith(conflict_mid):
                section = 'theirs'
                continue
            elif stripped_line.startswith(conflict_end):
                in_conflict = False
                conflict_blocks.append((index, current_conflict.copy()))
                current_conflict = {'ours': [], 'theirs': []}
                section = None
                continue

            if in_conflict and section:
                current_conflict[section].append((index + 1, line.rstrip('\n')))

        # Display conflicting sections
        if conflict_blocks:
            for block_num, (line_num, conflict) in enumerate(conflict_blocks, start=1):
                print(f"\nConflict {block_num} in file '{os.path.basename(file_path)}':")
                print(">>> Current changes (in your branch):")
                for idx, content in conflict['ours']:
                    print(f"Line {idx}: {content}")
                print(">>> Incoming changes (from the branch being merged):")
                for idx, content in conflict['theirs']:
                    print(f"Line {idx}: {content}")
        else:
            print(f"No conflict markers found in '{file_path}'.")
    except Exception as e:
        print(f"Error reading file '{file_path}': {e}")
