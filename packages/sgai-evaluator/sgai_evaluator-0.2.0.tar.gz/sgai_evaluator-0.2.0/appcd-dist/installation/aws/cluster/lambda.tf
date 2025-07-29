# ================== AWS Lambda Function ================== #
resource "aws_lambda_function" "cloudwatch_lambda" {
  depends_on       = [module.eks]
  function_name    = "cloudwatch-alert-lambda-go-${var.suffix}"
  filename         = "function.zip"
  source_code_hash = filebase64sha256("function.zip")
  role             = aws_iam_role.lambda_exec.arn
  handler          = "main"
  runtime          = "provided.al2"
  timeout          = 30
  memory_size      = 1024

  tags = local.tags

  environment {
    variables = {
      SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/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" # Replace with your Slack Webhook URL
      LOG_GROUP_NAME    = "/aws/containerinsights/${module.eks.cluster_name}/application"
      ENVIRONMENT       = "${module.eks.cluster_name}"
    }
  }
}

# ================== IAM Role for Lambda ================== #
resource "aws_iam_role" "lambda_exec" {
  name = "lambda_exec_role_${var.suffix}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

# Attach CloudWatch Logs Access Policy to Lambda Role
resource "aws_iam_policy_attachment" "lambda_logs" {
  name       = "lambda_logs_attachment_${var.suffix}"
  roles      = [aws_iam_role.lambda_exec.name]
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchLogsFullAccess"
}

# ================== CloudWatch Event Rule (Scheduled Trigger) ================== #
resource "aws_cloudwatch_event_rule" "weekly_rule" {
  name                = "weekly-lambda-trigger-${var.suffix}"
  schedule_expression = "cron(0 8 ? * SUN *)" # Runs every Sunday at 8 AM UTC
  tags                = local.tags
}

# Attach CloudWatch Event Rule to Lambda Function
resource "aws_cloudwatch_event_target" "lambda_target" {
  rule      = aws_cloudwatch_event_rule.weekly_rule.name
  target_id = "lambda-function"
  arn       = aws_lambda_function.cloudwatch_lambda.arn
}

# ================== Allow CloudWatch to Invoke Lambda ================== #
resource "aws_lambda_permission" "allow_cloudwatch" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.cloudwatch_lambda.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.weekly_rule.arn
}
