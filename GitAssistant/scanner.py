import os
import re

SENSITIVE_PATTERNS = [
    r'API[_-]?KEY\s*=\s*[\'"][A-Za-z0-9_\-]+[\'"]',
    r'PASSWORD\s*=\s*[\'"][^\'"]+[\'"]',
    r'TOKEN\s*=\s*[\'"][A-Za-z0-9_\-]+[\'"]'
]

def scan_repository(repo_path):
    sensitive_files = set()
    sensitive_data = set()

    for root, _, files in os.walk(repo_path):
        for file in files:
            full_path = os.path.join(root, file)
            with open(full_path, 'r', errors='ignore') as f:
                content = f.read()
                for pattern in SENSITIVE_PATTERNS:
                    if re.search(pattern, content, re.IGNORECASE):
                        sensitive_files.add(file)
                        sensitive_data.add(full_path)
                        break

    return sensitive_files, sensitive_data
