# Morsetastic Downloads

**Feel the rhythm of CW and learn to hear the melody of each character.**

Morsetastic is a simple CW reception trainer for Linux and Windows. It helps
beginners build confidence and experienced operators keep their reception sharp,
with focused practice in characters, groups, words and callsigns.

This public repository contains production downloads and release automation
only. Application source is kept separately in a private repository.
Morsetastic starts at V1.2; previous MorseForge archives remain separate.

## Downloads

[GitHub Releases](https://github.com/m0jwt/morsetastic-releases/releases) provide
version-specific ZIPs, notes and checksums. The same ZIPs are stored below, with
one directory per version and separate `linux` and `windows` subdirectories.

<!-- BEGIN RELEASE INDEX -->
Latest: **V1.3**

| Version | Linux x86-64 | Windows x86-64 | Notes |
| --- | --- | --- | --- |
| V1.3 | [ZIP](releases/v1.3/linux/Morsetastic-V1.3-Linux-x86_64.zip) | [ZIP](releases/v1.3/windows/Morsetastic-V1.3-Windows-x86_64.zip) | [Release notes](releases/v1.3/RELEASE_NOTES.md) |
| V1.2 | [ZIP](releases/v1.2/linux/Morsetastic-V1.2-Linux-x86_64.zip) | [ZIP](releases/v1.2/windows/Morsetastic-V1.2-Windows-x86_64.zip) | [Release notes](releases/v1.2/RELEASE_NOTES.md) |
<!-- END RELEASE INDEX -->

## Installation

Each ZIP contains the executable and five practice files at its root:
`default_words.txt`, `callsigns.txt`, `words400.txt`, `wyrazy100.txt` and
`wyrazy400.txt`. Extra English/Polish word lists use plain alphabet letters for
CW. Select a list with Configuration > Load word file.

Polish interface text is in `languages/pl.json`. Keep the `languages` folder
beside the executable and select English or Polski in Configuration. English is
built in and works if that folder is missing or damaged. Translation templates
and development source are not included in downloads.

Extract the entire ZIP into one folder; do not run from inside the ZIP.

- Linux x86-64: requires GTK3 and ALSA. Run `./morsetastic`; use
  `chmod +x morsetastic` if your extractor removed execution permission.
- Windows 11 x86-64: run `morsetastic.exe`. No extra audio DLL is required.

Morsetastic saves a separate user profile. If none exists, valid MorseForge
settings are used as a starting point without altering the old settings file.

About shows version, build date and checkpoint. Each release has `release.json`
with exact source/file hashes and `SHA256SUMS.txt`. From a version directory,
run `sha256sum -c SHA256SUMS.txt`. For separately downloaded ZIPs, compare
`sha256sum <ZIP>` or Windows `Get-FileHash <ZIP> -Algorithm SHA256` with the list.

## Publishing

Published ZIPs and tags are not overwritten. A later patch gets a new directory
and tag, for example `releases/v1.2.1/` and `v1.2.1`.

The private source supplies the build-and-prepare script. After reviewing and
testing the output, commit the version directory and README, create its annotated
tag and push manually. The tag starts Publish Release: validation, draft creation,
uploads and publication. Resume failed drafts through Actions > Publish Release
> Run workflow with the same tag. Published releases cannot be replaced.

Verification: `python3 -B tools/release.py verify --all`.
Packaging checks: `python3 -B -m unittest discover -s tests -v`.

Morsetastic is free to use, copy and share, and is provided as-is without warranty.
