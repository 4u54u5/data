from __future__ import annotations

import datetime as dt
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlencode, urlparse
import os

from core import SOURCE_REGISTRY, connect, html_escape, init_db, load_events, register_functions, seed

# ---------------------------------------------------------------------------
# Styling & i18n
# ---------------------------------------------------------------------------

STYLE = """
<style>
:root {
  --bg: #0f1117; --surface: #1a1d27; --surface2: #22253a;
  --accent: #4f8ef7; --accent2: #7c5cbf; --green: #3ecf8e;
  --yellow: #f5a623; --red: #e74c3c; --text: #e2e8f0;
  --muted: #8892a4; --border: #2d3150;
  font-size: 15px;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body { background: var(--bg); color: var(--text); font-family: 'Segoe UI', system-ui, sans-serif; min-height: 100vh; }
a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }

/* Layout */
.header { background: var(--surface); border-bottom: 1px solid var(--border); padding: 12px 24px; display: flex; align-items: center; gap: 16px; }
.header h1 { font-size: 1.15rem; font-weight: 700; letter-spacing: .3px; }
.header .subtitle { color: var(--muted); font-size: .82rem; }
.container { max-width: 1400px; margin: 0 auto; padding: 20px 24px; }

/* KPI bar */
.kpi-row { display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 20px; }
.kpi { background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 14px 18px; flex: 1; min-width: 140px; }
.kpi .val { font-size: 1.6rem; font-weight: 700; }
.kpi .lbl { color: var(--muted); font-size: .78rem; margin-top: 2px; }
.kpi.green .val { color: var(--green); }
.kpi.yellow .val { color: var(--yellow); }
.kpi.red .val { color: var(--red); }
.kpi.blue .val { color: var(--accent); }

/* Filters */
.filter-bar { background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 14px 18px; margin-bottom: 20px; display: flex; flex-wrap: wrap; gap: 12px; align-items: flex-end; }
.filter-group { display: flex; flex-direction: column; gap: 4px; }
.filter-group label { font-size: .75rem; color: var(--muted); text-transform: uppercase; letter-spacing: .5px; }
select, input[type=text] { background: var(--surface2); border: 1px solid var(--border); color: var(--text); border-radius: 5px; padding: 6px 10px; font-size: .85rem; min-width: 130px; }
select:focus, input[type=text]:focus { outline: 2px solid var(--accent); }
button[type=submit] { background: var(--accent); color: #fff; border: none; border-radius: 5px; padding: 7px 16px; font-size: .85rem; cursor: pointer; align-self: flex-end; }
button[type=submit]:hover { opacity: .88; }
.btn-reset { background: var(--surface2); color: var(--muted); border: 1px solid var(--border); border-radius: 5px; padding: 7px 12px; font-size: .82rem; cursor: pointer; text-decoration: none; display: inline-block; }
.btn-reset:hover { color: var(--text); text-decoration: none; }

/* Tabs */
.tabs { display: flex; gap: 4px; border-bottom: 1px solid var(--border); margin-bottom: 20px; }
.tab { padding: 8px 16px; font-size: .85rem; cursor: pointer; border-bottom: 2px solid transparent; color: var(--muted); text-decoration: none; }
.tab.active { color: var(--accent); border-bottom-color: var(--accent); }
.tab:hover { color: var(--text); text-decoration: none; }

/* Cards */
.cards { display: flex; flex-direction: column; gap: 14px; }
.card { background: var(--surface); border: 1px solid var(--border); border-radius: 10px; padding: 18px 20px; position: relative; }
.card:hover { border-color: var(--accent2); }
.card-header { display: flex; align-items: flex-start; gap: 10px; flex-wrap: wrap; margin-bottom: 10px; }
.card-title { font-size: 1rem; font-weight: 600; flex: 1; min-width: 200px; }
.badge { display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: .72rem; font-weight: 600; white-space: nowrap; }
.badge-country { background: #1e3a5f; color: #7eb8f7; }
.badge-type { background: #1e3a2f; color: #5ecfa0; }
.badge-impact-positive { background: #1a3a2a; color: var(--green); }
.badge-impact-neutral { background: #2a2a1a; color: var(--yellow); }
.badge-impact-watch { background: #3a1a1a; color: var(--red); }
.badge-high { background: #1a2a3a; color: var(--accent); }
.badge-medium { background: #2a2a3a; color: #a78bfa; }
.badge-low { background: #3a2a1a; color: var(--yellow); }
.card-meta { color: var(--muted); font-size: .78rem; margin-bottom: 8px; }
.card-summary { font-size: .88rem; line-height: 1.6; color: #c8d0de; margin-bottom: 10px; }
.card-footer { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }
.tag { background: var(--surface2); border: 1px solid var(--border); color: var(--muted); font-size: .72rem; padding: 2px 7px; border-radius: 10px; }
.score-bar-wrap { margin: 6px 0; }
.score-bar-label { font-size: .75rem; color: var(--muted); margin-bottom: 3px; }
.score-bar { background: var(--surface2); border-radius: 4px; height: 6px; }
.score-bar-fill { height: 6px; border-radius: 4px; }
.score-bar-fill.green { background: var(--green); }
.score-bar-fill.yellow { background: var(--yellow); }
.score-bar-fill.red { background: var(--red); }
.score-bar-fill.blue { background: var(--accent); }

/* Deep dive */
.deep-dive { background: var(--surface2); border: 1px solid var(--border); border-radius: 8px; padding: 16px; margin-top: 14px; font-size: .85rem; }
.deep-dive h3 { font-size: .9rem; color: var(--accent); margin-bottom: 10px; }
.deep-dive-section { margin-bottom: 12px; }
.deep-dive-section h4 { font-size: .8rem; color: var(--muted); text-transform: uppercase; letter-spacing: .4px; margin-bottom: 6px; }
.company-chip { display: inline-flex; align-items: center; gap: 4px; background: var(--surface); border: 1px solid var(--border); border-radius: 5px; padding: 3px 8px; font-size: .78rem; margin: 2px; }
.company-chip .role { color: var(--muted); font-size: .7rem; }
.proc-category { margin-bottom: 10px; }
.proc-category-title { font-size: .8rem; font-weight: 600; color: var(--yellow); margin-bottom: 4px; }

/* Monitor */
.monitor-card { background: var(--surface); border: 1px solid var(--border); border-radius: 10px; padding: 16px 18px; margin-bottom: 14px; }
.monitor-card h3 { font-size: .92rem; color: var(--accent); margin-bottom: 8px; }
.monitor-item { display: flex; gap: 8px; align-items: flex-start; padding: 6px 0; border-bottom: 1px solid var(--border); font-size: .84rem; }
.monitor-item:last-child { border-bottom: none; }
.monitor-item .icon { font-size: 1rem; min-width: 20px; }
.monitor-item .content { flex: 1; }
.monitor-item .label { color: var(--muted); font-size: .74rem; }
.alert-high { color: var(--red); }
.alert-medium { color: var(--yellow); }
.alert-low { color: var(--green); }

/* Sources */
.source-table { width: 100%; border-collapse: collapse; font-size: .84rem; }
.source-table th { background: var(--surface2); color: var(--muted); text-align: left; padding: 8px 12px; font-weight: 600; font-size: .75rem; text-transform: uppercase; letter-spacing: .4px; }
.source-table td { padding: 8px 12px; border-bottom: 1px solid var(--border); }
.source-table tr:hover td { background: var(--surface2); }

/* Graph / relation */
.relation-stage { margin-bottom: 20px; }
.relation-stage h3 { font-size: .9rem; color: var(--accent); margin-bottom: 10px; }
.relation-row { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 8px; }
.relation-node { background: var(--surface2); border: 1px solid var(--border); border-radius: 6px; padding: 6px 12px; font-size: .8rem; }
.relation-node.actor { border-color: var(--green); color: var(--green); }
.relation-node.investor { border-color: var(--yellow); color: var(--yellow); }
.relation-node.partner { border-color: var(--accent); color: var(--accent); }
.relation-node.beneficiary { border-color: var(--accent2); color: #c4b5fd; }
.relation-node.mentioned { border-color: var(--border); color: var(--muted); }
.arrow { color: var(--muted); align-self: center; font-size: 1.1rem; }

/* Responsive */
@media (max-width: 700px) {
  .container { padding: 12px; }
  .kpi-row { gap: 8px; }
  .kpi { min-width: 100px; }
  .filter-bar { flex-direction: column; }
}
</style>
"""

