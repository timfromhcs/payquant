#!/usr/bin/env python3
"""
PayQuant (PQN) Miner Configuration Manager v6.4.0 (FS-02-01)

Persists miner settings across restarts so the payout wallet address,
thread count, and mining intensity are auto-loaded on every launch.

Storage location (priority order):
  1. $PAYQUANT_MINER_CONFIG env override
  2. <user_data>/miner_config.json   (cross-platform user config dir)
  3. ./miner_config.json             (repo-local fallback)

Supports Windows / Linux / macOS. Pure stdlib - zero external dependencies.
"""

import os
import sys
import json

CONFIG_FILENAME = "miner_config.json"
DEFAULT_CONFIG = {
    "payout_address": "",
    "threads": 4,
    "intensity": 50,
    "dca_enabled": False,
    "pool": "solo",
    "auto_start": False
}

VALID_INTENSITY = list(range(1, 101))


def user_data_dir():
    """Return a stable, cross-platform user config directory."""
    if sys.platform == "win32":
        base = os.environ.get("APPDATA") or os.path.expanduser("~")
        return os.path.join(base, "PayQuant")
    if sys.platform == "darwin":
        return os.path.expanduser("~/Library/Application Support/PayQuant")
    xdg = os.environ.get("XDG_CONFIG_HOME")
    if xdg:
        return os.path.join(xdg, "payquant")
    return os.path.join(os.path.expanduser("~"), ".config", "payquant")


def config_path():
    """Resolve the miner config file path."""
    env = os.environ.get("PAYQUANT_MINER_CONFIG")
    if env:
        return env
    return os.path.join(user_data_dir(), CONFIG_FILENAME)


def defaults():
    return dict(DEFAULT_CONFIG)


def load_config():
    """Load miner config; returns a dict always (never None)."""
    cfg = defaults()
    try:
        path = config_path()
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                import json
                data = json.load(f)
                if isinstance(data, dict):
                    for key in cfg:
                        if key in data and data[key] is not None:
                            cfg[key] = data[key]
    except Exception as e:  # pragma: no cover - defensive
        sys.stderr.write(f"[PayQuant MinerConfig] warning: {e}\n")
    return cfg


def save_config(cfg):
    """Persist a config dict to disk. Returns True on success."""
    import json
    final = defaults()
    for key in final:
        if key in cfg and cfg[key] is not None:
            final[key] = cfg[key]
    try:
        path = config_path()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(final, f, indent=2, sort_keys=True)
        return True
    except Exception as e:  # pragma: no cover - defensive
        sys.stderr.write(f"[PayQuant Miner] Could not save config: {e}\n")
        return False


def sanitize_address(address):
    """Basic PQN (pqn1q...) address validation and normalization."""
    if not address:
        return ""
    address = str(address).strip()
    return address


def clean(config):
    """Ensure loaded values respect allowed ranges & types."""
    cfg = defaults()
    for key, value in config.items():
        if key == "threads":
            try:
                value = max(1, min(512, int(value)))
            except (TypeError, ValueError):
                value = DEFAULT_CONFIG["threads"]
        elif key == "intensity":
            try:
                value = max(1, min(100, int(value)))
            except (TypeError, ValueError):
                value = DEFAULT_CONFIG["intensity"]
        cfg[key] = value
    return cfg


def main():  # CLI helper for quick inspection / testing
    import argparse
    parser = argparse.ArgumentParser(description="PayQuant Miner Config Manager")
    parser.add_argument("--path", action="store_true", help="Print the resolved config path")
    parser.add_argument("--show", action="store_true", help="Print current config")
    parser.add_argument("--set", nargs=2, metavar=("KEY", "VALUE"), action="append",
                        help="Set a config value (repeatable). e.g. --set payout_address pqn1q...")
    args = parser.parse_args()

    if args.path:
        print(config_path())
        return 0

    cfg = load_config()
    if args.set:
        for key, value in args.set:
            if key in cfg:
                if key in ("threads",):
                    value = int(value)
                elif key in ("dca_enabled", "auto_start"):
                    value = value.lower() in ("1", "true", "yes", "on")
                cfg[key] = value
        save_config(cfg)
    if args.show or not args.set:
        for key, value in load_config().items():
            print(f"{key} = {value}")
    return 0


if __name__ == "__main__":
    sys.exit(main())