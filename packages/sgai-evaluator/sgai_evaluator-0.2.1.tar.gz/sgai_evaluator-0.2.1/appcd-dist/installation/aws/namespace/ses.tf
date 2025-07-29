resource "aws_ses_domain_identity" "email" {
  domain = var.host_domain
}

locals {
  ses_secret_key = "${var.namespace}-smtp-user_v2"
}


### MAIL_FROM setup

resource "aws_ses_domain_mail_from" "email" {
  domain           = aws_ses_domain_identity.email.domain
  mail_from_domain = "support.${aws_ses_domain_identity.email.domain}"
}

### Blanket sender policy
data "aws_iam_policy_document" "sender" {
  statement {
    sid       = "SendEmail"
    actions   = ["ses:SendRawEmail"]
    resources = ["*"]
    condition {
      test     = "StringLike"
      variable = "ses:FromAddress"
      values   = ["*@${aws_ses_domain_mail_from.email.mail_from_domain}"]
    }
  }
}

resource "aws_iam_policy" "sender" {
  name   = "${var.namespace}-email-sender"
  policy = data.aws_iam_policy_document.sender.json
  tags   = local.tags
}


// create a ses user for smtp config
resource "aws_iam_user" "ses_smtp_user" {
  name = "ses-smtp-user-${var.namespace}"
  tags = local.tags
}

resource "aws_iam_user_policy_attachment" "ses_smtp_user" {
  user       = aws_iam_user.ses_smtp_user.name
  policy_arn = aws_iam_policy.sender.arn
}

resource "aws_iam_access_key" "smtp_user" {
  user = aws_iam_user.ses_smtp_user.name
}

// store the smtp username and password in the secret manager
resource "aws_secretsmanager_secret" "ses_smtp_user" {
  name = local.ses_secret_key
  tags = local.tags
}

resource "aws_secretsmanager_secret_version" "ses_smtp_user" {
  secret_id = aws_secretsmanager_secret.ses_smtp_user.id
  secret_string = jsonencode({
    username                    = aws_iam_access_key.smtp_user.id,
    password                    = aws_iam_access_key.smtp_user.ses_smtp_password_v4,
    host                        = "email-smtp.${var.region}.amazonaws.com",
    troubleshooting_sender_mail = "support@${aws_ses_domain_mail_from.email.mail_from_domain}"
    tags                        = local.tags
  })
}
