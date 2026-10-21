# Morsetastic CW Trainer

**Hear the melody of CW in every character and word.**

Morsetastic is a simple CW reception trainer for Linux and Windows. You can use
it to learn Morse or keep your reception sharp, practising individual characters,
groups, words and callsigns.

Choose a lesson or select your own characters, and adjust the speed and spacing
to suit you. Characters you find difficult come up more often.

## Downloads

[GitHub Releases](https://github.com/m0jwt/morsetastic-releases/releases) provide
version-specific ZIPs, notes and checksums. The same ZIPs are stored below, with
one directory per version and separate `linux` and `windows` subdirectories.
Release notes describe the changes and details for each version.

<!-- BEGIN RELEASE INDEX -->
Latest: **V1.3**

| Version | Linux x86-64 | Windows x86-64 | Notes |
| --- | --- | --- | --- |
| V1.3 | [ZIP](releases/v1.3/linux/Morsetastic-V1.3-Linux-x86_64.zip) | [ZIP](releases/v1.3/windows/Morsetastic-V1.3-Windows-x86_64.zip) | [Release notes](releases/v1.3/RELEASE_NOTES.md) |
| V1.2 | [ZIP](releases/v1.2/linux/Morsetastic-V1.2-Linux-x86_64.zip) | [ZIP](releases/v1.2/windows/Morsetastic-V1.2-Windows-x86_64.zip) | [Release notes](releases/v1.2/RELEASE_NOTES.md) |
<!-- END RELEASE INDEX -->

## Installation

Extract the entire ZIP into one folder. Keep the practice files and the
`languages` folder beside the executable; do not run from inside the ZIP.

- Linux x86-64: requires GTK3 and ALSA. Run `./morsetastic`; use
  `chmod +x morsetastic` if your extractor removed execution permission.
- Windows 11 x86-64: run `morsetastic.exe`. No extra audio DLL is required.

Select English or Polski in Configuration. Polish interface text is supplied in
`languages/pl.json`. English is built in and remains available if a translation
file is missing or damaged. Morsetastic saves settings in its own per-user
profile.

About shows version, build date and checkpoint. Each release has `release.json`
with exact source/file hashes and `SHA256SUMS.txt`. From a version directory,
run `sha256sum -c SHA256SUMS.txt`. For separately downloaded ZIPs, compare
`sha256sum <ZIP>` or Windows `Get-FileHash <ZIP> -Algorithm SHA256` with the list.

## Features

- Single-character practice, random character groups, words and callsigns.
- Selectable letters, numbers and symbols, with Default, lesson and Custom sets.
- Adaptive practice that revisits characters needing more work, with bars
  showing their training priority.
- Adjustable speed, tone, character spacing and repeat timing.
- Options to repeat after errors and hide the transmitted character.
- Timed exercises, per-character statistics, copy timing and saved reports.
- English and Polish interface, help and reports, with built-in English fallback.
- A choice of system appearance or the Morsetastic light-blue theme.
- Audio-output selection and saved practice settings.

## Lessons

Choose Default, a named lesson or your own Custom character selection in
Configuration. Each lesson lists the characters it includes.

Lessons compare similar-sounding characters alongside contrasting sounds to
help you hear the differences. Letters and numbers are mixed, with combinations
such as S/H/5 and U/V/4; other sets introduce symbols alongside letters and
numbers. The aim is to recognise each character's rhythm, rather than count
its dots and dashes.

There is no compulsory order, pass mark or automatic advancement. Choose a set
you find useful and revisit difficult combinations as needed. Lessons change
the selected characters, not your chosen speed, spacing or exercise settings.

In Words mode, only words using active characters are eligible. If no words
match, choose another file or a wider character selection.

## Practice Files

Downloads include English and Polish word lists and a callsign list:

| File | Practice |
| --- | --- |
| `default_words.txt` | Default English words |
| `callsigns.txt` | Callsigns |
| `words400.txt` | Additional English words |
| `wyrazy100.txt` | Polish words |
| `wyrazy400.txt` | Additional Polish words |

These files sit beside the executable. Choose Configuration > Load word file
to use a supplied list or load your own plain-text file. Polish practice words
replace diacritics with plain alphabet letters for CW; for example, `dzien`
and `czlowiek` are intentional CW spellings.

## Inspiration and Credits

- G4ILO's Morse Machine inspired the adaptive single-character training idea.
- RUFZ.XP, by Mathias Kolpe, DL4MM, and Alessandro Vitiello, IV3XYM, inspired
  the string/callsign-copy direction.
- Morsetastic is created by M0JWT and shaped by an interest in CW practice
  and amateur radio.

## Licence

Morsetastic is free to use, copy and share. I hope you enjoy the program and
find it useful. It is provided as-is, without warranty. Feedback is welcome.
