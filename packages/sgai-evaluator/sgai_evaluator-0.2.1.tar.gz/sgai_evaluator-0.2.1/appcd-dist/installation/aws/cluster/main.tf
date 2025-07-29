provider "aws" {
  region = var.region
}
terraform {
  required_providers {
    helm = {
      source  = "hashicorp/helm"
      version = ">= 2.9, < 3.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = ">= 2.20.0"
    }
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0.0"
    }
  }
}


data "aws_caller_identity" "current" {}

# Filter out local zones, which are not currently supported
# with managed node groups
data "aws_availability_zones" "available" {
  filter {
    name   = "opt-in-status"
    values = ["opt-in-not-required"]
  }
}

locals {
  cluster_name = "${var.suffix}-eks"
  # https://karpenter.sh/docs/upgrading/compatibility/#compatibility-matrix
  # Check the compatibility matrix for the version of karpenter
  cluster_version = "1.32"
  azs             = slice(data.aws_availability_zones.available.names, 0, 3)
  vpc_cidr        = "10.0.0.0/16"
  tags = merge(var.tags, {
    "repository"  = "https://github.com/appcd-dev/appcd-dist"
    "created_for" = var.suffix,
  })
  karpenter_iam_role_name = format("karpenter-for-%s", local.cluster_name)

  default_node_group = {
    // https://github.com/awslabs/amazon-eks-ami/blob/master/files/eni-max-pods.txt#L499
    instance_types = [var.instance_type]
    capacity_type  = var.use_spot_instances ? "SPOT" : "ON_DEMAND"

    max_size     = max(var.max_instances, 2)
    desired_size = 2
  }

  gpu_node_group = {
    ami_type       = "AL2_x86_64_GPU"
    instance_types = ["g4dn.xlarge", "g5.xlarge"]
    capacity_type  = var.use_spot_instances ? "SPOT" : "ON_DEMAND"

    max_size     = max(var.max_instances, 3)
    desired_size = 1

    labels = {
      "nvidia.com/gpu.present" = "true"
    }
    taints = {
      # Ensure only GPU workloads are scheduled on this node group
      gpu = {
        key    = "nvidia.com/gpu"
        value  = "Exists"
        effect = "NO_SCHEDULE"
      }
    }
  }

  eks_managed_node_groups = merge({
    default_node_group = local.default_node_group
  }, var.enable_gpu ? { gpu_node_group = local.gpu_node_group } : {})
}

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.16.0"

  name = "appcd-vpc-${var.suffix}"

  cidr             = local.vpc_cidr
  azs              = local.azs
  private_subnets  = [for k, v in local.azs : cidrsubnet(local.vpc_cidr, 8, k)]
  public_subnets   = [for k, v in local.azs : cidrsubnet(local.vpc_cidr, 8, k + 4)]
  database_subnets = [for k, v in local.azs : cidrsubnet(local.vpc_cidr, 8, k + 8)]

  create_database_subnet_group = true
  enable_nat_gateway           = true
  single_nat_gateway           = true

  enable_flow_log                                 = true
  flow_log_destination_type                       = "cloud-watch-logs"
  create_flow_log_cloudwatch_log_group            = true
  create_flow_log_cloudwatch_iam_role             = true
  flow_log_max_aggregation_interval               = 60
  flow_log_cloudwatch_log_group_retention_in_days = var.flow_log_retention_days

  public_subnet_tags = {
    "kubernetes.io/cluster/${local.cluster_name}" = "shared"
    "kubernetes.io/role/elb"                      = 1
  }

  private_subnet_tags = {
    "kubernetes.io/cluster/${local.cluster_name}" = "shared"
    "kubernetes.io/role/internal-elb"             = 1
    "karpenter.sh/discovery"                      = local.cluster_name
  }
  tags = merge(local.tags, {
    "terraform" = "true"
  })
}


module "ebs_kms_key" {
  source  = "terraform-aws-modules/kms/aws"
  version = "~> 2.0"

