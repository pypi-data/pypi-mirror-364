resource "helm_release" "ollama" {
  // only enable if GPU is enabled
  // blocker issue on nvidia operator: NVIDIA/gpu-operator#755
  count      = var.enable_gpu ? 1 : 0
  depends_on = [kubernetes_namespace.appcd]
  name       = "ollama"
  repository = "https://otwld.github.io/ollama-helm/"
  chart      = "ollama"
  namespace  = local.namespace
  values = [
    templatefile("${path.module}/values/ollama/values.yaml", {
      enable_gpu = var.enable_gpu
    })
  ]
}
