#!/usr/bin/env python3
"""Validate the candidate feeds in feeds.py and write the blogroll outputs.

Outputs (all generated; do not edit by hand):
  blogroll.opml     subscription list for any feed reader / FeedLand
  README.md         the same list as Markdown, with validation status
  ghost-page.html   HTML for the Ghost page (paste into an HTML card)
  validation.json   per-feed result of the last run

Stdlib only. Run:  python3 build.py
"""
import concurrent.futures as cf
import datetime as dt
import html
import json
import pathlib
import re
import urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

from feeds import EVENTS, FOLDERS, SUICIDE_PREVENTION

HERE = pathlib.Path(__file__).parent
UA = "center17-blogroll/0.1 (+https://center17.org/)"
TIMEOUT = 25


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml;q=0.9, */*;q=0.5"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return r.status, r.headers.get("content-type", ""), r.read(2_000_000)


def _iso(d):
    """Lenient ISO-8601: tolerate 'Z', date-only and year-month strings."""
    d = d.strip().replace("Z", "+00:00")
    for fmt in (None, "%Y-%m-%d", "%Y-%m"):
        try:
            return dt.datetime.fromisoformat(d) if fmt is None else dt.datetime.strptime(d, fmt)
        except ValueError:
            continue
    return None


def _latest(dates, parser):
    out = []
    for d in dates:
        try:
            v = parser(d)
        except Exception:  # noqa: BLE001
            v = None
        if v is not None:
            out.append(v.replace(tzinfo=v.tzinfo or dt.timezone.utc))
    return max(out, default=None)


def parse_feed(data):
    """Return (kind, title, latest_date) or raise."""
    root = ET.fromstring(data)
    tag = root.tag.lower()
    if tag.endswith("rss"):
        ch = root.find("channel")
        title = (ch.findtext("title") or "").strip()
        dates = [i.findtext("pubDate") for i in ch.findall("item") if i.findtext("pubDate")]
        return "rss", title, _latest(dates, parsedate_to_datetime)
    if tag.endswith("feed"):
        ns = {"a": "http://www.w3.org/2005/Atom"}
        title = (root.findtext("a:title", namespaces=ns) or "").strip()
        dates = [e.findtext("a:updated", namespaces=ns) or e.findtext("a:published", namespaces=ns) for e in root.findall("a:entry", ns)]
        return "atom", title, _latest([d for d in dates if d], _iso)
    if tag.endswith("rdf"):
        ns = {"r": "http://purl.org/rss/1.0/", "dc": "http://purl.org/dc/elements/1.1/"}
        title = (root.findtext("r:channel/r:title", namespaces=ns) or "").strip()
        dates = [i.findtext("dc:date", namespaces=ns) for i in root.findall("r:item", ns)]
        return "rss1", title, _latest([d for d in dates if d], _iso)
    raise ValueError(f"not a feed (root <{root.tag}>)")


def check(entry):
    title, url, site, note = entry
    res = {"title": title, "feed": url, "site": site, "note": note, "ok": False}
    try:
        status, ctype, data = fetch(url)
        kind, ftitle, latest = parse_feed(data)
        res.update(ok=True, kind=kind, feed_title=ftitle, latest=latest.isoformat() if latest else None, status=status)
    except Exception as e:  # noqa: BLE001
        res["error"] = f"{type(e).__name__}: {str(e)[:120]}"
    return res


def main():
    jobs = [(folder, e) for folder, entries in FOLDERS.items() for e in entries]
    with cf.ThreadPoolExecutor(max_workers=12) as ex:
        results = list(ex.map(lambda fe: (fe[0], check(fe[1])), jobs))
    by_folder = {}
    for folder, r in results:
        by_folder.setdefault(folder, []).append(r)
    (HERE / "validation.json").write_text(json.dumps(by_folder, indent=1))

    stamp = dt.date.today().isoformat()
    ok_total = sum(r["ok"] for rs in by_folder.values() for r in rs)
    # ---- OPML
    o = [f'<?xml version="1.0" encoding="UTF-8"?>\n<opml version="2.0">\n<head>\n<title>Center17 blogroll</title>\n<dateModified>{dt.datetime.now(dt.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")}</dateModified>\n<ownerName>Center17</ownerName>\n<ownerId>https://center17.org/</ownerId>\n</head>\n<body>']
    for folder, rs in by_folder.items():
        o.append(f'<outline text="{html.escape(folder)}">')
        for r in rs:
            if not r["ok"]:
                continue
            o.append(f'  <outline type="rss" text="{html.escape(r["title"])}" title="{html.escape(r["title"])}" xmlUrl="{html.escape(r["feed"])}" htmlUrl="{html.escape(r["site"])}"/>')
        o.append("</outline>")
    o.append("</body>\n</opml>\n")
    (HERE / "blogroll.opml").write_text("\n".join(o))

    # ---- README
    m = ["# Center17 blogroll", "",
         "Feeds for computational psychiatry, neuroimaging and neuromodulation, kept for students and collaborators of [Center17](https://center17.org/).",
         "", f"- **Subscribe to everything:** [`blogroll.opml`](blogroll.opml) imports into any feed reader (NetNewsWire, Feedly, Inoreader, FeedLand, Miniflux…).",
         f"- Last validated {stamp}: {ok_total} feeds live. Edit `feeds.py`, run `python3 build.py`; dead feeds are dropped automatically.", ""]
    for folder, rs in by_folder.items():
        m += [f"## {folder}", "", "| Feed | Site | Latest item | Note |", "|---|---|---|---|"]
        for r in rs:
            if r["ok"]:
                m.append(f"| [{r['title']}]({r['feed']}) | [{re.sub(r'^https?://(www\\.)?','',r['site']).rstrip('/')}]({r['site']}) | {(r['latest'] or '')[:10]} | {r['note']} |")
        dead = [r for r in rs if not r["ok"]]
        if dead:
            m += ["", "<details><summary>Not currently reachable (kept in feeds.py, excluded from the OPML)</summary>", ""]
            m += [f"- {r['title']}: `{r['error']}`" for r in dead]
            m += ["", "</details>"]
        m.append("")
    m += ["## Annual anchors", "", "| Event | When | Note |", "|---|---|---|"]
    m += [f"| [{n}]({u}) | {w} | {note} |" for n, u, w, note in EVENTS]
    m += ["", "## Suicide prevention", "", "Kept alongside Aaron Swartz Day. If you are in crisis, use the first line that applies to where you are.", "",
          "| Resource | Note |", "|---|---|"]
    m += [f"| [{n}]({u}) | {note} |" for n, u, note in SUICIDE_PREVENTION]
    m.append("")
    (HERE / "README.md").write_text("\n".join(m))

    # ---- Ghost page HTML (plain markup; Ghost's HTML card keeps it)
    h = [f'<p>Feeds for computational psychiatry, neuroimaging and neuromodulation, kept for students and collaborators. <a href="https://github.com/m9h/center17-blogroll/raw/main/blogroll.opml">Subscribe to all of them at once (OPML)</a>, or pick from the list. Validated {stamp}; the source is <a href="https://github.com/m9h/center17-blogroll">on GitHub</a>.</p>']
    for folder, rs in by_folder.items():
        h.append(f"<h2>{html.escape(folder)}</h2><ul>")
        for r in rs:
            if r["ok"]:
                note = f" <small>{html.escape(r['note'])}</small>" if r["note"] else ""
                h.append(f'<li><a href="{html.escape(r["site"])}">{html.escape(r["title"])}</a> <a href="{html.escape(r["feed"])}" title="RSS">⌁</a>{note}</li>')
        h.append("</ul>")
    h.append("<h2>Annual anchors</h2><ul>")
    h += [f'<li><a href="{html.escape(u)}">{html.escape(n)}</a>: {html.escape(w)}{(" <small>" + html.escape(note) + "</small>") if note else ""}</li>' for n, u, w, note in EVENTS]
    h.append("</ul><h2>Suicide prevention</h2><p>Kept alongside Aaron Swartz Day. If you are in crisis, use the first line that applies to where you are.</p><ul>")
    h += [f'<li><a href="{html.escape(u)}">{html.escape(n)}</a>{(": " + html.escape(note)) if note else ""}</li>' for n, u, note in SUICIDE_PREVENTION]
    h.append("</ul>")
    (HERE / "ghost-page.html").write_text("\n".join(h) + "\n")

    # ---- report
    for folder, rs in by_folder.items():
        print(f"== {folder}: {sum(r['ok'] for r in rs)}/{len(rs)} live")
        for r in rs:
            flag = "ok  " if r["ok"] else "DEAD"
            extra = (r.get("latest") or "")[:10] if r["ok"] else r.get("error", "")
            print(f"   {flag} {r['title'][:42]:42} {extra}")


if __name__ == "__main__":
    main()
