"""
generate_report: Build a self contained HTML FinOps cost optimization report.

Azure SRE Agent Python tool. Renders one self contained HTML file with no
external assets, no CDN, and no image dependencies. All styling is inline CSS
and every chart is drawn with plain HTML and CSS bars, so the report opens fully
styled offline. Writes the report to /mnt/data and returns a file link.

The report has two halves:
- FinOps overview: spend by subscription and resource group, and estimated
  monthly savings by dimension.
- Termination candidates: idle or orphaned resources scored by a confidence to
  terminate value from 0 to 100, each with a copyable az delete command. The
  agent never runs these commands; they are for an operator to review and run.

See references/report-layout.md for the input shape.
"""

import html
import os
from datetime import datetime, timezone

OUTPUT_DIR = "/mnt/data"

# Confidence band presentation: pill background, text, border, and bar fill.
BAND_PILL = {
    "Very high": ("#0f766e1A", "#0f766e", "#0f766e55"),
    "High": ("#15803d1A", "#15803d", "#15803d55"),
    "Medium": ("#b453091A", "#b45309", "#b4530955"),
    "Low": ("#b91c1c1A", "#b91c1c", "#b91c1c55"),
}
BAND_BAR = {"Very high": "#16a34a", "High": "#16a34a", "Medium": "#d97706", "Low": "#dc2626"}
CURRENCY_SYMBOL = {"USD": "$", "EUR": "\u20ac", "GBP": "\u00a3", "JPY": "\u00a5"}


def _esc(value):
    return html.escape("" if value is None else str(value), quote=True)


def _money(value, currency):
    symbol = CURRENCY_SYMBOL.get((currency or "").upper())
    number = f"{float(value or 0.0):,.2f}"
    return f"{symbol}{number}" if symbol else f"{number} {currency}".strip()


def _band_from_confidence(confidence):
    score = float(confidence or 0.0)
    if score >= 90:
        return "Very high"
    if score >= 70:
        return "High"
    if score >= 50:
        return "Medium"
    return "Low"


def _group_title(text):
    return f"<div class='group-title'>{_esc(text)}</div>"


def _bar_rows(items, currency):
    """Horizontal CSS bars for a list of {name, cost}, already sorted descending."""
    rows = [item for item in items if item]
    if not rows:
        return "<p class='small'>No data.</p>"
    top = max(float(item.get("cost", 0.0) or 0.0) for item in rows) or 1.0
    out = []
    for item in rows:
        cost = float(item.get("cost", 0.0) or 0.0)
        width = max(2.0, cost / top * 100.0)
        out.append(
            "<div class='chart-row money'>"
            f"<div class='chart-name'>{_esc(item.get('name', ''))}</div>"
            f"<div class='chart-bar'><div style='width:{width:.1f}%;background:#0f766e'></div></div>"
            f"<div class='chart-score'>{_money(cost, currency)}</div></div>"
        )
    return "".join(out)


def _candidate_chart(candidates):
    ranked = sorted(candidates, key=lambda c: float(c.get("confidence", 0.0) or 0.0), reverse=True)[:8]
    if not ranked:
        return ""
    top = max(float(c.get("confidence", 0.0) or 0.0) for c in ranked) or 1.0
    out = []
    for candidate in ranked:
        confidence = float(candidate.get("confidence", 0.0) or 0.0)
        band = candidate.get("band") or _band_from_confidence(confidence)
        width = max(2.0, confidence / top * 100.0)
        out.append(
            "<div class='chart-row'>"
            f"<div class='chart-name'>{_esc(candidate.get('resource', ''))}</div>"
            f"<div class='chart-bar'><div style='width:{width:.1f}%;background:{BAND_BAR.get(band, '#16a34a')}'></div></div>"
            f"<div class='chart-score'>{int(round(confidence))}</div></div>"
        )
    return "".join(out)


