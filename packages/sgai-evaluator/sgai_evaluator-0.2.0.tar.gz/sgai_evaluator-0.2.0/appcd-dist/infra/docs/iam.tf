resource "aws_iam_openid_connect_provider" "github" {
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = ["a031c46782e6e6c662c2c87c76da9aa62ccabd8e"]
  url             = "https://token.actions.githubusercontent.com"
}

resource "aws_iam_role" "github_actions_role" {
  name = "GitHubActionsRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Federated = aws_iam_openid_connect_provider.github.arn
        },
        Action = "sts:AssumeRoleWithWebIdentity",
        Condition = {
          "ForAnyValue:StringLike" = {
            "token.actions.githubusercontent.com:sub" : [
              "repo:appcd-dev/appcd-dist:ref:refs/heads/main",
              "repo:appcd-dev/appcd-dist:pull_request",
              "repo:appcd-dev/appcd-dist:ref:refs/tags/*",
              "repo:appcd-dev/license-manager:ref:refs/heads/main",
              "repo:appcd-dev/license-manager:ref:refs/tags/*",
              "repo:appcd-dev/cloud2code:ref:refs/heads/main",
              "repo:appcd-dev/cloud2code:ref:refs/tags/*",
              "repo:appcd-dev/appcd:ref:refs/tags/*",
              "repo:appcd-dev/external-docs:ref:refs/heads/main",
              "repo:appcd-dev/external-docs:pull_request",
              "repo:appcd-dev/external-docs:ref:refs/tags/*",
            ]
          }
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "github_actions_policy" {
  role = aws_iam_role.github_actions_role.name

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "s3:Put*",
          "s3:Get*",
          "s3:DeleteObject*",
          "s3:List*"
        ],
        Resource = [
          "${aws_s3_bucket.docs_bucket.arn}",
          "${aws_s3_bucket.docs_bucket.arn}/*",
          "${aws_s3_bucket.staging_bucket.arn}",
          "${aws_s3_bucket.staging_bucket.arn}/*",
          "${aws_s3_bucket.ent_docs_bucket.arn}",
          "${aws_s3_bucket.ent_docs_bucket.arn}/*",
          
          "arn:aws:s3:::appcd-public-releases",
          "arn:aws:s3:::appcd-public-releases/*",

          "arn:aws:s3:::stackgen-public-releases",
          "arn:aws:s3:::stackgen-public-releases/*",
        ]
      }
    ]
  })
}

// Outputs
output "github_actions_role_arn" {
  value = aws_iam_role.github_actions_role.arn
}
