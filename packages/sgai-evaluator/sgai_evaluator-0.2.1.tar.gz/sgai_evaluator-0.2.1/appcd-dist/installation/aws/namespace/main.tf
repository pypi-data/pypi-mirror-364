provider "aws" {
  region = var.region
}

locals {
  cluster_endpoint  = var.existing_cluster.lookup ? data.aws_eks_cluster.appcd_cluster[0].endpoint : var.cluster_endpoint
  cluster_name      = var.existing_cluster.lookup ? data.aws_eks_cluster.appcd_cluster[0].name : var.cluster_name
  cluster_cert_data = var.existing_cluster.lookup ? data.aws_eks_cluster.appcd_cluster[0].certificate_authority[0].data : var.cluster_certificate_authority_data
}

# data cluster lookup
data "aws_eks_cluster" "appcd_cluster" {
  count = var.existing_cluster.lookup ? 1 : 0
  name  = "${var.existing_cluster.created_for}-eks"
}

provider "kubernetes" {
  host                   = local.cluster_endpoint
  cluster_ca_certificate = base64decode(local.cluster_cert_data)

  exec {
    api_version = "client.authentication.k8s.io/v1beta1"
    command     = "aws"
    # This requires the awscli to be installed locally where Terraform is executed
    args = ["eks", "get-token", "--cluster-name", local.cluster_name]
  }
}

locals {
  namespace = "appcd-${var.namespace}"
  tags = merge(
    var.tags,
    {
      "repo"      = "https://github.com/appcd-dev/appcd-dist",
      "namespace" = local.namespace
    }
  )
}

resource "kubernetes_namespace" "appcd" {
  metadata {
    name = local.namespace
  }
}

