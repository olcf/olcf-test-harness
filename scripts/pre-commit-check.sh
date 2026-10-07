#!/usr/bin/env bash

set -o pipefail

# Use colors only when output is sent to a terminal.
if [[ -t 1 ]]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    BOLD='\033[1m'
    RESET='\033[0m'
else
    RED=''
    GREEN=''
    YELLOW=''
    BLUE=''
    BOLD=''
    RESET=''
fi

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"

cd "$REPO_ROOT"

declare -a FAILED_CHECKS=()
TOTAL_CHECKS=4
CURRENT_CHECK=0

print_header() {
    printf "\n%b━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━%b\n" \
        "$BLUE" "$RESET"
    printf "%b  Pre-commit checks%b\n" "$BOLD" "$RESET"
    printf "%b━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━%b\n\n" \
        "$BLUE" "$RESET"
}

run_check() {
    local name="$1"
    shift

    CURRENT_CHECK=$((CURRENT_CHECK + 1))

    printf "%b[%d/%d]%b %b%s%b\n" \
        "$BLUE" "$CURRENT_CHECK" "$TOTAL_CHECKS" "$RESET" \
        "$BOLD" "$name" "$RESET"

    printf "      \$"
    printf " %q" "$@"
    printf "\n\n"

    if "$@"; then
        printf "\n%b      ✔ %s passed%b\n\n" \
            "$GREEN" "$name" "$RESET"
    else
        local status=$?

        printf "\n%b      ✘ %s failed (exit code %d)%b\n\n" \
            "$RED" "$name" "$status" "$RESET"

        FAILED_CHECKS+=("$name")
    fi
}

require_command() {
    local command_name="$1"

    if ! command -v "$command_name" >/dev/null 2>&1; then
        printf "%bMissing required command: %s%b\n" \
            "$RED" "$command_name" "$RESET"
        printf "Install it and try again.\n"
        exit 127
    fi
}

print_header

printf "%bRepository:%b %s\n" "$BOLD" "$RESET" "$REPO_ROOT"
printf "%bPython:%b    %s\n\n" "$BOLD" "$RESET" \
    "$(command -v python 2>/dev/null || printf 'not found')"

for command_name in ruff mypy pytest; do
    require_command "$command_name"
done

run_check "Ruff linting" \
    ruff check
    # TODO can updated this to "python -m ruff" when we move past Python 3.6

run_check "Ruff formatting" \
    ruff format --check
    # TODO can updated this to "python -m ruff" when we move past Python 3.6

run_check "MyPy type checking" \
    python -m mypy

run_check "Pytest test suite" \
    python -m pytest -v

printf "%b━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━%b\n" \
    "$BLUE" "$RESET"

if (( ${#FAILED_CHECKS[@]} == 0 )); then
    printf "%b%b✔ All pre-commit checks passed!%b\n" \
        "$GREEN" "$BOLD" "$RESET"
    printf "%bThe commit may proceed.%b\n\n" "$GREEN" "$RESET"
    exit 0
fi

printf "%b%b✘ Pre-commit checks failed%b\n\n" \
    "$RED" "$BOLD" "$RESET"

printf "%bFailed checks:%b\n" "$BOLD" "$RESET"

for failed_check in "${FAILED_CHECKS[@]}"; do
    printf "  %b•%b %s\n" "$RED" "$RESET" "$failed_check"
done

printf "\n%bFix the failures and try committing again.%b\n\n" \
    "$YELLOW" "$RESET"

exit 1