def _render_candidates(candidates, currency):
    if not candidates:
        return ""
    total_saving = 0.0
    counts = {"Very high": 0, "High": 0, "Medium": 0, "Low": 0}
    for candidate in candidates:
        band = candidate.get("band") or _band_from_confidence(candidate.get("confidence"))
        candidate["band"] = band
        counts[band] = counts.get(band, 0) + 1
        if not candidate.get("excluded"):
            total_saving += float(candidate.get("monthly_saving", 0.0) or 0.0)

    cards = (
        "<div class='grid'>"
        f"<div class='card'><h3>Total candidates</h3><div class='num'>{len(candidates)}</div></div>"
        f"<div class='card'><h3>Est. monthly savings*</h3><div class='num' style='color:#15803d'>{_money(total_saving, currency)}</div></div>"
        f"<div class='card'><h3>Very high confidence</h3><div class='num'>{counts['Very high']}</div></div>"
        f"<div class='card'><h3>High confidence</h3><div class='num'>{counts['High']}</div></div>"
        f"<div class='card'><h3>Medium or low confidence</h3><div class='num'>{counts['Medium'] + counts['Low']}</div></div>"
        "</div>"
    )

    note = (
        "<div class='small' style='margin:8px 0 0'>*Lower bound estimate. Deallocated VMs show direct "
        "compute savings as 0 because compute is already stopped; their attached disks and public IPs may "
        "still bill and appear as their own candidates where detected. Resources that could not be priced "
        "are marked Excluded and are not counted in the total.</div>"
    )

    chart = _candidate_chart(candidates)
    chart_block = (
        "<div class='section'><h2>Top termination candidates</h2>"
        "<div class='note'>This chart favours the clearest evidence: unattached disks, old snapshots, orphan "
        "NICs, and unassociated public IPs. Shared network, DR, and firewall looking resources are "
        "intentionally scored low.</div>"
        f"<div style='margin-top:16px'>{chart}</div></div>"
    ) if chart else ""

    how = (
        "<div class='section'><h2>How to read the confidence score</h2>"
        "<div class='note'>90 or above means the resource is unattached and old enough to look abandoned. "
        "70 to 89 means likely safe but still worth a quick owner check. 50 to 69 means the signal is real "
        "but recent or ambiguous. Below 50 means it likely belongs to DR or shared infrastructure and should "
        "not be terminated without deeper validation.</div>"
        "<div class='small' style='margin-top:10px'>Confidence is a conservative termination heuristic, not "
        "an automatic delete recommendation. The agent never runs these commands. Each delete command is for "
        "an operator to review and run.</div></div>"
    )

    subs = sorted({str(c.get("subscription", "")) for c in candidates if c.get("subscription")})
    sub_options = "".join(f"<option value='{_esc(s)}'>{_esc(s)}</option>" for s in subs)

    ordered = sorted(candidates, key=lambda c: float(c.get("confidence", 0.0) or 0.0), reverse=True)
    body_rows = []
    for index, candidate in enumerate(ordered, start=1):
        confidence = float(candidate.get("confidence", 0.0) or 0.0)
        band = candidate.get("band") or _band_from_confidence(confidence)
        pill_bg, pill_text, pill_border = BAND_PILL.get(band, BAND_PILL["Low"])
        bar_color = BAND_BAR.get(band, "#16a34a")
        if candidate.get("excluded"):
            saving_cell = (
                "<strong>Excluded</strong>"
                f"<div class='small'>{_esc(candidate.get('exclusion_reason', 'Not priced; excluded from total'))}</div>"
            )
        else:
            saving_cell = f"<strong>{_money(candidate.get('monthly_saving'), currency)}/mo</strong>"
            if candidate.get("saving_note"):
                saving_cell += f"<div class='small'>{_esc(candidate.get('saving_note'))}</div>"
        search = " ".join(
            str(candidate.get(key, ""))
            for key in ("resource", "resource_type", "subscription", "resource_group", "location", "reason")
        ).lower()
        delete_command = candidate.get("delete_command") or (
            f"az resource delete --ids '{candidate.get('resource_id', '')}'" if candidate.get("resource_id") else ""
        )
        cmd_id = f"cmd-{index}"
        if delete_command:
            delete_cell = (
                f"<div class='code-box' id='{cmd_id}'>{_esc(delete_command)}</div>"
                f"<button class='copy-btn' data-copy='{cmd_id}'>Copy</button>"
            )
        else:
            delete_cell = "<span class='small'>No delete command</span>"
        bar_width = max(2.0, min(100.0, confidence))
        body_rows.append(
            f"<tr data-subscription='{_esc(candidate.get('subscription', ''))}' data-band='{_esc(band)}' data-search='{_esc(search)}'>"
            f"<td>{_esc(candidate.get('resource', ''))}</td>"
            f"<td>{_esc(candidate.get('resource_type', ''))}</td>"
            f"<td>{_esc(candidate.get('subscription', ''))}</td>"
            f"<td>{_esc(candidate.get('resource_group', ''))}</td>"
            f"<td>{_esc(candidate.get('location', ''))}</td>"
            f"<td>{saving_cell}</td>"
            f"<td><div class='bar-wrap'><div class='bar-fill' style='width:{bar_width:.0f}%;background:{bar_color}'></div>"
            f"<span class='bar-label'>{int(round(confidence))}</span></div></td>"
            f"<td><span class='pill' style='background:{pill_bg};color:{pill_text};border-color:{pill_border}'>{_esc(band)}</span></td>"
            f"<td>{_esc(candidate.get('reason', ''))}</td>"
            f"<td>{_esc(candidate.get('next_step', ''))}</td>"
            f"<td>{delete_cell}</td></tr>"
        )

    table = (
        "<div class='section'><h2>Filterable termination candidates</h2>"
        "<div class='controls'>"
        "<div><label for='subscriptionFilter'>Subscription</label><br>"
        f"<select id='subscriptionFilter'><option value='all'>All subscriptions</option>{sub_options}</select></div>"
        "<div><label for='bandFilter'>Confidence band</label><br>"
        "<select id='bandFilter'><option value='all'>All bands</option>"
        "<option value='Very high'>Very high</option><option value='High'>High</option>"
        "<option value='Medium'>Medium</option><option value='Low'>Low</option></select></div>"
        "<div><label for='searchBox'>Search</label><br>"
        "<input id='searchBox' type='text' placeholder='resource, group, location, type'></div>"
        "</div>"
        f"<div id='resultSummary' class='summary-line'>Showing {len(ordered)} of {len(ordered)} candidates</div>"
        "<div style='overflow-x:auto'><table><thead><tr>"
        "<th>Resource</th><th>Type</th><th>Subscription</th><th>Resource group</th><th>Location</th>"
        "<th>Est. monthly savings</th><th>Confidence</th><th>Band</th><th>Why it looks unused</th>"
        "<th>Recommended next step</th><th>Delete command</th></tr></thead>"
        f"<tbody id='candidateRows'>{''.join(body_rows)}</tbody></table></div></div>"
    )

    return cards + note + chart_block + how + table


