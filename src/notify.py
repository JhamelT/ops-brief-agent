import os

import boto3

ses = boto3.client("ses")
EMAIL = os.environ["NOTIFY_EMAIL"]


def send_brief(subject, body_text, body_html):
    ses.send_email(
        Source=EMAIL,
        Destination={"ToAddresses": [EMAIL]},
        Message={
            "Subject": {"Data": subject},
            "Body": {
                "Text": {"Data": body_text},
                "Html": {"Data": body_html},
            },
        },
    )