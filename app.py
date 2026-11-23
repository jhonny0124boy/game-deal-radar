"""Game Deal Radar — Premium Light Gaming Deals Platform with Left Sidebar Navigation."""

from datetime import datetime, timedelta, timezone
from html import escape
from pathlib import Path

import pandas as pd
import streamlit as st

from src.game_radar.fetchers import fetch_steam_charts, fetch_usd_to_twd_rate
from src.game_radar.logo import render_brand_logo
from src.game_radar.pipeline import load_watchlist, run_sync, save_watchlist
from src.game_radar.schemas import WatchlistItem
from src.game_radar.storage import DealRepository
from src.game_radar.ui_theme import DESIGN_SYSTEM_CSS, render_cover, render_section_header

WATCHLIST_PATH = Path("watchlist.json")
DB_PATH = Path("data/game_radar.duckdb")
FAVICON_PATH = Path("assets/favicon.svg")

st.set_page_config(
    page_title="Game Deal Radar",
    page_icon=str(FAVICON_PATH) if FAVICON_PATH.exists() else "🎮",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(DESIGN_SYSTEM_CSS, unsafe_allow_html=True)


@st.cache_data(ttl=3600)
def get_fx_rate() -> float:
    return fetch_usd_to_twd_rate()


@st.cache_data(ttl=1800)
def get_steam_charts() -> dict:
    return fetch_steam_charts(limit=30)


def to_twd(usd: float, rate: float) -> int:
    return round(usd * rate)


fx_rate = get_fx_rate()

# ==========================================
# Left Sidebar Navigation (Steam-inspired Light Storefront)
# ==========================================
with st.sidebar:
    st.markdown(render_brand_logo(variant="full", size=42), unsafe_allow_html=True)

    if st.button("同步最新資料", type="primary", use_container_width=True):
        with st.spinner("正在同步 Steam 與 Epic 最新資料..."):
            try:
                summary = run_sync(WATCHLIST_PATH, DB_PATH)
                st.cache_data.clear()
                st.session_state["toast_msg"] = (
                    f"同步完成！Steam 價格 {summary['deals_saved']} 筆、Epic 限免 {summary['epic_free_saved']} 筆"
                )
                st.rerun()
            except Exception as exc:
                st.error(f"同步失敗：{exc}")

    st.markdown('<div class="gdr-sidebar-label">NAVIGATION</div>', unsafe_allow_html=True)

    NAV_OPTIONS = [
        "📦 Steam 追蹤清單",
        "🎁 Epic 每週限免",
        "🏆 Steam 台灣熱門榜",
        "💸 Steam 官方精選特價",
        "⚙️ 編輯追蹤清單",
    ]
    active_page = st.radio(
        "功能導覽",
        options=NAV_OPTIONS,
        label_visibility="collapsed",
        key="nav_page",
    )

if "toast_msg" in st.session_state:
    st.toast(st.session_state.pop("toast_msg"), icon="✅")

# Auto-sync on first visit or when data is older than 6 hours
AUTO_SYNC_INTERVAL = timedelta(hours=6)
_check_repo = DealRepository(DB_PATH)
try:
    _last_sync = _check_repo.get_last_sync_time()
finally:
    _check_repo.close()

_needs_auto_sync = _last_sync is None
if _last_sync is not None:
    _last_utc = _last_sync.replace(tzinfo=timezone.utc) if _last_sync.tzinfo is None else _last_sync.astimezone(timezone.utc)
    if datetime.now(timezone.utc) - _last_utc > AUTO_SYNC_INTERVAL:
        _needs_auto_sync = True

if _needs_auto_sync and not st.session_state.get("auto_sync_attempted"):
    st.session_state["auto_sync_attempted"] = True
    with st.spinner("初次載入或資料超過 6 小時，正在自動同步最新價格與限免..."):
        try:
            run_sync(WATCHLIST_PATH, DB_PATH)
            st.cache_data.clear()
        except Exception as exc:
            st.warning(f"自動同步暫時失敗（可稍後點擊左側手動同步）：{exc}")

# Load current data
watchlist = load_watchlist(WATCHLIST_PATH)
repo = DealRepository(DB_PATH)
try:
    latest_deals = repo.get_latest_deals()
    epic_free_games = repo.get_epic_free_games()
finally:
    repo.close()

active_titles = {w.title for w in watchlist if w.enabled}
steam_deals = [d for d in latest_deals if d["store"] == "Steam" and d["query_title"] in active_titles]


def render_chart_grid(items: list[dict], state_key: str, section_title: str, badge_html: str = "") -> None:
    if state_key not in st.session_state:
        st.session_state[state_key] = 12
    st.markdown(render_section_header(section_title, count=len(items), badge_html=badge_html), unsafe_allow_html=True)
    show_n = st.session_state[state_key]
    visible = items[:show_n]
    for i in range(0, len(visible), 4):
        cols = st.columns(4)
        for j, g in enumerate(visible[i : i + 4]):
            with cols[j]:
                with st.container(border=True):
                    st.markdown(render_cover(g["image"], g["name"]), unsafe_allow_html=True)
                    st.markdown(
                        f'<div class="gdr-game-title" title="{escape(g["name"])}">{escape(g["name"])}</div>',
                        unsafe_allow_html=True,
                    )
                    if g["final_price_twd"] == 0:
                        st.markdown(
                            '<div class="gdr-price-row"><span class="gdr-price-sale">免費遊玩</span></div>',
                            unsafe_allow_html=True,
                        )
                    elif g["discount_pct"] > 0:
                        st.markdown(
                            f'<div class="gdr-price-row">'
                            f'<span class="gdr-price-sale">NT$ {g["final_price_twd"]:,}</span>'
                            f'<span class="gdr-discount-badge">-{g["discount_pct"]}%</span>'
                            f'<span class="gdr-price-orig">NT$ {g["original_price_twd"]:,}</span>'
                            f'</div>',
                            unsafe_allow_html=True,
                        )
                    else:
                        st.markdown(
                            f'<div class="gdr-price-row"><span class="gdr-price-current">NT$ {g["final_price_twd"]:,}</span></div>',
                            unsafe_allow_html=True,
                        )
                    if g["url"]:
                        st.link_button("Steam 商店", g["url"], use_container_width=True)

    if show_n < len(items):
        if st.button(
            f"⬇️ 顯示更多（目前 {show_n} / {len(items)}）",
            key=f"more_{state_key}",
            use_container_width=True,
        ):
            st.session_state[state_key] = min(show_n + 12, len(items))
            st.rerun()


# ==========================================
# Page 1: Steam Watchlist
# ==========================================
if active_page == "📦 Steam 追蹤清單":
    with st.container(border=True):
        s_col, a_col = st.columns([2, 3], vertical_alignment="bottom")
        with s_col:
            search_query = st.text_input(
                "🔍 搜尋已追蹤遊戲",
                placeholder="輸入中文或英文關鍵字篩選...",
            )
        with a_col:
            with st.form("quick_add_form", clear_on_submit=True, border=False):
                f1, f2 = st.columns([3.2, 1], vertical_alignment="bottom")
                new_title = f1.text_input(
                    "➕ 快速新增追蹤遊戲（支援中/英文）",
                    placeholder="例如：艾爾登法環、空洞騎士、Cyberpunk 2077",
                )
                add_clicked = f2.form_submit_button("加入清單", type="primary", use_container_width=True)
                if add_clicked and new_title.strip():
                    updated = [w for w in watchlist if w.title.lower() != new_title.strip().lower()]
                    updated.append(WatchlistItem(title=new_title.strip(), target_price_usd=0.0, enabled=True))
                    save_watchlist(WATCHLIST_PATH, updated)
                    st.session_state["toast_msg"] = f"已加入「{new_title.strip()}」，請點擊左側同步最新價格"
                    st.rerun()

    filtered_deals = [
        d
        for d in steam_deals
        if not search_query.strip()
        or search_query.strip().lower() in d["matched_title"].lower()
        or search_query.strip().lower() in d["query_title"].lower()
    ]

    st.markdown(render_section_header("Steam 追蹤清單", count=len(filtered_deals)), unsafe_allow_html=True)

    if not filtered_deals:
        if search_query.strip():
            st.info(f"找不到符合「{search_query.strip()}」的已追蹤遊戲，請嘗試其他關鍵字。")
        else:
            st.info("目前尚未有同步的追蹤遊戲，請先點擊左側「🔄 同步最新資料」或在上方新增遊戲。")
    else:
        for row_start in range(0, len(filtered_deals), 4):
            row_items = filtered_deals[row_start : row_start + 4]
            cols = st.columns(4)
            for idx, deal in enumerate(row_items):
                cur_twd = to_twd(deal["current_price_usd"], fx_rate)
                norm_twd = to_twd(deal["normal_price_usd"], fx_rate)
                hist_twd = (
                    to_twd(deal["historical_low_usd"], fx_rate)
                    if deal["historical_low_usd"] is not None
                    else None
                )
                has_discount = deal["discount_pct"] > 0
                is_hist_low = hist_twd is not None and cur_twd <= hist_twd + 5

                with cols[idx]:
                    with st.container(border=True):
                        st.markdown(render_cover(deal["thumb_url"], deal["matched_title"]), unsafe_allow_html=True)
                        st.markdown(
                            f'<div class="gdr-game-title" title="{escape(deal["matched_title"])}">{escape(deal["matched_title"])}</div>',
                            unsafe_allow_html=True,
                        )

                        if has_discount:
                            st.markdown(
                                f'<div class="gdr-price-row">'
                                f'<span class="gdr-price-sale">NT$ {cur_twd:,}</span>'
                                f'<span class="gdr-discount-badge">-{deal["discount_pct"]}%</span>'
                                f'<span class="gdr-price-orig">NT$ {norm_twd:,}</span>'
                                f'</div>',
                                unsafe_allow_html=True,
                            )
                        else:
                            st.markdown(
                                f'<div class="gdr-price-row">'
                                f'<span class="gdr-price-current">NT$ {cur_twd:,}</span>'
                                f'<span class="gdr-meta-line" style="margin:0;">原價</span>'
                                f'</div>',
                                unsafe_allow_html=True,
                            )

                        hist_label = f"NT$ {hist_twd:,}" if hist_twd is not None else "查無紀錄"
                        low_pill = '<span class="gdr-hist-low-pill">史低</span>' if is_hist_low else ""
                        st.markdown(
                            f'<div class="gdr-meta-line">歷史最低：{hist_label}{low_pill}</div>',
                            unsafe_allow_html=True,
                        )

                        b1, b2 = st.columns([2.4, 1])
                        if deal["deal_url"]:
                            b1.link_button("前往購買", deal["deal_url"], type="primary", use_container_width=True)
                        if b2.button("🗑️", key=f"del_{deal['query_title']}", help="從清單刪除", use_container_width=True):
                            remaining = [w for w in watchlist if w.title != deal["query_title"]]
                            save_watchlist(WATCHLIST_PATH, remaining)
                            del_repo = DealRepository(DB_PATH)
                            try:
                                del_repo.delete_game(deal["query_title"])
                            finally:
                                del_repo.close()
                            st.session_state["toast_msg"] = f"已從追蹤清單移除「{deal['matched_title']}」"
                            st.rerun()

                        with st.expander("📈 歷史價格"):
                            hist_repo = DealRepository(DB_PATH)
                            try:
                                history = hist_repo.get_price_history(deal["query_title"], "Steam")
                            finally:
                                hist_repo.close()
                            if history:
                                df = pd.DataFrame(history)
                                df["時間"] = pd.to_datetime(df["fetched_at"]).dt.strftime("%m/%d %H:%M")
                                df["NT$"] = df["current_price_usd"].apply(lambda x: to_twd(x, fx_rate))
                                st.line_chart(df.set_index("時間")["NT$"], height=130)
                            else:
                                st.caption("尚無歷史紀錄")


# ==========================================
# Page 2: Steam Top Sellers
# ==========================================
elif active_page == "🏆 Steam 台灣熱門榜":
    try:
        charts = get_steam_charts()
        render_chart_grid(charts["top_sellers"], "top_show_count", "Steam 台灣熱門暢銷榜")
    except Exception as exc:
        st.warning(f"暫時無法載入 Steam 熱門榜：{exc}")


# ==========================================
# Page 3: Steam Official Specials
# ==========================================
elif active_page == "💸 Steam 官方精選特價":
    try:
        charts = get_steam_charts()
        render_chart_grid(
            charts["specials"],
            "spec_show_count",
            "Steam 官方精選特價",
            badge_html='<span class="gdr-special-badge">官方折扣精選</span>',
        )
    except Exception as exc:
        st.warning(f"暫時無法載入 Steam 官方精選特價：{exc}")


# ==========================================
# Page 4: Epic Games Weekly Free
# ==========================================
elif active_page == "🎁 Epic 每週限免":
    free_now = [g for g in epic_free_games if g["status"] == "FREE_NOW"]
    upcoming = [g for g in epic_free_games if g["status"] == "UPCOMING"]

    st.markdown(
        render_section_header(
            "本週限時免費領取",
            count=len(free_now),
            badge_html='<span class="gdr-epic-badge">EPIC GAMES</span>',
        ),
        unsafe_allow_html=True,
    )
    if not free_now:
        st.info("目前尚未同步到 Epic 本週限免資料，請點擊左側「🔄 同步最新資料」。")
    else:
        cols = st.columns(3)
        for idx, game in enumerate(free_now):
            with cols[idx % 3]:
                with st.container(border=True):
                    st.markdown(render_cover(game["thumb_url"], game["title"]), unsafe_allow_html=True)
                    st.markdown('<span class="gdr-free-pill">本週免費領取</span>', unsafe_allow_html=True)
                    st.markdown(f'<div class="gdr-game-title">{escape(game["title"])}</div>', unsafe_allow_html=True)
                    if game["end_date"]:
                        st.markdown(
                            f'<div class="gdr-meta-line">截止日期：{escape(game["end_date"][:10])}</div>',
                            unsafe_allow_html=True,
                        )
                    if game["store_url"]:
                        st.link_button("前往 Epic 免費領取", game["store_url"], type="primary", use_container_width=True)

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    st.markdown(render_section_header("下週限免預告", count=len(upcoming)), unsafe_allow_html=True)
    if not upcoming:
        st.caption("目前沒有下週預告資料（或請點擊左側重新同步）。")
    else:
        cols = st.columns(3)
        for idx, game in enumerate(upcoming):
            with cols[idx % 3]:
                with st.container(border=True):
                    st.markdown(render_cover(game["thumb_url"], game["title"]), unsafe_allow_html=True)
                    st.markdown('<span class="gdr-upcoming-pill">即將免費</span>', unsafe_allow_html=True)
                    st.markdown(f'<div class="gdr-game-title">{escape(game["title"])}</div>', unsafe_allow_html=True)
                    if game["start_date"]:
                        st.markdown(
                            f'<div class="gdr-meta-line">開放領取：{escape(game["start_date"][:10])}</div>',
                            unsafe_allow_html=True,
                        )
                    if game["store_url"]:
                        st.link_button("前往 Epic 商店頁", game["store_url"], use_container_width=True)


# ==========================================
# Page 5: Edit Watchlist
# ==========================================
elif active_page == "⚙️ 編輯追蹤清單":
    st.markdown(render_section_header("編輯追蹤遊戲清單", count=len(watchlist)), unsafe_allow_html=True)
    st.caption("可直接勾選/取消「啟用追蹤」、修改遊戲名稱（支援中/英文）、新增列或刪除列，完成後按「💾 儲存清單變更」。")

    edit_df = pd.DataFrame(
        [{"啟用追蹤": item.enabled, "遊戲名稱": item.title} for item in watchlist]
    )
    if edit_df.empty:
        edit_df = pd.DataFrame({"啟用追蹤": pd.Series(dtype="bool"), "遊戲名稱": pd.Series(dtype="str")})

    edited_df = st.data_editor(
        edit_df,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "啟用追蹤": st.column_config.CheckboxColumn("啟用追蹤", default=True, width="small"),
            "遊戲名稱": st.column_config.TextColumn("遊戲名稱（中文或英文）", required=True, width="large"),
        },
        key="watchlist_editor",
    )

    if st.button("💾 儲存清單變更", type="primary"):
        new_items: list[WatchlistItem] = []
        seen_names: set[str] = set()
        for _, row in edited_df.iterrows():
            name = str(row.get("遊戲名稱") or "").strip()
            if not name or name.lower() in seen_names:
                continue
            seen_names.add(name.lower())
            enabled = bool(row.get("啟用追蹤", True))
            new_items.append(WatchlistItem(title=name, enabled=enabled))

        save_watchlist(WATCHLIST_PATH, new_items)
        st.session_state["toast_msg"] = (
            f"已儲存清單（共 {len(new_items)} 款，啟用 {sum(1 for x in new_items if x.enabled)} 款）"
        )
        st.rerun()


# ==========================================
# Clean Footer
# ==========================================
st.markdown(
    """
    <div class="gdr-footer">
        <div>Game Deal Radar · Steam &amp; Epic 遊戲特價與限免監控</div>
        <div>資料來源：Steam Store API · CheapShark API · Epic Games Store API</div>
    </div>
    """,
    unsafe_allow_html=True,
)
