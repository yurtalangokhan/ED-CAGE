"""Prepare repository-native Booking Microservices artifacts for ED-CAGE.

ED-CAGE's current CMP checks discover standard Compose filenames only at the
evaluated repository root. Booking Microservices keeps its Compose artifact at
deployments/docker-compose/docker-compose.yaml. This script copies that exact
file to docker-compose.yaml at the case-study root without changing its content.

The root-level copy is a scan-discovery alias only. Start the application using
the original nested Compose path or the repository's Aspire AppHost.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import shutil
import sys


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--ed-cage-root",
        type=Path,
        default=None,
        help="ED-CAGE repository root. Defaults to the parent of scripts/.",
    )
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Remove the generated root-level Compose discovery alias.",
    )
    args = parser.parse_args()

    script_path = Path(__file__).resolve()
    ed_cage_root = (
        args.ed_cage_root.resolve()
        if args.ed_cage_root
        else script_path.parent.parent.resolve()
    )

    case_root = ed_cage_root / "case-studies" / "booking-microservices"
    source = case_root / "deployments" / "docker-compose" / "docker-compose.yaml"
    target = case_root / "docker-compose.yaml"
    kubernetes_main = (
        case_root / "deployments" / "kubernetes" / "booking-microservices.yml"
    )
    kubernetes_cert = (
        case_root / "deployments" / "kubernetes" / "booking-cert-manager.yml"
    )

    if args.cleanup:
        if target.exists():
            target.unlink()
            print(f"Removed: {target}")
        else:
            print(f"Nothing to remove: {target}")
        return 0

    required = [source, kubernetes_main, kubernetes_cert]
    missing = [path for path in required if not path.exists()]
    if missing:
        for path in missing:
            print(f"Missing required artifact: {path}", file=sys.stderr)
        return 2

    if target.exists() and sha256(target) != sha256(source):
        print(
            f"Refusing to overwrite a different file: {target}\n"
            "Remove it manually or run with a clean case-study checkout.",
            file=sys.stderr,
        )
        return 3

    shutil.copy2(source, target)

    source_hash = sha256(source)
    target_hash = sha256(target)
    if source_hash != target_hash:
        print("Copied Compose artifact failed hash verification.", file=sys.stderr)
        return 4

    print(f"Prepared Compose discovery alias: {target}")
    print(f"SHA-256: {target_hash}")
    print(f"Kubernetes artifact: {kubernetes_main}")
    print(f"TLS issuer artifact: {kubernetes_cert}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
