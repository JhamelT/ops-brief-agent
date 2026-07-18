BRAND = "#1a2332"
ACCENT = "#e8871e"


def _row(label, value):
    return (
        f'<tr><td style="padding:6px 12px;color:#555;font-size:13px;">{label}</td>'
        f'<td style="padding:6px 12px;font-size:13px;text-align:right;font-weight:600;">{value}</td></tr>'
    )


def render_html(signals, diff, brief_text, usage):
    spend = signals["spend"]

    spend_rows = "".join(
        _row(s["service"], f'${s["usd"]:.4f}') for s in spend["by_service"]
    )

    alarms = signals["alarms_in_alarm"]
    alarm_block = (
        "".join(
            f'<li style="margin:4px 0;font-size:13px;">{a["name"]}: {a["reason"]}</li>'
            for a in alarms
        )
        if alarms
        else '<li style="margin:4px 0;font-size:13px;color:#2e7d32;">No alarms in ALARM state</li>'
    )

    instances = signals["running_instances"]
    inst_block = (
        "".join(
            f'<li style="margin:4px 0;font-size:13px;">{i["id"]} ({i["type"]})'
            + (' <span style="color:#c62828;font-weight:600;">UNTAGGED</span>' if i["untagged"] else "")
            + "</li>"
            for i in instances
        )
        if instances
        else '<li style="margin:4px 0;font-size:13px;color:#2e7d32;">No running instances</li>'
    )

    if diff.get("first_run"):
        changes = '<p style="font-size:13px;color:#555;">First run. Baseline stored; deltas begin tomorrow.</p>'
    else:
        parts = []
        for key, label in [
            ("new_alarms", "New alarms"), ("resolved_alarms", "Resolved alarms"),
            ("new_instances", "New instances"), ("terminated_instances", "Terminated instances"),
        ]:
            if diff.get(key):
                parts.append(f'<li style="margin:4px 0;font-size:13px;">{label}: {", ".join(diff[key])}</li>')
        delta = diff.get("spend_delta_usd", 0)
        color = "#c62828" if delta > 0 else "#2e7d32"
        parts.append(
            f'<li style="margin:4px 0;font-size:13px;">Spend delta vs previous run: '
            f'<span style="color:{color};font-weight:600;">${delta:+.4f}</span></li>'
        )
        changes = f'<ul style="padding-left:18px;margin:6px 0;">{"".join(parts)}</ul>'

    return f"""
<div style="max-width:600px;margin:0 auto;font-family:Arial,Helvetica,sans-serif;color:#222;">
  <div style="background:{BRAND};padding:20px 24px;border-radius:8px 8px 0 0;">
    <div style="color:#fff;font-size:20px;font-weight:700;">Ops Brief</div>
    <div style="color:{ACCENT};font-size:12px;margin-top:4px;">{spend["date"]} · autonomous run · nothing was clicked</div>
  </div>
  <div style="border:1px solid #e0e0e0;border-top:none;border-radius:0 0 8px 8px;padding:20px 24px;">
    <p style="font-size:14px;line-height:1.55;margin-top:0;">{brief_text}</p>
    <h3 style="font-size:13px;text-transform:uppercase;letter-spacing:.05em;color:{ACCENT};margin:18px 0 6px;">Changes Since Last Run</h3>
    {changes}
    <h3 style="font-size:13px;text-transform:uppercase;letter-spacing:.05em;color:{ACCENT};margin:18px 0 6px;">Alarms</h3>
    <ul style="padding-left:18px;margin:6px 0;">{alarm_block}</ul>
    <h3 style="font-size:13px;text-transform:uppercase;letter-spacing:.05em;color:{ACCENT};margin:18px 0 6px;">Running EC2</h3>
    <ul style="padding-left:18px;margin:6px 0;">{inst_block}</ul>
    <h3 style="font-size:13px;text-transform:uppercase;letter-spacing:.05em;color:{ACCENT};margin:18px 0 6px;">Spend {spend["date"]} · ${spend["total_usd"]:.4f} total</h3>
    <table style="width:100%;border-collapse:collapse;">{spend_rows}</table>
    <p style="font-size:11px;color:#999;margin-top:20px;border-top:1px solid #eee;padding-top:10px;">
      Facts collected in code from CloudWatch, EC2, and Cost Explorer. Narrative by Amazon Nova 2 Lite
      ({usage.get("totalTokens", "?")} tokens). Layout rendered in Python, not by the model.
    </p>
  </div>
</div>"""