def _render_findings(findings, currency):
    if not findings:
        return ""
    headers = ["Resource", "Dimension", "Current", "Proposed", "Monthly saving", "Risk", "Priority"]
    numeric_columns = {4}
    head = ""
    for index, header in enumerate(headers):
        is_numeric = "true" if index in numeric_columns else "false"
        head += (
            f"<th><button type='button' class='sort-btn' data-numeric='{is_numeric}' "
            f"onclick=\"sortTable('findingsTable',{index},this)\">{_esc(header)}"
            "<span class='indicator'></span></button></th>"
        )
    body = ""
    for finding in sorted(findings, key=lambda item: float(item.get("priority_score", 0.0) or 0.0), reverse=True):
        cells = [
            _esc(finding.get("resource", "")),
            _esc(finding.get("dimension", "")),
            _esc(finding.get("current", "")),
            _esc(finding.get("proposed", "")),
            _esc(_money(finding.get("monthly_saving"), currency)),
            _esc(finding.get("risk", "")),
            _esc(finding.get("priority_band", "")),
        ]
        body += "<tr>" + "".join(f"<td>{cell}</td>" for cell in cells) + "</tr>"
    return (
        "<div class='section'><h2>Savings recommendations</h2>"
        "<div class='note'>Rate, tier, retention, commitment, and scheduling changes ranked by priority. "
        "These are proposals for a human to review; the agent applies nothing.</div>"
        "<div style='margin:12px 0'><input type='search' class='filter-input' placeholder='Filter rows...' "
        "oninput=\"filterTable('findingsTable',this.value)\"></div>"
        "<div style='overflow-x:auto'>"
        f"<table id='findingsTable'><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>"
        "<p class='small' id='findingsTable-count'></p></div>"
    )


