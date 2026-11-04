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

from events import EVENTS
from feeds import FOLDERS, SUICIDE_PREVENTION

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


def _one(d, parser):
    try:
        v = parser(d) if d else None
    except Exception:  # noqa: BLE001
        v = None
    return v.replace(tzinfo=v.tzinfo or dt.timezone.utc) if v is not None else None


def parse_feed(data):
    """Return (kind, title, latest_date, items); items are dicts title/link/date."""
    root = ET.fromstring(data)
    tag = root.tag.lower()
    items = []
    if tag.endswith("rss"):
        ch = root.find("channel")
        title = (ch.findtext("title") or "").strip()
        for i in ch.findall("item"):
            items.append({"title": (i.findtext("title") or "").strip(), "link": (i.findtext("link") or "").strip(),
                          "date": _one(i.findtext("pubDate"), parsedate_to_datetime)})
        kind = "rss"
    elif tag.endswith("feed"):
        ns = {"a": "http://www.w3.org/2005/Atom"}
        title = (root.findtext("a:title", namespaces=ns) or "").strip()
        for e in root.findall("a:entry", ns):
            link = ""
            for l in e.findall("a:link", ns):
                if l.get("rel", "alternate") == "alternate":
                    link = l.get("href", ""); break
            items.append({"title": (e.findtext("a:title", namespaces=ns) or "").strip(), "link": link,
                          "date": _one(e.findtext("a:published", namespaces=ns) or e.findtext("a:updated", namespaces=ns), _iso)})
        kind = "atom"
    elif tag.endswith("rdf"):
        ns = {"r": "http://purl.org/rss/1.0/", "dc": "http://purl.org/dc/elements/1.1/"}
        title = (root.findtext("r:channel/r:title", namespaces=ns) or "").strip()
        for i in root.findall("r:item", ns):
            items.append({"title": (i.findtext("r:title", namespaces=ns) or "").strip(), "link": (i.findtext("r:link", namespaces=ns) or "").strip(),
                          "date": _one(i.findtext("dc:date", namespaces=ns), _iso)})
        kind = "rss1"
    else:
        raise ValueError(f"not a feed (root <{root.tag}>)")
    dated = [x["date"] for x in items if x["date"]]
    return kind, title, (max(dated) if dated else None), items


def check(entry):
    title, url, site, note = entry
    res = {"title": title, "feed": url, "site": site, "note": note, "ok": False}
    try:
        status, ctype, data = fetch(url)
        kind, ftitle, latest, items = parse_feed(data)
        res.update(ok=True, kind=kind, feed_title=ftitle, latest=latest.isoformat() if latest else None, status=status,
                   items=[{"title": x["title"], "link": x["link"], "date": x["date"].isoformat()} for x in items if x["date"] and x["link"]][:40])
    except Exception as e:  # noqa: BLE001
        res["error"] = f"{type(e).__name__}: {str(e)[:120]}"
    return res


