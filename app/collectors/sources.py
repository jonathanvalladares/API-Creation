"""
Canonical list of SSBCI news sources.
Each entry describes one feed or scrape target consumed by a collector.
"""

RSS_SOURCES = [
    {
        "name": "Google News – SSBCI",
        "category": "media",
        "description": "Google News aggregated results for 'SSBCI State Small Business Credit Initiative'",
        "url": "https://news.google.com/rss/search?q=%22SSBCI%22+%22State+Small+Business+Credit+Initiative%22&hl=en-US&gl=US&ceid=US:en",
    },
    {
        "name": "Google News – Treasury SSBCI",
        "category": "media",
        "description": "Google News aggregated results for 'Treasury SSBCI'",
        "url": "https://news.google.com/rss/search?q=%22Treasury%22+%22SSBCI%22&hl=en-US&gl=US&ceid=US:en",
    },
    {
        "name": "Federal Register – SSBCI",
        "category": "federal",
        "description": "Federal Register notices and rules mentioning SSBCI",
        "url": "https://www.federalregister.gov/api/v1/articles.rss?conditions%5Bterm%5D=SSBCI",
    },
    {
        "name": "Treasury Press Releases",
        "category": "federal",
        "description": "U.S. Treasury Department press releases RSS feed",
        "url": "https://home.treasury.gov/news/press-releases/rss.xml",
    },
    {
        "name": "SBA News RSS",
        "category": "federal",
        "description": "U.S. Small Business Administration news feed",
        "url": "https://www.sba.gov/rss.xml",
    },
    {
        "name": "GovInfo – SSBCI",
        "category": "federal",
        "description": "GovInfo Federal Register results for SSBCI",
        "url": "https://www.govinfo.gov/rss/fr.xml",
    },
]

# Sources that require custom HTML scraping (no RSS)
SCRAPE_SOURCES = [
    {
        "name": "Treasury SSBCI – Main Page",
        "category": "federal",
        "description": "Official U.S. Treasury SSBCI program page",
        "url": "https://home.treasury.gov/policy-issues/small-business-programs/state-small-business-credit-initiative-ssbci",
    },
    {
        "name": "Treasury SSBCI – Resources",
        "category": "federal",
        "description": "SSBCI 2.0 program resources, guidance, and policy documents",
        "url": "https://home.treasury.gov/policy-issues/small-business-programs/state-small-business-credit-initiative-ssbci/ssbci-2-resources",
    },
    {
        "name": "Treasury SSBCI – Capital Program Contacts",
        "category": "federal",
        "description": "List of SSBCI state capital programs and contact information",
        "url": "https://home.treasury.gov/policy-issues/small-business-programs/state-small-business-credit-initiative-ssbci/capital-program-list-of-programs-and-contacts",
    },
    {
        "name": "Treasury SSBCI – Program Reports",
        "category": "federal",
        "description": "SSBCI 2.0 quarterly and annual program reports",
        "url": "https://home.treasury.gov/policy-issues/small-business-programs/state-small-business-credit-initiative-ssbci/ssbci-2-program-reports",
    },
]

# Known static documents — inserted directly on every collection run
STATIC_ARTICLES = [
    {
        "title": "SSBCI Fact Sheet",
        "url": "https://home.treasury.gov/system/files/256/State-Small-Business-Credit-Initiative-SSBCI-Fact-Sheet.pdf",
        "source": "Treasury SSBCI – Main Page",
        "source_category": "federal",
        "summary": "Official U.S. Treasury fact sheet for the State Small Business Credit Initiative (SSBCI), covering program overview, eligibility, and funding details.",
        "tags": "ssbci,state small business credit initiative,treasury ssbci",
    },
    {
        "title": "SSBCI Quarterly Report – January 2022",
        "url": "https://home.treasury.gov/system/files/256/SSBCI-QuarterlyReport-January22.pdf",
        "source": "Treasury SSBCI – Program Reports",
        "source_category": "federal",
        "summary": "SSBCI quarterly progress report for the period ending January 2022, covering capital deployment, program participation, and state-level activity.",
        "tags": "ssbci,state small business credit initiative,treasury ssbci",
    },
    {
        "title": "SSBCI Quarterly Report – September 2022",
        "url": "https://home.treasury.gov/system/files/256/SSBCI-QuarterlyReport-September12.pdf",
        "source": "Treasury SSBCI – Program Reports",
        "source_category": "federal",
        "summary": "SSBCI quarterly progress report for the period ending September 2022.",
        "tags": "ssbci,state small business credit initiative,treasury ssbci",
    },
    {
        "title": "SSBCI Quarterly Report – June 2023",
        "url": "https://home.treasury.gov/system/files/256/SSBCI-QuarterlyReport-June10.pdf",
        "source": "Treasury SSBCI – Program Reports",
        "source_category": "federal",
        "summary": "SSBCI quarterly progress report for the period ending June 2023.",
        "tags": "ssbci,state small business credit initiative,treasury ssbci",
    },
    {
        "title": "SSBCI Quarterly Report – March 2024",
        "url": "https://home.treasury.gov/system/files/256/SSBCI-QuarterlyReport-March-27.pdf",
        "source": "Treasury SSBCI – Program Reports",
        "source_category": "federal",
        "summary": "SSBCI quarterly progress report for the period ending March 2024.",
        "tags": "ssbci,state small business credit initiative,treasury ssbci",
    },
]

SSBCI_KEYWORDS = [
    "ssbci",
    "state small business credit initiative",
    "treasury ssbci",
    "small business credit",
]
