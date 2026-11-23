"""Reusable original SVG Logo component (Radar Pulse Monogram) for Game Deal Radar."""

from typing import Literal


def get_logo_icon_svg(size: int = 40) -> str:
    """Return scalable inline SVG for the Icon Only variant."""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" '
        f'width="{size}" height="{size}" fill="none" role="img" aria-label="Game Deal Radar Logo">'
        f'<rect x="1" y="1" width="46" height="46" rx="12" fill="#EEF3FC" stroke="#DCE5F7" stroke-width="1.5"/>'
        f'<path d="M 31 12.2 A 14 14 0 1 0 38 24 H 25.5" '
        f'stroke="#3157A4" stroke-width="4.2" stroke-linecap="round" stroke-linejoin="round"/>'
        f'<path d="M 24 16.5 A 7.5 7.5 0 0 0 16.5 24" '
        f'stroke="#3157A4" stroke-opacity="0.32" stroke-width="2.6" stroke-linecap="round"/>'
        f'<circle cx="35.5" cy="12.5" r="4" fill="#16A36A"/>'
        f"</svg>"
    )


def render_brand_logo(
    variant: Literal["full", "icon"] = "full",
    size: int = 42,
    subtitle: str = "遊戲特價與限免情報",
) -> str:
    """Render reusable Brand Logo HTML (Icon Only or Icon + Wordmark)."""
    icon_svg = get_logo_icon_svg(size=size)
    if variant == "icon":
        return f'<div style="display:inline-flex;align-items:center;">{icon_svg}</div>'

    return (
        f'<div class="gdr-brand" style="margin-bottom: 1rem;">'
        f'  <div style="flex-shrink:0;line-height:0;">{icon_svg}</div>'
        f"  <div>"
        f'    <div class="gdr-title" style="font-size: 1.18rem;">Game Deal Radar</div>'
        f'    <div class="gdr-subtitle" style="font-size: 0.78rem;">{subtitle}</div>'
        f"  </div>"
        f"</div>"
    )
