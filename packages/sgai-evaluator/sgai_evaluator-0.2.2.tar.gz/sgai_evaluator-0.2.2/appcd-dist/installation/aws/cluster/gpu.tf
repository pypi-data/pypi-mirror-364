module "eks_data_addons" {
  count   = var.enable_gpu ? 1 : 0
  source  = "aws-ia/eks-data-addons/aws"
  version = "1.33.0"

  oidc_provider_arn = module.eks.oidc_provider_arn

  # Example to deploy EFA K8s Device Plugin for GPU/Neuron instances
  enable_aws_efa_k8s_device_plugin = true

  # Example to deploy NVIDIA GPU Operator
  enable_nvidia_gpu_operator = true

  #   nvidia_device_plugin_helm_config = {
  #     version: "0.15.0"
  #   }

  nvidia_gpu_operator_helm_config = {
    version = "v24.3.0"
    set = [
      {
        name  = "operator.defaultRuntime"
        value = "containerd"
      },
      {
        name : "securityContext.privileged",
        value : false
      }
    ]
  }
}

resource "helm_release" "nvidia_device_plugin" {
  count            = var.enable_gpu ? 1 : 0
  name             = "nvidia-device-plugin"
  repository       = "https://nvidia.github.io/k8s-device-plugin"
  chart            = "nvidia-device-plugin"
  version          = "0.15.0"
  namespace        = "nvidia-device-plugin"
  create_namespace = true
  wait             = false
  values = [
    <<-EOT
      runtimeClassName: nvidia
      affinity:
        nodeAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            nodeSelectorTerms:
            - matchExpressions:
              - key: 'nvidia.com/gpu.present'
                operator: In
                values:
                - 'true'
    EOT
  ]
}

resource "kubernetes_runtime_class_v1" "nvidia" {
  count = var.enable_gpu ? 1 : 0
  metadata {
    name = "nvidia"
  }
  handler = "nvidia"
}

resource "kubernetes_manifest" "gpu_node_pool" {
  count      = var.enable_gpu ? 1 : 0
  depends_on = [kubernetes_manifest.node_class]
  manifest = {
    apiVersion = "karpenter.sh/v1beta1"
    kind       = "NodePool"
    metadata = {
      name = "gpus"
    }
    spec = {
      template = {
        spec = {
          taints = [
            {
              key    = "nvidia.com/gpu"
              value  = "Exists"
              effect = "NoSchedule"
            }
          ]
          #   labels = {
          #     "nvidia.com/gpu.present" = "true"
          #     "gpu-type" = "nvidia"
          #   }
          nodeClassRef = {
            name = kubernetes_manifest.node_class.manifest.metadata.name
          }
          requirements = [
            {
              key      = "karpenter.k8s.aws/instance-family"
              operator = "In"
              values   = ["g4dn", "g4dn", "g5"]
            },
            {
              key      = "kubernetes.io/arch"
              operator = "In"
              values   = ["amd64"]
            },
            {
              key      = "karpenter.sh/capacity-type"
              operator = "In"
              values   = ["spot", "on-demand"]
            }
          ]
        }
      }
      disruption = {
        consolidationPolicy = "WhenUnderutilized"
        expireAfter         = "720h" # 30 * 24h = 48h
      }
      limits = {
        "nvidia.com/gpu" = 4
        cpu              = 12000
      }
    }
  }
}