RIVER_CSS = """
@font-face{font-family:'System';src:local('Iosevka'),local('PragmataPro'),local('IBM Plex Mono'),local('SF Mono'),local('Menlo'),local('Consolas')}
:root{--mono:'System','IBM Plex Mono','SF Mono',Menlo,Consolas,monospace;--red:#c8102e;--fg:#d4d4d4;--dim:#888}
*{margin:0;padding:0;box-sizing:border-box}body{background:#111;color:var(--fg);font-family:'Palatino Linotype',Palatino,'Book Antiqua',Georgia,serif;font-size:17px;line-height:1.7;-webkit-font-smoothing:antialiased}
a{color:inherit;text-decoration:none;border-bottom:1px solid #555}a:hover{border-bottom-color:var(--red)}
.topnav{position:sticky;top:0;background:rgba(17,17,17,.94);backdrop-filter:blur(6px);border-bottom:1px solid #2a2a2a}
.topnav .inner{max-width:1100px;margin:0 auto;padding:14px 40px;display:flex;align-items:baseline;gap:28px;font-family:var(--mono);font-size:.74rem;text-transform:uppercase;letter-spacing:.14em}
.topnav a{border-bottom:none;color:#999}.topnav a:hover{color:var(--fg)}.topnav .brand{color:var(--fg);margin-right:12px}.topnav .brand b{color:var(--red)}.topnav .ext{margin-left:auto}.topnav .ext::after{content:" \\2197"}
.page{max-width:1100px;margin:0 auto;padding:48px 40px 80px}
.masthead{padding-bottom:36px;border-bottom:3px solid var(--fg);margin-bottom:48px;display:grid;grid-template-columns:1fr 320px;gap:40px;align-items:end}
.masthead h1{font-family:var(--mono);font-size:2.2rem;font-weight:400;letter-spacing:.06em;line-height:1.1;margin-bottom:10px}.masthead h1 b{color:var(--red)}
.masthead .lede{font-style:italic;color:var(--dim);max-width:560px}.masthead .now{font-family:var(--mono);font-size:.74rem;line-height:1.9;color:var(--dim)}
.masthead .now dt{text-transform:uppercase;letter-spacing:.14em;font-size:.62rem;color:#666;margin-top:8px}.masthead .now a{color:#bbb}
.day{position:relative;margin-bottom:40px;padding-left:48px}
.day-label{position:absolute;left:-8px;top:0;font-family:var(--mono);font-size:.6rem;text-transform:uppercase;letter-spacing:.18em;color:#999;writing-mode:vertical-lr;transform:rotate(180deg);white-space:nowrap}
.rule{height:1px;background:#333;margin-bottom:16px}
.row{display:grid;grid-template-columns:210px 1fr 70px;gap:16px;padding:10px 0;border-bottom:1px dotted #2a2a2a;align-items:baseline}.row:last-child{border-bottom:none}
.row:hover .row-title{color:var(--red)}.empty{font-family:var(--mono);font-size:.72rem;color:#777;letter-spacing:.06em;margin-top:10px}.empty a{color:#aaa}.row-src{font-family:var(--mono);font-size:.74rem;color:#999;overflow-wrap:anywhere}.row-title{font-size:.95rem}.row-time{font-family:var(--mono);font-size:.7rem;color:#999;text-align:right;white-space:nowrap}
footer{margin-top:64px;padding-top:24px;border-top:3px solid var(--fg);display:flex;justify-content:space-between;font-size:.78rem;color:#999}
footer nav{display:flex;gap:20px}footer nav a{font-family:var(--mono);font-size:.7rem;text-transform:uppercase;letter-spacing:.1em;color:var(--dim);border-bottom:none}
@media(max-width:700px){.topnav .inner{padding:12px 20px;gap:16px;flex-wrap:wrap}.topnav .ext{margin-left:0}.page{padding:32px 20px 48px}.masthead{grid-template-columns:1fr}.day{padding-left:0}.day-label{position:static;writing-mode:horizontal-tb;transform:none;display:block;margin-bottom:8px}.row{grid-template-columns:1fr;gap:4px}.row-time{text-align:left}}
"""


def _d(s):
    return dt.date.fromisoformat(s)


def _when(e):
    a, b = _d(e["start"]), _d(e["end"])
    if a == b:
        return a.strftime("%-d %B %Y")
    if a.month == b.month:
        return f"{a.day} to {b.day} {a.strftime('%B %Y')}"
    return f"{a.strftime('%-d %B')} to {b.strftime('%-d %B %Y')}"


def _ics_fold(line):
    out, b = [], line.encode("utf-8")
    while len(b) > 73:
        cut = 73
        while cut > 0 and (b[cut] & 0xC0) == 0x80:
            cut -= 1
        out.append(b[:cut].decode("utf-8")); b = b" " + b[cut:]
    out.append(b.decode("utf-8"))
    return "\r\n".join(out)


def _ics_text(t):
    bs = chr(92)
    return t.replace(bs, bs + bs).replace(";", bs + ";").replace(",", bs + ",").replace(chr(10), bs + "n")


