#!/usr/bin/env bash
# Shared preparation for parser tests and released-source acceptance.
set -euo pipefail
if ! command -v clang++ >/dev/null 2>&1; then
  if [[ "$(uname -s)" != Linux ]] || ! command -v apt-get >/dev/null 2>&1; then
    echo 'Install Clang with AddressSanitizer and UndefinedBehaviorSanitizer support.' >&2
    exit 1
  fi
  privilege=()
  if [[ "$EUID" != 0 ]]; then privilege=(sudo); fi
  "${privilege[@]}" apt-get update
  "${privilege[@]}" apt-get install -y --no-install-recommends clang
fi
clang++ --version
