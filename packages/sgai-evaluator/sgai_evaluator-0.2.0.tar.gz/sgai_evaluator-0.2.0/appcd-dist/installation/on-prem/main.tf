provider "aws" {
  region = var.region
}

data "aws_caller_identity" "current" {}

# get my public IP
data "http" "my_ip" {
  url = "http://ipv4.icanhazip.com"
}


locals {
  tags = merge(var.tags, {
    "maintained_by" = "support@stackgen.com"
    "created_for"   = var.suffix
  })
  appcd_lb_cidr_blocks = length(var.lb_cidr_blocks) == 0 ? [] : concat(var.lb_cidr_blocks, formatlist("%s/32", module.appcd_vpc_eks.nat_public_ips))
  devops_ips           = concat(var.devops_ips, [chomp(data.http.my_ip.response_body)])
}

module "ops_user" {
  count  = var.ops_user.enable ? 1 : 0
  source = "./modules/ops"
  prefix = var.suffix
  oidc_provider = {
    client_id_list  = var.ops_user.oidc_provider.client_id_list
    thumbprint_list = var.ops_user.oidc_provider.thumbprint_list
    url             = var.ops_user.oidc_provider.url
  }
  assume_role_policy = {
    test     = var.ops_user.assume_role_policy.test
    variable = var.ops_user.assume_role_policy.variable
    values   = var.ops_user.assume_role_policy.values
  }
}


module "appcd_vpc_eks" {
  source             = "./modules/vpc"
  suffix             = var.suffix
  tags               = local.tags
  region             = var.region
  max_instances      = var.max_instances
  instance_type      = var.instance_type
  devops_ips         = local.devops_ips
  use_spot_instances = var.use_spot_instances
  STACKGEN_PAT       = var.STACKGEN_PAT
  sns_topic_arn      = aws_sns_topic.alerts.arn
  ops_user = {
    rolearn  = var.ops_user.enable ? module.ops_user[0].ops_arn : ""
    username = var.ops_user.enable ? module.ops_user[0].k8s_user : ""
  }
}

module "k8s_deps" {
  source = "./modules/k8s_deps"

  load-balancer-ssl-cert-arn         = var.load-balancer-ssl-cert-arn
  tags                               = local.tags
  enable_ops                         = var.enable_ops
  domain                             = var.domain
  cluster_endpoint                   = module.appcd_vpc_eks.cluster_endpoint
  cluster_certificate_authority_data = module.appcd_vpc_eks.cluster_certificate_authority_data
  cluster_name                       = module.appcd_vpc_eks.cluster_name
  cluster_version                    = module.appcd_vpc_eks.cluster_version
  oidc_provider_arn                  = module.appcd_vpc_eks.oidc_provider_arn

  STACKGEN_PAT = var.STACKGEN_PAT
  namespace    = var.namespace

  database_subnets           = module.appcd_vpc_eks.database_subnets
  database_security_group_id = module.appcd_vpc_eks.database_security_group_id
  db_instance_class          = var.db_instance_class

  lb_cidr_blocks = local.appcd_lb_cidr_blocks

  appcd_authentication = var.appcd_authentication
  volume_name          = module.appcd_vpc_eks.pvc_name
  alerts_sns_topic_arn = aws_sns_topic.alerts.arn
}


provider "kubernetes" {
  alias                  = "kubernetes"
  host                   = module.appcd_vpc_eks.cluster_endpoint
  cluster_ca_certificate = base64decode(module.appcd_vpc_eks.cluster_certificate_authority_data)

  exec {
    api_version = "client.authentication.k8s.io/v1beta1"
    command     = "aws"
    args        = ["eks", "get-token", "--cluster-name", module.appcd_vpc_eks.cluster_name]
  }
}

provider "helm" {
  kubernetes {
    host                   = module.appcd_vpc_eks.cluster_endpoint
    cluster_ca_certificate = base64decode(module.appcd_vpc_eks.cluster_certificate_authority_data)

    exec {
      api_version = "client.authentication.k8s.io/v1beta1"
      command     = "aws"
      args        = ["eks", "get-token", "--cluster-name", module.appcd_vpc_eks.cluster_name]
    }
  }
}

locals {
  secret_data = {}

  github_secrets = var.scm_configuration.scm_type == "github" ? {
    scm_github_client_id     = var.scm_configuration.github_config.client_id
    scm_github_client_secret = var.scm_configuration.github_config.client_secret
  } : {}

  gitlab_secrets = var.scm_configuration.scm_type == "gitlab" ? {
    gitlab_client_id     = var.scm_configuration.gitlab_config.client_id
    gitlab_client_secret = var.scm_configuration.gitlab_config.client_secret
  } : {}

  azure_devops_secrets = var.scm_configuration.scm_type == "azuredev" ? {
    scm_azure_devops_client_id     = var.scm_configuration.azuredev_config.client_id
    scm_azure_devops_client_secret = var.scm_configuration.azuredev_config.client_secret
  } : {}

  final_scm_secrets = merge(
    local.secret_data,
    local.github_secrets,
    local.gitlab_secrets,
    local.azure_devops_secrets,
  )
}

