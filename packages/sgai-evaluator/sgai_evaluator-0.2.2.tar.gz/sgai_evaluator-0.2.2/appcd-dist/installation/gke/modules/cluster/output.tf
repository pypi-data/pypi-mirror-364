
output "vpc_network_id" {
  value = module.vpc.network_id
}

output "cluster_name" {
  description = "The name of the cluster"
  value       = module.gke.name
}

output "cluster_endpoint" {
  description = "The endpoint of the GKE cluster"
  value       = module.gke.endpoint
}

output "cluster_ca_certificate" {
  description = "The Kubernetes Cluster CA Certificate"
  value       = module.gke.ca_certificate
}

output "cluster_access_token" {
  description = "The Kubernetes Cluster Access Token"
  value       = data.google_client_config.default.access_token
  sensitive   = true
}

output "network_self_link" {
  description = "The self link of the network"
  value       = module.vpc.network_self_link
}

output "nodes_subnet" {
  description = "The IP range for the pods in the cluster"
  value       = local.cluster_ip_ranges.nodes
}
