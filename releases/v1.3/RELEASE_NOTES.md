# Morsetastic V1.3

This release combines character comparison lessons, appearance choices, more
efficient GUI drawing and keyboard input fixes.

## Held-Key Fix

- Holding a keyboard or keypad key now submits one practice answer, rather than
  treating keyboard autorepeat as more answers or error replays.
- Release and press again to submit another character. Intentional double
  letters, keypad digits and overlapping presses of different keys still work.
- Key tracking resets when the main window loses focus, so releasing a key
  outside the application does not leave it stuck on return.
- No changes to tone generation, prompt separation, scoring rules or settings.

## Single-Character Key Bursts

- Single mode now accepts one answer per playback. Rapid separate key presses
  while the next character or replay is queued are discarded before scoring.
- Input opens again when the audio worker starts that next playback. The current
  character and its mandatory separation are preserved; no audio is cut short.
- Words and String modes retain their existing fast typing and matching rules.

## Character Lessons

- Configuration now offers Default, 41 named lessons and a separately saved
  Custom selection. Every lesson name includes its characters.
- Every lesson contains six distinct characters, mixing letters and numbers.
- There are 24 two-pair comparison lessons, five three-way-family lessons
  (including S/H/5 and U/V/4), and 12 lessons with one symbol each.
- The symbols `. , ? / = +` each appear in two different mixed lessons.
- Lessons are freely selectable comparison sets, not a compulsory learning order.
- English and Polish Help explain the comparison method, the lesson families,
  choosing a comfortable speed and practising without automatic advancement.

## GUI Drawing Improvements

- General GUI drawing improvements: only changed elements are redrawn,
  reducing CPU use.

## Appearance

- Choose between System colours and the Morsetastic light-blue theme in
  Configuration. Your choice is saved.

## Stability

- Audio-device startup and unrecoverable write failures stop the exercise with
  an English/Polish status message instead of leaving input waiting indefinitely
  or accumulating replays for a stopped audio worker. Start can retry the device.
- Failed streams discard unplayable queued prompts; healthy playback keeps the
  complete current character and mandatory silence unchanged.
