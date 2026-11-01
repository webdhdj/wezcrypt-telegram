#!/bin/bash
# Verifies that the WezCrypt patch set does NOT touch forbidden areas:
# sponsored-messages pipeline, MTProto/crypto, certificate validation, networking.
# Usage: verify-no-forbidden-changes.sh <patch-file>
set -euo pipefail
PATCH="${1:?usage: verify-no-forbidden-changes.sh <patch-file>}"
FORBIDDEN='AdMessages|ChatHistoryListNode|ChatController|MtProto|MTProto|Crypto|Security\.swift|Network\.swift|certificate|Certificate|SSLPin|pinning'
if grep -E '^(\+\+\+|---) ' "$PATCH" | grep -E "$FORBIDDEN"; then
  echo "FAIL: patch touches a forbidden file" >&2
  exit 1
fi
if grep -E '^\+' "$PATCH" | grep -Ei 'api\.telegram|analytics|tracker|telemetry|http://[a-z0-9.-]+/' ; then
  echo "FAIL: patch adds an external endpoint / tracker" >&2
  exit 1
fi
echo "OK: patch touches only allowed files:"
grep -E '^\+\+\+ ' "$PATCH" | sed 's/^+++ //'
