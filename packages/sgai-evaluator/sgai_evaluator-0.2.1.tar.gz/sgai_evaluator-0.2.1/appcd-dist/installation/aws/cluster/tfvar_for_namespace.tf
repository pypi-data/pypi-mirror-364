
locals {
  tfVars = <<EOF
region                             = "${var.region}"
azs                                = ${format("[\"%s\"]", join("\",\"", local.azs))}
cluster_certificate_authority_data = "${module.eks.cluster_certificate_authority_data}"
cluster_endpoint                   = "${module.eks.cluster_endpoint}"
cluster_name                       = "${module.eks.cluster_name}"
database_subnet_group_name         = "${module.vpc.database_subnet_group_name}"
vpc_id                             = "${module.vpc.vpc_id}"
eks_sg_id                          = "${module.eks.node_security_group_id}"
data_bucket_name                   = "${aws_s3_bucket.csi-backend.bucket}"
alerts_sns_topic_arn               = "${aws_sns_topic.alerts.arn}"
EOF
}

resource "local_file" "tf_vars" {
  filename = "../terraform.tfvars"
  content  = local.tfVars
}

# make an secret manager entry for the tfvars
resource "aws_secretsmanager_secret" "tf_vars" {
  name = "/cluster/${var.suffix}/tf_vars"
}

resource "aws_secretsmanager_secret_version" "tf_vars" {
  secret_id     = aws_secretsmanager_secret.tf_vars.id
  secret_string = local.tfVars
}

output "tf_vars" {
  description = "tfvars"
  value       = local.tfVars
}

output "tf_vars_for_namespace" {
  description = "command to get the secret manager entry for the tfvars"
  value       = "aws secretsmanager get-secret-value --secret-id ${aws_secretsmanager_secret.tf_vars.id} --region ${var.region} --query SecretString --output text"
}
