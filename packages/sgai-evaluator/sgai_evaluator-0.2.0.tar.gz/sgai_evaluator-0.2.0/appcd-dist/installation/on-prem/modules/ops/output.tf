output "ops_arn" {
  value = aws_iam_role.ops_oidc_auth_role.arn
}

output "k8s_user" {
  value = local.k8s_user
}

output "role_id" {
  value = aws_iam_role.ops_oidc_auth_role.id
}
