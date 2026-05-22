"""
全球市場 & 台股電子盤 最新數據總整理
====================================
Streamlit 一頁式戰情看板 — 麻糬爸風格
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import datetime as dt
from functools import lru_cache
import warnings
warnings.filterwarnings("ignore")

# ============================================================
# 頁面設定
# ============================================================
st.set_page_config(
    page_title="全球市場戰情看板",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============================================================
# 自訂 CSS — 麻糬爸風格 (手繪感、圓角、暖色調)
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700;900&display=swap');

/* ── 全域 ── */
.stApp {
    background: linear-gradient(135deg, #FFF8F0 0%, #FFF3E8 50%, #F0F4FF 100%);
    font-family: 'Noto Sans TC', sans-serif;
}
.block-container {
    max-width: 1200px;
    padding: 1rem 2rem 2rem 2rem;
}

/* ── 隱藏 Streamlit 預設元素 ── */
#MainMenu, footer, header {visibility: hidden;}
.stDeployButton {display: none;}

/* ── 大標題 ── */
.main-title {
    background: linear-gradient(135deg, #FF6B35 0%, #FF8C42 100%);
    color: white;
    text-align: center;
    padding: 20px 30px;
    border-radius: 20px;
    margin-bottom: 8px;
    box-shadow: 0 4px 15px rgba(255,107,53,0.3);
    position: relative;
    overflow: hidden;
}
.main-title::before {
    content: '✨';
    position: absolute;
    left: 20px;
    top: 50%;
    transform: translateY(-50%);
    font-size: 28px;
}
.main-title::after {
    content: '✨';
    position: absolute;
    right: 20px;
    top: 50%;
    transform: translateY(-50%);
    font-size: 28px;
}
.main-title h1 {
    font-size: 28px;
    font-weight: 900;
    margin: 0;
    letter-spacing: 2px;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.15);
}
.main-title .date-line {
    font-size: 14px;
    opacity: 0.9;
    margin-top: 4px;
}

/* ── 區塊卡片 ── */
.section-card {
    background: white;
    border-radius: 16px;
    padding: 16px 20px;
    margin-bottom: 12px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    border: 2px solid #f0e8d8;
    position: relative;
}
.section-card.commodities { border-color: #FF9800; border-top: 4px solid #FF9800; }
.section-card.indices { border-color: #4CAF50; border-top: 4px solid #4CAF50; }
.section-card.tech { border-color: #2196F3; border-top: 4px solid #2196F3; }
.section-card.tw-market { border-color: #E91E63; border-top: 4px solid #E91E63; }
.section-card.forex { border-color: #9C27B0; border-top: 4px solid #9C27B0; }
.section-card.bonds { border-color: #607D8B; border-top: 4px solid #607D8B; }
.section-card.summary { border-color: #795548; border-top: 4px solid #795548; }

/* ── 區塊標題 ── */
.section-title {
    font-size: 17px;
    font-weight: 900;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.section-title .icon { font-size: 22px; }
.section-title.commodities { color: #E65100; }
.section-title.indices { color: #1B5E20; }
.section-title.tech { color: #0D47A1; }
.section-title.tw-market { color: #880E4F; }
.section-title.forex { color: #6A1B9A; }
.section-title.bonds { color: #37474F; }
.section-title.summary { color: #4E342E; }

/* ── 數據表格 ── */
.data-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    font-size: 13px;
}
.data-table th {
    background: #f8f4ee;
    padding: 6px 10px;
    text-align: right;
    font-weight: 700;
    color: #666;
    border-bottom: 2px solid #e8e0d4;
    font-size: 12px;
}
.data-table th:first-child { text-align: left; border-radius: 8px 0 0 0; }
.data-table th:last-child { border-radius: 0 8px 0 0; }
.data-table td {
    padding: 7px 10px;
    text-align: right;
    border-bottom: 1px solid #f0ebe4;
    font-variant-numeric: tabular-nums;
}
.data-table td:first-child {
    text-align: left;
    font-weight: 600;
    color: #333;
}
.data-table tr:nth-child(even) { background: #fdfaf6; }
.data-table tr:hover { background: #fff5e6; }

/* ── 漲跌色 ── */
.up { color: #D32F2F; font-weight: 700; }
.down { color: #2E7D32; font-weight: 700; }
.flat { color: #9E9E9E; }

/* ── 指數大卡片 ── */
.idx-card {
    background: linear-gradient(135deg, #f8fdf6 0%, #f0f8f0 100%);
    border-radius: 14px;
    padding: 14px 16px;
    text-align: center;
    border: 1.5px solid #c8e6c9;
    transition: transform 0.2s;
}
.idx-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
.idx-card .name { font-size: 13px; font-weight: 700; color: #2E7D32; margin-bottom: 4px; }
.idx-card .price { font-size: 22px; font-weight: 900; color: #1a1a1a; }
.idx-card .change { font-size: 13px; font-weight: 700; margin-top: 2px; }

/* ── 科技排名 ── */
.tech-row {
    display: flex;
    align-items: center;
    padding: 7px 0;
    border-bottom: 1px solid #e8f0fe;
    gap: 8px;
}
.tech-row:last-child { border-bottom: none; }
.tech-rank {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 900;
    font-size: 13px;
    flex-shrink: 0;
}
.tech-rank.gold { background: #FFF8E1; color: #F57F17; border: 2px solid #FFD54F; }
.tech-rank.silver { background: #F5F5F5; color: #757575; border: 2px solid #BDBDBD; }
.tech-rank.bronze { background: #FBE9E7; color: #BF360C; border: 2px solid #FFAB91; }
.tech-rank.normal { background: #F5F5F5; color: #999; border: 1px solid #E0E0E0; }
.tech-name { flex: 1; font-weight: 600; font-size: 13px; color: #333; }
.tech-price { width: 80px; text-align: right; font-size: 13px; color: #555; font-variant-numeric: tabular-nums; }
.tech-chg { width: 75px; text-align: right; font-weight: 800; font-size: 14px; }
.tech-bar-wrap { flex: 0 0 80px; height: 14px; background: #f0f0f0; border-radius: 7px; overflow: hidden; }
.tech-bar { height: 100%; border-radius: 7px; }

/* ── 台股卡片 ── */
.tw-card {
    border-radius: 14px;
    padding: 14px 16px;
    text-align: center;
    border: 1.5px solid;
}
.tw-card .label { font-size: 12px; font-weight: 700; margin-bottom: 4px; }
.tw-card .value { font-size: 24px; font-weight: 900; }
.tw-card .chg { font-size: 13px; font-weight: 700; margin-top: 2px; }

/* ── 小結語 ── */
.note-box {
    background: #fffdf5;
    border-left: 3px solid;
    padding: 8px 12px;
    margin-top: 10px;
    border-radius: 0 8px 8px 0;
    font-size: 13px;
    font-weight: 600;
}
.note-box.orange { border-color: #FF9800; color: #E65100; }
.note-box.green { border-color: #4CAF50; color: #1B5E20; }
.note-box.blue { border-color: #2196F3; color: #0D47A1; }
.note-box.pink { border-color: #E91E63; color: #880E4F; }
.note-box.purple { border-color: #9C27B0; color: #6A1B9A; }
.note-box.gray { border-color: #607D8B; color: #37474F; }

/* ── 總結 ── */
.summary-item {
    display: flex;
    align-items: flex-start;
    gap: 8px;
    padding: 5px 0;
    font-size: 13px;
    color: #4E342E;
    font-weight: 600;
}
.summary-item .check { color: #4CAF50; font-size: 16px; flex-shrink: 0; }

/* ── 底部 ── */
.footer-text {
    text-align: center;
    color: #bbb;
    font-size: 11px;
    margin-top: 16px;
    padding: 10px;
}

/* ── 提醒框 ── */
.reminder-box {
    background: linear-gradient(135deg, #FFF8E1, #FFFDE7);
    border: 2px dashed #FFB74D;
    border-radius: 14px;
    padding: 12px 16px;
    text-align: center;
    font-size: 13px;
    font-weight: 600;
    color: #E65100;
}

/* ── 隱藏 Streamlit 多餘的 column gap ── */
[data-testid="stHorizontalBlock"] { gap: 12px; }
</style>
""", unsafe_allow_html=True)


