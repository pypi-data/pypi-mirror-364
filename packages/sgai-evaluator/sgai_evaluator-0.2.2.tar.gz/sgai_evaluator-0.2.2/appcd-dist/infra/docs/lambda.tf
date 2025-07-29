/*
  We have 2 lambda functions used to support the docs site.
  - index_url_rewrite = This function is used to rewrite URLs to support directory level URIs
  - basic_auth = This function is used to add basic auth to the docs site and includes the same functionality as index_url_rewrite
 */

// Common Resources between functions
resource "aws_iam_role" "lambda_exec_role" {
  name = "lambda_execution_role"

  assume_role_policy = data.aws_iam_policy_document.assume_role_policy_doc.json
}

data "aws_iam_policy_document" "assume_role_policy_doc" {
  statement {
    sid    = "AllowAwsToAssumeRole"
    effect = "Allow"

    actions = ["sts:AssumeRole"]

    principals {
      type = "Service"

      identifiers = [
        "edgelambda.amazonaws.com",
        "lambda.amazonaws.com",
      ]
    }
  }
}

resource "aws_iam_role_policy_attachment" "lambda_exec_attach" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = "arn:aws:iam::aws:policy/AWSLambdaExecute"
}


// Index URL Rewrite Lambda Function resources
data "archive_file" "index_url_rewrite" {
  type        = "zip"
  source_file = "index_url_rewrite.py"
  output_path = "index_url_rewrite.zip"
}

resource "aws_lambda_function" "docs_edge_lambda" {
  function_name = "indexURLRewriteLambda"
  role          = aws_iam_role.lambda_exec_role.arn
  handler       = "index_url_rewrite.lambda_handler"
  runtime       = "python3.8"
  filename      = "${path.module}/index_url_rewrite.zip"
  publish       = true

  source_code_hash = data.archive_file.index_url_rewrite.output_base64sha256
  provider         = aws.us-east-1

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_cloudwatch_log_group" "lambda_log_group" {
  name              = "/aws/lambda/${aws_lambda_function.docs_edge_lambda.function_name}"
  retention_in_days = 14
  provider          = aws.us-east-1
}

// Basic Auth Lambda Function resources
data "archive_file" "basic_auth_lambda" {
  type        = "zip"
  source_file = "basic_auth_lambda.py"
  output_path = "basic_auth_lambda.zip"
}

resource "aws_lambda_function" "basic_auth_lambda" {
  function_name = "basicAuthLambda"
  role          = aws_iam_role.lambda_exec_role.arn
  handler       = "basic_auth_lambda.lambda_handler"
  runtime       = "python3.8"
  filename      = "${path.module}/basic_auth_lambda.zip"
  publish       = true

  source_code_hash = data.archive_file.basic_auth_lambda.output_base64sha256
  provider         = aws.us-east-1
}

resource "aws_cloudwatch_log_group" "basic_auth_lambda" {
  name              = "/aws/lambda/${aws_lambda_function.basic_auth_lambda.function_name}"
  retention_in_days = 14
  provider          = aws.us-east-1
}
