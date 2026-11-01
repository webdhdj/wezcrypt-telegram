#!/usr/bin/env python3
"""
WezCrypt Telegram — customization applier for a pristine Telegram-iOS checkout.

What it does (and only this):
  1. Writes build-system/wezcrypt-configuration.json from the official
     template_minimal_development_configuration.json, setting:
       - bundle_id            = com.wezcrypt.telegram
       - api_id / api_hash    = read from env WEZCRYPT_API_ID / WEZCRYPT_API_HASH
                                (your OWN credentials from https://my.telegram.org/apps;
                                 never hardcoded, never committed)
       - team_id              = read from env WEZCRYPT_TEAM_ID (your Apple Team ID)
       - app_specific_url_scheme = "wezcrypttg" (avoids clashing with the official app's "tg")
  2. Sets CFBundleDisplayName in every Telegram/Telegram-iOS/*.lproj/InfoPlist.strings
     to the compliant display name (default "WezCrypt").

What it deliberately does NOT do:
  - It does NOT touch the sponsored-messages pipeline
    (TelegramCore AdMessages.swift / ChatHistoryListNode / ChatController).
    Telegram API Terms of Service section 3.3 requires channel-capable clients
    to include support for official sponsored messages and forbids interfering
    with that functionality; section 4.2 makes breach punishable by API
    disconnection. The ad-free path in this build is the official one already
    implemented upstream: Telegram Premium's server-side `no_ads` entitlement
    (account.toggleSponsoredMessages), which the client already honors.
  - It does NOT touch MTProto, encryption, certificate validation, or any
    networking/security code.
  - It does NOT add analytics or trackers.

Display-name note (API Terms 2.3): an app title must not include the word
"Telegram" unless preceded by "Unofficial". The home-screen display name is
therefore "WezCrypt". "WezCrypt Telegram" remains the project codename only.
Override with --display-name if you accept the Terms risk yourself.

Usage:
  WEZCRYPT_API_ID=... WEZCRYPT_API_HASH=... WEZCRYPT_TEAM_ID=... \
    python3 customize.py /path/to/Telegram-iOS [--display-name WezCrypt]
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path

BUNDLE_ID = "com.wezcrypt.telegram"
URL_SCHEME = "wezcrypttg"


def fail(msg: str) -> None:
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("checkout", help="Path to a pristine Telegram-iOS checkout (release-13.1.2)")
    ap.add_argument("--display-name", default="WezCrypt")
    args = ap.parse_args()

    root = Path(args.checkout).resolve()
    if not (root / "build-system" / "template_minimal_development_configuration.json").exists():
        fail(f"{root} does not look like a Telegram-iOS checkout (missing build-system template)")

    versions_file = root / "versions.json"
    if versions_file.exists():
        versions = json.loads(versions_file.read_text())
        print(f"upstream app version: {versions.get('app')}  xcode: {versions.get('xcode')}  bazel: {versions.get('bazel')}")

    api_id = os.environ.get("WEZCRYPT_API_ID", "")
    api_hash = os.environ.get("WEZCRYPT_API_HASH", "")
    team_id = os.environ.get("WEZCRYPT_TEAM_ID", "")
    if not api_id or not api_hash or not team_id:
        print("warning: WEZCRYPT_API_ID / WEZCRYPT_API_HASH / WEZCRYPT_TEAM_ID not all set; "
              "writing placeholders — the build will NOT work until you fill them from "
              "https://my.telegram.org/apps and your Apple Developer account.")

    template = json.loads((root / "build-system" / "template_minimal_development_configuration.json").read_text())
    config = dict(template)
    config.update({
        "bundle_id": BUNDLE_ID,
        "api_id": api_id or "{! get one at https://my.telegram.org/apps !}",
        "api_hash": api_hash or "{! get one at https://my.telegram.org/apps !}",
        "team_id": team_id or "{! your Apple Team ID !}",
        "app_specific_url_scheme": URL_SCHEME,
        "is_internal_build": "true",
        "is_appstore_build": "false",
    })
    out_config = root / "build-system" / "wezcrypt-configuration.json"
    out_config.write_text(json.dumps(config, indent="\t") + "\n")
    print(f"wrote {out_config} (bundle_id={BUNDLE_ID})")

    # --- Display name in every locale's InfoPlist.strings ---
    lproj_dirs = sorted((root / "Telegram" / "Telegram-iOS").glob("*.lproj"))
    if not lproj_dirs:
        fail("no *.lproj directories found under Telegram/Telegram-iOS")
    changed = 0
    pattern = re.compile(r'^"CFBundleDisplayName"\s*=.*$', re.MULTILINE)
    for d in lproj_dirs:
        strings = d / "InfoPlist.strings"
        if not strings.exists():
            continue
        text = strings.read_text(encoding="utf-8")
        new_line = f'"CFBundleDisplayName" = "{args.display_name}";'
        if pattern.search(text):
            new_text = pattern.sub(new_line, text)
        else:
            new_text = text.rstrip("\n") + "\n" + new_line + "\n"
        if new_text != text:
            strings.write_text(new_text, encoding="utf-8")
            changed += 1
    print(f"display name '{args.display_name}' applied to {changed} InfoPlist.strings files")
    print("done. No sponsored-message, MTProto, crypto, or networking code was modified.")


if __name__ == "__main__":
    main()
