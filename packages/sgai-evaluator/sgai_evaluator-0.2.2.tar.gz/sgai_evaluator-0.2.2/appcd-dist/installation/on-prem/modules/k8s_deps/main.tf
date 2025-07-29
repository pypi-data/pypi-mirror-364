terraform {
  required_version = ">= 0.13"

  required_providers {
    kubectl = {
      source  = "alekc/kubectl"
      version = ">= 2.0.0"
    }
  }
}

locals {
  karpenter_version     = "1.4.0"
  karpenter_namespace   = "karpenter"
  temporal_helm_version = "0.57.0"
  tags = merge(var.tags, {
    "appcd_module" = "k8s_deps"
  })
  karpenter_iam_role_name = format("karpenter-for-%s", var.cluster_name)
  db_username             = "postgres"
  db_password             = random_id.this.hex
  temporal_namespace      = var.namespace
}

provider "helm" {
  kubernetes {
    host                   = var.cluster_endpoint
    cluster_ca_certificate = base64decode(var.cluster_certificate_authority_data)

    exec {
      api_version = "client.authentication.k8s.io/v1beta1"
      command     = "aws"
      args        = ["eks", "get-token", "--cluster-name", var.cluster_name]
    }
  }
}

provider "kubernetes" {
  host                   = var.cluster_endpoint
  cluster_ca_certificate = base64decode(var.cluster_certificate_authority_data)

  exec {
    api_version = "client.authentication.k8s.io/v1beta1"
    command     = "aws"
    args        = ["eks", "get-token", "--cluster-name", var.cluster_name]
  }
}

provider "kubectl" {
  apply_retry_count      = 5
  host                   = var.cluster_endpoint
  cluster_ca_certificate = base64decode(var.cluster_certificate_authority_data)
  load_config_file       = false

  exec {
    api_version = "client.authentication.k8s.io/v1beta1"
    command     = "aws"
    # This requires the awscli to be installed locally where Terraform is executed
    args = ["eks", "get-token", "--cluster-name", var.cluster_name]
  }
}

locals {
  eks_addon_base = {
    kube-proxy = {
      most_recent = true
    }
  }
  eks_addons = merge(local.eks_addon_base)
}

data "aws_region" "current" {}

