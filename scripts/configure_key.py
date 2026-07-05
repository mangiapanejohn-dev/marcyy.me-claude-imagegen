#!/usr/bin/env python3
"""Manage the locally stored OpenAI API key (and optional custom base URL,
for third-party OpenAI-compatible relay/proxy services) for the imagegen
skill.

Subcommands: set, status, delete, validate. Never prints the key value itself.
"""

# imagegen · by Marc (marcyy.me)

from __future__ import annotations

import argparse
import os
import sys

import _key_store


def _die(message: str, code: int = 1) -> None:
    print(f"Error: {message}", file=sys.stderr)
    raise SystemExit(code)


def _dependency_hint(package: str) -> str:
    return f"Install it with `uv pip install {package}` (or `pip install {package}`)."


def _cmd_set(args: argparse.Namespace) -> None:
    key = args.key
    base_url = args.base_url

    if key is None and base_url is None:
        # Back-compat: no flags at all means "read the key from stdin."
        if sys.stdin.isatty():
            _die("Nothing to set. Pass --key and/or --base-url, or pipe a key via stdin.")
        key = sys.stdin.readline().strip()

    updates: dict = {}
    if key is not None:
        if not key or "\n" in key or len(key) < 20:
            _die("That doesn't look like a valid API key.")
        updates["openai_api_key"] = key.strip()

    if base_url is not None:
        base_url = base_url.strip()
        if not base_url:
            updates["base_url"] = None  # explicit empty string clears it
        elif not (base_url.startswith("http://") or base_url.startswith("https://")):
            _die("--base-url must start with http:// or https://")
        else:
            updates["base_url"] = base_url

    if not updates:
        _die("Nothing to set.")

    _key_store.save_config(updates)

    saved = []
    if "openai_api_key" in updates:
        saved.append("API key")
    if "base_url" in updates:
        saved.append("base URL cleared" if updates["base_url"] is None else "base URL")
    print(f"Saved ({', '.join(saved)}) to {_key_store.CONFIG_FILE} (mode 600).")


def _cmd_status(_args: argparse.Namespace) -> None:
    st = _key_store.status()
    if os.getenv("OPENAI_API_KEY"):
        print("OPENAI_API_KEY is set in this environment (takes priority over the stored config).")
    print(f"Configured: {'yes' if st['configured'] else 'no'}")
    print(f"Config path: {st['path']}")
    if st["mode_ok"] is not None:
        print(
            "Permissions: ok (600)"
            if st["mode_ok"]
            else "Permissions: WARNING - not 600, tighten with chmod 600"
        )
    base_url = os.getenv("OPENAI_BASE_URL") or st["base_url"]
    print(f"Base URL: {base_url if base_url else 'default (api.openai.com)'}")


def _cmd_delete(_args: argparse.Namespace) -> None:
    removed = _key_store.delete_key()
    print("Removed stored key and base URL." if removed else "No stored config to remove.")


def _cmd_validate(_args: argparse.Namespace) -> None:
    key = os.getenv("OPENAI_API_KEY") or _key_store.load_key()
    if not key:
        _die("No API key configured (env var or stored config).")
    base_url = os.getenv("OPENAI_BASE_URL") or _key_store.load_base_url()

    try:
        from openai import OpenAI
    except ImportError:
        _die(f"openai SDK not installed. {_dependency_hint('openai')}")

    client = OpenAI(api_key=key, base_url=base_url) if base_url else OpenAI(api_key=key)
    try:
        client.models.list()
    except Exception as exc:  # noqa: BLE001 - surface whatever the SDK raises
        msg = str(exc)
        if "401" in msg or "invalid_api_key" in msg.lower() or "unauthorized" in msg.lower():
            _die(f"Key rejected by the API: {exc}")
        _die(
            "Couldn't verify via /v1/models. If you're using a relay/proxy that only "
            "proxies image generation (not /v1/models), this may be a false alarm — "
            f"try generating an image directly instead. Raw error: {exc}"
        )
    print("Key is valid." + (f" (base_url: {base_url})" if base_url else ""))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Manage the imagegen skill's stored OpenAI API key / base URL"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_set = sub.add_parser("set", help="Store a new API key and/or base URL")
    p_set.add_argument("--key", help="API key value; omit (with no --base-url) to read one line from stdin")
    p_set.add_argument(
        "--base-url",
        help="Custom API base URL for a relay/proxy service, e.g. https://xxx.example.com/v1. "
        "Pass an empty string to clear it and revert to the official OpenAI endpoint.",
    )
    p_set.set_defaults(func=_cmd_set)

    p_status = sub.add_parser("status", help="Show whether a key/base URL is configured")
    p_status.set_defaults(func=_cmd_status)

    p_delete = sub.add_parser("delete", help="Remove the stored key and base URL")
    p_delete.set_defaults(func=_cmd_delete)

    p_validate = sub.add_parser("validate", help="Call the API to confirm the key (and base URL) work")
    p_validate.set_defaults(func=_cmd_validate)

    args = parser.parse_args()
    args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
