import os
from git import Repo, GitCommandError, InvalidGitRepositoryError

def current_active_branch(repo_path):
    """Return the current active branch."""
    repo = Repo(repo_path)
    return repo.active_branch.name

def merge_branches(repo_path, branch_to_merge):
    """Merge a specified branch into the current branch."""
    try:
        repo = Repo(repo_path)
    except (InvalidGitRepositoryError, GitCommandError):
        print(f"Error: {repo_path} is not a valid Git repository.")
        return

    if branch_to_merge not in [b.name for b in repo.branches]:
        print(f"Branch '{branch_to_merge}' does not exist in this repository.")
        return

    current_branch = repo.active_branch.name
    print(f"Attempting to merge '{branch_to_merge}' into '{current_branch}'...\n")

    try:
        repo.git.merge(branch_to_merge)
        print(f"Branch '{branch_to_merge}' merged successfully into '{current_branch}'.")
    except GitCommandError as e:
        if 'CONFLICT' in str(e):
            print(f"Merge conflict detected.")
            handle_merge_conflicts(repo)
        else:
            print(f"An error occurred during merge: {e}")

def handle_merge_conflicts(repo):
    """Handle merge conflicts block by block."""
    print("\nConflicts detected in the following files:")
    conflicts = repo.index.unmerged_blobs()
    resolved_files = []

    for file_path in conflicts.keys():
        print(f" - {file_path}")
        full_file_path = os.path.join(repo.working_tree_dir, file_path)

        if os.path.isfile(full_file_path):
            resolved = extract_and_resolve_conflicts_block_by_block(full_file_path)
            if resolved:
                resolved_files.append(file_path)
            else:
                print(f"Could not resolve conflicts in '{file_path}'.")

    if resolved_files:
        repo.git.add(resolved_files)
        try:
            repo.index.commit("Merge resolved by GitAssistant")
            print("\nMerge conflicts resolved and committed.")
        except Exception as e:
            print(f"An error occurred while committing the merge: {e}")
    else:
        print("No conflicts were resolved.")

def extract_and_resolve_conflicts_block_by_block(file_path):
    """Extract and resolve merge conflicts block by block."""
    conflict_start = '<<<<<<<'
    conflict_mid = '======='
    conflict_end = '>>>>>>>'

    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()

        new_lines = []
        conflicts_found = False
        i = 0

        while i < len(lines):
            line = lines[i]
            if line.startswith(conflict_start):
                conflicts_found = True

                # Extract "ours" block
                conflict_block = {'ours': [], 'theirs': []}
                i += 1
                while i < len(lines) and not lines[i].startswith(conflict_mid):
                    conflict_block['ours'].append(lines[i])
                    i += 1

                # Extract "theirs" block
                i += 1
                while i < len(lines) and not lines[i].startswith(conflict_end):
                    conflict_block['theirs'].append(lines[i])
                    i += 1

                i += 1  # Skip the end marker (>>>>>>>)

                # Show conflict block to the user
                print("\nConflict detected in:")
                print(">>> Your changes (ours):")
                for idx, line in enumerate(conflict_block['ours'], start=1):
                    print(f"{idx}: {line.strip()}")

                print(">>> Incoming changes (theirs):")
                for idx, line in enumerate(conflict_block['theirs'], start=1):
                    print(f"{idx}: {line.strip()}")

                # Ask user what they want to keep
                while True:
                    choice = input("Choose (o)urs, (t)heirs, (b)oth, or (e)dit manually: ").lower()
                    if choice == 'o':
                        new_lines.extend(conflict_block['ours'])
                        break
                    elif choice == 't':
                        new_lines.extend(conflict_block['theirs'])
                        break
                    elif choice == 'b':
                        new_lines.extend(conflict_block['ours'] + conflict_block['theirs'])
                        break
                    elif choice == 'e':
                        print("Enter custom changes. Type a single '.' on a new line to finish.")
                        custom_block = []
                        while True:
                            user_input = input()
                            if user_input == '.':
                                break
                            custom_block.append(user_input + '\n')
                        new_lines.extend(custom_block)
                        break
                    else:
                        print("Invalid choice. Please enter 'o', 't', 'b', or 'e'.")
            else:
                new_lines.append(line)
                i += 1

        if conflicts_found:
            with open(file_path, 'w') as file:
                file.writelines(new_lines)
            return True
        else:
            print(f"No conflict markers found in '{file_path}'.")
            return False
    except Exception as e:
        print(f"Error processing conflicts in '{file_path}': {e}")
        return False
