"""Switch data source paths in model.bim between local and remote."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODEL = ROOT / "Material Tracker Pro.SemanticModel" / "model.bim"
REMOTE_CONFIG = ROOT / "paths.remote.json"
LOCAL_CONFIG = ROOT / "paths.local.json"


def to_bim_path(path: str) -> str:
    return path.replace("\\", "\\\\")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def switch(mode: str) -> int:
    if mode not in ("Local", "Remote"):
        raise ValueError("Mode must be Local or Remote")

    remote = load_json(REMOTE_CONFIG)
    local = load_json(LOCAL_CONFIG)
    content = MODEL.read_text(encoding="utf-8")
    total = 0

    local_by_file = {m["file"]: m["path"] for m in local["mappings"]}

    for remote_mapping in remote["mappings"]:
        fname = remote_mapping["file"]
        remote_path = remote_mapping["path"]
        local_path = local_by_file.get(fname)
        if not local_path:
            raise KeyError(f"No local mapping for {fname}")

        from_path = remote_path if mode == "Local" else local_path
        to_path = local_path if mode == "Local" else remote_path
        from_bim = to_bim_path(from_path)
        to_bim = to_bim_path(to_path)

        count = content.count(from_bim)
        if count:
            content = content.replace(from_bim, to_bim)
            total += count
            print(f"  {fname}: {count} replacement(s)")

    rf = remote.get("salesFolder", {})
    lf = local.get("salesFolder", {})
    if rf.get("path") and lf.get("path"):
        from_folder = rf["path"] if mode == "Local" else lf["path"]
        to_folder = lf["path"] if mode == "Local" else rf["path"]
        from_bim = to_bim_path(from_folder)
        to_bim = to_bim_path(to_folder)
        count = content.count(from_bim)
        if count:
            content = content.replace(from_bim, to_bim)
            total += count
            print(f"  salesFolder: {count} replacement(s)")

    if total:
        MODEL.write_text(content, encoding="utf-8", newline="\n")
        print(f"Switched to {mode} mode — {total} total replacement(s)")
    else:
        print(f"No path changes needed — already in {mode} mode.")

    verify = MODEL.read_text(encoding="utf-8")
    if mode == "Local":
        if "D:\\\\Box\\\\" in verify:
            print("VERIFY FAILED: still contains D:\\Box\\ paths", file=sys.stderr)
            sys.exit(1)
        if "D:\\\\PBI\\\\Data\\\\" not in verify:
            print("VERIFY FAILED: missing D:\\PBI\\Data\\ paths", file=sys.stderr)
            sys.exit(1)
        print("VERIFY OK: model.bim uses local paths (D:\\PBI\\Data\\)")
    else:
        if "D:\\\\PBI\\\\Data\\\\" in verify:
            print("VERIFY FAILED: still contains D:\\PBI\\Data\\ paths", file=sys.stderr)
            sys.exit(1)
        if "D:\\\\Box\\\\" not in verify:
            print("VERIFY FAILED: missing D:\\Box\\ paths", file=sys.stderr)
            sys.exit(1)
        print("VERIFY OK: model.bim uses remote paths (D:\\Box\\)")

    return total


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python switch-paths.py Local|Remote", file=sys.stderr)
        sys.exit(1)
    switch(sys.argv[1])