def _document_head(title):
    return (
        "<!doctype html><html lang='en'><head>"
        "<meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width, initial-scale=1'>"
        f"<title>{_esc(title)}</title>"
        "<style>"
        "body{font-family:Segoe UI,Inter,Arial,sans-serif;margin:0;background:#f8fafc;color:#0f172a;}"
        ".container{max-width:1400px;margin:0 auto;padding:32px;}"
        ".header{margin-bottom:8px;}"
        ".h1{font-size:30px;font-weight:800;margin:0 0 8px;}"
        ".sub{color:#475569;margin:0;}"
        ".group-title{font-size:22px;font-weight:800;margin:26px 0 6px;}"
        ".grid{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:16px;margin:16px 0;}"
        ".card{background:#fff;border:1px solid #e2e8f0;border-radius:16px;padding:18px;box-shadow:0 1px 2px rgba(0,0,0,.04);}"
        ".card h3{margin:0 0 6px;font-size:13px;color:#64748b;font-weight:600;}"
        ".card .num{font-size:26px;font-weight:800;}"
        ".section{background:#fff;border:1px solid #e2e8f0;border-radius:16px;padding:20px;margin-top:16px;}"
        ".section h2{margin:0 0 12px;font-size:19px;}"
        ".chart-row{display:grid;grid-template-columns:280px 1fr 56px;gap:12px;align-items:center;margin:9px 0;}"
        ".chart-row.money{grid-template-columns:280px 1fr 130px;}"
        ".chart-name{font-size:14px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}"
        ".chart-bar{background:#e2e8f0;border-radius:999px;height:18px;overflow:hidden;}"
        ".chart-bar>div{height:100%;border-radius:999px;}"
        ".chart-score{text-align:right;font-weight:700;font-size:13px;}"
        ".controls{display:flex;flex-wrap:wrap;gap:12px;align-items:center;margin-bottom:14px;}"
        "label{font-size:14px;color:#334155;font-weight:600;}"
        "select,input{border:1px solid #cbd5e1;border-radius:10px;padding:9px 12px;font-size:14px;background:#fff;min-width:220px;}"
        "table{width:100%;border-collapse:collapse;font-size:14px;}"
        "th,td{padding:11px 10px;border-top:1px solid #e2e8f0;vertical-align:top;text-align:left;}"
        "th{background:#f8fafc;position:sticky;top:0;z-index:1;}"
        ".pill{display:inline-block;border:1px solid;border-radius:999px;padding:3px 10px;font-size:12px;font-weight:700;}"
        ".bar-wrap{position:relative;min-width:110px;background:#e2e8f0;height:18px;border-radius:999px;overflow:hidden;}"
        ".bar-fill{height:100%;border-radius:999px;}"
        ".bar-label{position:absolute;right:8px;top:0;line-height:18px;font-size:12px;font-weight:700;color:#111827;}"
        ".note{color:#475569;font-size:14px;line-height:1.5;}"
        ".small{font-size:12px;color:#64748b;line-height:1.5;}"
        ".code-box{background:#0f172a;color:#e2e8f0;border-radius:10px;padding:10px;font-family:ui-monospace,Consolas,Menlo,monospace;font-size:12px;line-height:1.45;white-space:pre-wrap;word-break:break-all;margin-top:8px;}"
        ".copy-btn{margin-top:8px;border:1px solid #cbd5e1;background:#fff;border-radius:8px;padding:6px 10px;font-size:12px;cursor:pointer;}"
        ".copy-btn:hover{background:#f8fafc;}"
        ".hidden{display:none;}"
        ".summary-line{margin:8px 0 12px;color:#334155;font-size:14px;}"
        ".sort-btn{background:none;border:0;font:inherit;font-weight:700;color:#334155;cursor:pointer;display:inline-flex;gap:4px;align-items:center;}"
        ".indicator{color:#0f766e;}"
        ".filter-input{min-width:260px;}"
        "@media (max-width:1100px){.grid{grid-template-columns:repeat(2,minmax(0,1fr));}.chart-row,.chart-row.money{grid-template-columns:1fr;}}"
        "@media print{.controls,.copy-btn,.filter-input,.indicator{display:none;}}"
        "</style></head>"
    )


