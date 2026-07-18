import json
from collectors import collect_signals


def lambda_handler(event, context):
    signals = collect_signals()
    print(json.dumps(signals, default=str))
    return {"statusCode": 200, "body": json.dumps(signals, default=str)}