LABELS = {
    "telecom_infra": "通信インフラ",
    "policy": "政策",
    "market_expansion": "市場拡大",
    "corporate_investment": "企業投資",
    "data_center": "データセンター",
    "positive": "ポジティブ",
    "neutral": "中立",
    "negative_or_watch": "要注意",
    "high": "高",
    "medium": "中",
    "low": "低",
    "short_term": "短期",
    "medium_term": "中期",
    "long_term": "長期",
    "high_expectation": "高期待",
    "medium_expectation": "中期待",
    "low_expectation": "低期待",
    "high_growth": "高成長",
    "medium_growth": "中成長",
    "watch_growth": "要監視",
    "actor": "実行者",
    "investor": "投資家",
    "partner": "パートナー",
    "beneficiary": "受益者",
    "mentioned": "言及",
}


def jp(key: str) -> str:
    return LABELS.get(key, key)


def all_events() -> list[dict]:
    with connect() as conn:
        register_functions(conn)
        return load_events(conn)


def filtered_events(events: list[dict], params: dict) -> list[dict]:
    country = params.get("country", "")
    event_type = params.get("event_type", "")
    impact = params.get("impact", "")
    theme = params.get("theme", "")
    q = params.get("q", "").lower()

    result = []
    for ev in events:
        if country and ev.get("country") != country:
            continue
        if event_type and ev.get("event_type") != event_type:
            continue
        if impact and ev.get("impact_direction") != impact:
            continue
        if theme and theme not in ev.get("themes", []):
            continue
        if q:
            haystack = (
                (ev.get("event_title_ja") or "")
                + (ev.get("summary_ja") or "")
                + (ev.get("country") or "")
            ).lower()
            if q not in haystack:
                continue
        result.append(ev)
    return result


