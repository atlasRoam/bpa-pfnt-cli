from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_DIRS = {"runs", "workspace", "acceptance", "backups", "logs", "oracles"}
FORBIDDEN_SUFFIXES = {".env", ".key", ".log", ".p12", ".pem", ".pfx", ".sqlite"}
RULES = {
    "user-profile-path": re.compile(rb"(?:[A-Za-z]:\\Users\\|/(?:home|Users)/)[^\x00\r\n]{1,180}", re.I),
    "legacy-install-path": re.compile(rb"[A-Za-z]:\\Program Files\\BPA[^\x00\r\n]{1,180}", re.I),
    "bearer-token": re.compile(rb"Bearer\s+[A-Za-z0-9._-]{16,}", re.I),
    "api-key": re.compile(rb"(?:api[_-]?key|token|password)\s*[:=]\s*[A-Za-z0-9._-]{16,}", re.I),
}


def main() -> None:
    findings: list[str] = []
    for path in ROOT.rglob("*"):
        if path.is_symlink():
            findings.append(f"symlink:{path.relative_to(ROOT).as_posix()}")
            continue
        if not path.is_file() or ".git" in path.parts:
            continue
        relative = path.relative_to(ROOT)
        if any(part.lower() in FORBIDDEN_DIRS for part in relative.parts):
            findings.append(f"forbidden-directory:{relative.as_posix()}")
        if path.suffix.lower() in FORBIDDEN_SUFFIXES:
            findings.append(f"forbidden-suffix:{relative.as_posix()}")
        data = path.read_bytes()
        for name, pattern in RULES.items():
            if pattern.search(data):
                findings.append(f"{name}:{relative.as_posix()}")
    required = (
        ROOT / "bpa_cli.exe",
        ROOT / "runtime" / "pfnt" / "pfnt.exe",
        ROOT / "MANIFEST.json",
        ROOT / "THIRD_PARTY_NOTICES.md",
    )
    for path in required:
        if not path.is_file():
            findings.append(f"missing-required:{path.relative_to(ROOT).as_posix()}")
    if findings:
        print("public-audit: FAIL", file=sys.stderr)
        for finding in sorted(set(findings)):
            print(f"- {finding}", file=sys.stderr)
        raise SystemExit(1)
    print("public-audit: PASS")


if __name__ == "__main__":
    main()
