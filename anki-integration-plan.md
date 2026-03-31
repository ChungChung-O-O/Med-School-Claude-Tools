# Anki Integration Plan
*Last updated: 2026-03-31 — algorithm designed, build pending deck arrival*

---

## Overview

When you receive the MSUCOM upperclassman Anki deck, this document defines how to integrate it into your study workflow:

1. Import and organize the deck
2. Discover the tag structure
3. Unsuspend cards block-by-block as you progress through OMS1
4. Track coverage via the SQLite MCP

---

## Step 0: Import the Deck

1. Import the `.apkg` file into Anki.
2. **Do not start reviewing yet** — all imported cards begin suspended. This is intentional.
3. The deck will appear under its original name (e.g. `MSUCOM` or `OMS1 Deck`).

---

## Step 1: Discover the Tag Structure

Before writing any automation, inspect the actual tag naming convention used:

### Option A — Anki Browser
Open Anki → Browse → look at the Tags column on the left sidebar.

### Option B — SQLite query (via Claude Code with SQLite MCP)
Run this to see all unique top-level tags:

```sql
SELECT DISTINCT value
FROM notes, json_each('["' || replace(replace(tags, ' ', '","'), '::','::') || '"]')
WHERE tags != ''
ORDER BY value
LIMIT 100;
```

Or simpler — just get a raw tag sample:
```sql
SELECT DISTINCT substr(tags, 1, 80) FROM notes WHERE tags != '' LIMIT 50;
```

### What you're looking for
The tag structure is likely one of these patterns:
- `MSUCOM::OMS1::Foundations::LectureName`
- `OMS1::MSK::Week1::LectureName`
- `Foundations::LectureName`
- Something custom per the creator

**Fill in the actual pattern here once the deck arrives:**
```
Actual tag pattern: ___________________
Example tag:        ___________________
Block-level prefix: ___________________
Lecture-level key:  ___________________
```

---

## Step 2: Deck Hierarchy Plan

Once tag structure is confirmed, rename/reorganize into this structure if not already:

```
MSUCOM
  └── OMS1
        ├── Foundations
        ├── Anatomy
        ├── MSK
        ├── Hem-Onc-ID
        ├── Neuro
        ├── Psych
        ├── GU
        ├── Endo
        ├── OMM
        └── Patient-Care
```

You can move cards between decks in Anki Browser via Edit → Change Deck.
Or do it via tag-based SQL if needed (not recommended — use the Anki UI for deck assignment).

---

## Step 3: Unsuspend Algorithm

### Philosophy
- Cards are suspended on import — they won't appear in reviews.
- Unsuspend **by block**, 3–5 days before that block starts, so SRS has time to space initial reviews.
- Within a block, optionally unsuspend **lecture by lecture** as you cover the material in class.

### Block-Level Unsuspend

When a new block begins (e.g. MSK block starts Aug 25):
- 3–5 days before: unsuspend all cards tagged with the MSK block prefix
- This seeds your Anki queue before lectures start

**Manual (Anki Browser)**:
1. Anki Browser → search: `tag:MSUCOM::OMS1::MSK is:suspended`
2. Ctrl+A to select all → Cards → Toggle Suspend

**Automated (future bot command `/unsuspend <block>`)**:
Use the AnkiConnect MCP (`mcp__anki__*` tools) if Anki is running:
```
mcp__anki__findNotes with query: "tag:MSUCOM::OMS1::MSK is:suspended"
→ get note IDs
→ mcp__anki__get_cards to get card IDs from note IDs
→ AnkiConnect "suspend": false
```

### Lecture-Level Unsuspend (optional, more granular)

After each lecture:
1. Find cards with that lecture's tag
2. Unsuspend only those cards

This keeps your daily review count manageable — you only review what you've seen in class.

**Lookup pattern:**
```
tag:MSUCOM::OMS1::MSK::UpperLimb is:suspended
```

---

## Step 4: Coverage Tracking Queries

These SQLite queries (run via the SQLite MCP) show your progress per block.

### How many cards exist per block?
```sql
-- After confirming tag pattern, replace 'MSUCOM::OMS1::' with actual prefix
SELECT 
    substr(n.tags, instr(n.tags, 'OMS1::') + 6, 
           case 
             when instr(substr(n.tags, instr(n.tags, 'OMS1::') + 6), ' ') > 0
             then instr(substr(n.tags, instr(n.tags, 'OMS1::') + 6), ' ') - 1
             else length(n.tags)
           end
    ) as block_tag,
    COUNT(DISTINCT c.id) as total_cards,
    SUM(CASE WHEN c.queue = -1 THEN 1 ELSE 0 END) as suspended,
    SUM(CASE WHEN c.queue != -1 THEN 1 ELSE 0 END) as active
FROM cards c
JOIN notes n ON c.nid = n.id
WHERE n.tags LIKE '%OMS1::%'
GROUP BY block_tag
ORDER BY block_tag;
```

### What's my retention rate in an active deck?
```sql
SELECT 
    COUNT(*) as reviews,
    SUM(CASE WHEN ease = 1 THEN 1 ELSE 0 END) as again,
    ROUND(100.0 * SUM(CASE WHEN ease > 1 THEN 1 ELSE 0 END) / COUNT(*), 1) as retention_pct
FROM revlog
WHERE id > (strftime('%s', 'now') - 7 * 86400) * 1000  -- last 7 days
```

### Weekly due forecast?
```sql
SELECT 
    date(crt + due * 86400, 'unixepoch', 'localtime') as due_date,
    COUNT(*) as cards_due
FROM cards
JOIN col ON 1=1
WHERE queue = 2
    AND due <= (SELECT (strftime('%s', 'now') - crt) / 86400 + 14 FROM col)
GROUP BY due_date
ORDER BY due_date;
```

---

## Step 5: Bot Command Design (to build when deck arrives)

Once the deck is live, add these to the secretary bot:

### `/coverage` — Block coverage summary
Shows active vs. suspended per block. Quick sanity check each week.

**Bot message:** "MSK: 320 active / 85 suspended | Foundations: 410 active / 0 suspended"

### `/unsuspend <block> [lecture]` — Unsuspend cards
Examples:
- `/unsuspend MSK` → unsuspend all MSK cards
- `/unsuspend MSK UpperLimb` → unsuspend just that lecture

**Implementation:** use `mcp__anki__findNotes` + AnkiConnect suspend API (requires Anki running locally).

### Update to `/deck` command
Currently sets a focus deck for due-count display. Could be extended to also pull coverage stats when a block-level deck is set.

---

## Pending (update when deck arrives)

- [ ] Confirm actual tag pattern
- [ ] Fill in tag mapping above
- [ ] Confirm deck name after import
- [ ] Verify AnkiConnect MCP works with the deck
- [ ] Build `/coverage` bot tool
- [ ] Build `/unsuspend` bot tool
- [ ] Add weekly Anki stats to morning briefing (retention %, weakest tag)
