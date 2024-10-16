# main.py

import os
from scanner import scan_repository
from git_ignore_manager import update_gitignore
from merge_helper import merge_branches , current_active_branch

def main():
    repo_path = input("Enter the path to your local Git repository: ").strip()
    if not os.path.isdir(repo_path):
        print("The specified path does not exist or is not a directory.")
        return

    sensitive_files, sensitive_data = scan_repository(repo_path)

    if sensitive_files:
        print("Sensitive files detected:")
        for file in set(sensitive_files):
            print(f" - {file}")
    else:
        print("No sensitive files detected.")
    head = current_active_branch(repo_path)
    print(f"Current active branch : {head}")
    if sensitive_data:
        print("Files containing sensitive data detected:")
        for file in set(sensitive_data):
            print(f" - {file}")
    else:
        print("No sensitive data detected in files.")

    update_gitignore(repo_path)

    merge_option = input("\nDo you want to merge a branch into the current branch? (y/n): ").lower()
    if merge_option == 'y':
        branch_to_merge = input("Enter the name of the branch to merge: ").strip()
        merge_branches(repo_path, branch_to_merge)
    else:
        print("Merge operation skipped.")

if __name__ == "__main__":
    main()