def render_page(title: str, body: str, params: dict | None = None) -> str:
    tab = params.get("tab", "events") if params else "events"
    qs_base = {k: v for k, v in (params or {}).items() if k != "tab"}

    def tab_url(t: str) -> str:
        p = {**qs_base, "tab": t}
        return "/?" + urlencode(p)

    tabs_html = ""
    for t, label in [("events", "イベント"), ("monitor", "モニター"), ("sources", "情報源"), ("graph", "関係図")]:
        active = "active" if tab == t else ""
        tabs_html += f'<a class="tab {active}" href="{tab_url(t)}">{label}</a>'

    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html_escape(title)}</title>
{STYLE}
</head>
<body>
<div class="header">
  <div>
    <h1>🌏 Asia Infra Event Radar</h1>
    <div class="subtitle">アジア通信・デジタルインフラ市場調査ダッシュボード</div>
  </div>
</div>
<div class="container">
{body}
</div>
</body>
</html>"""


def render_tabs(events: list[dict], filtered: list[dict], params: dict) -> str:
    tab = params.get("tab", "events")
    if tab == "monitor":
        return render_monitor(filtered, params)
    if tab == "sources":
        return render_sources(params)
    if tab == "graph":
        return render_graph(filtered, params)
    return render_kpis(events, filtered) + render_filter_bar(events, params) + render_cards(filtered, params)


def select(options: list[str], name: str, current: str, label: str, placeholder: str = "すべて") -> str:
    opts = f'<option value="">{placeholder}</option>'
    for o in options:
        sel = "selected" if o == current else ""
        opts += f'<option value="{html_escape(o)}" {sel}>{html_escape(jp(o) if o in LABELS else o)}</option>'
    return f'<div class="filter-group"><label>{label}</label><select name="{name}">{opts}</select></div>'


def render_kpis(all_evs: list[dict], filtered: list[dict]) -> str:
    total = len(all_evs)
    pos = sum(1 for e in filtered if e.get("impact_direction") == "positive")
    watch = sum(1 for e in filtered if e.get("impact_direction") == "negative_or_watch")
    high_conf = sum(1 for e in filtered if e.get("confidence_level") == "high")
    countries = len(set(e.get("country", "") for e in filtered))
    return f"""<div class="kpi-row">
  <div class="kpi blue"><div class="val">{len(filtered)}<span style="font-size:.9rem;color:var(--muted)">/{total}</span></div><div class="lbl">表示中イベント</div></div>
  <div class="kpi green"><div class="val">{pos}</div><div class="lbl">ポジティブ</div></div>
  <div class="kpi red"><div class="val">{watch}</div><div class="lbl">要注意</div></div>
  <div class="kpi yellow"><div class="val">{high_conf}</div><div class="lbl">高信頼度</div></div>
  <div class="kpi"><div class="val">{countries}</div><div class="lbl">対象国・地域</div></div>
