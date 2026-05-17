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
        "name": "Treasury SSBCI Official Page",
        "category": "federal",
        "description": "Official U.S. Treasury SSBCI program page – news & announcements section",
        "url": "https://home.treasury.gov/policy-issues/small-business-programs/state-small-business-credit-initiative-ssbci",
    },
]

SSBCI_KEYWORDS = [
    "ssbci",
    "state small business credit initiative",
    "treasury ssbci",
    "small business credit",
]
