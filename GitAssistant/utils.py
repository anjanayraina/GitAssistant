# GitAssistant/utils.py

import re

# Define patterns for sensitive files and data
SENSITIVE_FILE_PATTERNS = [
    r'.*\.env$',          # Files ending with .env
    r'.*\.key$',          # Files ending with .key
    r'.*\.pem$',          # Files ending with .pem
    r'.*\.p12$',          # Files ending with .p12
    r'.*\.crt$',          # Files ending with .crt
    r'.*id_rsa.*',        # Files containing id_rsa
    r'.*\.kdbx$',         # KeePass database files
]

SENSITIVE_DATA_PATTERNS = [
    r'API_KEY\s*=\s*[\'"].+[\'"]',   # API_KEY = "value"
    r'PASSWORD\s*=\s*[\'"].+[\'"]',  # PASSWORD = "value"
    r'AWS_SECRET_ACCESS_KEY\s*=\s*[\'"].+[\'"]',
    r'BEGIN PRIVATE KEY',            # -----BEGIN PRIVATE KEY-----
    r'BEGIN RSA PRIVATE KEY',        # -----BEGIN RSA PRIVATE KEY-----
    r'BEGIN EC PRIVATE KEY',         # -----BEGIN EC PRIVATE KEY-----
    r'[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+',  # Email addresses
]

def compile_patterns(patterns):
    """
    Compiles a list of regex patterns.

    :param patterns: List of string patterns
    :return: List of compiled regex patterns
    """
    return [re.compile(pattern) for pattern in patterns]

# Compile patterns for performance
COMPILED_FILE_PATTERNS = compile_patterns(SENSITIVE_FILE_PATTERNS)
COMPILED_DATA_PATTERNS = compile_patterns(SENSITIVE_DATA_PATTERNS)
