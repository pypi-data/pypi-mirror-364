import re


def lambda_handler(event, context):
    request = event["Records"][0]["cf"]["request"]
    uri = request["uri"]

    # Check if URI ends with a slash or does not contain a dot (assuming it's a directory path)
    if uri.endswith("/") or not re.search(r"/[^/]+\.[^/]+$", uri):
        if not uri.endswith("/"):
            uri += "/"
        request["uri"] = uri + "index.html"

    return request
