import base64
import json
import re


def lambda_handler(event, context):
    # Get request and headers
    request = event["Records"][0]["cf"]["request"]
    uri = request["uri"]
    headers = request.get("headers", {})

    # if uri starts with /binaries , do not require auth
    if uri.startswith("/binaries"):
        return request

    # Basic auth credentials
    auth_user = "stackgen"
    auth_pass = "user"

    # Construct the Basic Auth string
    auth_string = (
        "Basic " + base64.b64encode(f"{auth_user}:{auth_pass}".encode()).decode()
    )

    # Check for Authorization header
    auth_header = headers.get("authorization")
    if not auth_header or auth_header[0]["value"] != auth_string:
        # Respond with 401 Unauthorized if the header is missing or does not match
        return {
            "status": "401",
            "statusDescription": "Unauthorized",
            "body": "Unauthorized",
            "headers": {
                "www-authenticate": [{"key": "WWW-Authenticate", "value": "Basic"}]
            },
        }
    # Continue with the request if authenticated

    # Check if URI ends with a slash or does not contain a dot (assuming it's a directory path)
    if uri.endswith("/") or not re.search(r"/[^/]+\.[^/]+$", uri):
        if not uri.endswith("/"):
            uri += "/"
        request["uri"] = uri + "index.html"

    return request
