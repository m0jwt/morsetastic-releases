# Morsetastic V1.3

This release combines character comparison lessons, appearance choices, more
efficient GUI drawing and keyboard input fixes. The published V1.2 packages
remain unchanged. V1.2.1 was an unpublished development version.

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
- `+(AR)` has no space between `+` and the bracket, with an overline on AR.
  This denotes one character; the expected answer is still the single `+` key.
- Default remains unchanged, with `+`, `@` and later symbols unchecked.
- Existing profiles, custom selections, timing and language fallback are preserved.

## GUI Drawing Improvements

- Track dirty and animating bars separately and repaint only affected columns.
- Cache the chart for window restoration, using native paint bounds to limit
  screen copies. Resize and font changes rebuild the chart as needed.
- Replaying an unchanged prompt no longer repaints the chart. Stationary error
  flashes repaint at their start and expiry, not on every timer tick.
- Keep the existing gradients, highlights, animation rate and training behaviour.
- Stop the animation timer once bars have settled. Idle bars no longer generate
  continuous redraws, reducing unnecessary updates over remote desktop.

## Appearance

- Configuration now offers System and Morsetastic (light blue), applied on OK
  and saved per user. Cancel leaves both the appearance and saved file unchanged.
- System uses native widget colours and a neutral chart, retaining red error
  flashes and blue current-character indications. Copy text follows the system
  foreground instead of forcing black text on every background.
- Morsetastic retains reflective bars and light-blue controls with matched text
  and readable selected rows, even when the desktop uses a dark theme.
- Main, configuration, About, Help and statistics use the selected appearance.
- Windows slider backgrounds match the system panel in System mode,
  including after switching from light blue. Native slider handles keep their
  system accent colour.
- Existing profiles remain valid and keep the light-blue default. Audio, timing,
  scoring and selective bar drawing are unchanged.

## Stability

- Audio-device startup and unrecoverable write failures stop the exercise with
  an English/Polish status message instead of leaving input waiting indefinitely
  or accumulating replays for a stopped audio worker. Start can retry the device.
- Failed streams discard unplayable queued prompts; healthy playback keeps the
  complete current character and mandatory silence unchanged.
- Regression coverage includes held keys, rapid separate key presses, focus
  changes, audio failures and recovery, repeated repaint/resize activity and
  convergence to an idle chart in both appearance modes.
