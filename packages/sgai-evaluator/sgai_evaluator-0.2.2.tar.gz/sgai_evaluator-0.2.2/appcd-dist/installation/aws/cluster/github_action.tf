resource "aws_iam_openid_connect_provider" "github" {
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = ["6938fd4d98bab03faadb97b34396831e3780aea1"]
  url             = "https://token.actions.githubusercontent.com"
}

# The values field under condition is used to allow access for workflow triggered from specific repo and environment or branch or tag or "pull_request"
# For more info @ https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect#example-subject-claims
data "aws_iam_policy_document" "github_assume_role_policy" {
  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]
    effect  = "Allow"

    condition {
      test     = "StringLike"
      variable = "${replace(aws_iam_openid_connect_provider.github.url, "https://", "")}:sub"
      values   = ["repo:appcd-dev/appcd-dist:*"]
    }

    principals {
      identifiers = [aws_iam_openid_connect_provider.github.arn]
      type        = "Federated"
    }
  }
}

# Create a role policy that would allow fetching cluster info.
# This would help us avoid storing cluster's kube config in GitHub Action's secrets
resource "aws_iam_role_policy" "github_oidc_eks_policy" {
  name = "${var.suffix}-github-oidc-eks-policy"
  role = aws_iam_role.github_oidc_auth_role.id

  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Sid" : "DescribeCluster",
        "Effect" : "Allow",
        "Action" : "eks:DescribeCluster",
        "Resource" : "arn:aws:eks:*:*:cluster/*"
      },
      {
        "Sid" : "ListClusters",
        "Effect" : "Allow",
        "Action" : "eks:ListClusters",
        "Resource" : "*"
      }
    ]
  })
}

# Creating a role. It will used as value to role_to_assume for Configure AWS Crendentials action.
resource "aws_iam_role" "github_oidc_auth_role" {
  assume_role_policy = data.aws_iam_policy_document.github_assume_role_policy.json
  name               = "${var.suffix}-github-oidc-auth-role"
}


resource "kubernetes_cluster_role" "github_oidc_cluster_role" {
  metadata {
    name = "github-oidc-cluster-role"
  }

  rule {
    api_groups = ["*"]
    resources  = ["configmaps", "secrets", "horizontalpodautoscalers", "ingresses", "servicemonitors", "services", "deployments", "serviceaccounts"]
    verbs      = ["get", "watch", "update", "patch", "create", "list"]
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


resource "kubernetes_cluster_role_binding" "github_oidc_cluster_role_binding" {
  metadata {
    name = "github-oidc-cluster-role-binding"
  }

  subject {
    kind      = "User"
    name      = "github-oidc-auth-user"
    api_group = "rbac.authorization.k8s.io"
  }

  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "ClusterRole"
    name      = kubernetes_cluster_role.github_oidc_cluster_role.metadata[0].name
  }
}
