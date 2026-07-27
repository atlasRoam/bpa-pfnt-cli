from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "MANIFEST.json"
ASSET_ROOTS = (ROOT / "bpa_cli.exe", ROOT / "runtime", ROOT / "samples")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _actual_assets() -> dict[str, Path]:
    result: dict[str, Path] = {}
    for root in ASSET_ROOTS:
        files = (root,) if root.is_file() else tuple(root.rglob("*"))
        for path in files:
            if path.is_file():
                result[path.relative_to(ROOT).as_posix()] = path
    return result


def main() -> None:
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    expected = {item["path"]: item for item in payload["assets"]}
    actual = _actual_assets()
    if set(expected) != set(actual):
        missing = sorted(set(expected) - set(actual))
        unexpected = sorted(set(actual) - set(expected))
        raise SystemExit(f"asset-set mismatch: missing={missing} unexpected={unexpected}")
    for name, item in expected.items():
        relative = PurePosixPath(name)
        if relative.is_absolute() or ".." in relative.parts:
            raise SystemExit(f"unsafe manifest path: {name}")
        path = actual[name]
        if path.stat().st_size != item["size"]:
            raise SystemExit(f"size mismatch: {name}")
        if _sha256(path) != item["sha256"]:
            raise SystemExit(f"sha256 mismatch: {name}")
    print(f"distribution-verification: PASS ({len(actual)} assets)")


if __name__ == "__main__":
    main()
