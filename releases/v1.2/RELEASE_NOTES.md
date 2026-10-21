# Morsetastic V1.2

**Feel the rhythm of CW and learn to hear the melody of each character.**

Morsetastic is a simple CW reception trainer for Linux and Windows. It helps
beginners build confidence and experienced operators keep their reception sharp,
with focused practice in characters, groups, words and callsigns.

## First Morsetastic Release

- New application name, window titles, English/Polish descriptions, help,
  About and reports. Executables are `morsetastic` and `morsetastic.exe`.
- Independent source and public-download repositories starting at V1.2.
- Separate per-user settings; saving never overwrites an imported profile.
- English and Polish interface, including Configuration, messages and reports.
  English is compiled in. Missing, damaged or outdated catalogs fall back to
  English without losing practice settings; the authoring template is optional.
- Compact, resizable Configuration: character list on the left, practice settings
  and language on the right, callsign/audio/buttons below.
- New-profile defaults: characters through `=`, 2-second repeat wait and 1.5x
  character spacing. Existing selections and timing are preserved on import.
- Adaptive single-character practice and exact positional word/string matching.
  First-copy points and perfect-copy bonuses remain unchanged.
- Every prompt finishes before the next, followed by the larger of a configured
  200-400 ms minimum gap and a full word space at the selected speed.
- Speed up to 150 WPM, tone from 600-1000 Hz, native ALSA/WASAPI audio.
- Renamed build/package scripts and native regression checks. No change to the
  trainer, tone engine, scoring, timing or bar animation.

## Packages

Production Linux x86-64 GTK3 and Windows x86-64 native Win32-LCL builds.
Each ZIP has the executable and five practice files at its root:
`default_words.txt`, `callsigns.txt`, `words400.txt`, `wyrazy100.txt` and
`wyrazy400.txt`. Runtime Polish is `languages/pl.json`; keep the `languages`
folder next to the executable. The template and development sources are not
shipped. English works without any language files.

Linux requires GTK3 and ALSA. Windows uses WASAPI with no added audio DLL.
Extract the entire ZIP before running. About shows version, build date and
checkpoint; `release.json` and `SHA256SUMS.txt` record package provenance.
