output "configure_kubectl" {
  description = "Configure kubectl: make sure you're logged in with the correct AWS profile and run the following command to update your kubeconfig"
  value       = "aws eks --region ${var.region} update-kubeconfig --name ${module.eks.cluster_name}"
}

output "eks_sg_id" {
  description = "The security group for the EKS cluster"
  value       = module.eks.node_security_group_id
}

output "vpc_id" {
  description = "The VPC ID"
  value       = module.vpc.vpc_id
}

output "database_subnet_group_name" {
  description = "database subnet group name"
  value       = module.vpc.database_subnet_group_name
}

output "cluster_endpoint" {
  description = "k8s host value"
  value       = module.eks.cluster_endpoint
}

output "cluster_certificate_authority_data" {
  description = "k8s cluster_ca_certificate value"
  value       = base64decode(module.eks.cluster_certificate_authority_data)
}

output "cluster_name" {
  description = "k8s cluster_name"
  value       = module.eks.cluster_name
}

output "oidc_provider_arn" {
  description = "k8s oidc_provider_arn"
  value       = module.eks.oidc_provider_arn
}

output "azs" {
  description = "vpc azs"
  value       = module.vpc.azs
}
