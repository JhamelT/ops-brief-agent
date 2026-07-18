import json
import os

import boto3

bedrock = boto3.client("bedrock-runtime")
MODEL_ID = os.environ["MODEL_ID"]

SYSTEM = (
    "You are an infrastructure ops assistant. You will receive verified JSON "
    "facts collected from an AWS account, plus a diff against the previous run. "
    "Write a short morning ops brief in plain text. Rules: never invent numbers "
    "or resources not present in the JSON; lead with what changed since the "
    "last run; if nothing needs attention, say so in one line; keep it under "
    "200 words; no markdown formatting."
)


def write_brief(signals, diff):
    payload = {"signals": signals, "changes_since_last_run": diff}
    resp = bedrock.converse(
        modelId=MODEL_ID,
        system=[{"text": SYSTEM}],
        messages=[{
            "role": "user",
            "content": [{"text": json.dumps(payload, default=str)}],
        }],
        inferenceConfig={"maxTokens": 500, "temperature": 0.2},
    )
    usage = resp.get("usage", {})
    text = resp["output"]["message"]["content"][0]["text"]
    return text, usage