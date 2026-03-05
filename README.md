# med-school-claude-config

Private backup of Claude Code skills and configuration for medical school study pipeline.

## What's here

| Path | Description |
|------|-------------|
| `skills/` | All Claude Code skill definitions (SKILL.md files) |
| `Skills_Reference.txt` | Quick-reference cheat sheet for all skills |
| `med-context.md` | Tagging schema and metadata conventions for all outputs |
| `sync.sh` | One-command backup script |

## Skills

| Skill | Purpose |
|-------|---------|
| `hot-paper-reader` | Find best recent paper on 3 keywords → PDF |
| `specific-paper-reader` | Deep-read a specific paper (PMID/URL) → PDF |
| `medarticle-to-notebooklm` | Research articles / UpToDate → structured .txt for NotebookLM |
| `lecture-to-notebooklm` | Lecture slides (PPTX/PDF/DOCX) → structured .md for NotebookLM |
| `notebooklm-to-anki` | NotebookLM output → Anki deck (.apkg) |
| `clinical-vignette-coach` | Socratic vignette tutor → gap analysis + session log |
| `morning-briefing` | Daily briefing skill |

## Actual skill location

Skills are read by Claude Code from `~/.claude/skills/`. The `skills/` folder here is a synced copy for backup only. To restore after a fresh install, copy `skills/*/SKILL.md` back to `~/.claude/skills/*/SKILL.md`.

## How to back up

```bash
cd ~/Desktop/Medical\ School/Claude
./sync.sh
```

Or just ask Claude Code: "run sync.sh"

## What's excluded

Generated outputs (NotebookLM files, Anki decks, case review logs) are gitignored — they change constantly and don't need version control.