SCRIPT = r"""<script>
(function () {
  var subscriptionFilter = document.getElementById('subscriptionFilter');
  var bandFilter = document.getElementById('bandFilter');
  var searchBox = document.getElementById('searchBox');
  var resultSummary = document.getElementById('resultSummary');
  var body = document.getElementById('candidateRows');
  if (body) {
    var rows = Array.prototype.slice.call(body.rows);
    var apply = function () {
      var sub = subscriptionFilter ? subscriptionFilter.value : 'all';
      var band = bandFilter ? bandFilter.value : 'all';
      var q = searchBox ? searchBox.value.trim().toLowerCase() : '';
      var visible = 0;
      rows.forEach(function (row) {
        var okSub = sub === 'all' || row.getAttribute('data-subscription') === sub;
        var okBand = band === 'all' || row.getAttribute('data-band') === band;
        var okSearch = !q || (row.getAttribute('data-search') || '').indexOf(q) !== -1;
        var show = okSub && okBand && okSearch;
        row.classList.toggle('hidden', !show);
        if (show) visible += 1;
      });
      if (resultSummary) resultSummary.textContent = 'Showing ' + visible + ' of ' + rows.length + ' candidates';
    };
    if (subscriptionFilter) subscriptionFilter.addEventListener('change', apply);
    if (bandFilter) bandFilter.addEventListener('change', apply);
    if (searchBox) searchBox.addEventListener('input', apply);
    apply();
  }

  function filterTable(id, query) {
    var table = document.getElementById(id);
    if (!table) return;
    var term = query.toLowerCase();
    var trs = table.tBodies[0].rows;
    var shown = 0;
    for (var i = 0; i < trs.length; i++) {
      var match = trs[i].textContent.toLowerCase().indexOf(term) !== -1;
      trs[i].style.display = match ? '' : 'none';
      if (match) shown++;
    }
    var counter = document.getElementById(id + '-count');
    if (counter) counter.textContent = shown + ' of ' + trs.length + ' rows';
  }
  window.filterTable = filterTable;

  function sortTable(id, col, btn) {
    var table = document.getElementById(id);
    if (!table) return;
    var tbody = table.tBodies[0];
    var trs = Array.prototype.slice.call(tbody.rows);
    var asc = btn.getAttribute('data-asc') !== 'true';
    btn.setAttribute('data-asc', asc ? 'true' : 'false');
    var numeric = btn.getAttribute('data-numeric') === 'true';
    trs.sort(function (a, b) {
      var x = a.cells[col].textContent.trim();
      var y = b.cells[col].textContent.trim();
      if (numeric) {
        var nx = parseFloat(x.replace(/[^0-9.\-]/g, '')) || 0;
        var ny = parseFloat(y.replace(/[^0-9.\-]/g, '')) || 0;
        return asc ? nx - ny : ny - nx;
      }
      return asc ? x.localeCompare(y) : y.localeCompare(x);
    });
    for (var j = 0; j < trs.length; j++) tbody.appendChild(trs[j]);
  }
  window.sortTable = sortTable;

  var buttons = document.querySelectorAll('.copy-btn');
  for (var b = 0; b < buttons.length; b++) {
    buttons[b].addEventListener('click', function () {
      var id = this.getAttribute('data-copy');
      var node = document.getElementById(id);
      if (!node) return;
      var btn = this;
      var original = btn.textContent;
      var reset = function (label) { btn.textContent = label; setTimeout(function () { btn.textContent = original; }, 1200); };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(node.textContent).then(function () { reset('Copied'); }, function () { reset('Copy failed'); });
      } else {
        reset('Copied');
      }
    });
  }
})();
</script>"""


