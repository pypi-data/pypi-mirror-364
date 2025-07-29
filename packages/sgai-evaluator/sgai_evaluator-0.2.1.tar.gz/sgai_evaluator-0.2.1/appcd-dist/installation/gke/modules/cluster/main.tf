# Google provider configuration
locals {
  # Define the CIDR block for the VPC
  vpc_cidr             = "10.0.0.0/16"
  vpc_name             = "stackgen-vpc-${var.suffix}"
  cluster_name         = "stackgen-${var.suffix}"
  azs                  = var.zones
  service_account_name = "stackgen-cluster-${var.suffix}"

  labels = merge(var.labels, {
    "module" : "gke"
  })
  k8s_given_name = "stackgen-${var.suffix}"

  cluster_ip_ranges = {
    pods     = "10.0.0.0/22"
    services = "10.0.4.0/24"
    nodes    = "10.0.6.0/24"
    master   = "10.0.7.0/28"
  }
  master_authorized_networks = [for ip, name in var.devops_ips : {
    cidr_block   = "${ip}/32"
    display_name = name
  }]
}

# GKE Module Configuration
module "gke" {
  source                     = "terraform-google-modules/kubernetes-engine/google//modules/private-cluster"
  version                    = "v34.0.0"
  project_id                 = var.project_id
  name                       = local.cluster_name
  region                     = var.region
  zones                      = local.azs
  network                    = module.vpc.network_name
  subnetwork                 = local.cluster_name
  ip_range_pods              = "pods"
  ip_range_services          = "services"
  horizontal_pod_autoscaling = true
  deletion_protection        = true
  create_service_account     = true
  enable_private_endpoint    = false
  enable_private_nodes       = true
  master_authorized_networks = local.master_authorized_networks
  http_load_balancing        = true
  network_policy             = false
  master_ipv4_cidr_block     = local.cluster_ip_ranges.master

  node_pools_taints = {
    all = []
  }
  node_pools_tags = {
    all = []
  }
  gcs_fuse_csi_driver = true
  node_pools_oauth_scopes = {
    default-node-pool = [
      "https://www.googleapis.com/auth/cloud-platform",
      "https://www.googleapis.com/auth/devstorage.read_only"
    ]
  }

  node_pools = [
    {
      name                 = "base"
      enable_private_nodes = true
      machine_type         = var.machine_type
      node_locations       = join(",", local.azs)
      total_min_count      = var.min_count
      total_max_count      = var.max_count
      min_count            = var.min_count
      max_count            = var.max_count
      local_ssd_count      = 0
      spot                 = true
      service_account      = "${local.service_account_name}@${var.project_id}.iam.gserviceaccount.com"
      enable_secure_boot   = true
    }
  ]
}

data "google_client_config" "default" {}
