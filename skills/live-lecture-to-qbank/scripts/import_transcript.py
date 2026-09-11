#!/usr/bin/env python3
"""Versioned, local-only transcript ingestion for live-lecture review."""
import argparse, hashlib, json, os, re, shutil, sys, tempfile
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

TIME = r"(?:\d{2}:)?[0-5]\d:[0-5]\d(?:[.,]\d{1,3})?"
TIMING = re.compile(rf"^\s*({TIME})\s*-->\s*({TIME})(?:\s+.*)?$")
TEXT_TIME = re.compile(rf"^\s*\[({TIME})\]\s*(.+)$")

def die(message):
    raise ValueError(message)

def stamp():
    return datetime.now(ZoneInfo("America/Detroit")).isoformat()

def safe(value):
    result = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip()).strip(".-")
    if not result:
        die("course, unit, and source identity need filesystem-safe content")
    return result[:100]

def storage_key(identity):
    return f"{safe(identity)}-{hashlib.sha256(identity.encode()).hexdigest()[:10]}"

def normalize_text(text):
    return "\n".join(line.rstrip() for line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n")).strip()

def seconds(value):
    units = value.replace(",", ".").split(":")
    return float(units[-1]) + 60 * int(units[-2]) + (3600 * int(units[-3]) if len(units) == 3 else 0)

def caption_transcript(text, extension):
    blocks = [block.splitlines() for block in re.split(r"\n\s*\n", normalize_text(text)) if block.strip()]
    if extension == ".vtt" and blocks and blocks[0][0].strip().upper().startswith("WEBVTT"):
        blocks[0] = blocks[0][1:]
        if not blocks[0]: blocks.pop(0)
    cues, last_start = [], -1
    for block in blocks:
        cleaned = [line.strip() for line in block if line.strip()]
        if not cleaned:
            continue
        if extension == ".vtt" and cleaned[0].upper().startswith(("NOTE", "STYLE", "REGION")):
            continue
        timing_rows = [i for i, line in enumerate(cleaned) if "-->" in line]
        if not timing_rows:
            if extension == ".vtt" and not cues:  # VTT header metadata
                continue
            die("caption block has no valid timestamp")
        if len(timing_rows) != 1:
            die("caption block has multiple timestamp rows")
        row = timing_rows[0]; match = TIMING.match(cleaned[row])
        if not match:
            die("malformed caption timestamp: " + cleaned[row])
        start, end = seconds(match.group(1)), seconds(match.group(2))
        if end < start or start < last_start:
            die("caption timestamps must have nondecreasing starts and nonnegative durations")
        body = " ".join(re.sub(r"\s+", " ", line) for line in cleaned[row + 1:])
        if not body:
            die("caption cue has no text")
        cues.append((match.group(1).replace(",", "."), body)); last_start = start
    if not cues:
        die("caption file has no non-empty valid timestamped cues")
    return "\n".join(f"[{at}] {body}" for at, body in cues), "timestamp", len(cues)

def plain_transcript(text):
    lines = normalize_text(text).splitlines()
    timestamped = [(match.group(1).replace(",", "."), re.sub(r"\s+", " ", match.group(2))) for line in lines if (match := TEXT_TIME.match(line))]
    content_lines = [line for line in lines if line.strip() and not line.lstrip().startswith("#")]
    if timestamped:
        if len(timestamped) != len(content_lines):
            die("timestamped text contains a non-timestamped transcript line")
        starts = [seconds(at) for at, _ in timestamped]
        if starts != sorted(starts): die("timestamped text has decreasing timestamps")
        return "\n".join(f"[{at}] {body}" for at, body in timestamped), "timestamp", len(timestamped)
    paragraphs = [re.sub(r"\s+", " ", p.strip()) for p in re.split(r"\n\s*\n", normalize_text(text)) if p.strip()]
    if not paragraphs:
        die("plain-text transcript is empty")
    return "\n\n".join(f"[P{i:03d}] {p}" for i, p in enumerate(paragraphs, 1)), "paragraph", len(paragraphs)

def parse(path):
    if path.suffix.lower() not in {".txt", ".vtt", ".srt"}:
        die("input must be a .txt, .vtt, or .srt transcript export")
    try:
        raw = path.read_bytes()
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as error:
        die("transcript must be UTF-8: " + str(error))
    if not raw or not normalize_text(text):
        die("transcript is empty")
    if path.suffix.lower() in {".vtt", ".srt"}:
        normalized, locator_type, locator_count = caption_transcript(text, path.suffix.lower())
    else:
        normalized, locator_type, locator_count = plain_transcript(text)
    return raw, normalized + "\n", locator_type, locator_count

def load_index(path):
    if not path.exists():
        return {"schema_version": 1, "created_at": stamp(), "entries": {}}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("schema_version") != 1 or not isinstance(data.get("entries"), dict) or not all(isinstance(v, dict) and isinstance(v.get("content_versions"), list) and v["content_versions"] for v in data["entries"].values()):
            die("existing index is not valid")
        return data
    except (OSError, json.JSONDecodeError) as error:
        die("cannot read existing index: " + str(error))

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--course", required=True); parser.add_argument("--unit", required=True)
    parser.add_argument("--lecture-title", required=True); parser.add_argument("--source-identity", required=True)
    parser.add_argument("--recording-date", required=True); parser.add_argument("--source-kind", required=True, choices=("live", "prerecorded"))
    parser.add_argument("--source-url"); parser.add_argument("--output-root", type=Path, default=Path("~/Desktop/Agent/Claude_For_School/Transcripts").expanduser())
    args = parser.parse_args()
    try:
        datetime.strptime(args.recording_date, "%Y-%m-%d")
        if not args.input.is_file(): die("input transcript does not exist: " + str(args.input))
        raw, normalized, locator_type, locator_count = parse(args.input)
        raw_hash, normalized_hash = hashlib.sha256(raw).hexdigest(), hashlib.sha256(normalized.encode()).hexdigest()
        unit_root = args.output_root / safe(args.course) / safe(args.unit)
        index_path = unit_root / "index.json"; index = load_index(index_path)
        identity = args.source_identity.strip()
        if not identity: die("source identity is required")
        entry = index["entries"].get(identity)
        if entry and any(entry[field] != getattr(args, field.replace("-", "_")) for field in ("recording_date", "source_kind")):
            die("source identity conflicts with existing recording date or live/prerecorded status")
        if entry and entry["content_versions"][-1]["raw_sha256"] == raw_hash:
            print(json.dumps({"status": "unchanged", "source_identity": identity, "version_count": len(entry["content_versions"])}, indent=2)); return
        version_dir = unit_root / "lectures" / storage_key(identity) / "versions" / f"{len(entry['content_versions']) + 1 if entry else 1:03d}-{raw_hash[:12]}"
        version_dir.mkdir(parents=True, exist_ok=True)
        raw_target = version_dir / ("raw" + args.input.suffix.lower())
        normalized_target = version_dir / "normalized.txt"
        shutil.copyfile(args.input, raw_target); normalized_target.write_text(normalized, encoding="utf-8")
        version = {"raw_sha256": raw_hash, "normalized_sha256": normalized_hash, "imported_at": stamp(), "raw_path": str(raw_target.relative_to(unit_root)), "normalized_path": str(normalized_target.relative_to(unit_root)), "format": args.input.suffix.lower()[1:], "locator_type": locator_type, "locator_count": locator_count, "lecture_title": args.lecture_title, "recording_date": args.recording_date, "source_kind": args.source_kind, "source_url": args.source_url, "input_name": args.input.name}
        if not entry:
            entry = {"lecture_title": args.lecture_title, "recording_date": args.recording_date, "source_kind": args.source_kind, "source_url": args.source_url, "content_versions": []}; index["entries"][identity] = entry
        else:
            entry.update({"lecture_title": args.lecture_title, "source_url": args.source_url, "revised_at": stamp()})
        prior_normalized = entry["content_versions"][-1]["normalized_sha256"] if entry["content_versions"] else None
        entry["content_versions"].append(version); index["updated_at"] = stamp()
        index_path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=index_path.parent, delete=False) as temp:
            json.dump(index, temp, indent=2); temp.write("\n"); temp_name = temp.name
        os.replace(temp_name, index_path)
        status = "imported" if len(entry["content_versions"]) == 1 else "revised"
        downstream = "generate_or_review" if normalized_hash != prior_normalized else "skip_unchanged_normalized"
        print(json.dumps({"status": status, "downstream": downstream, "source_identity": identity, "version_count": len(entry["content_versions"]), "normalized_path": str(normalized_target)}, indent=2))
    except ValueError as error:
        print("error: " + str(error), file=sys.stderr); sys.exit(2)

if __name__ == "__main__": main()
