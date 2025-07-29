output "aks_setup" {
  value = module.aks.aks_setup
}

output "nginx_ingress_ip" {
  value = local.public_ip
}

output "NOTES" {
  value = <<-EOT
  To access the Kubernetes dashboard run the following command:
  ${module.aks.aks_setup}
  EOT
}

output "helm_upgrade_command" {
  value = "helm upgrade --wait --install appcd appcd-dist-${var.appcd_version}.tgz --namespace ${var.namespace} --values ${local_file.appcd_yaml.filename} --values ${path.module}/values/images.yaml"
}
