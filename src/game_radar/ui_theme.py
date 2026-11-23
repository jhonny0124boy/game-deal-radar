"""Global Design System (Premium Light Gaming Deals Platform) for Game Deal Radar."""

from html import escape

DESIGN_SYSTEM_CSS = """
<style>
:root {
    --bg-page: #F7F8FA;
    --bg-card: #FFFFFF;
    --bg-muted: #F0F2F6;
    --text-primary: #172033;
    --text-secondary: #7B8494;
    --brand-primary: #3157A4;
    --brand-hover: #254785;
    --discount-green: #16A36A;
    --discount-bg: #E8F7EF;
    --border-color: #E5E8EF;
    --danger: #E05252;
    --radius-card: 12px;
    --radius-btn: 8px;
    --shadow-sm: 0 1px 3px rgba(23, 32, 51, 0.05);
    --shadow-hover: 0 8px 20px rgba(23, 32, 51, 0.08);
}

/* Global Page Surface */
.stApp {
    background-color: var(--bg-page);
    color: var(--text-primary);
}
.block-container {
    padding-top: 3.75rem !important;
    padding-bottom: 2.5rem !important;
    padding-left: 2.25rem !important;
    padding-right: 2.25rem !important;
    max-width: 1440px;
}

/* Left Sidebar Navigation (Light Storefront Style) */
[data-testid="stSidebar"] {
    background-color: var(--bg-card) !important;
    border-right: 1px solid var(--border-color) !important;
}
[data-testid="stSidebarHeader"] {
    padding-top: 0.5rem !important;
    padding-bottom: 0.25rem !important;
    height: auto !important;
}
[data-testid="stSidebarUserContent"] {
    padding-top: 0.25rem !important;
}
[data-testid="stSidebar"] .stRadio > div {
    gap: 0.3rem;
}
[data-testid="stSidebar"] .stRadio label {
    background: transparent;
    border-radius: 8px;
    padding: 0.55rem 0.75rem;
    margin: 0 !important;
    font-weight: 600;
    color: var(--text-secondary);
    transition: all 0.16s ease;
    cursor: pointer;
}
[data-testid="stSidebar"] .stRadio label:hover {
    background: var(--bg-muted);
    color: var(--text-primary);
}
[data-testid="stSidebar"] .stRadio label:has(input:checked) {
    background: #EEF3FC !important;
    color: var(--brand-primary) !important;
    font-weight: 700 !important;
}
[data-testid="stSidebar"] .stRadio label > div:first-child {
    display: none;
}
.gdr-sidebar-label {
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    color: var(--text-secondary);
    text-transform: uppercase;
    margin: 1rem 0 0.4rem 0.2rem;
}

/* Brand Header */
.gdr-header {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 14px;
    padding: 1.15rem 1.5rem;
    box-shadow: var(--shadow-sm);
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    margin-bottom: 0.75rem;
}
.gdr-brand {
    display: flex;
    align-items: center;
    gap: 0.85rem;
}
.gdr-logo {
    width: 42px;
    height: 42px;
    border-radius: 10px;
    background: var(--brand-primary);
    color: #FFFFFF;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.25rem;
    font-weight: 800;
    flex-shrink: 0;
}
.gdr-title {
    font-size: 1.45rem;
    font-weight: 800;
    color: var(--text-primary);
    letter-spacing: -0.02em;
    line-height: 1.2;
}
.gdr-subtitle {
    font-size: 0.86rem;
    color: var(--text-secondary);
    margin-top: 2px;
}
.gdr-fx-pill {
    background: var(--bg-muted);
    color: var(--text-secondary);
    border: 1px solid var(--border-color);
    border-radius: 999px;
    padding: 4px 12px;
    font-size: 0.8rem;
    font-weight: 600;
    white-space: nowrap;
}

/* Navigation Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 0.45rem;
    flex-wrap: wrap;
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 0.35rem;
    margin-bottom: 1.25rem;
    box-shadow: var(--shadow-sm);
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important;
    padding: 0.5rem 1rem !important;
    font-weight: 600 !important;
    color: var(--text-secondary) !important;
    background: transparent !important;
    border: none !important;
    transition: all 0.18s ease;
}
.stTabs [data-baseweb="tab"] p {
    color: inherit !important;
    font-weight: 600 !important;
}
.stTabs [data-baseweb="tab"]:hover {
    color: var(--text-primary) !important;
    background: var(--bg-muted) !important;
}
.stTabs [data-baseweb="tab"][aria-selected="true"] {
    color: #FFFFFF !important;
    background: var(--brand-primary) !important;
}
.stTabs [data-baseweb="tab"][aria-selected="true"] p {
    color: #FFFFFF !important;
}
.stTabs [data-baseweb="tab-highlight"] {
    display: none !important;
}

/* Section Headers */
.gdr-section-head {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    margin: 0.5rem 0 0.85rem 0;
    padding-bottom: 0.45rem;
    border-bottom: 1px solid var(--border-color);
}
.gdr-section-title {
    font-size: 1.18rem;
    font-weight: 700;
    color: var(--text-primary);
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.gdr-count-badge {
    background: var(--bg-muted);
    color: var(--brand-primary);
    font-size: 0.78rem;
    font-weight: 700;
    padding: 2px 9px;
    border-radius: 999px;
}
.gdr-epic-badge {
    background: #172033;
    color: #FFFFFF;
    font-size: 0.72rem;
    font-weight: 700;
    padding: 2px 8px;
    border-radius: 6px;
    letter-spacing: 0.04em;
}
.gdr-special-badge {
    background: var(--discount-bg);
    color: var(--discount-green);
    font-size: 0.74rem;
    font-weight: 700;
    padding: 2px 9px;
    border-radius: 999px;
}

/* Unified Game Card Containers ONLY (scoped inside stColumn so root page never matches) */
[data-testid="stColumn"] [data-testid="stVerticalBlockBorderWrapper"]:has(.gdr-cover-wrap) {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: var(--radius-card) !important;
    box-shadow: var(--shadow-sm) !important;
    transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease !important;
}
[data-testid="stColumn"] [data-testid="stVerticalBlockBorderWrapper"]:has(.gdr-cover-wrap):hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-hover) !important;
    border-color: #CBD5E1 !important;
}

/* Cover Image Aspect Ratio Lock */
.gdr-cover-wrap {
    width: 100%;
    aspect-ratio: 16 / 9;
    border-radius: 8px;
    overflow: hidden;
    background: var(--bg-muted);
    margin-bottom: 0.55rem;
    border: 1px solid var(--border-color);
}
.gdr-cover-wrap img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
}

/* Game Title (2-line clamp for uniform card height) */
.gdr-game-title {
    font-size: 0.94rem;
    font-weight: 700;
    color: var(--text-primary);
    line-height: 1.35;
    height: 2.55rem;
    overflow: hidden;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    margin-bottom: 0.4rem;
}

/* Price Hierarchy */
.gdr-price-row {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 0.35rem;
    min-height: 2.35rem;
    align-content: flex-start;
    margin-bottom: 0.2rem;
}
.gdr-price-current {
    font-size: 1.05rem;
    font-weight: 800;
    color: var(--text-primary);
}
.gdr-price-sale {
    font-size: 1.05rem;
    font-weight: 800;
    color: var(--discount-green);
}
.gdr-discount-badge {
    background: var(--discount-bg);
    color: var(--discount-green);
    font-size: 0.78rem;
    font-weight: 800;
    padding: 2px 7px;
    border-radius: 6px;
}
.gdr-price-orig {
    font-size: 0.78rem;
    color: var(--text-secondary);
    text-decoration: line-through;
}
.gdr-meta-line {
    font-size: 0.78rem;
    color: var(--text-secondary);
    min-height: 1.2rem;
    margin-bottom: 0.45rem;
}
.gdr-hist-low-pill {
    background: #FFF4ED;
    color: #C2410C;
    font-weight: 700;
    padding: 1px 6px;
    border-radius: 4px;
    font-size: 0.72rem;
    margin-left: 4px;
}
.gdr-free-pill {
    background: var(--discount-bg);
    color: var(--discount-green);
    font-weight: 800;
    font-size: 0.76rem;
    padding: 2px 8px;
    border-radius: 6px;
    display: inline-block;
    margin-bottom: 0.35rem;
}
.gdr-upcoming-pill {
    background: var(--bg-muted);
    color: var(--text-secondary);
    font-weight: 700;
    font-size: 0.76rem;
    padding: 2px 8px;
    border-radius: 6px;
    display: inline-block;
    margin-bottom: 0.35rem;
}

/* Unified Inputs & Buttons */
.stTextInput input {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: var(--radius-btn) !important;
    color: var(--text-primary) !important;
    height: 42px !important;
}
.stTextInput input::placeholder {
    color: #94A3B8 !important;
    opacity: 1 !important;
}
.stTextInput input:focus {
    border-color: var(--brand-primary) !important;
    box-shadow: 0 0 0 2px rgba(49, 87, 164, 0.15) !important;
}
.stButton button, .stLinkButton a {
    border-radius: var(--radius-btn) !important;
    font-weight: 600 !important;
    min-height: 40px !important;
    white-space: nowrap !important;
    padding-left: 0.65rem !important;
    padding-right: 0.65rem !important;
    transition: all 0.16s ease !important;
}
.stButton button[kind="primary"], .stLinkButton a[kind="primary"] {
    background-color: var(--brand-primary) !important;
    border-color: var(--brand-primary) !important;
    color: #FFFFFF !important;
}
.stButton button[kind="primary"]:hover, .stLinkButton a[kind="primary"]:hover {
    background-color: var(--brand-hover) !important;
    border-color: var(--brand-hover) !important;
}
.stButton button[kind="secondary"], .stLinkButton a[kind="secondary"] {
    background-color: var(--bg-card) !important;
    border: 1px solid var(--border-color) !important;
    color: var(--text-primary) !important;
}
.stButton button[kind="secondary"]:hover, .stLinkButton a[kind="secondary"]:hover {
    background-color: var(--bg-muted) !important;
    border-color: #CBD5E1 !important;
}

/* Footer */
.gdr-footer {
    margin-top: 2.5rem;
    padding-top: 1rem;
    border-top: 1px solid var(--border-color);
    color: var(--text-secondary);
    font-size: 0.8rem;
    display: flex;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 0.5rem;
}

/* Responsive Breakpoints */
@media (max-width: 1120px) {
    .gdr-header {
        flex-direction: column;
        align-items: flex-start;
    }
    [data-testid="stHorizontalBlock"] {
        flex-wrap: wrap !important;
    }
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
        min-width: 220px !important;
        flex: 1 1 220px !important;
    }
}
@media (max-width: 768px) {
    .block-container {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
    .gdr-title {
        font-size: 1.25rem;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 0.45rem 0.7rem !important;
        font-size: 0.86rem !important;
    }
}
</style>
"""


def render_cover(image_url: str | None, alt_text: str) -> str:
    safe_alt = escape(alt_text)
    if image_url:
        return f'<div class="gdr-cover-wrap"><img src="{escape(image_url)}" alt="{safe_alt}" loading="lazy" /></div>'
    return '<div class="gdr-cover-wrap"></div>'


def render_section_header(title: str, count: int | None = None, badge_html: str = "") -> str:
    count_html = f'<span class="gdr-count-badge">{count} 款</span>' if count is not None else ""
    return (
        f'<div class="gdr-section-head">'
        f'<div class="gdr-section-title">{escape(title)} {count_html} {badge_html}</div>'
        f'</div>'
    )