# ============================================================
# 數據抓取
# ============================================================
@st.cache_data(ttl=300)  # 快取 5 分鐘
def fetch_all_data():
    """一次抓完所有 yfinance 數據"""
    data = {}

    # ── 1. 焦點原物料 ──
    commodities = {
        "GC=F":  ("GOLD# 黃金", "🥇"),
        "SI=F":  ("SILVER# 白銀", "🥈"),
        "HG=F":  ("HGCOP 銅", "🟤"),
        "BZ=F":  ("BRENT 布倫特原油", "🛢️"),
        "CL=F":  ("OIL WTI原油", "🛢️"),
        "NG=F":  ("NGAS 天然氣", "🔥"),
        "PA=F":  ("PALL 鈀", "💎"),
        "PL=F":  ("PLAT 鉑", "💎"),
    }
    data["commodities"] = {}
    for tk, (name, icon) in commodities.items():
        try:
            df = yf.download(tk, period="5d", interval="1d", progress=False)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            if not df.empty and len(df) >= 2:
                c = float(df["Close"].iloc[-1])
                p = float(df["Close"].iloc[-2])
                data["commodities"][tk] = {
                    "name": name, "icon": icon,
                    "price": c, "chg": c-p, "chg_pct": ((c-p)/p)*100
                }
        except Exception:
            pass

    # ── 2. 全球指數 ──
    indices = {
        "^DJI":  ("道瓊指數", "🇺🇸"),
        "^GSPC": ("S&P 500", "🇺🇸"),
        "^IXIC": ("那斯達克", "🇺🇸"),
        "^SOX":  ("費城半導體", "🇺🇸"),
    }
    data["indices"] = {}
    for tk, (name, icon) in indices.items():
        try:
            df = yf.download(tk, period="6mo", interval="1d", progress=False)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            if not df.empty and len(df) >= 2:
                c = float(df["Close"].iloc[-1])
                p = float(df["Close"].iloc[-2])
                hist = df["Close"].tail(60).values.astype(float).tolist()
                data["indices"][tk] = {
                    "name": name, "icon": icon,
                    "close": c, "chg": c-p, "chg_pct": ((c-p)/p)*100,
                    "history": hist
                }
        except Exception:
            pass

    # ── 3. 美股科技 Top7 ──
    techs = {
        "NVDA": "NVDA 輝達",
        "AMD":  "AMD 超微半導體",
        "INTC": "INTC 英特爾",
        "MU":   "MU 美光科技",
        "TSLA": "TSLA 特斯拉",
        "TSM":  "TSM 台積電",
        "AAPL": "AAPL 蘋果",
    }
    data["tech"] = {}
    for tk, name in techs.items():
        try:
            df = yf.download(tk, period="5d", interval="1d", progress=False)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            if not df.empty and len(df) >= 2:
                c = float(df["Close"].iloc[-1])
                p = float(df["Close"].iloc[-2])
                data["tech"][tk] = {
                    "name": name, "price": c,
                    "chg": c-p, "chg_pct": ((c-p)/p)*100
                }
        except Exception:
            pass

    # ── 4. 台股 ──
    tw_tickers = {
        "^TWII":   ("加權指數", "🇹🇼"),
        "2330.TW": ("台積電", "🏭"),
    }
    data["tw"] = {}
    for tk, (name, icon) in tw_tickers.items():
        try:
            df = yf.download(tk, period="6mo", interval="1d", progress=False)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            if not df.empty and len(df) >= 2:
                c = float(df["Close"].iloc[-1])
                p = float(df["Close"].iloc[-2])
                hist = df["Close"].tail(60).values.astype(float).tolist()
                data["tw"][tk] = {
                    "name": name, "icon": icon,
                    "close": c, "chg": c-p, "chg_pct": ((c-p)/p)*100,
                    "history": hist
                }
        except Exception:
            pass

    # ── 5. 匯率 ──
    fx_tickers = {
        "USDTWD=X": ("美元/台幣", "💱"),
        "DX-Y.NYB": ("美元指數 DXY", "💵"),
    }
    data["forex"] = {}
    for tk, (name, icon) in fx_tickers.items():
        try:
            df = yf.download(tk, period="5d", interval="1d", progress=False)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            if not df.empty and len(df) >= 2:
                c = float(df["Close"].iloc[-1])
                p = float(df["Close"].iloc[-2])
                chg = c - p
                chg_pct = ((c-p)/p)*100
                # 台幣：匯率上升 = 台幣貶值
                if tk == "USDTWD=X":
                    direction = "台幣貶值 📉" if chg > 0 else ("台幣升值 📈" if chg < 0 else "持平")
                else:
                    direction = "美元走強" if chg > 0 else ("美元走弱" if chg < 0 else "持平")
                data["forex"][tk] = {
                    "name": name, "icon": icon,
                    "price": c, "chg": chg, "chg_pct": chg_pct,
                    "direction": direction,
                }
        except Exception:
            pass

    # ── 6. 美國公債殖利率 ──
    bond_tickers = {
        "^TNX": ("10年期公債殖利率", "📜"),
        "^TYX": ("30年期公債殖利率", "📜"),
        "^FVX": ("5年期公債殖利率", "📜"),
        "^IRX": ("3個月期國庫券", "📜"),
    }
    data["bonds"] = {}
    for tk, (name, icon) in bond_tickers.items():
        try:
            df = yf.download(tk, period="5d", interval="1d", progress=False)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            if not df.empty and len(df) >= 2:
                c = float(df["Close"].iloc[-1])
                p = float(df["Close"].iloc[-2])
                chg = c - p
                direction = "殖利率上升 (債價跌)" if chg > 0 else ("殖利率下降 (債價漲)" if chg < 0 else "持平")
                data["bonds"][tk] = {
                    "name": name, "icon": icon,
                    "yield_pct": c, "chg": chg,
                    "chg_pct": ((c-p)/p)*100 if p != 0 else 0,
                    "direction": direction,
                }
        except Exception:
            pass

    data["update_time"] = dt.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    data["date"] = dt.date.today()
    return data


