"""Fetch the day's readings from Evangelizo, the feed behind evangeliodeldia.org.

Free, no key, no signup. Spanish by default.

    python gospel.py                        # today, Spanish
    python gospel.py --out today.json
    python gospel.py 2026-12-25 --lang AM   # a specific date, English
    python gospel.py --gospel-only

Two things worth knowing about this feed:
  * dates cannot be more than 30 days from today, so no backfilling a year
  * it returns HTML fragments, not JSON, so everything gets tag-stripped here

The commentary block (a Church Father, a saint, a pope) is the most useful part
for songwriting. It carries the day's theological angle already worked out.
"""

import argparse
import datetime as dt
import html
import json
import re
import ssl
import sys
import urllib.parse
import urllib.request

FEED = "https://feed.evangelizo.org/v2/reader.php"
UA = {"User-Agent": "gospel-song/1.0 (+daily devotional pipeline)"}

# content codes for the Roman ordinary calendar
PARTS = {
    "first_reading": "FR",
    "psalm": "PS",
    "second_reading": "SR",
    "gospel": "GSP",
}


def make_ssl_context():
    """Prefer the OS trust store.

    Antivirus and corporate TLS interception installs its own root in the
    Windows store but not in certifi, so the bundled-CA default fails with
    CERTIFICATE_VERIFY_FAILED on machines running AV HTTPS scanning.
    """
    try:
        import truststore
        return truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    except Exception:
        return ssl.create_default_context()


SSL_CTX = make_ssl_context()


def strip_html(s):
    s = re.sub(r"(?i)<br\s*/?>|</p>", "\n", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s)
    s = re.sub(r"[ \t\xa0]+", " ", s)
    s = re.sub(r"\n\s*\n+", "\n\n", s)
    return s.strip()


def get(type_, date, lang, content=None, timeout=25):
    q = {"date": date.strftime("%Y%m%d"), "type": type_, "lang": lang}
    if content:
        q["content"] = content
    url = FEED + "?" + urllib.parse.urlencode(q)
    req = urllib.request.Request(url, headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=SSL_CTX) as r:
            raw = r.read().decode("utf-8", "replace")
    except Exception as e:
        return {"error": str(e), "text": ""}
    if "wrong param" in raw or "Reader Evangelizo" in raw[:200]:
        return {"error": "feed rejected params", "text": ""}
    return {"text": strip_html(raw)}


def fetch_day(date, lang="SP"):
    out = {
        "date": date.isoformat(),
        "lang": lang,
        "source": "evangelizo.org / evangeliodeldia.org",
        "liturgic_title": get("liturgic_t", date, lang)["text"],
        "feast": get("feast", date, lang)["text"],
        "saint": get("saint", date, lang)["text"],
        "readings": {},
        "commentary": {},
    }
    for name, code in PARTS.items():
        text = get("reading", date, lang, code)["text"]
        if not text:
            continue
        out["readings"][name] = {
            "citation": get("reading_st", date, lang, code)["text"],
            "title": get("reading_lt", date, lang, code)["text"],
            "text": text,
        }
    out["commentary"] = {
        "title": get("comment_t", date, lang)["text"],
        "author": get("comment_a", date, lang)["text"],
        "source": get("comment_s", date, lang)["text"],
        "text": get("comment", date, lang)["text"],
    }
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("date", nargs="?", help="YYYY-MM-DD (default: today)")
    p.add_argument("--lang", default="SP",
                   help="SP spanish, AM english, PT, FR, IT, DE, PL, NL, AR")
    p.add_argument("--out", help="write JSON here instead of stdout")
    p.add_argument("--gospel-only", action="store_true")
    a = p.parse_args()

    date = dt.date.fromisoformat(a.date) if a.date else dt.date.today()
    if abs((date - dt.date.today()).days) > 30:
        print("warning: the feed only serves +/- 30 days from today",
              file=sys.stderr)

    data = fetch_day(date, a.lang)
    if a.gospel_only:
        data["readings"] = {"gospel": data["readings"].get("gospel", {})}

    blob = json.dumps(data, indent=2, ensure_ascii=False)
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            f.write(blob)
        g = data["readings"].get("gospel", {})
        c = data["commentary"]
        print(f"{date} [{a.lang}] -> {a.out}")
        print(f"  gospel     {g.get('citation','?')}  ({len(g.get('text',''))} chars)")
        print(f"  commentary {c.get('author','?')}  ({len(c.get('text',''))} chars)")
    else:
        sys.stdout.write(blob + "\n")


if __name__ == "__main__":
    main()
