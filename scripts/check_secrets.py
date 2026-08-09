#!/usr/bin/env python3
"""
PayQuant (PQN) - Secret Detection Gate v2.0.0-quantum
=====================================================
Scans a working tree for credentials/seeds/private material BEFORE committing
or pushing. Exit code 1 blocks deployment when a violation is found.

Checks
    1. Banned file extensions (*.key, *.pem, *.keystore, ...)
    2. Private-key/seed/api-key regex patterns
    3. Files inside suspicious directories (secrets/, private_keys/, ...)

Only the repository tree is scanned. Local-only satellite dirs outside the
tree (e.g. %APPDATA%/PayMainnetData or ~/.payquant) are intentionally never
scanned.
"""

import argparse
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SKIP_DIRS = {".git", "node_modules", "dist", "build", "__pycache__",
             "wallet/dist", "wallet/www", "target", ".venv", "venv"}

BANNED_EXT = (".pem", ".key", ".p12", ".pfx", ".keystore", ".ovpn",
              ".priv", ".id_rsa")

SUSPICIOUS_DIRS = ("secrets", "private_keys", "wallets", ".env-data",
                   "rope-state", "keyring")

BANNED_PATTERNS = (
    re.compile(r"-----BEGIN (RSA |OPENSSH |EC )?PRIVATE KEY-----"),
    re.compile(r"(?<![A-Za-z_0-9])(api[_-]?key|secret)\s*[:=]\s*[\"']?[A-Za-z0-9_\-]{16,}"),
    re.compile(r"BEGIN (RSA )?PRIVATE[ A-Z]*KEY"),
    re.compile(r"mnemonic\s*[:=]\s*[\"'][a-z ]{60,}[\"']"),
    re.compile(r"OUTSHIFT_API_KEY\s*=\s*\S+", re.IGNORECASE),
)

# Files that document key names but never hold real values (templates).
TEMPLATE_NAMES = {".env.example", ".env.template"}


def _walk(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        rel = os.path.relpath(dirpath, root)
        for fname in filenames:
            yield os.path.join(dirpath, fname), rel, fname


def scan(repo_root=None):
    root = repo_root or ROOT
    root = os.path.abspath(root)
    violations = []
    for path, rel, fname in _walk(root):
        relpath = os.path.join(rel, fname).replace(os.sep, "/")
        lower = fname.lower()
        if lower in TEMPLATE_NAMES:
            continue
        if lower.endswith(BANNED_EXT):
            violations.append(f"banned extension: {relpath}")
            continue
        try:
            if os.path.getsize(path) > 2_000_000:
                continue
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
        except OSError:
            continue
        if not text:
            continue
        for pat in BANNED_PATTERNS:
            if pat.search(text):
                violations.append(f"pattern [{pat.pattern}] -> {relpath}")
        parts = relpath.split("/")
        if any(s in parts for s in SUSPICIOUS_DIRS):
            violations.append(f"suspicious dir: {relpath}")
    return sorted(set(violations))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=None, help="repo root to scan")
    args = ap.parse_args()

    problems = scan(args.root)
    if problems:
        print("[check_secrets] SECRETS FOUND - blocking deployment:", flush=True)
        for v in problems:
            print("  -", v, flush=True)
        sys.exit(1)
    print("[check_secrets] OK - no private keys, seeds, or wallet data in tree.",
          flush=True)
    sys.exit(0)