#!/usr/bin/env python3
"""
PayQuant (PQN) Resource Path Helper Utility v6.0.0
Handles PyInstaller bundle paths (sys._MEIPASS) and local development fallbacks safely across platforms.
"""

import os
import sys

def get_resource_path(relative_path):
    """
    Returns absolute path to resource, works for dev and PyInstaller single-file executables
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

if __name__ == '__main__':
    print("==================================================")
    print("     PAYQUANT PATH HELPER DIAGNOSTIC TEST        ")
    print("==================================================")
    sample_path = get_resource_path("assets/logo.png")
    print(f"Resource Path Resolved: {sample_path}")
    print("==================================================")
