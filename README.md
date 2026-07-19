# Ops Brief Agent

An autonomous daily AWS ops brief. Every morning at 7:00 AM Central, EventBridge Scheduler invokes a Lambda that collects verified facts from the account, computes what changed since the previous run, has Amazon Nova 2 Lite write a short narrative around those facts, and delivers a rendered HTML brief through SES. No button, no dashboard, no prompt.

Built for the AWS Builder Center Weekend Agent Challenge (July 2026).

![Architecture](/docs
/ops-brief-agent-architecture.png)

## What it collects

- CloudWatch alarms currently in ALARM state
- Running EC2 instances, flagging anything untagged
- Yesterday's spend by service from Cost Explorer

## What makes it an agent

DynamoDB stores each run. On every invocation the Lambda loads the previous run and computes a diff: new alarms, resolved alarms, new or terminated instances, and the spend delta. A stateless script tells you what exists. This tells you what changed.

## Design rule

Facts are collected in code. The model only writes the narrative around numbers it was handed, and the prompt forbids stating anything not present in the JSON. Every table, count, and dollar figure in the email is rendered in Python from the collected signals. If the counts are wrong, my boto3 calls are wrong. Never because a model guessed.

## Architecture

EventBridge Scheduler (cron, America/Chicago) -> Lambda (Python 3.12) -> CloudWatch / EC2 / Cost Explorer -> DynamoDB (run memory, diff) -> Bedrock Converse API (Nova 2 Lite via cross-region inference profile) -> HTML rendered in Python -> SES (HTML + plain text parts).

IAM is scoped to resource ARNs everywhere the API supports it. The read APIs (DescribeAlarms, DescribeInstances, GetCostAndUsage) are `Resource: *` because those actions do not support resource-level permissions. EventBridge Scheduler invokes Lambda by assuming its own execution role, so the build includes a second IAM role trusting `scheduler.amazonaws.com`.

## Repo structure

```
terraform/          all infrastructure (providers, IAM, Lambda, DynamoDB, Scheduler)
src/
  handler.py        orchestration: collect -> diff -> brief -> render -> send -> store
  collectors.py     boto3 signal collection (CloudWatch, EC2, Cost Explorer)
  brief.py          Bedrock Converse call, grounded prompt
  render.py         HTML email layout, built in code
  notify.py         SES delivery
```

## Deploy it yourself

Prerequisites:

1. Bedrock model access for Amazon Nova 2 Lite (us-east-1)
2. An SES verified email identity (sandbox is fine; you are emailing yourself)
3. Terraform >= 1.7

```
cd terraform
# set notify_email in terraform.tfvars
terraform init
terraform plan
terraform apply
```

Test by invoking the Lambda with an empty event. First run stores the baseline; the second run exercises the diff.

## Cost

| Item | Monthly |
|---|---|
| Lambda, Scheduler, DynamoDB, SES | Free tier / effectively $0 |
| Bedrock Nova 2 Lite (~350 tokens/run) | Under $0.01 |
| Cost Explorer API ($0.01 per request) | $0.30 |

The most expensive component of this AI agent is the API call that checks what everything else costs.

## Production notes (v2)

Dated run history instead of a single latest item. Event-driven triggers on GuardDuty findings and cost anomalies alongside the schedule. DLQ and alarm on the Lambda so the watcher is watched. Verified sending domain with DKIM. S3 remote state with locking. CI applying reviewed plan artifacts.

## Write-up

Full build story on AWS Builder Center: [Weekend Agent Challenge: Ops Brief Agent](ARTICLE_URL_AFTER_PUBLISH)
