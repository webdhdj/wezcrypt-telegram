#!/bin/bash
# WezCrypt Telegram — build script. RUN ON macOS ONLY.
# Requirements (from upstream versions.json of release-13.1.2):
#   macOS 27, Xcode 27.1, Bazel 9.2.0 (fetched by Make.py tooling), ~90 GB free disk.
# This script fails loudly on any unmet precondition instead of producing a broken IPA.
set -euo pipefail

UPSTREAM_TAG="release-13.1.2"
EXPECTED_XCODE="27.1"

fail() { echo "ERROR: $*" >&2; exit 1; }

[ "$(uname)" = "Darwin" ] || fail "This must run on macOS. Current OS: $(uname). Telegram-iOS cannot be built on Linux/Windows."
command -v xcodebuild >/dev/null || fail "Xcode not installed."
XCODE_VER="$(xcodebuild -version | head -1 | awk '{print $2}')"
echo "Xcode version: $XCODE_VER (upstream versions.json expects $EXPECTED_XCODE)"
[ "$XCODE_VER" = "$EXPECTED_XCODE" ] || fail "Xcode $EXPECTED_XCODE required by Telegram-iOS $UPSTREAM_TAG; found $XCODE_VER. Install the exact version from developer.apple.com."
[ -n "${WEZCRYPT_API_ID:-}" ] || fail "WEZCRYPT_API_ID is empty. Get your OWN api_id at https://my.telegram.org/apps"
[ -n "${WEZCRYPT_API_HASH:-}" ] || fail "WEZCRYPT_API_HASH is empty. Get your OWN api_hash at https://my.telegram.org/apps"
[ -n "${WEZCRYPT_TEAM_ID:-}" ] || fail "WEZCRYPT_TEAM_ID is empty. Find it in Keychain Access > your Apple Development certificate > Organizational Unit."

WORK="${WEZCRYPT_WORKDIR:-$HOME/wezcrypt-telegram-build}"
mkdir -p "$WORK"
cd "$WORK"

if [ ! -d Telegram-iOS/.git ]; then
  git clone --recursive https://github.com/TelegramMessenger/Telegram-iOS.git Telegram-iOS
fi
cd Telegram-iOS
git fetch --tags
git checkout "$UPSTREAM_TAG"
git submodule update --init --recursive

# Apply WezCrypt customization (bundle id, display name, build configuration).
# The customization script ships next to this script in the WezCrypt Telegram repo.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$SCRIPT_DIR/customize.py" "$PWD"

# Codesigning material: copy the fake-codesigning reference and replace with YOUR
# provisioning profiles/certificates (see docs/BUILD_INSTRUCTIONS.md).
if [ ! -d "$WORK/codesigning" ]; then
  echo "WARNING: $WORK/codesigning not found — project generation with codesigning will fail."
  echo "Create it from build-system/fake-codesigning using your own Apple Developer profiles."
fi

# Generate the Xcode project (development configuration, Xcode-managed codesigning).
python3 build-system/Make/Make.py \
  --cacheDir="$HOME/telegram-bazel-cache" \
  generateProject \
  --configurationPath=build-system/wezcrypt-configuration.json \
  --xcodeManagedCodesigning

# Release build -> IPA. Requires distribution/development provisioning in $WORK/codesigning.
python3 build-system/Make/Make.py \
  --cacheDir="$HOME/telegram-bazel-cache" \
  build \
  --configurationPath=build-system/wezcrypt-configuration.json \
  --codesigningInformationPath="$WORK/codesigning" \
  --buildNumber="${WEZCRYPT_BUILD_NUMBER:-100001}" \
  --configuration=release_arm64

echo "Build finished. Locate the IPA under the build output directory printed above,"
echo "rename a copy to WezCryptTelegram.ipa and record its SHA-256:"
echo "  shasum -a 256 WezCryptTelegram.ipa"