</div>"""


def render_filter_bar(events: list[dict], params: dict) -> str:
    countries = sorted(set(e.get("country", "") for e in events if e.get("country")))
    event_types = sorted(set(e.get("event_type", "") for e in events if e.get("event_type")))
    impacts = ["positive", "neutral", "negative_or_watch"]
    all_themes: list[str] = []
    seen: set[str] = set()
    for e in events:
        for t in e.get("themes", []):
            if t not in seen:
                seen.add(t)
                all_themes.append(t)
    all_themes.sort()

    tab_input = f'<input type="hidden" name="tab" value="{html_escape(params.get("tab","events"))}">'
    q_val = html_escape(params.get("q", ""))
    q_input = f'<div class="filter-group"><label>キーワード検索</label><input type="text" name="q" value="{q_val}" placeholder="検索..."></div>'

    return f"""<form method="get" action="/">
<div class="filter-bar">
  {tab_input}
  {select(countries, "country", params.get("country",""), "国・地域")}
  {select(event_types, "event_type", params.get("event_type",""), "イベント種別")}
  {select(impacts, "impact", params.get("impact",""), "方向性")}
  {select(all_themes, "theme", params.get("theme",""), "テーマ")}
  {q_input}
  <button type="submit">絞り込む</button>
  <a href="/?tab={html_escape(params.get('tab','events'))}" class="btn-reset">リセット</a>
