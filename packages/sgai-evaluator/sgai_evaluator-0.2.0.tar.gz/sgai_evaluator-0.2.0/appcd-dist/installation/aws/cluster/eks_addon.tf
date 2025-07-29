provider "kubernetes" {
  host                   = module.eks.cluster_endpoint
  cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)

  exec {
    api_version = "client.authentication.k8s.io/v1beta1"
    command     = "aws"
    args        = ["eks", "get-token", "--cluster-name", module.eks.cluster_name]
  }
}


data "aws_region" "current" {}

locals {
  grafana_domain      = var.suffix == "developer" ? "dashboards.dev.stackgen.com" : "dashboards.${var.suffix}.stackgen.com"
  karpenter_namespace = "karpenter"
  karpenter_version   = "1.3.3"
  eks_addon_base = {
    kube-proxy = {
      most_recent = true
    }
  }
  eks_addons_dev = {
  }
  eks_addons = merge(local.eks_addon_base, var.is_dev_cluster ? local.eks_addons_dev : {})
  region     = data.aws_region.current.name
}

resource "kubernetes_manifest" "grafana_secret_store" {
  manifest = {
    "apiVersion" = "external-secrets.io/v1beta1"
    "kind"       = "SecretStore"
    "metadata" = {
      "name"      = "grafana-st"
      "namespace" = "kube-prometheus-stack"
    }
    spec = {
      "provider" = {
        "aws" = {
          "service" = "SecretsManager"
          "region"  = var.region
        }
      }
    }
  }
}
resource "kubernetes_manifest" "grafana_google_oauth_external_secret" {
  manifest = {
    apiVersion = "external-secrets.io/v1beta1"
    kind       = "ExternalSecret"
    metadata = {
      name      = "grafana-google-oauth"
      namespace = "kube-prometheus-stack"
    }
    spec = {
      refreshInterval = "1h"

      secretStoreRef = {
        name = "grafana-st"
        kind = "SecretStore"
      }

      target = {
        name           = "grafana-google-oauth"
        creationPolicy = "Owner"
      }

      data = [
        {
          secretKey = "GF_AUTH_GENERIC_OAUTH_CLIENT_ID"
          remoteRef = {
            key      = "stackgen/${var.suffix}/grafana"
            property = "GF_AUTH_GENERIC_OAUTH_CLIENT_ID"
          }
        },
        {
          secretKey = "GF_AUTH_GENERIC_OAUTH_CLIENT_SECRET"
          remoteRef = {
            key      = "stackgen/${var.suffix}/grafana"
            property = "GF_AUTH_GENERIC_OAUTH_CLIENT_SECRET"
          }
        }
      ]
    }
  }
}
module "eks_blueprints_addons" {
  source  = "aws-ia/eks-blueprints-addons/aws"
  version = "1.21.0"

  cluster_name      = module.eks.cluster_name
  cluster_endpoint  = module.eks.cluster_endpoint
  cluster_version   = module.eks.cluster_version
  oidc_provider_arn = module.eks.oidc_provider_arn

  enable_external_secrets             = true
  enable_aws_load_balancer_controller = true
  enable_ingress_nginx                = true
  enable_metrics_server               = true
  enable_aws_for_fluentbit            = true