locals {
  region = data.aws_region.current.name
  aws_for_fluentbit = {
    enable_containerinsights = var.enable_ops
    kubelet_monitoring       = var.enable_ops
    set = [{
      name  = "cloudWatchLogs.autoCreateGroup"
      value = true
      },
      {
        name  = "hostNetwork"
        value = true
      },
      {
        name  = "dnsPolicy"
        value = "ClusterFirstWithHostNet"
      },
      {
        name  = "cloudwatch.logRetentionDays"
        value = 30
      }
    ]
    application_log_conf = <<-EOT
        [INPUT]
            Name tail
            Tag application.*
            Exclude_Path /var/log/containers/cloudwatch-agent*, /var/log/containers/fluent-bit*, /var/log/containers/aws-node*, /var/log/containers/kube-proxy*
            Path /var/log/containers/*.log
            multiline.parser docker, cri
            DB /var/fluent-bit/state/flb_container.db
            Mem_Buf_Limit 50MB
            Skip_Long_Lines On
            Refresh_Interval 10
            Rotate_Wait 30
            storage.type filesystem
            Read_from_Head Off

        [INPUT]
            Name tail
            Tag application.*
            Path /var/log/containers/fluent-bit*
            multiline.parser docker, cri
            DB /var/fluent-bit/state/flb_log.db
            Mem_Buf_Limit 5MB
            Skip_Long_Lines On
            Refresh_Interval 10
            Read_from_Head Off

        [INPUT]
            Name tail
            Tag application.*
            Path /var/log/containers/cloudwatch-agent*
            multiline.parser docker, cri
            DB /var/fluent-bit/state/flb_cwagent.db
            Mem_Buf_Limit 5MB
            Skip_Long_Lines On
            Refresh_Interval 10
            Read_from_Head Off

        [FILTER]
            Name kubernetes
            Match application.*
            Kube_URL https://kubernetes.default.svc:443
            Kube_Tag_Prefix application.var.log.containers.
            Merge_Log On
            Merge_Log_Key log_processed
            K8S-Logging.Parser On
            K8S-Logging.Exclude On
            Labels Off
            Annotations Off
            Use_Kubelet On
            Kubelet_Port 10250
            Buffer_Size 0

        [OUTPUT]
            Name cloudwatch_logs
            Match application.*
            region ${local.region}
            log_group_name /aws/containerinsights/${var.cluster_name}/application
            log_stream_prefix $${HOSTNAME}-
            auto_create_group true
            extra_user_agent container-insights
            workers 1
      EOT
  }

  loadbalancer_range = length(var.lb_cidr_blocks) != 0 ? [{
    name  = "controller.service.loadBalancerSourceRanges"
    value = "{${join(",", var.lb_cidr_blocks)}}",
  }] : []
}

module "eks_blueprints_addons" {
  source  = "aws-ia/eks-blueprints-addons/aws"
  version = "1.21.0"

  cluster_name      = var.cluster_name
  cluster_endpoint  = var.cluster_endpoint
  cluster_version   = var.cluster_version
  oidc_provider_arn = var.oidc_provider_arn

  enable_ingress_nginx         = true
  enable_kube_prometheus_stack = var.enable_ops
  enable_metrics_server        = var.enable_ops
  enable_aws_for_fluentbit     = var.enable_ops

  ## Karpeneter configurations
  enable_karpenter                           = true
  karpenter_enable_spot_termination          = true
  karpenter_enable_instance_profile_creation = true
  karpenter_node = {
    create_iam_role          = true
    iam_role_use_name_prefix = false
    iam_role_name            = local.karpenter_iam_role_name
    iam_role_additional_policies = [
      "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
    ]
  }
  karpenter = {
    chart_version   = local.karpenter_version
    namespace       = local.karpenter_namespace
    upgrade_install = true
    wait            = true
    skip_crds       = true
    chart_version   = local.karpenter_version
    set = [
      {
        name  = "settings.featureGates.drift"
        value = true
      },
      {
        name  = "settings.featureGates.spotToSpotConsolidation"
        value = true
      }
    ]
  }

  aws_for_fluentbit_cw_log_group = {
    retention_in_days = 30
  }
  aws_for_fluentbit = local.aws_for_fluentbit

  eks_addons = local.eks_addons

  ingress_nginx = {
    repository = "oci://ghcr.io/nginxinc/charts"
    chart      = "nginx-ingress"

    chart_version = "1.2.2"
    set = concat(local.loadbalancer_range, [
      {
        name  = "controller.image.repository"
        value = "ghcr.io/appcd-dev/nginx/nginx-ingress"
      },
      {
        name  = "controller.service.annotations.service\\.beta\\.kubernetes\\.io/aws-load-balancer-type"
        value = "nlb"
      },
      {
        name  = "controller.service.annotations.service\\.beta\\.kubernetes\\.io/aws-load-balancer-ssl-ports"
        value = "https"
      },
      {
        name  = "controller.service.httpsPort.targetPort"
        value = "80"
      },
      {
        name  = "controller.service.annotations.service\\.beta\\.kubernetes\\.io/aws-load-balancer-scheme"
        value = "internet-facing"
      },
      {
        name  = "controller.service.annotations.service\\.beta\\.kubernetes\\.io/aws-load-balancer-nlb-target-type"
        value = "instance"
      },
      {
        name  = "controller.service.annotations.service\\.beta\\.kubernetes\\.io/aws-load-balancer-target-group-attributes"
        value = "preserve_client_ip.enabled=true"
      },
      {
        name  = "controller.service.annotations.service\\.beta\\.kubernetes\\.io/aws-load-balancer-ssl-cert"
        value = var.load-balancer-ssl-cert-arn
      },
      {
        name  = "controller.service.annotations.service\\.beta\\.kubernetes\\.io/aws-load-balancer-backend-protocol"
        value = "http"
      },
      {
        name  = "controller.service.annotations.service\\.beta\\.kubernetes\\.io/aws-load-balancer-attributes"
        value = "deletion_protection.enabled=true"
      },
      {
        name  = "controller.kind"
        value = "daemonset"
      },
      {
        name  = "controller.enableSnippets"
        value = "true"
      },
    ])
  }
  tags = local.tags
}

resource "kubernetes_namespace" "this" {
  metadata {
    name = var.namespace
  }
}

resource "kubernetes_secret" "ghcr_pkg" {
  depends_on = [kubernetes_namespace.this]
  metadata {
    name      = "ghcr-pkg"
    namespace = var.namespace
  }

  data = {
    ".dockerconfigjson" = jsonencode({
      "auths" = {
        "https://ghcr.io" = {
          "username" = "github_username"
          "password" = var.STACKGEN_PAT
          "email"    = "support"
          "auth"     = base64encode("github_username:${var.STACKGEN_PAT}")
        }
      }
    })
  }

  type = "kubernetes.io/dockerconfigjson"
}

# create alpha numeric password
resource "random_id" "this" {
  byte_length = 16
}

resource "random_id" "appcd_client_id" {
  byte_length = 16
}

resource "random_id" "appcd_client_secret" {
  byte_length = 36
}

resource "kubernetes_secret" "appcd_secrets" {
  depends_on = [kubernetes_namespace.this]
  metadata {
    name      = "appcd-secrets"
    namespace = var.namespace
  }

  type = "Opaque"

  data = {
    rds_port          = module.db.db_instance_port
    rds_password      = local.db_password
    rds_endpoint      = module.db.db_instance_address
    rds_host          = module.db.db_instance_address
    rds_read_endpoint = module.db.db_instance_address
    rds_username      = local.db_username

    appcd_client_id     = random_id.appcd_client_id.hex
    appcd_client_secret = random_id.appcd_client_secret.hex
  }
}

resource "kubernetes_secret" "temporal_default_store" {
  depends_on = [kubernetes_namespace.this]
  metadata {
    name      = "temporal-default-store"
    namespace = var.namespace
  }

  data = {
    password = local.db_password
  }

  type = "Opaque"
}

resource "kubernetes_secret" "temporal_visibility_store" {
  depends_on = [kubernetes_namespace.this]
  metadata {
    name      = "temporal-visibility-store"
    namespace = var.namespace
  }

  data = {
    password = local.db_password
  }

  type = "Opaque"
}

resource "helm_release" "temporal" {
  depends_on = [module.db]
  name       = "temporal"
  chart      = "https://github.com/temporalio/helm-charts/releases/download/temporal-${local.temporal_helm_version}/temporal-${local.temporal_helm_version}.tgz"
  namespace  = var.namespace
  wait       = true
  values = [
    templatefile("${path.module}/values/temporal.yaml", {
      enable_ops : var.enable_ops,
      postgres_user : local.db_username,
      postgres_host : module.db.db_instance_address,
      postgres_port : module.db.db_instance_port,
      namespace : var.namespace,
      domain : var.domain,
      image_pull_secret : kubernetes_secret.ghcr_pkg.metadata.0.name,
      image_registry : "ghcr.io/appcd-dev/",
    })
  ]
}

resource "helm_release" "karpenter_crd" {
  depends_on      = [module.eks_blueprints_addons]
  name            = "karpenter-crd"
  repository      = "oci://public.ecr.aws/karpenter"
  chart           = "karpenter-crd"
  version         = local.karpenter_version
  namespace       = local.karpenter_namespace
  upgrade_install = true
  wait            = true
  wait_for_jobs   = true
  force_update    = true
  cleanup_on_fail = true
}

resource "kubernetes_manifest" "karpenter_node_class" {
  depends_on = [module.eks_blueprints_addons, helm_release.karpenter_crd]
  manifest = {
    apiVersion = "karpenter.k8s.aws/v1"
    kind       = "EC2NodeClass"
    metadata = {
      name = "default"
    }
    spec = {
      amiSelectorTerms = [
        {
          alias = "al2@latest"
        }
      ]
      role = local.karpenter_iam_role_name
      subnetSelectorTerms = [
        {
          tags = {
            "karpenter.sh/discovery" = var.cluster_name
          }
        }
      ]
      securityGroupSelectorTerms = [
        {
          tags = {
            "karpenter.sh/discovery" = var.cluster_name
          }
        }
      ]
      tags = merge(local.tags, {
        "NodeType" = "default"
      })
    }
  }
}

resource "kubernetes_manifest" "karpenter_node_pool" {
  depends_on = [kubernetes_manifest.karpenter_node_class]
  manifest = {
    apiVersion = "karpenter.sh/v1",
    kind       = "NodePool",
    metadata = {
      name = "default"
    }
    spec = {
      limits = {
        cpu = "32"
      }
      disruption = {
        consolidationPolicy = "WhenEmptyOrUnderutilized"
        consolidateAfter    = "30s"
      }
      template = {
        spec = {
          requirements = [
            {
              key      = "kubernetes.io/arch"
              operator = "In"
              values   = ["arm64"]
            },
            {
              key      = "kubernetes.io/os"
              operator = "In"
              values   = ["linux"]
            },
            {
              key      = "karpenter.sh/capacity-type"
              operator = "In"
              values   = ["spot"]
            },
            {
              key      = "karpenter.k8s.aws/instance-category"
              operator = "In"
              values   = ["m", "r", "c", "t"]
            },
            {
              key      = "karpenter.k8s.aws/instance-generation"
              operator = "Gt"
              values   = ["3"]
            },
            {
              key      = "karpenter.k8s.aws/instance-cpu"
              operator = "In"
              values   = ["4", "8"]
            }
          ]
          nodeClassRef = {
            name  = "default"
            kind  = "EC2NodeClass"
            group = "karpenter.k8s.aws"
          }
        }
      }
    }
  }
}





resource "kubectl_manifest" "s3_claim" {
  depends_on = [
    kubernetes_namespace.this
  ]

  yaml_body = <<-YAML
  apiVersion: v1
  kind: PersistentVolumeClaim
  metadata:
    name: storage-${var.namespace}
    namespace: ${var.namespace}
  spec:
    accessModes:
      - ReadWriteMany
    storageClassName: ""
    resources:
      requests:
        storage: "1200Gi"
    volumeName: "${var.volume_name}"
YAML
}
