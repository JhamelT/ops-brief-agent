import json
import os
from datetime import datetime, timezone

from render import render_html

import boto3

from brief import write_brief
from collectors import collect_signals
from notify import send_brief

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])



def load_previous_run():
    resp = table.get_item(Key={"run_id": "latest"})
    return resp.get("Item", {}).get("signals")


def store_run(signals):
    item = {
        "run_id": "latest",
        "ran_at": datetime.now(timezone.utc).isoformat(),
        "signals": json.dumps(signals, default=str),
    }
    table.put_item(Item=item)


def compute_diff(previous, current):
    if previous is None:
        return {"first_run": True}
    prev = json.loads(previous) if isinstance(previous, str) else previous
    prev_alarms = {a["name"] for a in prev.get("alarms_in_alarm", [])}
    curr_alarms = {a["name"] for a in current["alarms_in_alarm"]}
    prev_ids = {i["id"] for i in prev.get("running_instances", [])}
    curr_ids = {i["id"] for i in current["running_instances"]}
    prev_spend = prev.get("spend", {}).get("total_usd", 0)
    curr_spend = current["spend"]["total_usd"]
    return {
        "new_alarms": sorted(curr_alarms - prev_alarms),
        "resolved_alarms": sorted(prev_alarms - curr_alarms),
        "new_instances": sorted(curr_ids - prev_ids),
        "terminated_instances": sorted(prev_ids - curr_ids),
        "spend_delta_usd": round(curr_spend - prev_spend, 4),
    }


def lambda_handler(event, context):
    signals = collect_signals()
    previous = load_previous_run()
    diff = compute_diff(previous, signals)
    brief_text, usage = write_brief(signals, diff)
    today = datetime.now(timezone.utc).date().isoformat()
    html = render_html(signals, diff, brief_text, usage)
    send_brief(f"Ops Brief {today}", brief_text, html)
    store_run(signals)
    print(json.dumps({"diff": diff, "token_usage": usage}, default=str))
    return {"statusCode": 200, "body": "brief sent"}