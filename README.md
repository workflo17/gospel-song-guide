# Evangelio del Día: daily song pipeline

Turning the day's Gospel from [evangeliodeldia.org](https://evangeliodeldia.org/SP/gospel) into a
Spanish devotional song and a 3 to 4 minute YouTube video, with free tools.

**Read the guide:** https://workflo17.github.io/gospel-song-guide/

- [The pipeline](https://workflo17.github.io/gospel-song-guide/) — how it fits together, which free
  tools to use, and the licence and YouTube policy traps.
- [Mac setup](https://workflo17.github.io/gospel-song-guide/mac.html) — eight sessions, in order,
  each ending in a check that either passes or fails.

## gospel.py

Fetches the day's readings and commentary from the Evangelizo feed. No API key, no signup.

```bash
python3 gospel.py                        # today, Spanish, to stdout
python3 gospel.py --out hoy.json         # to a file
python3 gospel.py 2026-08-20 --lang PT   # another date, Portuguese
python3 gospel.py --gospel-only          # skip the other readings
```

```
2026-08-15 [SP] -> hoy.json
  gospel     Lc 1,39-56.  (1523 chars)
  commentary Beato Columba Marmion (1858-1923), abad  (1403 chars)
```

Two limits from the feed itself: dates cannot be more than 30 days from today, and it returns HTML
fragments rather than JSON, which the script strips.

If it fails with a certificate error, antivirus software is intercepting HTTPS. `pip3 install
truststore` and run it again; the script picks it up automatically.

## Building the site

`docs/` is generated. Edit `workflow.html` or `mac-setup.html`, then:

```bash
python build_site.py
```

Those two files are body content only, because they are also published as Claude artifacts where the
document shell is supplied at publish time. `build_site.py` wraps them for GitHub Pages.

## Licence note

The Spanish scripture text served by the feed is a copyrighted translation, so generated JSON is
gitignored and never committed. Song lyrics built from this should be **original paraphrase**, not
the translation set to music.