# add secrets for auth and scm
resource "kubernetes_secret" "appcd_scm_secrets" {
  provider   = kubernetes.kubernetes
  depends_on = [module.appcd_vpc_eks]
  metadata {
    name      = "appcd-scm-secrets"
    namespace = var.namespace
  }

  data = local.final_scm_secrets
}

locals {
  appcdYAML = templatefile("${path.module}/values/appcd.yaml", {
    temporal_namespace : module.k8s_deps.temporal_namespace
    appcd_secrets : concat([module.k8s_deps.appcd_secrets, kubernetes_secret.appcd_scm_secrets.metadata[0].name], var.additional_secrets)
    enable_ops : var.enable_ops,
    auth_enabled : var.appcd_authentication.type != "none",
    enable_ingress : true,
    domain : var.domain,
    scm_github_auth_url : try(var.scm_configuration.github_config.auth_url, ""),
    scm_github_token_url : try(var.scm_configuration.github_config.token_url, ""),
    scm_gitlab_auth_url : try(var.scm_configuration.gitlab_config.auth_url, ""),
    scm_gitlab_token_url : try(var.scm_configuration.gitlab_config.token_url, ""),
    scm_azure_auth_url : try(var.scm_configuration.azuredev_config.auth_url, ""),
    scm_azure_token_url : try(var.scm_configuration.azuredev_config.token_url, ""),
    worm_enabled : true
    appcd_admin_emails : var.admin_emails
    enable_feature : var.enable_feature
    nginx : var.nginx_config
  })
}

resource "helm_release" "appcd" {
  depends_on = [module.k8s_deps]

  name = "appcd"
  # chart     = "https://releases.stackgen.com/appcd-dist/charts/appcd-dist-${var.appcd_version}.tgz"
  chart     = "appcd-dist-${var.appcd_version}.tgz"
  namespace = var.namespace
  wait      = true
  values = [
    local.appcdYAML,
    templatefile("${path.module}/values/images.yaml", {})
  ]
}


output "appcd_yaml" {
  value = local.appcdYAML
}

resource "local_file" "appcd_yaml" {
  content  = local.appcdYAML
  filename = "${path.module}/values/appcd-final.yaml"
}

output "helm_upgrade_command" {
  value = "helm upgrade --debug --wait --install appcd appcd-dist-${var.appcd_version}.tgz --namespace ${var.namespace} --values ${local_file.appcd_yaml.filename} --values ${path.module}/values/images.yaml"
}

# upload the final local_file.appcd_yaml.filename to Secret Manager
resource "aws_secretsmanager_secret" "appcd_yaml" {
  count = var.ops_user.enable ? 1 : 0
  name  = "/stackgen/${var.suffix}"
}

resource "aws_secretsmanager_secret_version" "appcd_yaml" {
  count         = var.ops_user.enable ? 1 : 0
  secret_id     = aws_secretsmanager_secret.appcd_yaml[0].id
  secret_string = local.appcdYAML
}

# Create a role policy that would allow fetching cluster info.
# This would help us avoid storing cluster's kube config in GitHub Action's secrets
resource "aws_iam_role_policy" "ops_provider_oidc_policy" {
  count = var.ops_user.enable ? 1 : 0
  name  = "${module.ops_user[0].k8s_user}-eks-policy"
  role  = module.ops_user[0].role_id

  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Sid" : "DescribeCluster",
        "Effect" : "Allow",
        "Action" : "eks:DescribeCluster",
        "Resource" : "arn:aws:eks:${var.region}:${data.aws_caller_identity.current.account_id}:cluster/${module.appcd_vpc_eks.cluster_name}"
      },
      {
        # get-secret-value
        "Sid" : "GetSecretValue",
        "Effect" : "Allow",
        "Action" : "secretsmanager:GetSecretValue",
        "Resource" : aws_secretsmanager_secret.appcd_yaml[0].arn
      },
      {
        # UpdateClusterConfig
        "Sid" : "UpdateClusterConfig",
        "Effect" : "Allow",
        "Action" : "eks:UpdateClusterConfig",
        "Resource" : "arn:aws:eks:${var.region}:${data.aws_caller_identity.current.account_id}:cluster/${module.appcd_vpc_eks.cluster_name}"
      },
      {
        "Sid" : "ListClusters",
        "Effect" : "Allow",
        "Action" : "eks:ListClusters",
        "Resource" : "arn:aws:eks:${var.region}:${data.aws_caller_identity.current.account_id}:cluster/${module.appcd_vpc_eks.cluster_name}"
      }
    ]
  })
}


# create sns topic for alerts
resource "aws_sns_topic" "alerts" {
  name = "${var.suffix}-infra-alerts"
  tags = merge(local.tags, {
    "name"    = "${var.suffix}-infra-alerts"
    "cluster" = var.suffix
  })
}

# send email to the alert email
resource "aws_sns_topic_subscription" "alerts_subscription" {
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email
}