# ============================================================
# 輔助函式
# ============================================================
def chg_html(val, fmt="+,.2f"):
    """漲跌 HTML span"""
    if val > 0:
        return f'<span class="up">▲{val:{fmt}}</span>'
    elif val < 0:
        return f'<span class="down">▼{abs(val):{fmt}}</span>'
    return f'<span class="flat">—{val:{fmt}}</span>'


def chg_pct_html(val):
    if val > 0:
        return f'<span class="up">(+{val:.2f}%)</span>'
    elif val < 0:
        return f'<span class="down">({val:.2f}%)</span>'
    return f'<span class="flat">(0.00%)</span>'


def chg_class(val):
    return "up" if val > 0 else ("down" if val < 0 else "flat")


# ============================================================
# 主畫面
# ============================================================
data = fetch_all_data()
today = data["date"]
wd_zh = ["一","二","三","四","五","六","日"][today.weekday()]

# ── 標題 ──
st.markdown(f"""
<div class="main-title">
    <h1>全球市場＆台股電子盤 最新數據總整理！</h1>
    <div class="date-line">{today.year}年 {today.month}月 {today.day}日（{wd_zh}）｜更新: {data["update_time"]}</div>
</div>
""", unsafe_allow_html=True)

# ── 小語 ──
st.markdown("""
<div style="text-align:center; margin: 4px 0 12px 0;">
    <span style="background:#FFF8E1; padding:4px 16px; border-radius:20px; font-size:13px; color:#F57F17; font-weight:600;">
        📝 波動是日常，紀律是勝利！數據看仔細，投資不怕怕！
    </span>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════
# ROW 1: 原物料 (左) + 全球指數 (右)
# ════════════════════════════════════════
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="section-card commodities">', unsafe_allow_html=True)
    st.markdown('<div class="section-title commodities"><span class="icon">🏆</span>1. 焦點原物料 / 能源價格</div>', unsafe_allow_html=True)

    rows = ""
    for tk, d in data.get("commodities", {}).items():
        cc = chg_class(d["chg_pct"])
        s = "+" if d["chg"] > 0 else ""
        rows += f"""<tr>
            <td>{d['icon']} {d['name']}</td>
            <td>{d['price']:,.2f}</td>
            <td class="{cc}">{s}{d['chg']:,.3f}</td>
            <td class="{cc}">({s}{d['chg_pct']:.2f}%)</td>
        </tr>"""

    st.markdown(f"""
    <table class="data-table">
        <tr><th>★ 商品</th><th>價格</th><th>漲跌</th><th>漲跌%</th></tr>
        {rows}
    </table>
    """, unsafe_allow_html=True)

    # 小結
    comm_vals = list(data.get("commodities", {}).values())
    if comm_vals:
        worst = min(comm_vals, key=lambda x: x["chg_pct"])
        if worst["chg_pct"] < -1:
            note = f"☆ {worst['name']}跌幅最大 {worst['chg_pct']:.2f}%！能源族群承壓～"
        else:
            note = "☆ 原物料整體波動不大，留意油價後續走向～"
        st.markdown(f'<div class="note-box orange">{note}</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="section-card indices">', unsafe_allow_html=True)
    st.markdown('<div class="section-title indices"><span class="icon">📈</span>2. 全球主要股市指數表現</div>', unsafe_allow_html=True)

    idx_items = list(data.get("indices", {}).values())
    if idx_items:
        # 2x2 指數卡片
        cols_idx = st.columns(2)
        for i, d in enumerate(idx_items):
            cc = chg_class(d["chg_pct"])
            s = "+" if d["chg"] > 0 else ""
            ar = "▲" if d["chg"] > 0 else ("▼" if d["chg"] < 0 else "—")
            with cols_idx[i % 2]:
                st.markdown(f"""
                <div class="idx-card">
                    <div class="name">{d['name']}</div>
                    <div class="price">{d['close']:,.2f}</div>
                    <div class="change {cc}">{ar}{s}{d['chg']:,.2f} ({s}{d['chg_pct']:.2f}%)</div>
                </div>
                """, unsafe_allow_html=True)
                # 迷你走勢圖
                if "history" in d:
                    import altair as alt
                    chart_df = pd.DataFrame({"day": range(len(d["history"])), "price": d["history"]})
                    line_color = "#D32F2F" if d["chg_pct"] > 0 else "#2E7D32"
                    c = alt.Chart(chart_df).mark_area(
                        line={"color": line_color, "strokeWidth": 2},
                        color=alt.Gradient(
                            gradient="linear", stops=[
                                alt.GradientStop(color=line_color, offset=0),
                                alt.GradientStop(color="white", offset=1),
                            ], x1=0, x2=0, y1=0, y2=1
                        ), opacity=0.3
                    ).encode(
                        x=alt.X("day:Q", axis=None),
                        y=alt.Y("price:Q", scale=alt.Scale(zero=False), axis=None),
                    ).properties(height=50, width="container").configure_view(strokeWidth=0)
                    st.altair_chart(c, use_container_width=True)

        # 小結
        up_cnt = sum(1 for d in idx_items if d["chg_pct"] > 0)
        best = max(idx_items, key=lambda x: x["chg_pct"])
        s = "+" if best["chg_pct"] > 0 else ""
        if up_cnt == len(idx_items):
            note2 = f"☆ 美股全面上漲！{best['name']}漲幅最大 {s}{best['chg_pct']:.2f}%，科技股強勢反彈中！"
        else:
            note2 = f"☆ 美股漲跌互見，{best['name']}表現最佳 {s}{best['chg_pct']:.2f}%"
        st.markdown(f'<div class="note-box green">{note2}</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════
# ROW 2: 科技 Top7 (左) + 台股 (右)
# ════════════════════════════════════════
col3, col4 = st.columns(2)

with col3:
    st.markdown('<div class="section-card tech">', unsafe_allow_html=True)
    st.markdown('<div class="section-title tech"><span class="icon">👑</span>3. 美股科技巨頭漲跌幅（Top7）</div>', unsafe_allow_html=True)

    sorted_tech = sorted(data.get("tech", {}).items(), key=lambda x: x[1]["chg_pct"], reverse=True)[:7]
    if sorted_tech:
        max_pct = max(abs(d["chg_pct"]) for _, d in sorted_tech)
        for i, (tk, d) in enumerate(sorted_tech):
            cc = chg_class(d["chg_pct"])
            s = "+" if d["chg_pct"] > 0 else ""
            rank_cls = ["gold","silver","bronze"][i] if i < 3 else "normal"
            bar_w = (abs(d["chg_pct"]) / max_pct * 100) if max_pct > 0 else 0
            bar_color = "#EF5350" if d["chg_pct"] > 0 else "#66BB6A"
            st.markdown(f"""
            <div class="tech-row">
                <div class="tech-rank {rank_cls}">{i+1}</div>
                <div class="tech-name">{d['name']}</div>
                <div class="tech-price">${d['price']:,.2f}</div>
                <div class="tech-chg {cc}">{s}{d['chg_pct']:.2f}%</div>
                <div class="tech-bar-wrap"><div class="tech-bar" style="width:{bar_w:.0f}%;background:{bar_color};"></div></div>
            </div>""", unsafe_allow_html=True)

        top3 = [d["name"].split()[0] for _, d in sorted_tech[:3]]
        note3 = f"☆ AI晶片、記憶體、半導體族群全面上攻！{', '.join(top3)} 領漲！"
        st.markdown(f'<div class="note-box blue">{note3}</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

with col4:
    st.markdown('<div class="section-card tw-market">', unsafe_allow_html=True)
    st.markdown('<div class="section-title tw-market"><span class="icon">🇹🇼</span>4. 台股電子盤表現</div>', unsafe_allow_html=True)

    tw_items = data.get("tw", {})
    if tw_items:
        tw_cols = st.columns(len(tw_items))
        for i, (tk, d) in enumerate(tw_items.items()):
            cc = chg_class(d["chg_pct"])
            s = "+" if d["chg"] > 0 else ""
            ar = "▲" if d["chg"] > 0 else ("▼" if d["chg"] < 0 else "")
            bg = "#FFF0F3" if d["chg_pct"] < 0 else "#F0FFF4"
            bc = "#E91E63" if d["chg_pct"] < 0 else "#4CAF50"
            with tw_cols[i]:
                st.markdown(f"""
                <div class="tw-card" style="background:{bg}; border-color:{bc};">
                    <div class="label" style="color:{bc};">{d['name']}</div>
                    <div class="value {cc}">{d['close']:,.2f}</div>
                    <div class="chg {cc}">{ar} {s}{d['chg']:,.2f} ({s}{d['chg_pct']:.2f}%)</div>
                </div>
                """, unsafe_allow_html=True)

        # 台股走勢圖
        import altair as alt
        chart_frames = []
        for tk, d in tw_items.items():
            if "history" in d:
                df_h = pd.DataFrame({"day": range(len(d["history"])), "price": d["history"], "name": d["name"]})
                chart_frames.append(df_h)
        if chart_frames:
            chart_df = pd.concat(chart_frames, ignore_index=True)
            c = alt.Chart(chart_df).mark_line(strokeWidth=2).encode(
                x=alt.X("day:Q", title="近60交易日"),
                y=alt.Y("price:Q", scale=alt.Scale(zero=False), title="價格"),
                color=alt.Color("name:N", legend=alt.Legend(title=None, orient="top"),
                                scale=alt.Scale(range=["#E91E63","#2196F3"])),
            ).properties(height=180).configure_view(strokeWidth=0)
            st.altair_chart(c, use_container_width=True)

        twii = tw_items.get("^TWII", {})
        if twii:
            dire = "上漲" if twii.get("chg",0) > 0 else "下跌"
            note4 = f"☆ 台股加權{dire} {abs(twii.get('chg',0)):,.0f} 點 ({twii.get('chg_pct',0):+.2f}%)，電子盤反彈力道不容小覷～"
            st.markdown(f'<div class="note-box pink">{note4}</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════
# ROW 3: 匯率 (左) + 美國公債 (右)
# ════════════════════════════════════════
col5, col6 = st.columns(2)

with col5:
    st.markdown('<div class="section-card forex">', unsafe_allow_html=True)
    st.markdown('<div class="section-title forex"><span class="icon">💱</span>5. 匯率</div>', unsafe_allow_html=True)

    fx_rows = ""
    for tk, d in data.get("forex", {}).items():
        cc = chg_class(d["chg"])
        s = "+" if d["chg"] > 0 else ""
        fx_rows += f"""<tr>
            <td>{d['icon']} {d['name']}</td>
            <td>{d['price']:,.4f}</td>
            <td class="{cc}">{s}{d['chg']:,.4f} ({s}{d['chg_pct']:.2f}%)</td>
            <td><b>{d['direction']}</b></td>
        </tr>"""

    st.markdown(f"""
    <table class="data-table">
        <tr><th>幣別</th><th>匯率</th><th>漲跌</th><th>趨勢</th></tr>
        {fx_rows}
    </table>
    """, unsafe_allow_html=True)

    fx_usd = data.get("forex", {}).get("USDTWD=X", {})
    if fx_usd:
        note5 = f"☆ 美元/台幣 {fx_usd['price']:.2f}，{fx_usd['direction']}，留意外資匯出動向"
        st.markdown(f'<div class="note-box purple">{note5}</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

with col6:
    st.markdown('<div class="section-card bonds">', unsafe_allow_html=True)
    st.markdown('<div class="section-title bonds"><span class="icon">📜</span>6. 美國公債殖利率</div>', unsafe_allow_html=True)

    bond_rows = ""
    for tk, d in data.get("bonds", {}).items():
        cc = chg_class(d["chg"])
        s = "+" if d["chg"] > 0 else ""
        bond_rows += f"""<tr>
            <td>{d['icon']} {d['name']}</td>
            <td>{d['yield_pct']:.3f}%</td>
            <td class="{cc}">{s}{d['chg']:.3f}</td>
            <td><b>{d['direction']}</b></td>
        </tr>"""

    st.markdown(f"""
    <table class="data-table">
        <tr><th>債券</th><th>殖利率</th><th>漲跌</th><th>趨勢</th></tr>
        {bond_rows}
    </table>
    """, unsafe_allow_html=True)

    tnx = data.get("bonds", {}).get("^TNX", {})
    if tnx:
        note6 = f"☆ 10年期殖利率 {tnx['yield_pct']:.3f}%，{tnx['direction']}"
        st.markdown(f'<div class="note-box gray">{note6}</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════
# ROW 4: 總結
# ════════════════════════════════════════
st.markdown('<div class="section-card summary">', unsafe_allow_html=True)

scol1, scol2 = st.columns([3, 2])
with scol1:
    st.markdown('<div class="section-title summary"><span class="icon">📋</span>今日總結</div>', unsafe_allow_html=True)

    summaries = []

    # 原物料
    comm_vals = list(data.get("commodities", {}).values())
    if comm_vals:
        worst_c = min(comm_vals, key=lambda x: x["chg_pct"])
        if worst_c["chg_pct"] < -1:
            summaries.append(f"國際原物料震盪，{worst_c['name']}跌幅達 {worst_c['chg_pct']:.2f}%，能源族群承壓")
        else:
            summaries.append("國際原物料價格波動不大，整體平穩")

    # 美股指數
    idx_vals = list(data.get("indices", {}).values())
    if idx_vals:
        up_cnt = sum(1 for d in idx_vals if d["chg_pct"] > 0)
        best_i = max(idx_vals, key=lambda x: x["chg_pct"])
        if up_cnt == len(idx_vals):
            summaries.append(f"美股四大指數全面收紅，{best_i['name']}漲幅最大 +{best_i['chg_pct']:.2f}%")
        else:
            summaries.append(f"美股漲跌互見，{best_i['name']}表現最佳 +{best_i['chg_pct']:.2f}%")

    # 科技
    if sorted_tech:
        t1_name = sorted_tech[0][1]["name"]
        t1_pct = sorted_tech[0][1]["chg_pct"]
        summaries.append(f"科技巨頭 {t1_name} 領漲 +{t1_pct:.2f}%，AI與半導體族群領軍")

    # 台股
    twii = data.get("tw", {}).get("^TWII", {})
    if twii:
        dire = "上漲" if twii.get("chg",0) > 0 else "下跌"
        summaries.append(f"台股加權收 {twii.get('close',0):,.0f}，{dire} {abs(twii.get('chg',0)):,.0f} 點")

    # 匯率
    fx_usd = data.get("forex", {}).get("USDTWD=X", {})
    if fx_usd:
        summaries.append(f"美元/台幣 {fx_usd['price']:.2f}，{fx_usd['direction']}")

    for s in summaries:
        st.markdown(f'<div class="summary-item"><span class="check">✅</span>{s}</div>', unsafe_allow_html=True)

with scol2:
    st.markdown("""
    <div class="reminder-box">
        ☆ 投資小提醒！<br>
        市場永遠在變，數據會說話，<br>
        保持紀律，穩穩向前進！！📈
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ── Footer ──
st.markdown(f"""
<div class="footer-text">
    資料來源: Yahoo Finance (yfinance) ｜ 更新時間: {data["update_time"]} ｜ Powered by Streamlit + Python
</div>
""", unsafe_allow_html=True)
