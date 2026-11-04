"""Annual anchors for the Center17 calendar.

Each entry is a dict. Dates are ISO strings; `end` is inclusive. `status` is
"announced" (dates published by the organiser) or "expected" (placeholder from
the event's usual pattern, to be replaced when announced). build.py turns this
into events.ics, events.html and the Upcoming block on the river.
"""

EVENTS = [
    # ---- 2026
    dict(slug="aaron-swartz-day-2026", name="Aaron Swartz Day and International Hackathon",
         start="2026-11-08", end="2026-11-08", city="Internet Archive, San Francisco, and satellite hackathons",
         url="https://www.aaronswartzday.org/", status="announced",
         note="10am to 5pm Pacific. Open access, open data, SecureDrop; see the suicide-prevention resources on the blogroll."),
    dict(slug="neurips-2026", name="NeurIPS 2026",
         start="2026-12-06", end="2026-12-12", city="Sydney, with official satellites in Atlanta (8 to 13 Dec) and Paris (9 to 13 Dec)",
         url="https://neurips.cc/Conferences/2026", status="announced",
         note="Tutorials 7 Dec, main sessions 8 to 10 Dec, workshops 11 to 12 Dec."),
    dict(slug="brainhack-global-2026", name="Brainhack Global 2026 (local hubs)",
         start="2026-11-16", end="2026-12-18", city="Hybrid hubs worldwide",
         url="https://brainhack.org/global.html", status="expected",
         note="Brainhack Global runs as local events from late autumn into spring; the 2025 edition ran autumn 2025 to spring 2026. Dates per hub on brainhack.org."),
    # ---- 2027
    dict(slug="sobp-2027", name="SOBP Annual Meeting and Brainhack",
         start="2027-05-06", end="2027-05-08", city="Chicago, Illinois",
         url="https://sobp.org/sobp-annual-meeting/", status="announced",
         note="Society of Biological Psychiatry. The Brainhack usually sits alongside the meeting."),
    dict(slug="ohbm-2027", name="OHBM 2027 Annual Meeting",
         start="2027-06-26", end="2027-06-30", city="Metro Toronto Convention Centre, Toronto",
         url="https://humanbrainmapping.org/ohbm-2027/", status="announced",
         note="Organization for Human Brain Mapping. Registration opens January 2027."),
    dict(slug="cpc-zurich-2027", name="Computational Psychiatry Course, Zurich (TNU)",
         start="2027-09-06", end="2027-09-11", city="Zurich and online",
         url="https://www.translationalneuromodeling.org/cpcourse/", status="expected",
         note="The starting block. Held the first or second week of September; 2026 was 7 to 12 September. Dates are usually announced in February."),
    dict(slug="aaron-swartz-day-2027", name="Aaron Swartz Day and International Hackathon",
         start="2027-11-06", end="2027-11-07", city="Internet Archive, San Francisco, and satellite hackathons",
         url="https://www.aaronswartzday.org/", status="expected",
         note="Held on the weekend nearest 8 November."),
    # ---- 2028 and 2029 (announced far ahead)
    dict(slug="sobp-2028", name="SOBP Annual Meeting", start="2028-04-20", end="2028-04-22",
         city="San Francisco Marriott Marquis, San Francisco", url="https://sobp.org/sobp-annual-meeting/", status="announced", note=""),
    dict(slug="ohbm-2028", name="OHBM 2028 Annual Meeting", start="2028-06-18", end="2028-06-22",
         city="Yokohama", url="https://humanbrainmapping.org/FutureMeetings/", status="announced", note=""),
    dict(slug="sobp-2029", name="SOBP Annual Meeting", start="2029-04-19", end="2029-04-21",
         city="Boston Marriott Copley Place, Boston", url="https://sobp.org/sobp-annual-meeting/", status="announced", note=""),
]