def main(report_data: dict, report_title: str = "Azure FinOps Cost Optimization Report") -> dict:
    """Render the HTML report and return its file link.

    report_data: see references/report-layout.md for the expected shape.
    """
    data = report_data or {}
    totals = data.get("totals", {})
    currency = totals.get("currency", "")
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    analyzed = float(totals.get("analyzed_spend", 0.0) or 0.0)
    savings = float(totals.get("estimated_monthly_savings", 0.0) or 0.0)
    pct = (savings / analyzed * 100.0) if analyzed else 0.0

    findings = data.get("findings", [])
    candidates = data.get("candidates", [])

    priority_bands = {"High": 0, "Medium": 0, "Low": 0}
    for finding in findings:
        band = finding.get("priority_band", "Low")
        priority_bands[band] = priority_bands.get(band, 0) + 1

    candidate_bands = {"Very high": 0, "High": 0, "Medium": 0, "Low": 0}
    for candidate in candidates:
        band = candidate.get("band") or _band_from_confidence(candidate.get("confidence"))
        candidate_bands[band] = candidate_bands.get(band, 0) + 1

    header = (
        "<div class='header'>"
        f"<p class='h1'>{_esc(report_title)}</p>"
        f"<p class='sub'>Generated {generated}. Scope {_esc(data.get('generated_for', 'agent read scope'))}. "
        f"Window {int(data.get('window_days', 30) or 30)} days. Cost source {_esc(data.get('data_source', 'CostManagement'))}. "
        "Accessible subscriptions only.</p></div>"
    )

    summary_cards = (
        "<div class='grid'>"
        f"<div class='card'><h3>Analyzed spend (30 days)</h3><div class='num'>{_money(analyzed, currency)}</div></div>"
        f"<div class='card'><h3>Est. monthly savings</h3><div class='num' style='color:#15803d'>{_money(savings, currency)}</div></div>"
        f"<div class='card'><h3>Savings of spend</h3><div class='num'>{pct:.1f}%</div></div>"
        f"<div class='card'><h3>Termination candidates</h3><div class='num'>{len(candidates)}</div></div>"
        f"<div class='card'><h3>Recommendations</h3><div class='num'>{len(findings)}</div></div>"
        "</div>"
    )

    overview = []
    subs = data.get("subscriptions", [])
    if subs:
        ordered_subs = sorted(subs, key=lambda item: float(item.get("cost", 0.0) or 0.0), reverse=True)
        overview.append(
            "<div class='section'><h2>Spend by subscription</h2>" + _bar_rows(ordered_subs, currency) + "</div>"
        )
    rgs = data.get("resource_groups", [])
    if rgs:
        ordered_rgs = sorted(rgs, key=lambda item: float(item.get("cost", 0.0) or 0.0), reverse=True)
        overview.append(
            "<div class='section'><h2>Spend by resource group</h2>" + _bar_rows(ordered_rgs, currency) + "</div>"
        )
    by_dimension = data.get("savings_by_dimension", {})
    if by_dimension:
        dim_items = sorted(
            [{"name": key, "cost": value} for key, value in by_dimension.items()],
            key=lambda item: float(item.get("cost", 0.0) or 0.0),
            reverse=True,
        )
        overview.append(
            "<div class='section'><h2>Estimated monthly savings by dimension</h2>" + _bar_rows(dim_items, currency) + "</div>"
        )

    candidates_html = _render_candidates(candidates, currency)
    findings_html = _render_findings(findings, currency)

    limitation = (
        "<div class='section'><h2>Method and limits</h2>"
        "<div class='note'>Spend narrows where to look; savings and confidence decide what to act on first. "
        "Termination candidates are scored by a conservative confidence to terminate heuristic based on "
        "association state, age, and naming. Where Azure Monitor metrics or Activity Logs could not be read, "
        "the score relies on those heuristics only and the resource is treated more cautiously.</div>"
        "<div class='small' style='margin-top:8px'>This report is read only. It proposes changes and provides "
        "operator ready delete commands, but the agent runs none of them.</div></div>"
    )

    parts = [header, summary_cards]
    if overview:
        parts.append(_group_title("FinOps overview"))
        parts.extend(overview)
    if candidates_html:
        parts.append(_group_title("Termination candidates"))
        parts.append(candidates_html)
    if findings_html:
        parts.append(findings_html)
    parts.append(limitation)

    document = (
        _document_head(report_title)
        + "<body><div class='container'>"
        + "".join(parts)
        + "</div>"
        + SCRIPT
        + "</body></html>"
    )

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    filename = f"finops-report-{stamp}.html"
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(document)

    return {
        "report_path": f"/api/files/{filename}",
        "local_path": path,
        "summary": {
            "analyzed_spend": analyzed,
            "estimated_monthly_savings": savings,
            "savings_percent": round(pct, 1),
            "findings_total": len(findings),
            "findings_by_band": priority_bands,
            "candidates_total": len(candidates),
            "candidates_by_band": candidate_bands,
            "currency": currency,
        },
    }


def _cli():
    import argparse
    import json
    import sys

    parser = argparse.ArgumentParser(description="Build a self contained HTML FinOps report.")
    parser.add_argument("--input", type=str, default=None, help="Path to a JSON file with report_data. Reads stdin if omitted.")
    parser.add_argument("--title", type=str, default="Azure FinOps Cost Optimization Report")
    args = parser.parse_args()
    if args.input:
        with open(args.input, "r", encoding="utf-8") as handle:
            report_data = json.load(handle)
    else:
        report_data = json.load(sys.stdin)
    print(json.dumps(main(report_data=report_data, report_title=args.title), indent=2))


if __name__ == "__main__":
    _cli()