  description = "key to encrypt EKS managed node group volumes"

  # Policy
  key_administrators = [
    data.aws_caller_identity.current.arn
  ]

  key_service_roles_for_autoscaling = [
    # required for the ASG to manage encrypted volumes for nodes
    "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/aws-service-role/autoscaling.amazonaws.com/AWSServiceRoleForAutoScaling",
    # required for the cluster / persistentvolume-controller to create encrypted PVCs
    module.eks.cluster_iam_role_arn,
  ]

  # Aliases
  aliases = ["eks/${var.suffix}/ebs-node-encryption"]

  tags = local.tags
}


module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "20.24.2"

  cluster_name    = local.cluster_name
  cluster_version = local.cluster_version
  vpc_id          = module.vpc.vpc_id
  subnet_ids      = module.vpc.private_subnets

  cluster_endpoint_public_access = true
  eks_managed_node_group_defaults = {
    ami_type = "AL2_ARM_64"
    block_device_mappings = {
      xvda = {
        device_name = "/dev/xvda"
        ebs = {
          volume_size           = 256
          volume_type           = "gp3"
          delete_on_termination = true
          encrypted             = true
          kms_key_id            = module.ebs_kms_key.key_arn
          delete_on_termination = true
        }
      }
    }
  }

  tags = merge(local.tags, {})

  cluster_security_group_tags = {
    "karpenter.sh/discovery" = local.cluster_name
  }
  node_security_group_tags = {
    "karpenter.sh/discovery" = local.cluster_name
  }

  eks_managed_node_groups = local.eks_managed_node_groups
}


# monitor the auto scaling group for cpu utilization
resource "aws_cloudwatch_metric_alarm" "cpu_utilization_alarm" {
  alarm_name          = "${local.cluster_name}-cpu-utilization-alarm"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = 60
  statistic           = "Average"
  threshold           = 80
  alarm_actions       = [aws_sns_topic.alerts.arn]
  tags                = merge(local.tags, {})
  dimensions = {
    AutoScalingGroupName = module.eks.eks_managed_node_groups_autoscaling_group_names[0]
  }
}

data "aws_iam_role" "stackgen_readonly_role" {
  count = local.hasReadOnlyRole ? 1 : 0
  name  = var.read_only_role_name
}

locals {
  hasReadOnlyRole = var.read_only_role_name != "" ? true : false
}


module "eks_aws_auth" {
  source  = "terraform-aws-modules/eks/aws//modules/aws-auth"
  version = "20.24.2"

  manage_aws_auth_configmap = true

  aws_auth_roles = concat([
    # We need to add in the Karpenter node IAM role for nodes launched by Karpenter
    {
      rolearn  = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/${local.karpenter_iam_role_name}"
      username = "system:node:{{EC2PrivateDNSName}}"
      groups = [
        "system:bootstrappers",
        "system:nodes",
      ]
    },
    {
      rolearn  = module.eks.eks_managed_node_groups.default_node_group.iam_role_arn
      username = "system:node:{{EC2PrivateDNSName}}"
      groups = [
        "system:bootstrappers",
        "system:nodes",
        "system:masters"
      ]
    },
    {
      rolearn  = aws_iam_role.github_oidc_auth_role.arn
      username = "github-oidc-auth-user"
      groups   = []
    }
    ],
    var.enable_gpu ? [{
      rolearn  = module.eks.eks_managed_node_groups.gpu_node_group.iam_role_arn
      username = "system:node:{{EC2PrivateDNSName}}"
      groups = [
        "system:bootstrappers",
        "system:nodes",
        "system:masters"
      ]
    }] : [],
    local.hasReadOnlyRole ? [{
      rolearn  = data.aws_iam_role.stackgen_readonly_role[0].arn
      username = "developer-${replace(data.aws_iam_role.stackgen_readonly_role[0].arn, "/[^a-zA-Z0-9]/", "-")}"
      groups   = [local.k8s_read_readonly_group]
    }] : []
  )
}
