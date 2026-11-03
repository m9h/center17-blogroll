"""Candidate feeds for the Center17 blogroll, grouped by folder.

Each entry: (title, feed_url, site_url, note). `build.py` fetches every feed,
drops the ones that don't parse as RSS/Atom, and writes blogroll.opml, README.md
and ghost-page.html from the survivors. Edit this file, not the outputs.
"""

FOLDERS = {
    "Computational psychiatry": [
        ("arXiv q-bio.NC (Neurons and Cognition)", "https://rss.arxiv.org/rss/q-bio.NC", "https://arxiv.org/list/q-bio.NC/recent", "daily preprints"),
        ("The Transmitter", "https://www.thetransmitter.org/feed/", "https://www.thetransmitter.org/", "Simons Foundation neuroscience news"),
        ("Neuromatch", "https://neuromatch.io/feed/", "https://neuromatch.io/", ""),
        ("Brain Inspired (podcast)", "https://braininspired.co/feed/", "https://braininspired.co/", "Paul Middlebrooks"),
        ("Nature Mental Health", "https://www.nature.com/natmentalhealth.rss", "https://www.nature.com/natmentalhealth/", ""),
        ("Translational Psychiatry", "https://www.nature.com/tp.rss", "https://www.nature.com/tp/", ""),
        ("Molecular Psychiatry", "https://www.nature.com/mp.rss", "https://www.nature.com/mp/", ""),
        ("Biological Psychiatry (SOBP)", "https://www.biologicalpsychiatryjournal.com/current.rss", "https://www.biologicalpsychiatryjournal.com/", "SOBP's journal"),
        ("Biological Psychiatry: CNNI", "https://www.biologicalpsychiatrycnni.org/current.rss", "https://www.biologicalpsychiatrycnni.org/", "Cognitive Neuroscience and Neuroimaging"),
        ("PLOS Computational Biology", "https://journals.plos.org/ploscompbiol/feed/atom", "https://journals.plos.org/ploscompbiol/", ""),
        ("eLife: Neuroscience", "https://elifesciences.org/rss/subject/neuroscience.xml", "https://elifesciences.org/subjects/neuroscience", ""),
    ],
    "Neuroimaging": [
        ("OHBM blog", "https://www.ohbmbrainmappingblog.com/blog/feed", "https://www.ohbmbrainmappingblog.com/", ""),
        ("NeuroStars (latest)", "https://neurostars.org/latest.rss", "https://neurostars.org/", "Q&A forum"),
        ("Brainder (Anderson Winkler)", "https://brainder.org/feed/", "https://brainder.org/", ""),
        ("practiCal fMRI", "https://practicalfmri.blogspot.com/feeds/posts/default", "https://practicalfmri.blogspot.com/", ""),
        ("MNE-Python releases", "https://github.com/mne-tools/mne-python/releases.atom", "https://mne.tools/", ""),
        ("nilearn releases", "https://github.com/nilearn/nilearn/releases.atom", "https://nilearn.github.io/", ""),
        ("FreeSurfer releases", "https://github.com/freesurfer/freesurfer/releases.atom", "https://surfer.nmr.mgh.harvard.edu/", ""),
        ("OpenNeuro (GitHub releases)", "https://github.com/OpenNeuroOrg/openneuro/releases.atom", "https://openneuro.org/", ""),
        ("NeuroImage", "https://rss.sciencedirect.com/publication/science/10538119", "https://www.sciencedirect.com/journal/neuroimage", ""),
        ("Brainhack", "https://brainhack.org/feed.xml", "https://brainhack.org/", ""),
        ("DANDI (GitHub releases)", "https://github.com/dandi/dandi-cli/releases.atom", "https://dandiarchive.org/", "neurophysiology data archive"),
    ],
    "Neuromodulation": [
        ("Brain Stimulation (journal)", "https://rss.sciencedirect.com/publication/science/1935861X", "https://www.brainstimjrnl.com/", ""),
        ("Neuromodulation (INS journal)", "https://rss.sciencedirect.com/publication/science/10947159", "https://www.neuromodulationjournal.org/", ""),
        ("Journal of Neural Engineering", "https://iopscience.iop.org/journal/rss/1741-2552", "https://iopscience.iop.org/journal/1741-2552", ""),
        ("SimNIBS releases", "https://github.com/simnibs/simnibs/releases.atom", "https://simnibs.github.io/simnibs/", ""),
        ("TI-Toolbox releases", "https://github.com/idossha/TI-Toolbox/releases.atom", "https://github.com/idossha/TI-Toolbox", "temporal interference"),
        ("OpenBCI blog", "https://openbci.com/community/feed/", "https://openbci.com/community/", ""),
        ("NeuroTechX (Medium)", "https://medium.com/feed/neurotechx", "https://neurotechx.com/", ""),
        ("IEEE Brain", "https://brain.ieee.org/feed/", "https://brain.ieee.org/", ""),
    ],
    "Open web and tools": [
        ("Center17", "https://center17.org/rss/", "https://center17.org/", "this blog"),
        ("Scripting News (Dave Winer)", "http://scripting.com/rss.xml", "http://scripting.com/", "RSS, OPML, textcasting"),
        ("rss.chat worknotes", "https://news.rss.chat/worknotes/rss.xml", "https://rss.chat/", ""),
        ("Ghost changelog", "https://ghost.org/changelog/rss/", "https://ghost.org/changelog/", ""),
        ("JAX releases", "https://github.com/jax-ml/jax/releases.atom", "https://jax.readthedocs.io/", ""),
        ("Equinox releases", "https://github.com/patrick-kidger/equinox/releases.atom", "https://docs.kidger.site/equinox/", "Kidger stack"),
        ("Diffrax releases", "https://github.com/patrick-kidger/diffrax/releases.atom", "https://docs.kidger.site/diffrax/", "Kidger stack"),
        ("NeuroFedora blog", "https://neuroblog.fedoraproject.org/feeds/all.atom.xml", "https://neuro.fedoraproject.org/", ""),
    ],
}

# Dated anchors, not feeds. (name, url, when, note)
EVENTS = [
    ("Computational Psychiatry Course, Zurich (TNU, ETH/UZH)", "https://www.translationalneuromodeling.org/cpcourse/", "annually in early September; 2026: 7–12 Sept, hybrid", "the starting block"),
    ("SOBP Annual Meeting and Brainhack", "https://sobp.org/", "annually late April / early May; 2026: 30 Apr–2 May, New York", "Society of Biological Psychiatry"),
    ("Aaron Swartz Day", "https://www.aaronswartzday.org/", "annually around 8 November, Internet Archive, San Francisco", "open access, open data; see the suicide-prevention resources below"),
    ("OHBM Annual Meeting", "https://www.humanbrainmapping.org/", "annually in June", ""),
    ("Brainhack Global", "https://brainhack.org/global.html", "annually in December", ""),
]

# Suicide prevention resources (kept with Aaron Swartz Day). (name, url, note)
SUICIDE_PREVENTION = [
    ("988 Suicide & Crisis Lifeline (US)", "https://988lifeline.org/", "call or text 988"),
    ("Crisis Text Line", "https://www.crisistextline.org/", "text HOME to 741741 (US)"),
    ("International Association for Suicide Prevention: crisis centres by country", "https://www.iasp.info/suicidalthoughts/", ""),
    ("Samaritans (UK and Ireland)", "https://www.samaritans.org/", "116 123"),
    ("American Foundation for Suicide Prevention", "https://afsp.org/", "research funding and resources"),
    ("Zero Suicide (Education Development Center)", "https://zerosuicide.edc.org/", "health-system framework"),
]
