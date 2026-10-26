#!/usr/bin/env bash
# Install the skill into every agent harness found on this machine.
#
# Copies (not symlinks: three different tools, one Windows privilege model). Re-run
# after editing SKILL.md — the repo copy is canonical.
#
#   ./install.sh              # every harness detected on PATH
#   ./install.sh --dir ~/.foo/skills   # one extra location, nothing else
set -euo pipefail

name="context-engineering"
here="$(cd "$(dirname "$0")" && pwd)"
src="$here/SKILL.md"
[ -f "$src" ] || { echo "no SKILL.md next to $0" >&2; exit 1; }

install_to() {
  mkdir -p "$1/$name"
  cp "$src" "$1/$name/SKILL.md"
  echo "  $1/$name/SKILL.md"
}

if [ "${1:-}" = "--dir" ]; then
  [ -n "${2:-}" ] || { echo "usage: $0 --dir <skills-dir>" >&2; exit 2; }
  install_to "$2"
else
  found=0
  # ~/.agents/skills is the Agent Skills standard location: Codex reads it, and so does pi.
  if command -v codex >/dev/null || [ -d "$HOME/.agents" ]; then
    install_to "$HOME/.agents/skills"; found=1
  fi
  if command -v claude >/dev/null; then
    install_to "$HOME/.claude/skills"; found=1
  fi
  # pi's own directory; skipped when the standard one is already in place, because a
  # second copy under the same name is a duplicate skill, not a second install.
  if command -v pi >/dev/null && ! { command -v codex >/dev/null || [ -d "$HOME/.agents" ]; }; then
    install_to "$HOME/.pi/agent/skills"; found=1
  fi
  [ "$found" = 1 ] || { echo "no harness found; use: $0 --dir <skills-dir>" >&2; exit 1; }
fi

echo "installed $name from $src"