def write_events(stamp):
    today = dt.date.today()
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    evs = sorted(EVENTS, key=lambda e: e["start"])
    # ---- events.ics
    L = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Center17//center17-blogroll//EN", "CALSCALE:GREGORIAN", "METHOD:PUBLISH",
         "X-WR-CALNAME:Center17 events", "X-WR-CALDESC:Annual anchors for computational psychiatry\, neuroimaging\, neuromodulation and the open web.",
         "REFRESH-INTERVAL;VALUE=DURATION:P1D", "X-PUBLISHED-TTL:P1D"]
    for e in evs:
        end_excl = (_d(e["end"]) + dt.timedelta(days=1)).strftime("%Y%m%d")
        summary = e["name"] + (" (expected dates)" if e["status"] == "expected" else "")
        desc = (e["note"] + "\n" if e["note"] else "") + ("Placeholder from the usual pattern; replaced when the organiser announces dates.\n" if e["status"] == "expected" else "") + e["url"]
        L += ["BEGIN:VEVENT", f"UID:{e['slug']}@center17.org", f"DTSTAMP:{now}",
              f"DTSTART;VALUE=DATE:{_d(e['start']).strftime('%Y%m%d')}", f"DTEND;VALUE=DATE:{end_excl}",
              f"SUMMARY:{_ics_text(summary)}", f"LOCATION:{_ics_text(e['city'])}", f"URL:{e['url']}",
              f"DESCRIPTION:{_ics_text(desc)}", "STATUS:" + ("CONFIRMED" if e["status"] == "announced" else "TENTATIVE"),
              "CATEGORIES:Center17", "TRANSP:TRANSPARENT", "END:VEVENT"]
    L.append("END:VCALENDAR")
    (HERE / "events.ics").write_bytes(("\r\n".join(_ics_fold(x) for x in L) + "\r\n").encode("utf-8"))

    # ---- events.html (same design as the river)
    def row(e):
        a, b = _d(e["start"]), _d(e["end"])
        past = b < today
        flag = ' <small>(expected)</small>' if e["status"] == "expected" else ""
        note = f'<span class="row-desc">{html.escape(e["city"])}{(". " + html.escape(e["note"])) if e["note"] else ""}</span>'
        return (f'<a class="row{" past" if past else ""}" href="{html.escape(e["url"])}"><span class="row-src">{html.escape(_when(e))}</span>'
                f'<span class="row-title">{html.escape(e["name"])}{flag}{note}</span><span class="row-time">{a.strftime("%a")[:3]}</span></a>')
    upcoming = [e for e in evs if _d(e["end"]) >= today]
    past = [e for e in evs if _d(e["end"]) < today]
    h = ['<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">',
         '<title>Center17 events: the annual anchors</title>',
         '<meta name="description" content="The annual anchors Center17 plans around: the Zurich Computational Psychiatry Course, the SOBP Brainhack, OHBM, NeurIPS, Brainhack Global and Aaron Swartz Day. Subscribe as an iCalendar feed.">',
         f"<style>{RIVER_CSS}.row-desc{{display:block;font-size:.88rem;color:#888;margin-top:2px}}.row.past{{opacity:.45}}small{{font-family:var(--mono);font-size:.68rem;color:#999;letter-spacing:.06em}}</style></head><body>",
         NAV_HTML,
         '<div class="page"><header class="masthead"><div><h1>The <b>calendar</b></h1>',
         '<p class="lede">The annual anchors Center17 plans around. Dates marked expected are placeholders from each event\'s usual pattern and get replaced when announced.</p></div>',
         '<dl class="now"><dt>Subscribe</dt><dd><a href="events.ics">iCalendar feed</a> (Apple Calendar, Google Calendar, Thunderbird)</dd>'
         '<dt>Also</dt><dd><a href="./">The river</a> &middot; <a href="https://center17.org/blogroll/">The blogroll</a></dd>'
         f'<dt>Updated</dt><dd>{stamp}</dd></dl></header>']
    h.append('<div class="day"><span class="day-label">Upcoming</span><div class="rule"></div>' + "".join(row(e) for e in upcoming) + "</div>")
    if past:
        h.append('<div class="day"><span class="day-label">Past</span><div class="rule"></div>' + "".join(row(e) for e in reversed(past)) + "</div>")
    h.append('<footer><span>&copy; 2017&ndash;2026 Center17</span><nav><a href="https://center17.org/">Blog</a><a href="https://projects.center17.org/">Projects</a>'
             '<a href="https://center17.org/blogroll/">Blogroll</a><a href="events.ics">ICS</a></nav></footer></div></body></html>')
    (HERE / "events.html").write_text("\n".join(h) + "\n")
    print(f"== events: {len(evs)} total, {len(upcoming)} upcoming")
    return upcoming[:4]


