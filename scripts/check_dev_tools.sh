#!/usr/bin/env bash
# Check that required development tools are installed.
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
BOLD='\033[1m'
RESET='\033[0m'

errors=0

for cmd in uv just python3; do
    if command -v "$cmd" &>/dev/null; then
        version=$("$cmd" --version 2>&1 | head -1)
        printf "${GREEN}✓${RESET} %-10s %s\n" "$cmd" "$version"
    else
        printf "${RED}✗${RESET} %-10s ${RED}not found${RESET}\n" "$cmd"
        errors=$((errors + 1))
    fi
done

echo ""
if [ "$errors" -gt 0 ]; then
    echo -e "${RED}${BOLD}$errors tool(s) missing.${RESET} See docs/guides/getting-started.md for install instructions."
    exit 1
else
    echo -e "${GREEN}${BOLD}All development tools are installed.${RESET}"
fi
