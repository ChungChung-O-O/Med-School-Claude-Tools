#!/bin/bash
# sync.sh — Back up Claude skills and config to GitHub
# Usage: ./sync.sh
# Or ask Claude: "run sync.sh"

set -e

SKILLS_SRC="$HOME/.claude/skills"
REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILLS_DEST="$REPO_DIR/skills"

echo "Syncing skills from ~/.claude/skills/ ..."

for skill_dir in "$SKILLS_SRC"/*/; do
    skill_name=$(basename "$skill_dir")
    skill_file="$skill_dir/SKILL.md"
    if [ -f "$skill_file" ]; then
        mkdir -p "$SKILLS_DEST/$skill_name"
        cp "$skill_file" "$SKILLS_DEST/$skill_name/SKILL.md"
        echo "  Copied: $skill_name"
    fi
done

echo "Committing and pushing..."

cd "$REPO_DIR"
git add skills/ Skills_Reference.txt med-context.md
git diff --cached --quiet && echo "Nothing changed — already up to date." && exit 0

TIMESTAMP=$(date "+%Y-%m-%d %H:%M")
git commit -m "Backup: $TIMESTAMP"
git push origin main

echo "Done. Backup pushed to GitHub."
