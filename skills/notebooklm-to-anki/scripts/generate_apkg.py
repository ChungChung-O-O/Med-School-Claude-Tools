#!/usr/bin/env python3
"""
Generate an Anki .apkg deck from a JSON input file.

Usage:
    python3 generate_apkg.py <path_to_input.json>

Input JSON schema:
{
  "deck": "MedSchool",
  "topic_slug": "HeartFailure",
  "output_path": "~/Desktop/Claude Code/Claude_For_School/Anki/Anki_HeartFailure_2024-01-01.apkg",
  "cards": [
    {
      "type": "basic",
      "front": "What is the first-line treatment for HFrEF?",
      "back": "ACE inhibitor (or ARB) + beta-blocker + MRA",
      "extra": "GDMT: ACE/ARB, BB, MRA, SGLT2i all reduce mortality in HFrEF.",
      "tags": ["Course::OST510", "System::Cardiovascular", "Source::Lecture", "Yield::High", "Boards::Cardiology"]
    },
    {
      "type": "cloze",
      "text": "In HFrEF, {{c1::ACE inhibitors}} reduce afterload by blocking angiotensin II production.",
      "extra": "Also reduce preload via aldosterone suppression.",
      "tags": ["Course::OST510", "System::Cardiovascular", "Source::Lecture", "Yield::High", "Boards::Cardiology"]
    }
  ]
}

Fixed model IDs (never change — Anki uses these to identify note types):
  Basic: 1607392319
  Cloze: 1607392320
"""

import json
import os
import sys
import hashlib

try:
    import genanki
except ImportError:
    print("genanki not installed. Run: pip3 install genanki")
    sys.exit(1)

# Fixed model IDs -- Anki uses these to identify note types across imports.
# Changing them would cause Anki to treat cards as belonging to a different model.
BASIC_MODEL = genanki.Model(
    1607392319,
    'Claude Medical Basic',
    fields=[
        {'name': 'Front'},
        {'name': 'Back'},
        {'name': 'Extra'},
    ],
    templates=[{
        'name': 'Card 1',
        'qfmt': '{{Front}}',
        'afmt': '{{FrontSide}}<hr id=answer>{{Back}}<br><br><i style="color:#888">{{Extra}}</i>',
    }],
    css='.card { font-family: helvetica; font-size: 16px; text-align: left; color: black; background-color: white; } hr { border-top: 1px solid #ccc; }'
)

CLOZE_MODEL = genanki.Model(
    1607392320,
    'Claude Medical Cloze',
    fields=[
        {'name': 'Text'},
        {'name': 'Extra'},
    ],
    templates=[{
        'name': 'Cloze',
        'qfmt': '{{cloze:Text}}',
        'afmt': '{{cloze:Text}}<br><br><i style="color:#888">{{Extra}}</i>',
    }],
    model_type=genanki.Model.CLOZE,
    css='.card { font-family: helvetica; font-size: 16px; text-align: left; color: black; background-color: white; } .cloze { font-weight: bold; color: #0066cc; }'
)


def generate(data: dict):
    # All med school cards go into the single MedSchool home deck.
    # Accepts an optional "deck" field in the JSON; defaults to "MedSchool".
    # Never derive a Claude::<slug>_<date> name — that pattern is retired.
    deck_name = data.get("deck", "MedSchool")

    deck_id = int(hashlib.md5(deck_name.encode()).hexdigest(), 16) % (2**31)
    deck = genanki.Deck(deck_id, deck_name)

    basic_count = 0
    cloze_count = 0

    for card in data["cards"]:
        tags = card.get("tags", [])
        extra = card.get("extra", "")

        if card["type"] == "basic":
            note = genanki.Note(
                model=BASIC_MODEL,
                fields=[card["front"], card["back"], extra],
                tags=tags
            )
            basic_count += 1
        elif card["type"] == "cloze":
            if "{{c1::" not in card["text"]:
                print(f"Warning: cloze card missing {{{{c1::}}}} syntax, skipping: {card['text'][:60]}...")
                continue
            note = genanki.Note(
                model=CLOZE_MODEL,
                fields=[card["text"], extra],
                tags=tags
            )
            cloze_count += 1
        else:
            print(f"Warning: unknown card type '{card['type']}', skipping.")
            continue

        deck.add_note(note)

    outpath = os.path.expanduser(data["output_path"])
    os.makedirs(os.path.dirname(outpath), exist_ok=True)
    genanki.Package(deck).write_to_file(outpath)

    print(f"Deck: {deck_name}")
    print(f"Cards: {basic_count} basic + {cloze_count} cloze = {basic_count + cloze_count} total")
    print(f"Saved: {outpath}")
    return outpath


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 generate_apkg.py <input.json>")
        sys.exit(1)
    with open(sys.argv[1]) as f:
        data = json.load(f)
    generate(data)
