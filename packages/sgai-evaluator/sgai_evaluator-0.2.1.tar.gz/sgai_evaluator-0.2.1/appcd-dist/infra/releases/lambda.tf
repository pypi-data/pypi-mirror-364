resource "aws_iam_role" "lambda_role" {
  name = "appcd_lambda_releases_sync_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Effect = "Allow",
        Principal = {
          Service = "lambda.amazonaws.com"
        },
      },
    ],
  })
}

# IAM policy for the Lambda function to access S3
resource "aws_iam_policy" "lambda_policy" {
  name        = "appcd_lambda_releases_sync_policy"
  description = "IAM policy for appcd lambda function to access S3"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = [
          "s3:List*",
        ],
        Effect   = "Allow",
        Resource = ["*"],
      },
    ],
  })
}

# Attach the policy to the role
resource "aws_iam_role_policy_attachment" "lambda_attach" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_policy.arn
}

# Attach basic execution policy to the role
resource "aws_iam_role_policy_attachment" "lambda_exec_attach" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/AWSLambdaExecute"
}

# Lambda deployment package
data "archive_file" "lambda" {
  type        = "zip"
  source_file = "s3_upload_lambda.py"
  output_path = "lambda_function.zip"
}

# Lambda function
resource "aws_lambda_function" "appcd_lambda" {
  function_name = "appcd_lambda_releases_sync"
  role          = aws_iam_role.lambda_role.arn

  filename         = "lambda_function.zip"
  source_code_hash = data.archive_file.lambda.output_base64sha256
  handler          = "s3_upload_lambda.lambda_handler"
  runtime          = "python3.8"

  reserved_concurrent_executions = 1

  # Environment variables
  environment {
    variables = {
      BUCKET_NAME    = aws_s3_bucket.bucket.id
      DIRECTORY_NAME = "appcd-dist"
    }
  }
}

# Cloudwatch log group for the lambda function
resource "aws_cloudwatch_log_group" "lambda_log_group" {
  name              = "/aws/lambda/${aws_lambda_function.appcd_lambda.function_name}"
  retention_in_days = 14
}

# Lambda permission for S3 to invoke the function
resource "aws_lambda_permission" "allow_bucket" {
  statement_id  = "AllowExecutionFromS3Bucket"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.appcd_lambda.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.bucket.arn
}

# S3 event notification to trigger the Lambda function
resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket = aws_s3_bucket.bucket.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.appcd_lambda.arn
    events              = ["s3:ObjectCreated:*", "s3:ObjectRemoved:*"]
    filter_prefix       = "appcd-dist/"
    filter_suffix       = ".zip"
  }

  depends_on = [aws_lambda_function.appcd_lambda, aws_lambda_permission.allow_bucket]
}

# Outputs
output "lambda_function_name" {
  value = aws_lambda_function.appcd_lambda.function_name
}
