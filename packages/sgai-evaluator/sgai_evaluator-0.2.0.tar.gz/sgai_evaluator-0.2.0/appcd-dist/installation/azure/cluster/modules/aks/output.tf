output "aks_setup" {
  value = "az aks get-credentials --resource-group ${var.resource_group} --name ${module.aks.aks_name} --overwrite-existing --admin"
}

output "aks_name" {
  value = module.aks.aks_name
}

output "kubeconfig" {
  value     = module.aks.kube_config_raw
  sensitive = true
}

output "client_certificate" {
  value = module.aks.client_certificate
}

output "client_key" {
  value = module.aks.client_key
}

output "cluster_ca_certificate" {
  value = module.aks.cluster_ca_certificate
}

output "host" {
  value = module.aks.host
}

output "username" {
  value     = module.aks.username
  sensitive = true
}

output "password" {
  sensitive = true
  value     = module.aks.password
}

output "virtual_network" {
  value = module.network
}

output "postgresql" {
  value = azurerm_postgresql_flexible_server.postgresql
}
