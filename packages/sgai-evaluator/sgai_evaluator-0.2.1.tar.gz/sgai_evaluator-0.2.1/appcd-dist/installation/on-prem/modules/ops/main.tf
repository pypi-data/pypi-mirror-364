locals {
  user     = "${var.prefix}-stackgen-cicd"
  k8s_user = "ops-provider-auth-user"
}
data "aws_iam_openid_connect_provider" "existing" {
  url = var.oidc_provider.url
}

resource "aws_iam_openid_connect_provider" "ops_provider" {
  count           = length(data.aws_iam_openid_connect_provider.existing.arn) > 0 ? 0 : 1
  client_id_list  = [var.oidc_provider.client_id_list]
  thumbprint_list = [var.oidc_provider.thumbprint_list]
  url             = var.oidc_provider.url
  lifecycle {
    ignore_changes = [client_id_list, thumbprint_list]
  }
}

locals {
  ops_provider_arn = coalesce(
    try(data.aws_iam_openid_connect_provider.existing.arn, null),
    try(aws_iam_openid_connect_provider.ops_provider[0].arn, null)
  )
  ops_provider_url = coalesce(
    try(data.aws_iam_openid_connect_provider.existing.url, null),
    try(aws_iam_openid_connect_provider.ops_provider[0].url, null)
  )
}

# The values field under condition is used to allow access for workflow triggered from specific repo and environment or branch or tag or "pull_request"
# For more info @ https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect#example-subject-claims
data "aws_iam_policy_document" "ops_assume_role_policy" {
  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]
    effect  = "Allow"

    condition {
      test     = var.assume_role_policy.test
      variable = var.assume_role_policy.variable
      values   = var.assume_role_policy.values
    }

    principals {
      identifiers = [local.ops_provider_arn]
      type        = "Federated"
    }
  }
}

# Creating a role. It will used as value to role_to_assume for Configure AWS Crendentials action.
resource "aws_iam_role" "ops_oidc_auth_role" {
  assume_role_policy = data.aws_iam_policy_document.ops_assume_role_policy.json
  name               = "${local.user}-auth-role"
}


resource "kubernetes_cluster_role" "ops_cluster_role" {
  metadata {
    name = "${local.user}-cluster-role"
  }

  rule {
    api_groups = ["*"]
    resources  = ["configmaps", "secrets", "horizontalpodautoscalers", "ingresses", "", "services", "deployments", "serviceaccounts"]
    verbs      = ["get", "watch", "update", "patch", "create"]
  }

  rule {
    api_groups = ["monitoring.coreos.com"]
    resources  = ["servicemonitors", "alertmanagerconfigs", "prometheusrules"]
    verbs      = ["get", "watch", "update", "patch", "create"]
  }

  rule {
    api_groups = ["batch"]
    resources  = ["jobs"]
    verbs      = ["create", "list", "get", "delete", "watch"]
  }

  rule {
    api_groups = ["*"]
    resources  = ["secrets", "configmaps"]
    verbs      = ["delete", "list", "create"]
  }

  rule {
    api_groups = ["*"]
    resources  = ["pods", "replicasets", "services"]
    verbs      = ["watch", "list"]
  }
}


resource "kubernetes_cluster_role_binding" "ops_cluster_role_binding" {
  metadata {
    name = "${local.user}-cluster-role-binding"
  }

  subject {
    kind      = "User"
    name      = local.k8s_user
    api_group = "rbac.authorization.k8s.io"
  }

  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "ClusterRole"
    name      = kubernetes_cluster_role.ops_cluster_role.metadata[0].name
  }
}