</div>
</form>"""


def company_list(companies: list[dict]) -> str:
    if not companies:
        return '<span style="color:var(--muted);font-size:.8rem">なし</span>'
    chips = ""
    for c in companies:
        role = jp(c.get("relation_type", ""))
        chips += f'<span class="company-chip"><span>{html_escape(c["name"])}</span><span class="role">({html_escape(c.get("country",""))})</span></span>'
    return chips


def procurement_category_text(cat: dict) -> str:
    companies_text = "、".join(c["name"] for c in cat.get("companies", [])[:6])
    if len(cat.get("companies", [])) > 6:
        companies_text += f"他{len(cat['companies'])-6}社"
    return companies_text


def render_procurement_categories(categories: list[dict]) -> str:
    if not categories:
        return ""
    html = '<div class="deep-dive-section"><h4>調達カテゴリ</h4>'
    for cat in categories:
        title = html_escape(cat["category"])
        companies_text = html_escape(procurement_category_text(cat))
        html += f'<div class="proc-category"><div class="proc-category-title">{title}</div><div style="font-size:.78rem;color:var(--muted)">{companies_text}</div></div>'
    html += "</div>"
    return html


def deep_dive_prompt(ev: dict) -> str:
    title = ev.get("event_title_ja", "")
    country = ev.get("country", "")
    event_type = jp(ev.get("event_type", ""))
    actors = "、".join(c["name"] for c in ev.get("executing_companies", []))
    themes = "、".join(ev.get("themes", []))
    return f"【{country}】{title}｜種別:{event_type}｜実行者:{actors or 'なし'}｜テーマ:{themes}"


def render_deep_dive(ev: dict) -> str:
    actors = ev.get("executing_companies", [])
    funders = ev.get("funding_sources", [])
    all_cos = ev.get("companies", [])
    others = [c for c in all_cos if c["relation_type"] not in ("actor", "investor")]
    themes = ev.get("themes", [])
    proc_cats = ev.get("procurement_categories", [])

    exp_score = ev.get("expectation_score", 0)
    exp_level = jp(ev.get("expectation_level", ""))
    exp_reason = html_escape(ev.get("expectation_reason", ""))
    grw_score = ev.get("growth_score", 0)
    grw_level = jp(ev.get("growth_level", ""))
    grw_horizon = html_escape(ev.get("growth_horizon", ""))
    grw_drivers = html_escape(ev.get("growth_drivers", ""))
    grw_risks = html_escape(ev.get("growth_risks", ""))

    exp_color = "green" if exp_score >= 70 else ("yellow" if exp_score >= 50 else "red")
    grw_color = "green" if grw_score >= 75 else ("yellow" if grw_score >= 60 else "red")

    prompt = html_escape(deep_dive_prompt(ev))

    html = f"""<div class="deep-dive">
<h3>詳細分析</h3>
<div style="display:flex;gap:20px;flex-wrap:wrap;margin-bottom:12px;">
  <div style="flex:1;min-width:180px;">
    <div class="score-bar-label">期待スコア: {exp_score}/100 ({exp_level})</div>
    <div class="score-bar"><div class="score-bar-fill {exp_color}" style="width:{exp_score}%"></div></div>
    <div style="font-size:.76rem;color:var(--muted);margin-top:3px">{exp_reason}</div>
  </div>
  <div style="flex:1;min-width:180px;">
    <div class="score-bar-label">成長スコア: {grw_score}/100 ({grw_level})</div>
    <div class="score-bar"><div class="score-bar-fill {grw_color}" style="width:{grw_score}%"></div></div>
    <div style="font-size:.76rem;color:var(--muted);margin-top:3px">期間: {grw_horizon}</div>
  </div>
</div>
<div style="display:flex;gap:16px;flex-wrap:wrap;margin-bottom:12px;font-size:.82rem;">
  <div style="flex:1;min-width:160px;"><span style="color:var(--green);font-weight:600">▲ 成長ドライバー</span><br><span style="color:var(--muted)">{grw_drivers}</span></div>
  <div style="flex:1;min-width:160px;"><span style="color:var(--red);font-weight:600">▼ 主なリスク</span><br><span style="color:var(--muted)">{grw_risks}</span></div>
