#!/usr/bin/env python3
"""Prepare or verify binary-only Morsetastic releases. Requires Python 3 only."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import stat
import struct
import tempfile
import zipfile


ROOT = Path(__file__).resolve().parent.parent
FIELDS = {"version", "source_commit", "build_date", "production", "platform",
          "archive", "sha256", "files"}
BEGIN = "<!-- BEGIN RELEASE INDEX -->"
END = "<!-- END RELEASE INDEX -->"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def tag_for(version):
    if not re.fullmatch(r"V[0-9]+\.[0-9]+(?:\.[0-9]+)?", version):
        raise ValueError("Invalid version")
    return "v" + version[1:]


def validate_package(folder, platform, info):
    if set(info) != FIELDS or info["platform"] != platform:
        raise ValueError("Invalid package metadata")
    tag_for(info["version"])
    if (info["production"] is not True
            or not re.fullmatch(r"[0-9a-f]{40}", info["source_commit"])
            or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", info["build_date"])):
        raise ValueError("A production build and exact source commit are required")
    binary = "morsetastic" if platform == "linux" else "morsetastic.exe"
    required = {binary, "default_words.txt", "callsigns.txt"}
    expected = set(info["files"])
    languages = {name for name in expected if name.startswith("languages/")}
    extras = expected - required - languages
    legacy_extras = any(name.startswith("extras/") for name in extras)
    extra_pattern = (r"extras/[A-Za-z0-9][A-Za-z0-9_.-]*\.(txt|md)" if legacy_extras
                     else r"[A-Za-z0-9][A-Za-z0-9_.-]*\.txt")
    archive_name = f"Morsetastic-{info['version']}-{platform.title()}-x86_64.zip"
    if (info["archive"] != archive_name or not required <= expected
            or len({name.lower() for name in expected}) != len(expected)
            or any(not re.fullmatch(extra_pattern, name) for name in extras)
            or any(not re.fullmatch(r"languages/[a-z0-9-]{2,12}\.json", name)
                   or name in {"languages/en.json", "languages/template.json"}
                   for name in languages)
            or (legacy_extras and not {"extras/default_words.txt", "extras/callsigns.txt"} <= extras)):
        raise ValueError("Unexpected package name or files")
    archive = folder / archive_name
    if digest(archive.read_bytes()) != info["sha256"]:
        raise ValueError("ZIP checksum mismatch")
    with zipfile.ZipFile(archive) as z:
        if len(z.infolist()) != len(expected) or set(z.namelist()) != expected:
            raise ValueError("ZIP members must exactly match the package manifest")
        if any(item.file_size > 16 * 1024 * 1024 for item in z.infolist()):
            raise ValueError("Unexpectedly large package member")
        if any(stat.S_IFMT(item.external_attr >> 16) not in (0, stat.S_IFREG)
               for item in z.infolist()):
            raise ValueError("Package members must be regular files")
        files = {name: z.read(name) for name in expected}
        if {name: digest(data) for name, data in files.items()} != info["files"]:
            raise ValueError("Package member checksum mismatch")
        for name in languages:
            data = files[name]
            if len(data) > 128 * 1024:
                raise ValueError("Language catalog is too large")
            try:
                catalog = json.loads(data.decode("utf-8"))
            except (ValueError, UnicodeError) as error:
                raise ValueError("Invalid language catalog") from error
            if (not isinstance(catalog, dict)
                    or set(catalog) != {"format", "code", "name", "messages"}
                    or type(catalog["format"]) is not int or catalog["format"] != 1
                    or catalog["code"] != Path(name).stem
                    or not isinstance(catalog["name"], str) or not catalog["name"].strip()
                    or not isinstance(catalog["messages"], dict) or not catalog["messages"]
                    or any(not isinstance(value, str) or not value.strip()
                           for value in catalog["messages"].values())):
                raise ValueError("Invalid language catalog")
        if legacy_extras and any(files["extras/" + name] != files[name]
                                 for name in ("default_words.txt", "callsigns.txt")):
            raise ValueError("Extras copies of the original practice files do not match")
        if platform == "linux" and not (z.getinfo(binary).external_attr >> 16) & 0o111:
            raise ValueError("Linux executable permissions are missing")
    data = files[binary]
    if platform == "linux":
        if (len(data) < 20 or data[:6] != b"\x7fELF\x02\x01"
                or struct.unpack_from("<H", data, 18)[0] != 62):
            raise ValueError("Expected a Linux x86-64 executable")
    else:
        if len(data) < 64 or data[:2] != b"MZ":
            raise ValueError("Expected a Windows executable")
        offset = struct.unpack_from("<I", data, 60)[0]
        if (offset + 26 > len(data) or data[offset:offset + 4] != b"PE\0\0"
                or struct.unpack_from("<H", data, offset + 4)[0] != 0x8664
                or struct.unpack_from("<H", data, offset + 24)[0] != 0x20b):
            raise ValueError("Expected a Windows x86-64 executable")
    stamp = f"Version {info['version']} build {info['build_date']}-".encode("ascii")
    match = re.search(re.escape(stamp) + rb"([0-9a-f]{7,40})", data)
    if not match or not info["source_commit"].startswith(match[1].decode("ascii")):
        raise ValueError("Executable build stamp does not match package provenance")
    return archive


def verify(root, tag):
    tag_for("V" + tag[1:])
    if not tag.startswith("v"):
        raise ValueError("Invalid tag")
    folder = root / "releases" / tag
    if {p.name for p in folder.iterdir()} != {
            "linux", "windows", "RELEASE_NOTES.md", "SHA256SUMS.txt", "release.json"}:
        raise ValueError("Unexpected files in the release directory")
    manifest = json.loads((folder / "release.json").read_text())
    if set(manifest) != {"tag", "packages"} or manifest["tag"] != tag:
        raise ValueError("Invalid release manifest")
    packages = manifest["packages"]
    if set(packages) != {"linux", "windows"}:
        raise ValueError("Both platforms are required")
    sums = []
    for platform, info in sorted(packages.items()):
        if tag_for(info["version"]) != tag:
            raise ValueError("Release directory does not match package version")
        if {p.name for p in (folder / platform).iterdir()} != {info["archive"]}:
            raise ValueError("Unexpected files in a platform directory")
        archive = validate_package(folder / platform, platform, info)
        sums.append(f"{info['sha256']}  {platform}/{archive.name}\n")
    practice_files = {
        platform: {name: sha for name, sha in info["files"].items()
                   if name not in ("morsetastic", "morsetastic.exe")}
        for platform, info in packages.items()
    }
    if (packages["linux"]["source_commit"] != packages["windows"]["source_commit"]
            or practice_files["linux"] != practice_files["windows"]):
        raise ValueError("Platforms have different source commits or practice files")
    if (folder / "SHA256SUMS.txt").read_text() != "".join(sums):
        raise ValueError("Release checksum list does not match the manifest")
    if not (folder / "RELEASE_NOTES.md").read_text().strip():
        raise ValueError("Release notes are empty")
    return manifest


def update_index(root, tag):
    readme = (root / "README.md").read_text()
    if readme.count(BEGIN) != 1 or readme.count(END) != 1:
        raise ValueError("README release index markers are missing or duplicated")
    folders = [p for p in (root / "releases").iterdir()
               if p.is_dir() and re.fullmatch(r"v[0-9]+\.[0-9]+(?:\.[0-9]+)?", p.name)]
    folders.sort(key=lambda p: tuple(int(n) for n in p.name[1:].split(".")), reverse=True)
    lines = [BEGIN, f"Latest: **V{tag[1:]}**", "", "| Version | Linux x86-64 | Windows x86-64 | Notes |",
             "| --- | --- | --- | --- |"]
    for folder in folders:
        version = "V" + folder.name[1:]
        base = "releases/" + folder.name
        lines.append(f"| {version} | [ZIP]({base}/linux/Morsetastic-{version}-Linux-x86_64.zip) "
                     f"| [ZIP]({base}/windows/Morsetastic-{version}-Windows-x86_64.zip) "
                     f"| [Release notes]({base}/RELEASE_NOTES.md) |")
    lines.append(END)
    before, rest = readme.split(BEGIN, 1)
    _, after = rest.split(END, 1)
    (root / "README.md").write_text(before + "\n".join(lines) + after)


def prepare(root, linux, windows, notes):
    packages = {platform: json.loads((folder / "BUILD_INFO.json").read_text())
                for platform, folder in (("linux", linux), ("windows", windows))}
    tag = tag_for(packages["linux"]["version"])
    target = root / "releases" / tag
    if target.exists():
        raise ValueError("Release already exists; use a new version")
    if not notes.read_text().strip():
        raise ValueError("Release notes are empty")
    readme = (root / "README.md").read_text()
    if readme.count(BEGIN) != 1 or readme.count(END) != 1:
        raise ValueError("README release index markers are missing or duplicated")
    (root / "releases").mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".prepare-", dir=root / "releases") as temp:
        staging = Path(temp)
        folder = staging / "releases" / tag
        folder.mkdir(parents=True)
        sums = []
        for platform, source in (("linux", linux), ("windows", windows)):
            info = packages[platform]
            archive = validate_package(source, platform, info)
            (folder / platform).mkdir()
            shutil.copy2(archive, folder / platform / archive.name)
            sums.append(f"{info['sha256']}  {platform}/{archive.name}\n")
        (folder / "SHA256SUMS.txt").write_text("".join(sums))
        (folder / "release.json").write_text(json.dumps({"tag": tag, "packages": packages}, indent=2) + "\n")
        shutil.copy2(notes, folder / "RELEASE_NOTES.md")
        verify(staging, tag)
        folder.rename(target)
    update_index(root, tag)
    return tag


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    commands = parser.add_subparsers(dest="command", required=True)
    check = commands.add_parser("verify")
    check.add_argument("tag", nargs="?")
    check.add_argument("--all", action="store_true")
    assemble = commands.add_parser("prepare")
    for name in ("linux", "windows", "notes"):
        assemble.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == "prepare":
            tag = prepare(args.root, args.linux, args.windows, args.notes)
            print(f"Prepared and verified {tag}")
        else:
            tags = ([p.parent.name for p in sorted((args.root / "releases").glob("*/release.json"))]
                    if args.all else [args.tag])
            if not tags or any(tag is None for tag in tags):
                raise ValueError("Specify a release tag or --all")
            for tag in tags:
                verify(args.root, tag)
                print(f"Verified {tag}")
    except (ValueError, OSError, KeyError, TypeError, zipfile.BadZipFile) as error:
        parser.exit(1, f"Release validation failed: {error}\n")


if __name__ == "__main__":
    main()
