"""
Constants used by the feature_engineering module.
"""

# ------------------------------------------------------------------ #
# Experience gap thresholds (years)
# ------------------------------------------------------------------ #

#: Minimum experience gap for a match to be meaningful.
MIN_EXPERIENCE_GAP_YEARS: int = 2

#: Gap at which the experience score peaks at 1.0.
OPTIMAL_EXPERIENCE_GAP_YEARS: int = 7

# ------------------------------------------------------------------ #
# Timezone compatibility
# ------------------------------------------------------------------ #

#: Absolute UTC-offset difference (hours) beyond which availability
#: is considered incompatible.
MAX_COMPATIBLE_TZ_DIFF_HOURS: int = 6

#: Mapping of common timezone abbreviations to UTC offset in hours.
TIMEZONE_UTC_OFFSETS: dict[str, int] = {
    # UTC
    "UTC": 0,
    "GMT": 0,
    # Americas
    "NST": -3,
    "AST": -4,
    "ADT": -3,
    "EST": -5,
    "EDT": -4,
    "CST": -6,
    "CDT": -5,
    "MST": -7,
    "MDT": -6,
    "PST": -8,
    "PDT": -7,
    "AKST": -9,
    "AKDT": -8,
    "HST": -10,
    # Europe
    "WET": 0,
    "CET": 1,
    "CEST": 2,
    "EET": 2,
    "EEST": 3,
    "MSK": 3,
    # Asia / Pacific
    "IST": 5,
    "PKT": 5,
    "BST_ASIA": 6,
    "ICT": 7,
    "WIB": 7,
    "CST_CN": 8,
    "HKT": 8,
    "SGT": 8,
    "MYT": 8,
    "JST": 9,
    "KST": 9,
    "AEST": 10,
    "AEDT": 11,
    "NZST": 12,
    "NZDT": 13,
    # Common IANA short-form aliases people type in profiles
    "ET": -5,
    "CT": -6,
    "MT": -7,
    "PT": -8,
}

# ------------------------------------------------------------------ #
# Industry groups
# ------------------------------------------------------------------ #

#: Clusters of closely related industries.  A mentor and mentee in
#: the same group score 0.5 (partial industry match).
INDUSTRY_GROUPS: dict[str, list[str]] = {
    "technology": [
        "technology", "tech", "software", "it", "information technology",
        "saas", "cloud", "cybersecurity", "devops", "data", "ai",
        "artificial intelligence", "machine learning", "ml",
    ],
    "finance": [
        "finance", "financial services", "banking", "investment",
        "fintech", "insurance", "accounting", "audit",
    ],
    "healthcare": [
        "healthcare", "health", "medical", "biotech", "biotechnology",
        "pharma", "pharmaceutical", "life sciences", "clinical",
    ],
    "media_entertainment": [
        "media", "entertainment", "gaming", "publishing", "advertising",
        "marketing", "creative", "design",
    ],
    "education": [
        "education", "edtech", "e-learning", "academia", "research",
        "university", "training",
    ],
    "retail_ecommerce": [
        "retail", "e-commerce", "ecommerce", "consumer goods",
        "fmcg", "fashion",
    ],
    "consulting_professional": [
        "consulting", "professional services", "management consulting",
        "strategy", "hr", "human resources", "legal",
    ],
    "energy": [
        "energy", "oil and gas", "utilities", "renewable energy",
        "cleantech", "sustainability",
    ],
    "manufacturing": [
        "manufacturing", "automotive", "aerospace", "industrial",
        "engineering", "supply chain", "logistics",
    ],
    "real_estate": [
        "real estate", "construction", "property", "architecture",
    ],
    "non_profit": [
        "non-profit", "nonprofit", "ngo", "government", "public sector",
        "social impact",
    ],
}

