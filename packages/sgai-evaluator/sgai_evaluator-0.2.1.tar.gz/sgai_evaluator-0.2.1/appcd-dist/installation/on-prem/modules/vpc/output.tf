output "configure_kubectl" {
  description = "Configure kubectl: make sure you're logged in with the correct AWS profile and run the following command to update your kubeconfig"
  value       = "aws eks --region ${var.region} update-kubeconfig --name ${module.eks.cluster_name}"
}

output "cluster_endpoint" {
  description = "EKS cluster information"
  value       = module.eks.cluster_endpoint
}

output "cluster_name" {
  description = "EKS cluster information"
  value       = module.eks.cluster_name
}

output "cluster_certificate_authority_data" {
  description = "EKS cluster information"
  value       = module.eks.cluster_certificate_authority_data
}

output "karpenter_iam_role_name" {
  description = "The IAM role name for Karpenter"
  value       = local.karpenter_iam_role_name
}

output "cluster_version" {
  description = "The Kubernetes version for the EKS cluster"
  value       = module.eks.cluster_version
}

output "oidc_provider_arn" {
  description = "The OIDC provider ARN for the EKS cluster"
  value       = module.eks.oidc_provider_arn
}

output "db-subnet-group" {
  description = "The RDS subnet group name"
  value       = module.vpc.database_subnet_group
}

output "database_subnets" {
  description = "The RDS subnet group"
  value       = module.vpc.database_subnets
}

output "eks_sg_id" {
  description = "The RDS security group"
  value       = module.eks.node_security_group_id
}

output "azs" {
  description = "value of availability zones"
  value       = module.vpc.azs
}

output "database_security_group_id" {
  description = "value of security group ids"
  value       = [aws_security_group.rds_sg.id]
}

output "nat_public_ips" {
  description = "value of vpc cidr block"
  value       = module.vpc.nat_public_ips
}

output "pvc_name" {
  value       = local.pv_name
  description = "The name of the PVC"
}
