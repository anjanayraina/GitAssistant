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
        if 'Merge conflict' in str(e):
            print(f"Merge conflict detected.")
            handle_merge_conflicts(repo)
        else:
            print(f"An error occurred during merge: {e}")

def handle_merge_conflicts(repo):
    """
    Handles merge conflicts by listing conflicting files and extracting conflicting lines.
    Allows the user to choose which version to keep.

    :param repo: Repo object representing the Git repository
    """
    print("\nConflicts detected in the following files:")
    conflicts = repo.index.unmerged_blobs()
    resolved_files = []

    for file_path in conflicts.keys():
        if file_path:
            print(f" - {file_path}")
            full_file_path = os.path.join(repo.working_tree_dir, file_path)
            if os.path.isfile(full_file_path):
                resolved = extract_and_resolve_conflicts(full_file_path)
                if resolved:
                    resolved_files.append(file_path)
                else:
                    print(f"Could not resolve conflicts in '{file_path}'.")
            else:
                print(f"Error: '{full_file_path}' is not a valid file.")
        else:
            print("Warning: Encountered an empty file path in conflicts.")

    if resolved_files:
        # Add resolved files to the index
        repo.git.add(resolved_files)
        try:
            # Commit the merge
            repo.index.commit(f"Merge resolved by GitAssistant")
            print("\nMerge conflicts resolved and committed.")
        except Exception as e:
            print(f"An error occurred while committing the merge: {e}")
    else:
        print("No conflicts were resolved.")

def extract_and_resolve_conflicts(file_path):
    """
    Extracts conflicting sections from a file and resolves them based on user input.

    :param file_path: Path to the conflicting file
    :return: True if conflicts were resolved, False otherwise
    """
    conflict_start = '<<<<<<<'
    conflict_mid = '======='
    conflict_end = '>>>>>>>'

    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()

        new_lines = []
        i = 0
        conflicts_found = False

        while i < len(lines):
            line = lines[i]
            if line.startswith(conflict_start):
                conflicts_found = True
                conflict_block = {
                    'ours': [],
                    'theirs': []
                }

                i += 1
                # Collect 'ours' lines
                while i < len(lines) and not lines[i].startswith(conflict_mid):
                    conflict_block['ours'].append(lines[i])
                    i += 1

                i += 1  # Skip the '=======' line

                # Collect 'theirs' lines
                while i < len(lines) and not lines[i].startswith(conflict_end):
                    conflict_block['theirs'].append(lines[i])
                    i += 1

                i += 1  # Skip the '>>>>>>>' line

                # Display the conflict to the user
                print(f"\nConflict in file '{os.path.basename(file_path)}':")
                print(">>> Current changes (in your branch):")
                for idx, content in enumerate(conflict_block['ours'], start=1):
                    print(f"Line {idx}: {content.rstrip()}")

                print(">>> Incoming changes (from the branch being merged):")
                for idx, content in enumerate(conflict_block['theirs'], start=1):
                    print(f"Line {idx}: {content.rstrip()}")

                # Ask the user which version to accept
                while True:
                    choice = input("Choose which changes to keep? (o)urs, (t)heirs: ").lower()
                    if choice == 'o':
                        new_lines.extend(conflict_block['ours'])
                        break
                    elif choice == 't':
                        new_lines.extend(conflict_block['theirs'])
                        break
                    else:
                        print("Invalid choice. Please enter 'o' for ours or 't' for theirs.")
            else:
                new_lines.append(line)
                i += 1

        if conflicts_found:
            # Write the resolved content back to the file
            with open(file_path, 'w') as file:
                file.writelines(new_lines)
            return True
        else:
            print(f"No conflict markers found in '{file_path}'.")
            return False
    except Exception as e:
        print(f"Error reading file '{file_path}': {e}")
        return False