NAV_HTML = ('<nav class="topnav"><div class="inner"><a class="brand" href="https://center17.org/">Center<b>17</b></a>'
            '<a href="https://center17.org/about/">About</a><a href="https://center17.org/data/">Data</a><a href="https://huggingface.co/mhough">Models</a>'
            '<a href="./">Blog</a><a href="https://www.wefunkradio.com/">WeFunk</a><a class="ext" href="events.html">Calendar</a></div></nav>')


def write_river(by_folder, stamp, max_items=120, max_per_feed=6):
    now = dt.datetime.now(dt.timezone.utc)
    upcoming = write_events(stamp)
    items = []
    for folder, rs in by_folder.items():
        for r in rs:
            if not r.get("ok"):
                continue
            for it in r.get("items", [])[:max_per_feed]:
                d = dt.datetime.fromisoformat(it["date"])
                if d > now + dt.timedelta(days=1):
                    continue  # future-dated junk
                items.append({"source": r["title"], "site": r["site"], "folder": folder, "title": it["title"] or it["link"], "link": it["link"], "date": d})
    items.sort(key=lambda x: x["date"], reverse=True)
    items = items[:max_items]

    # HTML
    h = ['<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">',
         '<title>Center17 river: the blogroll, newest first</title>',
         '<meta name="description" content="The newest items across the Center17 blogroll: computational psychiatry, neuroimaging, neuromodulation and the open web.">',
         '<link rel="alternate" type="application/rss+xml" title="Center17 river" href="river.xml">',
         f"<style>{RIVER_CSS}</style></head><body>",
         NAV_HTML,
         '<div class="page"><header class="masthead"><div><h1>The <b>river</b></h1>',
         '<p class="lede">The newest items from the Center17 blogroll, in one stream. Computational psychiatry, neuroimaging, neuromodulation and the open web.</p></div>',
         f'<dl class="now"><dt>Subscribe</dt><dd><a href="river.xml">River as RSS</a> &middot; <a href="blogroll.opml">Blogroll as OPML</a></dd>'
         f'<dt>Browse</dt><dd><a href="https://center17.org/blogroll/">The blogroll</a> &middot; <a href="https://github.com/m9h/center17-blogroll">Source</a></dd>'
         f'<dt>Updated</dt><dd>{now.strftime("%Y-%m-%d %H:%M")} UTC</dd></dl></header>']
    if upcoming:
        h.append('<div class="day"><span class="day-label">Upcoming</span><div class="rule"></div>' + "".join(
            f'<a class="row" href="{html.escape(e["url"])}"><span class="row-src">{html.escape(_when(e))}</span><span class="row-title">{html.escape(e["name"])}'
            f'{" <small>(expected)</small>" if e["status"]=="expected" else ""}</span><span class="row-time">{_d(e["start"]).strftime("%a")}</span></a>' for e in upcoming) + '<p class="empty"><a href="events.html">Full calendar</a> &middot; <a href="events.ics">subscribe (ICS)</a></p></div>')
    day = None
    for it in items:
        d = it["date"].astimezone(dt.timezone.utc).strftime("%Y-%m-%d")
        if d != day:
            if day is not None:
                h.append("</div>")
            h.append(f'<div class="day"><span class="day-label">{d}</span><div class="rule"></div>')
            day = d
        h.append(f'<a class="row" href="{html.escape(it["link"])}"><span class="row-src">{html.escape(it["source"])}</span>'
                 f'<span class="row-title">{html.escape(it["title"])}</span><span class="row-time">{it["date"].astimezone(dt.timezone.utc).strftime("%H:%M")}</span></a>')
    if day is not None:
        h.append("</div>")
    h.append('<footer><span>&copy; 2017&ndash;2026 Center17</span><nav><a href="https://center17.org/">Blog</a><a href="https://projects.center17.org/">Projects</a>'
             '<a href="https://center17.org/blogroll/">Blogroll</a><a href="river.xml">RSS</a></nav></footer></div></body></html>')
    (HERE / "index.html").write_text("\n".join(h) + "\n")

    # RSS 2.0
    def rfc(d):
        return d.astimezone(dt.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
    x = ['<?xml version="1.0" encoding="UTF-8"?>', '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:source="http://source.scripting.com/">', "<channel>",
         "<title>Center17 river</title>", "<link>https://projects.center17.org/center17-blogroll/</link>",
         "<description>The newest items across the Center17 blogroll: computational psychiatry, neuroimaging, neuromodulation and the open web.</description>",
         f"<lastBuildDate>{rfc(now)}</lastBuildDate>", '<atom:link href="https://projects.center17.org/center17-blogroll/river.xml" rel="self" type="application/rss+xml"/>']
    for it in items:
        x.append("<item>" + f"<title>{html.escape(it['title'])}</title><link>{html.escape(it['link'])}</link><guid isPermaLink=\"true\">{html.escape(it['link'])}</guid>"
                 f"<pubDate>{rfc(it['date'])}</pubDate><source url=\"{html.escape(it['site'])}\">{html.escape(it['source'])}</source><category>{html.escape(it['folder'])}</category></item>")
    x += ["</channel>", "</rss>", ""]
    (HERE / "river.xml").write_text("\n".join(x))
    print(f"== river: {len(items)} items, newest {items[0]['date'].isoformat() if items else '-'}")


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
    m += ["## Annual anchors", "", "Also as a calendar you can subscribe to: [`events.ics`](https://projects.center17.org/center17-blogroll/events.ics).", "", "| Event | When | Where |", "|---|---|---|"]
    m += [f"| [{e['name']}]({e['url']}) | {_when(e)}{' (expected)' if e['status']=='expected' else ''} | {e['city']} |" for e in EVENTS]
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
    h += [f'<li><a href="{html.escape(e["url"])}">{html.escape(e["name"])}</a>: {_when(e)}{" (expected)" if e["status"]=="expected" else ""}, {html.escape(e["city"])}</li>' for e in EVENTS]
    h.append("</ul><h2>Suicide prevention</h2><p>Kept alongside Aaron Swartz Day. If you are in crisis, use the first line that applies to where you are.</p><ul>")
    h += [f'<li><a href="{html.escape(u)}">{html.escape(n)}</a>{(": " + html.escape(note)) if note else ""}</li>' for n, u, note in SUICIDE_PREVENTION]
    h.append("</ul>")
    (HERE / "ghost-page.html").write_text("\n".join(h) + "\n")

    # ---- River: newest items across the blogroll (index.html for GitHub Pages, river.xml as RSS)
    write_river(by_folder, stamp)

    # ---- report
    for folder, rs in by_folder.items():
        print(f"== {folder}: {sum(r['ok'] for r in rs)}/{len(rs)} live")
        for r in rs:
            flag = "ok  " if r["ok"] else "DEAD"
            extra = (r.get("latest") or "")[:10] if r["ok"] else r.get("error", "")
            print(f"   {flag} {r['title'][:42]:42} {extra}")


if __name__ == "__main__":
    main()
