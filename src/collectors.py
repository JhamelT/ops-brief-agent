import boto3
from datetime import datetime, timedelta, timezone

cloudwatch = boto3.client("cloudwatch")
ec2 = boto3.client("ec2")
ce = boto3.client("ce")


def get_alarm_state():
    resp = cloudwatch.describe_alarms(StateValue="ALARM")
    return [
        {
            "name": a["AlarmName"],
            "reason": a.get("StateReason", ""),
            "since": a["StateUpdatedTimestamp"].isoformat(),
        }
        for a in resp["MetricAlarms"]
    ]


def get_ec2_inventory():
    resp = ec2.describe_instances(
        Filters=[{"Name": "instance-state-name", "Values": ["running"]}]
    )
    instances = []
    for reservation in resp["Reservations"]:
        for inst in reservation["Instances"]:
            tags = {t["Key"]: t["Value"] for t in inst.get("Tags", [])}
            instances.append({
                "id": inst["InstanceId"],
                "type": inst["InstanceType"],
                "launched": inst["LaunchTime"].isoformat(),
                "untagged": "Name" not in tags,
            })
    return instances


def get_yesterday_spend():
    today = datetime.now(timezone.utc).date()
    yesterday = today - timedelta(days=1)
    resp = ce.get_cost_and_usage(
        TimePeriod={"Start": yesterday.isoformat(), "End": today.isoformat()},
        Granularity="DAILY",
        Metrics=["UnblendedCost"],
        GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
    )
    by_service = []
    total = 0.0
    for group in resp["ResultsByTime"][0]["Groups"]:
        amount = float(group["Metrics"]["UnblendedCost"]["Amount"])
        total += amount
        if amount >= 0.001:
            by_service.append({"service": group["Keys"][0], "usd": round(amount, 4)})
    by_service.sort(key=lambda x: x["usd"], reverse=True)
    return {"date": yesterday.isoformat(), "total_usd": round(total, 4), "by_service": by_service[:8]}


def collect_signals():
    return {
        "alarms_in_alarm": get_alarm_state(),
        "running_instances": get_ec2_inventory(),
        "spend": get_yesterday_spend(),
    }