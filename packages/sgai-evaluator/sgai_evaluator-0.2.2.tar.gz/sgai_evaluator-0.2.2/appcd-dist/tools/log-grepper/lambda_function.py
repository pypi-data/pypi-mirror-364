import json
import boto3
import os
import time
import re
from datetime import datetime, timedelta

# Initialize the AWS Logs client with a specific region
AWS_REGION = "us-west-2"  # Change this if needed
logs_client = boto3.client("logs", region_name=AWS_REGION)

def parse_duration(duration_str):
    """
    Convert duration string (e.g., '1h', '30m', '1d') to minutes.
    """
    match = re.match(r"(\d+)([hmd])", duration_str)
    if not match:
        raise ValueError("Invalid duration format. Use '1h', '30m', '1d', etc.")

    value, unit = int(match.group(1)), match.group(2)
    if unit == "h":
        return value * 60
    elif unit == "m":
        return value
    elif unit == "d":
        return value * 1440
    else:
        raise ValueError("Unsupported time unit.")

def get_application_log_groups():
    """
    Get all log groups that contain '/application'.
    """
    log_groups = []
    paginator = logs_client.get_paginator("describe_log_groups")

    for page in paginator.paginate():
        for log_group in page.get("logGroups", []):
            if "/application" in log_group["logGroupName"]:
                log_groups.append(log_group["logGroupName"])

    return log_groups

def query_cloudwatch(log_groups, query, duration_minutes):
    """
    Run a CloudWatch Logs Insights query.
    """
    if not log_groups:
        return ["No matching log groups found."]

    # Define time range for query execution
    end_time = int(time.time() * 1000)
    start_time = end_time - (duration_minutes * 60 * 1000)

    # Start query execution
    response = logs_client.start_query(
        logGroupNames=log_groups,
        startTime=start_time,
        endTime=end_time,
        queryString=query,
    )

    query_id = response["queryId"]

    # Poll for query results
    for _ in range(20):  # Retry up to 20 times, increased from 10
        time.sleep(1)  # Wait before polling, decreased from 2
        result = logs_client.get_query_results(queryId=query_id)

        if result["status"] == "Complete":
            return result["results"]

    return ["Query timeout: No results received."]

def lambda_handler(event, context):
    try:
        print(json.dumps(event)) # added to see the event object
        # Parse request
        body = json.loads(event.get("body", "{}"))
        days = body.get("days", "1d")  # Default to 1 day if not provided
        request_id = body.get("request_id")

        # Convert duration to minutes
        duration_minutes = parse_duration(days)

        # Get all relevant log groups
        log_groups = get_application_log_groups()

        if not log_groups:
            return {"statusCode": 404, "body": json.dumps({"error": "No log groups found matching '/application'"})}

        # CloudWatch Log Insights query
        if request_id:
            query = f"""
            fields @timestamp, @message
            | parse @message '"service":"*"' as service
            | parse @message '"level":"*"' as level
            | parse @message '"requestID":"*"' as requestID
            | parse @message '"msg":"*"' as msg
            | filter requestID == "{request_id}"
            | sort @timestamp desc
            | limit 1000
            """
        else:
            query = """
            fields @timestamp, @message
            | parse @message '"service":"*"' as service
            | parse @message '"level":"*"' as level
            | parse @message '"requestID":"*"' as requestID
            | parse @message '"msg":"*"' as msg
            | sort @timestamp desc
            | limit 1000
            """

        # Execute query
        result = query_cloudwatch(log_groups, query, duration_minutes)

        return {
            "statusCode": 200,
            "body": json.dumps({"logs": result})
        }

    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}