
resource "kubernetes_config_map" "dex_configmap" {
  metadata {
    name      = "dex-configmap"
    namespace = var.namespace
  }
  data = {
    stylecss : templatefile("${path.module}/values/dex/style.css", {})
    header : templatefile("${path.module}/values/dex/header.html", {})
    footer : templatefile("${path.module}/values/dex/footer.html", {})
    login : templatefile("${path.module}/values/dex/login.html", {})
  }
}

resource "helm_release" "dex" {
  depends_on = [
    kubernetes_config_map.dex_configmap
  ]
  count      = var.appcd_authentication.type == "none" ? 0 : 1
  name       = "dex"
  repository = "https://charts.dexidp.io"
  chart      = "dex"
  namespace  = var.namespace
  version    = "0.19.1"
  values = [
    templatefile("${path.module}/values/dex.yaml", {
      host_domain               = var.domain,
      appcd_authentication_type = var.appcd_authentication.type
      appcd_authentication_config = indent(8, yamlencode(merge({
        redirectURI : "https://${var.domain}/auth/callback"
      }, var.appcd_authentication.config))),
      rds_endpoint = module.db.db_instance_address
    })
  ]
}