  enable_kube_prometheus_stack = true
  kube_prometheus_stack = {
    values = [<<-EOT
    prometheus:
      prometheusSpec:
        podMonitorSelectorNilUsesHelmValues: false
        serviceMonitorSelectorNilUsesHelmValues: false
        logLevel: debug
    alertmanager:
      alertmanagerSpec:
        replicas: 2
        alertmanagerConfigNamespaceSelector: {}
        logLevel: debug
        config:
          global:
            resolve_timeout: 5m
          route:
            receiver: "null"
            group_by: ["namespace"]
            continue: false
            routes:
              - receiver: "null"
                matchers:
                  - alertname=~"InfoInhibitor|Watchdog"
                continue: false  # Drop these alerts completely
    grafana:
      envFromSecret: grafana-google-oauth
      grafana.ini:
        auth.generic_oauth:
          enabled: true
          name: "Google"
          allow_sign_up: true
          client_id: "$${GF_AUTH_GENERIC_OAUTH_CLIENT_ID}"
          client_secret: "$${GF_AUTH_GENERIC_OAUTH_CLIENT_SECRET}"
          scopes: "openid email profile"
          auth_url: "https://accounts.google.com/o/oauth2/v2/auth"
          token_url: "https://oauth2.googleapis.com/token"
          api_url: "https://openidconnect.googleapis.com/v1/userinfo"
          role_attribute_path: "contains(email, '@stackgen.com') && 'Admin' || 'Viewer'"
        server:
          root_url: "https://${local.grafana_domain}"
        users:
          auto_assign_org_role: Viewer
      ingress:
        enabled: true
        hosts:
          - "${local.grafana_domain}"  
        path: /
        pathType: Prefix
        annotations:
          kubernetes.io/ingress.class: "nginx"
          nginx.ingress.kubernetes.io/ssl-redirect: "true"
          nginx.ingress.kubernetes.io/backend-protocol: "HTTPS"
    EOT
    ]
  }
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
  aws_for_fluentbit_cw_log_group = {
    retention_in_days = var.is_dev_cluster ? 7 : 30
  }
  aws_for_fluentbit = {
    enable_containerinsights = true
    kubelet_monitoring       = true
    set = [
      {
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
            log_group_name /aws/containerinsights/${module.eks.cluster_name}/application
            log_stream_prefix $${HOSTNAME}-
            auto_create_group true
            extra_user_agent container-insights
            workers 1
      EOT
  }

  karpenter = {
    chart_version = local.karpenter_version
    namespace     = local.karpenter_namespace
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

  eks_addons = local.eks_addons

  ingress_nginx = {
    repository = "oci://ghcr.io/nginxinc/charts"
    chart      = "nginx-ingress"

    chart_version = "1.4.2"
    set = [
      {
        name  = "controller.service.annotations.service\\.beta\\.kubernetes\\.io/aws-load-balancer-type"
        value = "nlb"
      },
      {
        name  = "controller.image.repository"
        value = "ghcr.io/appcd-dev/nginx/nginx-ingress"
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
        name  = "controller.enableSnippets"
        value = "true"
      },
      {
        name  = "prometheus.create"
        value = "true"
      },
      {
        name  = "prometheus.service.create"
        value = "true"
      },
      {
        name  = "controller.enableLatencyMetrics"
        value = "true"
      },
      {
        name  = "controller.metrics.enabled",
        value = "true"
      },
      {
        name  = "controller.kind"
        value = "daemonset"
      },
      {
        name  = "prometheus.serviceMonitor.create",
        value = "true"
      },
      {
        name  = "prometheus.serviceMonitor.labels.release",
        value = "kube-prometheus-stack"
      }
    ]
  }

  tags = local.tags
}

resource "helm_release" "karpenter_crd" {
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
  atomic          = true
}


resource "kubernetes_manifest" "node_class" {
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
            "karpenter.sh/discovery" = local.cluster_name
          }
        }
      ]
      securityGroupSelectorTerms = [
        {
          tags = {
            "karpenter.sh/discovery" = local.cluster_name
          }
        }
      ]
      tags = merge(local.tags, {
        "NodeType" = "default"
      })
    }
  }
}

resource "kubernetes_manifest" "node_pool" {
  depends_on = [kubernetes_manifest.node_class]
  manifest = {
    apiVersion = "karpenter.sh/v1",
    kind       = "NodePool",
    metadata = {
      name = "default"
    }
    spec = {
      limits = {
        cpu = "64"
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
              values   = ["8", "16", "32"]
            }
          ]
          nodeClassRef = {
            name  = kubernetes_manifest.node_class.manifest.metadata.name
            kind  = "EC2NodeClass"
            group = "karpenter.k8s.aws"
          }
        }
      }
    }
  }
}

