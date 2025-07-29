
locals {
  k8s_read_readonly_group = "developer-readonly"
}
# Developer readonly access RBAC configuration

resource "kubernetes_cluster_role" "developer_readonly" {
  metadata {
    name = local.k8s_read_readonly_group
    labels = {
      "app.kubernetes.io/name"    = local.k8s_read_readonly_group
      "app.kubernetes.io/part-of" = "appcd"
    }
  }

  rule {
    api_groups = [""]
    resources  = ["*"]
    verbs      = ["get", "list", "watch"]
  }
}

resource "kubernetes_cluster_role_binding" "developer_readonly" {
  metadata {
    name = local.k8s_read_readonly_group
    labels = {
      "app.kubernetes.io/name"    = local.k8s_read_readonly_group
      "app.kubernetes.io/part-of" = "appcd"
    }
  }

  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "ClusterRole"
    name      = kubernetes_cluster_role.developer_readonly.metadata[0].name
  }

  subject {
    kind      = "Group"
    name      = local.k8s_read_readonly_group
    api_group = "rbac.authorization.k8s.io"
  }
}
