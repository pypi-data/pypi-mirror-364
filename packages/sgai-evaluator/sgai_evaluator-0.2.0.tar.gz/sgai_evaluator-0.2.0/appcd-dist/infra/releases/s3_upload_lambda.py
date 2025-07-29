import os
from urllib.parse import quote
import boto3

# Initialize S3 client
s3_client = boto3.client("s3")


def lambda_handler(event, context):
    bucket_name = "appcd-public-releases"
    directory_name = "appcd-dist"
    html_file_name = "index.html"
    latest_file_name = "latest.txt"
    target_bucket = bucket_name
    target_key = os.path.join(directory_name, html_file_name)

    # Initialize a list to hold all file keys
    all_file_keys = []

    # Function to recursively fetch all file keys
    def fetch_keys(bucket, prefix, continuation_token=None):
        if continuation_token:
            response = s3_client.list_objects_v2(
                Bucket=bucket, Prefix=prefix, ContinuationToken=continuation_token
            )
        else:
            response = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)

        # Extract file keys
        for item in response.get("Contents", []):
            all_file_keys.append(item["Key"])

        # Check if there are more pages, if so, fetch them
        if response.get("IsTruncated"):
            fetch_keys(bucket, prefix, response.get("NextContinuationToken"))

    # Fetch all files from the directory
    fetch_keys(bucket_name, directory_name)

    # Sort file keys in reverse order and exclude 'index.html' and 'latest.txt'
    sorted_keys = [
        key
        for key in sorted(all_file_keys, reverse=True)
        if not key.endswith((html_file_name, latest_file_name))
    ]

    # Identify the latest zip file
    latest_zip_file = next((key for key in sorted_keys if key.endswith(".zip")), None)

    # Update latest.txt file
    latest_zip_file = quote(latest_zip_file) # URL encode the file name
    latest_zip_file = latest_zip_file.split("/")[-1] # Extract the file name from the path
    print("Latest zip file value: " + latest_zip_file)
    if latest_zip_file:
        s3_client.put_object(
            Bucket=bucket_name,
            Key=os.path.join(directory_name, latest_file_name),
            Body=latest_zip_file,
            ContentType="text/plain",
        )

    # Start HTML document
    html_content = "<html><head><title>StackGen Distribution</title></head><body>"
    html_content += "<h1>StackGen Distribution</h1>"

    # Iterate over files and create a link for each (excluding latest.txt)
    for file_key in sorted_keys:
        file_name = os.path.basename(file_key)
        file_url = f"https://releases.stackgen.com/{file_key}"
        html_content += f"<p><a href='{file_url}'>{file_name}</a></p>"

    # Close HTML document
    html_content += "</body></html>"

    # Upload HTML file to S3
    s3_client.put_object(
        Bucket=target_bucket, Key=target_key, Body=html_content, ContentType="text/html"
    )

    return {
        "statusCode": 200,
        "body": f"HTML page updated successfully. Path: {target_key}",
    }


if __name__ == "__main__":
    print("Running lambda_handler")
    lambda_handler(None, None)
