#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
HOOKS_DIR="${REPO_ROOT}/.githooks"
HOOK_PATH="${HOOKS_DIR}/pre-commit"
CHECK_SCRIPT="${REPO_ROOT}/scripts/pre-commit-check.sh"

if [[ ! -d "${REPO_ROOT}/.git" ]]; then
    echo "Error: this script must be run inside a Git repository."
    exit 1
fi

if [[ ! -f "$CHECK_SCRIPT" ]]; then
    echo "Error: pre-commit check script not found:"
    echo "  $CHECK_SCRIPT"
    exit 1
fi

mkdir -p "$HOOKS_DIR"

cat > "$HOOK_PATH" <<'EOF'
#!/usr/bin/env bash

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
exec "${REPO_ROOT}/scripts/pre-commit-check.sh"
EOF

chmod +x "$HOOK_PATH"

git -C "$REPO_ROOT" config core.hooksPath .githooks

echo "Installed pre-commit hook."
echo
echo "Git hooks path:"
git -C "$REPO_ROOT" config --get core.hooksPath
echo
echo "Hook:"
echo "  $HOOK_PATH"
echo
echo "Run it manually with:"
echo "  $HOOK_PATH"
