"""Build and verify the explicitly inventoried BLE pattern source distribution."""

import argparse
import gzip
import hashlib
import io
import json
# Fixed Git/interpreter argument vectors, no shell.
import subprocess  # nosec B404
import sys
import tarfile
import tempfile
from pathlib import Path

if __package__:
    from .release_version_adapter import checked_version
else:
    from release_version_adapter import checked_version

PREFIX = "esphome-ble-sensor-patterns"
MAX_FILE = 16 * 1024 * 1024
MAX_TOTAL = 128 * 1024 * 1024


def source_path(root, name):
    """Resolve an explicit relative name without traversing symbolic links."""
    if name.startswith("/") or "\\" in name or "\0" in name or any(p in {"", ".", ".."} for p in name.split("/")):
        raise ValueError("Unsafe source inventory path")
    path = root
    for part in name.split("/"):
        path = path / part
        if path.is_symlink():
            raise ValueError("Source inventory cannot contain symlinks")
    return path


def inventory(root):
    """Require unique, explicit regular-file paths with no symlink components."""
    names = json.loads((root / "source-files.json").read_text())
    if not isinstance(names, list) or not names or any(not isinstance(n, str) for n in names):
        raise ValueError("Source inventory must be a nonempty path array")
    if names != sorted(set(names)):
        raise ValueError("Source inventory must be unique and sorted")
    total = 0
    for name in names:
        path = source_path(root, name)
        if not path.is_file() or path.stat().st_size > MAX_FILE:
            raise ValueError("Source inventory requires bounded regular files")
        total += path.stat().st_size
    if total > MAX_TOTAL:
        raise ValueError("Source inventory exceeds size limit")
    return names


def build(root, output, base, channel):
    """Package reviewed tracked inputs using the validated frozen-plan version."""
    version = checked_version(root, base, channel)
    names = inventory(root)
    # Fixed read-only Git inventory command.
    tracked = set(subprocess.check_output(  # nosec B603, B607
        ["git", "ls-files", "-z"], cwd=root
    ).decode().split("\0"))
    if not set(names) <= tracked:
        raise ValueError("Source inventory includes untracked inputs")
    output.mkdir(parents=True, exist_ok=True)
    if any(output.iterdir()):
        raise ValueError("Source output directory must be empty")
    archive = output / f"{PREFIX}-{version}.tar.gz"
    with (
        archive.open("wb") as stream,
        gzip.GzipFile(filename="", mode="wb", fileobj=stream, mtime=0) as compressed,
        tarfile.open(fileobj=compressed, mode="w") as package,
    ):
        for name in names:
            path = root / name
            raw = path.read_bytes()
            entry = tarfile.TarInfo(f"{PREFIX}/{name}")
            entry.size = len(raw)
            entry.mode = 0o755 if path.stat().st_mode & 0o111 else 0o644
            package.addfile(entry, io.BytesIO(raw))
    (output / "SHA256SUMS").write_text(f"{hashlib.sha256(archive.read_bytes()).hexdigest()}  {archive.name}\n")
    return archive


def extract_verified(root, archive, destination):
    """Compare exact member bytes and modes before any source file is extracted."""
    names = inventory(root)
    expected = {f"{PREFIX}/{name}": root / name for name in names}
    with tarfile.open(archive, "r:gz") as package:
        members = package.getmembers()
        if len(members) != len(expected) or {m.name for m in members} != set(expected):
            raise ValueError("Source archive differs from explicit inventory")
        for member in members:
            path = expected[member.name]
            mode = 0o755 if path.stat().st_mode & 0o111 else 0o644
            if not member.isfile() or member.size != path.stat().st_size or member.mode != mode:
                raise ValueError("Source archive has invalid member type, size or mode")
            if member.uid != 0 or member.gid != 0 or member.mtime != 0:
                raise ValueError("Source archive metadata is not normalized")
            with package.extractfile(member) as stream:
                if stream.read(MAX_FILE + 1) != path.read_bytes():
                    raise ValueError("Source archive bytes differ from declared input")
        # Exact inventory, type, size and bytes were verified above.
        package.extractall(destination, filter="data")  # nosec B202
    return destination / PREFIX


def acceptance(root, archive):
    """Exercise the exact extracted source using preinstalled host test tools."""
    with tempfile.TemporaryDirectory(prefix="ble-patterns-source-") as temporary:
        source = extract_verified(root, archive, Path(temporary))
        # Current fixed interpreter, owned tests, no shell/network/hardware actions.
        subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests",
                        "-p", "test_*.py", "-v"], cwd=source, check=True)  # nosec B603


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    pack = commands.add_parser("build")
    pack.add_argument("base")
    pack.add_argument("channel", choices=["nightly", "beta", "rc", "stable"])
    pack.add_argument("output", type=Path)
    verify = commands.add_parser("verify")
    verify.add_argument("archive", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    if args.command == "build":
        print(build(root, args.output.resolve(), args.base, args.channel))
    else:
        acceptance(root, args.archive.resolve())


if __name__ == "__main__":
    main()
