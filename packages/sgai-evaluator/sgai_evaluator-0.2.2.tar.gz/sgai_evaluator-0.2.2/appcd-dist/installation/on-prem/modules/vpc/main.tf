terraform {
  required_version = ">= 1"

  required_providers {
    kubectl = {
      source  = "alekc/kubectl"
      version = ">= 2.0.0"
    }
  }
}

provider "kubernetes" {
  host                   = try(module.eks.cluster_endpoint, "")
  cluster_ca_certificate = base64decode(try(module.eks.cluster_certificate_authority_data, ""))

  exec {
    api_version = "client.authentication.k8s.io/v1beta1"
    command     = "aws"
    args        = ["eks", "get-token", "--cluster-name", try(module.eks.cluster_name, "")]
  }
}

data "aws_caller_identity" "current" {}

data "aws_iam_session_context" "current" {
  arn = data.aws_caller_identity.current.arn
}


data "aws_availability_zones" "available" {
  filter {
    name   = "opt-in-status"
    values = ["opt-in-not-required"]
  }
}

locals {
  cluster_name = "${var.suffix}-eks"
  azs          = slice(data.aws_availability_zones.available.names, 0, 3)
  vpc_cidr     = "10.0.0.0/16"
  tags = merge(var.tags, {
    "appcd_module" = "vpc"
  })
  karpenter_iam_role_name = format("karpenter-for-%s", local.cluster_name)
  min_instance_count      = 2
  pv_name                 = "s3-pv-appcd-${var.suffix}"
  authorized_networks     = [for x in var.devops_ips : "${x}/32"]
}

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.8.1"

  name = "appcd-vpc-${var.suffix}"

  cidr             = local.vpc_cidr
  azs              = local.azs
  private_subnets  = [for k, v in local.azs : cidrsubnet(local.vpc_cidr, 8, k)]
  public_subnets   = [for k, v in local.azs : cidrsubnet(local.vpc_cidr, 8, k + 4)]
  database_subnets = [for k, v in local.azs : cidrsubnet(local.vpc_cidr, 8, k + 8)]

  create_database_subnet_group = true
  enable_nat_gateway           = true
  single_nat_gateway           = true

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

resource "aws_security_group" "rds_sg" {
  name        = "${var.suffix}_rds"
  vpc_id      = module.vpc.vpc_id
  description = "Control traffic to RDS ${var.suffix}"

  tags = merge(var.tags)

  lifecycle {
    create_before_destroy = true
  }
  tags_all = var.tags
}