</div>"""

    if actors:
        html += f'<div class="deep-dive-section"><h4>実行者</h4><div>{company_list(actors)}</div></div>'
    if funders:
        html += f'<div class="deep-dive-section"><h4>投資家・資金提供</h4><div>{company_list(funders)}</div></div>'
    if others:
        html += f'<div class="deep-dive-section"><h4>関連企業</h4><div>{company_list(others)}</div></div>'
    if themes:
        tags = "".join(f'<span class="tag">{html_escape(t)}</span>' for t in themes)
        html += f'<div class="deep-dive-section"><h4>テーマ</h4><div style="display:flex;gap:4px;flex-wrap:wrap">{tags}</div></div>'

    html += render_procurement_categories(proc_cats)

    html += f'<div style="margin-top:12px;padding:8px;background:var(--surface);border-radius:5px;font-size:.75rem;color:var(--muted)"><strong>ディープダイブ用プロンプト:</strong><br>{prompt}</div>'
    html += "</div>"
    return html


def monitor_priority(ev: dict) -> str:
    score = ev.get("expectation_score", 0)
    if score >= 75:
        return "high"
    if score >= 55:
        return "medium"
    return "low"


def monitor_cadence(ev: dict) -> str:
    horizon = ev.get("time_horizon", "")
    if horizon == "short_term":
        return "毎週"
    if horizon == "medium_term":
        return "隔週"
    return "月次"


def monitor_alerts(ev: dict) -> list[str]:
    alerts = []
    impact = ev.get("impact_direction", "")
    conf = ev.get("confidence_level", "")
    event_type = ev.get("event_type", "")
    themes = ev.get("themes", [])

    if impact == "positive" and conf == "high":
        alerts.append("高信頼度ポジティブ: 入札・調達情報を優先確認")
    if impact == "negative_or_watch":
        alerts.append("要注意: 競合動向・規制変更を継続監視")
    if "data center" in themes:
        alerts.append("データセンター: 電力・用地・建設パートナー情報を追跡")
    if "5G" in themes or "telecom" in themes:
        alerts.append("5G/通信: 基地局展開進捗・設備調達動向を確認")
    if event_type == "corporate_investment":
        alerts.append("投資案件: 資金調達ラウンド・建設着工情報に注目")
    return alerts or ["標準モニタリング継続"]


def monitor_queries(ev: dict) -> list[str]:
    title = ev.get("event_title_ja", "")
    country = ev.get("country", "")
    actors = [c["name"] for c in ev.get("executing_companies", [])]
    themes = ev.get("themes", [])
    queries = []
    if actors:
        queries.append(f"{actors[0]} {country} 入札 OR 調達 OR 契約")
    if "data center" in themes:
        queries.append(f"{country} データセンター 建設 OR 電力 OR 冷却 2024 OR 2025")
    if "5G" in themes:
        queries.append(f"{country} 5G 基地局 OR RAN 展開 OR 入札")
    if not queries:
        queries.append(f"{country} デジタルインフラ 投資 OR 政策")
    return queries


def render_monitor(events: list[dict], params: dict) -> str:
    if not events:
        return '<div style="color:var(--muted);padding:20px">表示するイベントがありません。フィルターを調整してください。</div>'

    html = render_filter_bar(events, {**params, "tab": "monitor"})
    html += f'<div style="color:var(--muted);font-size:.82rem;margin-bottom:14px">{len(events)}件のイベントをモニタリング中</div>'

    for ev in events[:20]:
        priority = monitor_priority(ev)
        cadence = monitor_cadence(ev)
        alerts = monitor_alerts(ev)
        queries = monitor_queries(ev)
        title = html_escape(ev.get("event_title_ja", ""))
        country = html_escape(ev.get("country", ""))
        priority_class = f"alert-{priority}"

        html += f'<div class="monitor-card">'
        html += f'<h3><span class="{priority_class}">{"🔴" if priority=="high" else "🟡" if priority=="medium" else "🟢"}</span> {title}</h3>'
        html += f'<div style="font-size:.78rem;color:var(--muted);margin-bottom:8px">国: {country} ｜ 確認頻度: {cadence}</div>'

        html += '<div style="margin-bottom:8px">'
        for alert in alerts:
            html += f'<div class="monitor-item"><span class="icon">⚡</span><div class="content"><div>{html_escape(alert)}</div></div></div>'
        html += '</div>'

        html += '<div><div style="font-size:.75rem;color:var(--muted);margin-bottom:4px">推奨検索クエリ</div>'
        for q in queries:
            html += f'<div style="font-size:.78rem;background:var(--surface2);border-radius:4px;padding:4px 8px;margin-bottom:3px;font-family:monospace">{html_escape(q)}</div>'
        html += '</div>'
        html += '</div>'

    return html


def render_bars(events: list[dict]) -> str:
    from collections import Counter
    country_counts = Counter(ev.get("country", "不明") for ev in events)
    if not country_counts:
        return ""
    max_count = max(country_counts.values()) or 1
    html = '<div style="margin-bottom:20px"><div style="font-size:.82rem;color:var(--muted);margin-bottom:8px">国別イベント数</div>'
    for country, count in sorted(country_counts.items(), key=lambda x: -x[1])[:10]:
        pct = int(count / max_count * 100)
        html += f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:5px;font-size:.82rem">'
        html += f'<div style="min-width:120px;color:var(--text)">{html_escape(country)}</div>'
        html += f'<div style="flex:1;background:var(--surface2);border-radius:3px;height:14px"><div style="width:{pct}%;background:var(--accent);height:14px;border-radius:3px"></div></div>'
        html += f'<div style="min-width:24px;color:var(--muted)">{count}</div>'
        html += '</div>'
    html += '</div>'
    return html


def render_sources(params: dict) -> str:
    html = '<div style="margin-bottom:14px"><h2 style="font-size:1rem;margin-bottom:14px">情報源レジストリ</h2>'
    html += '<table class="source-table"><thead><tr>'
    for col in ["情報源名", "国", "種別", "主要テーマ", "URL"]:
        html += f'<th>{col}</th>'
    html += '</tr></thead><tbody>'
    for src in SOURCE_REGISTRY:
        url = html_escape(src.get("url", ""))
        html += f'<tr><td>{html_escape(src.get("name",""))}</td><td>{html_escape(src.get("country",""))}</td><td>{html_escape(src.get("type",""))}</td><td>{html_escape(src.get("focus",""))}</td><td><a href="{url}" target="_blank">{url}</a></td></tr>'
    html += '</tbody></table></div>'
    return html


def render_graph(events: list[dict], params: dict) -> str:
    html = render_filter_bar(events, {**params, "tab": "graph"})
    html += '<div style="margin-bottom:14px"><h2 style="font-size:1rem;margin-bottom:6px">イベント・企業関係図</h2>'
    html += f'<div style="color:var(--muted);font-size:.8rem;margin-bottom:14px">{len(events)}件のイベントを表示中</div>'
    for ev in events[:15]:
        html += render_relation_stage(ev)
    html += '</div>'
    return html


def render_relation_stage(ev: dict) -> str:
    title = html_escape(ev.get("event_title_ja", ""))
    companies = ev.get("companies", [])
    html = f'<div class="relation-stage"><h3>{title}</h3><div class="relation-row">'
    if not companies:
        html += '<span style="color:var(--muted);font-size:.8rem">関連企業なし</span>'
    for c in companies:
        role = c.get("relation_type", "mentioned")
        html += f'<div class="relation-node {html_escape(role)}">{html_escape(c["name"])} <span style="font-size:.7rem">({html_escape(jp(role))})</span></div>'
    html += '</div></div>'
    return html


def render_procurement_stage(ev: dict) -> str:
    cats = ev.get("procurement_categories", [])
    if not cats:
        return ""
    html = '<div style="margin-top:10px">'
    for cat in cats:
        title = html_escape(cat["category"])
        cos = "、".join(html_escape(c["name"]) for c in cat.get("companies", [])[:5])
        html += f'<div style="font-size:.78rem;margin-bottom:4px"><span style="color:var(--yellow)">{title}:</span> <span style="color:var(--muted)">{cos}</span></div>'
    html += '</div>'
    return html


def render_card(ev: dict, params: dict) -> str:
    title = html_escape(ev.get("event_title_ja", ""))
    country = html_escape(ev.get("country", ""))
    region = html_escape(ev.get("region", ""))
    event_type = html_escape(jp(ev.get("event_type", "")))
    impact = ev.get("impact_direction", "neutral")
    impact_label = html_escape(jp(impact))
    conf = html_escape(jp(ev.get("confidence_level", "")))
    horizon = html_escape(jp(ev.get("time_horizon", "")))
    summary = html_escape(ev.get("summary_ja", ""))
    source = html_escape(ev.get("source_name", ""))
    pub = html_escape(ev.get("published_at", ""))
    url = html_escape(ev.get("original_url", "") or "")
    themes = ev.get("themes", [])

    impact_badge_class = {
        "positive": "badge-impact-positive",
        "neutral": "badge-impact-neutral",
        "negative_or_watch": "badge-impact-watch",
    }.get(impact, "badge-impact-neutral")

    conf_badge = {
        "high": "badge-high",
        "medium": "badge-medium",
        "low": "badge-low",
    }.get(ev.get("confidence_level", ""), "badge-medium")

    theme_tags = "".join(f'<span class="tag">{html_escape(t)}</span>' for t in themes)
    source_link = f'<a href="{url}" target="_blank">{source}</a>' if url else source

    exp_score = ev.get("expectation_score", 0)
    exp_color = "green" if exp_score >= 70 else ("yellow" if exp_score >= 50 else "red")

    dd_param = {**params, "dd": str(ev.get("id", ""))}
    dd_url = "/?" + urlencode(dd_param)
    current_dd = params.get("dd", "")
    show_dd = str(ev.get("id", "")) == current_dd

    dd_toggle = f'<a href="{html_escape(dd_url)}" style="font-size:.78rem;color:var(--accent2)">{"▲ 詳細を閉じる" if show_dd else "▼ 詳細を開く"}</a>'

    html = f"""<div class="card">
  <div class="card-header">
    <div class="card-title">{title}</div>
    <span class="badge badge-country">{country}</span>
    <span class="badge badge-type">{event_type}</span>
    <span class="badge {impact_badge_class}">{impact_label}</span>
    <span class="badge {conf_badge}">{conf}</span>
  </div>
  <div class="card-meta">{source_link} ｜ {pub} ｜ 期間: {horizon}</div>
  <div class="card-summary">{summary}</div>
  <div class="score-bar-wrap">
    <div class="score-bar-label">期待スコア: {exp_score}</div>
    <div class="score-bar"><div class="score-bar-fill {exp_color}" style="width:{exp_score}%"></div></div>
  </div>
  <div class="card-footer">{theme_tags}&nbsp;&nbsp;{dd_toggle}</div>"""

    if show_dd:
        html += render_deep_dive(ev)

    html += "</div>"
    return html


def render_cards(events: list[dict], params: dict) -> str:
    if not events:
        return '<div style="color:var(--muted);padding:20px">条件に合うイベントが見つかりませんでした。</div>'
    html = f'<div style="color:var(--muted);font-size:.82rem;margin-bottom:10px">{len(events)}件のイベント</div>'
    html += '<div class="cards">'
    for ev in events:
        html += render_card(ev, params)
    html += '</div>'
    return html


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # suppress access log

    def do_GET(self):
        parsed = urlparse(self.path)
        raw_params = parse_qs(parsed.query, keep_blank_values=False)
        params = {k: v[0] for k, v in raw_params.items()}

        if parsed.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"ok")
            return

        if parsed.path != "/":
            self.send_response(404)
            self.end_headers()
            return

        try:
            events = all_events()
            filt = filtered_events(events, params)
            tab = params.get("tab", "events")
            body = render_tabs(events, filt, params) if tab != "events" else (
                render_kpis(events, filt) + render_filter_bar(events, params) + render_cards(filt, params)
            )
            page = render_page("Asia Infra Event Radar", body, params)
            encoded = page.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)
        except Exception as exc:
            import traceback
            err = traceback.format_exc()
            self.send_response(500)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(err.encode("utf-8"))


def run(host="0.0.0.0", port=None):
    if port is None:
        port = int(os.environ.get("PORT", 8787))
    with connect() as conn:
        register_functions(conn)
        init_db(conn)
        seed(conn)
    print(f"Asia Infra Event Radar: http://{host}:{port}")
    ThreadingHTTPServer((host, port), Handler).serve_forever()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", default=None, type=int)
    args = parser.parse_args()
    run(host=args.host, port=args.port)