resource "aws_security_group_rule" "rds_sg_rule" {
  type                     = "ingress"
  from_port                = "5432"
  to_port                  = "5432"
  protocol                 = "tcp"
  security_group_id        = aws_security_group.rds_sg.id
  source_security_group_id = module.eks.node_security_group_id
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
  source              = "terraform-aws-modules/eks/aws"
  version             = "20.31.1"
  authentication_mode = "API_AND_CONFIG_MAP"

  cluster_name    = local.cluster_name
  cluster_version = "1.32"

  vpc_id                               = module.vpc.vpc_id
  subnet_ids                           = module.vpc.private_subnets
  cluster_endpoint_public_access       = true
  cluster_endpoint_public_access_cidrs = local.authorized_networks
  eks_managed_node_group_defaults = {
    ami_type = "AL2_ARM_64"
  }

  access_entries = {
    current_user = {
      kubernetes_groups = []
      principal_arn     = data.aws_iam_session_context.current.issuer_arn

      policy_associations = {
        cluster = {
          policy_arn = "arn:aws:eks::aws:cluster-access-policy/AmazonEKSClusterAdminPolicy"
          access_scope = {
            type = "cluster"
          }
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

  eks_managed_node_groups = {
    appcd_default = {
      name                       = var.suffix
      use_mixed_instances_policy = true
      mixed_instances_policy = {
        instances_distribution = {
          on_demand_base_capacity                  = 0
          on_demand_percentage_above_base_capacity = 20
          spot_allocation_strategy                 = "capacity-optimized"
        }
      }
      block_device_mappings = {
        xvda = {
          device_name = "/dev/xvda"
          ebs = {
            delete_on_termination = true
            encrypted             = false
            volume_size           = 20
            volume_type           = "gp3"
            encrypted             = true
            kms_key_id            = module.ebs_kms_key.key_arn
            delete_on_termination = true
          }
        }
      }
      // m7g.large can have 29 IP
      // m7g.xlarge can have 58 IP
      // https://github.com/awslabs/amazon-eks-ami/blob/master/files/eni-max-pods.txt#L499
      instance_types = [var.instance_type]
      capacity_type  = var.use_spot_instances ? "SPOT" : "ON_DEMAND"
      network_interfaces = [{
        delete_on_termination = true
      }]


      max_size         = max(var.max_instances, local.min_instance_count)
      min_size         = local.min_instance_count
      desired_size     = max(local.min_instance_count, 2)
      root_volume_type = "gp3"
    }
  }
}


// create s3 bucket
resource "aws_s3_bucket" "csi-backend" {
  bucket = "appcd-blobs-${var.suffix}-artifacts"
  tags   = local.tags
}

resource "aws_s3_bucket_versioning" "csi-backend-versioning" {
  bucket = aws_s3_bucket.csi-backend.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "csi-backend" {
  bucket = aws_s3_bucket.csi-backend.id

  rule {
    id = "expire"

    expiration {
      days = 45
    }

    status = "Enabled"

    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }
  }
}


// remove public acccess to the bucket
resource "aws_s3_bucket_public_access_block" "csi-backend" {
  bucket = aws_s3_bucket.csi-backend.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

module "s3-csi-driver" {
  depends_on = [module.eks]
  source     = "github.com/appcd-dev/terraform-aws-s3-csi-driver?ref=83640d82cf0dfdd4e73b012b48cad9e884ff5b34"

  aws_region    = var.region
  bucket_name   = aws_s3_bucket.csi-backend.id
  iam_role_name = var.suffix
  eks_cluster   = module.eks.cluster_name
  tags          = local.tags
}

resource "kubernetes_storage_class" "s3_csi" {
  depends_on             = [module.s3-csi-driver]
  storage_provisioner    = "s3.csi.aws.com"
  allow_volume_expansion = true
  metadata {
    name = "s3-csi"
  }
}


resource "kubectl_manifest" "persistent_volume" {
  depends_on = [module.s3-csi-driver]
  yaml_body  = <<-YAML
  apiVersion: v1
  kind: PersistentVolume
  metadata:
    name: ${local.pv_name}
  spec:
    capacity:
      storage: 1200Gi
    accessModes:
      - ReadWriteMany
    mountOptions:
      - allow-delete
      - region ${var.region}
      - uid=1001
      - gid=1001
      - file-mode=0666
      - allow-other
    csi:
      driver: s3.csi.aws.com
      volumeHandle: s3-csi-driver-volume
      volumeAttributes:
        bucketName: ${aws_s3_bucket.csi-backend.id}
YAML
}

# monitor the auto scaling group for cpu utilization
resource "aws_cloudwatch_metric_alarm" "cpu_utilization_alarm" {
  count               = var.sns_topic_arn == "" ? 0 : 1
  alarm_name          = "${local.cluster_name}-cpu-utilization-alarm"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = 60
  statistic           = "Average"
  threshold           = 80
  alarm_actions       = [var.sns_topic_arn]
  tags                = merge(local.tags, {})
  dimensions = {
    AutoScalingGroupName = module.eks.eks_managed_node_groups_autoscaling_group_names[0]
  }
}

resource "aws_autoscaling_policy" "eks_autoscaling_policy" {
  depends_on = [module.eks]

  name                   = "${module.eks.eks_managed_node_groups_autoscaling_group_names[0]}-autoscaling-policy"
  autoscaling_group_name = module.eks.eks_managed_node_groups_autoscaling_group_names[0]
  policy_type            = "TargetTrackingScaling"

  target_tracking_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ASGAverageCPUUtilization"
    }
    target_value = var.autoscaling_average_cpu
  }
}

locals {
  default_aws_auth_roles = [{
    rolearn  = module.eks.eks_managed_node_groups.appcd_default.iam_role_arn
    username = "system:node:{{EC2PrivateDNSName}}"
    groups = [
      "system:bootstrappers",
      "system:nodes",
      "system:masters"
    ]
    },
    {
      rolearn  = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/${local.karpenter_iam_role_name}"
      username = "system:node:{{EC2PrivateDNSName}}"
      groups = [
        "system:bootstrappers",
        "system:nodes",
      ]
  }]
  ops_user = var.ops_user.rolearn == "" ? [] : [{
    rolearn  = var.ops_user.rolearn
    username = var.ops_user.username
    groups   = []
  }]
}

module "eks_aws_auth" {
  source  = "terraform-aws-modules/eks/aws//modules/aws-auth"
  version = "~> 20.0"

  manage_aws_auth_configmap = true

  aws_auth_roles = concat(local.default_aws_auth_roles, local.ops_user)
}
