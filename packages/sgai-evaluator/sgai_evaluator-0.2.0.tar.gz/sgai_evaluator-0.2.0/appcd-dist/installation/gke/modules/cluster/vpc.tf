module "vpc" {
  source       = "terraform-google-modules/network/google"
  version      = "9.3.0"
  project_id   = var.project_id
  network_name = local.vpc_name
  routing_mode = "GLOBAL"

  subnets = [
    {
      subnet_name           = local.cluster_name
      subnet_ip             = local.cluster_ip_ranges.nodes
      subnet_region         = var.region
      subnet_private_access = true
    },
  ]

  secondary_ranges = {
    "${local.cluster_name}" = [
      {
        range_name    = "pods"
        ip_cidr_range = local.cluster_ip_ranges.pods
      },
      {
        range_name    = "services"
        ip_cidr_range = local.cluster_ip_ranges.services
      },
    ]
  }
}

# Enable Private Service Connect (PSC)
resource "google_compute_global_address" "private_service_access_address" {
  depends_on = [module.vpc]
  project    = var.project_id

  name    = "stackgen-psa-${var.suffix}"
  network = module.vpc.network_self_link

  purpose      = "VPC_PEERING"
  address_type = "INTERNAL"

  address       = "10.100.0.0"
  prefix_length = 16
}

# Create Private VPC Connection (Service Networking)
resource "google_service_networking_connection" "private_vpc_connection" {
  network = module.vpc.network_self_link
  service = "servicenetworking.googleapis.com"

  reserved_peering_ranges = [google_compute_global_address.private_service_access_address.name]

  depends_on = [google_compute_global_address.private_service_access_address]
}

# NAT and Router configuration
resource "google_compute_router" "nat_router" {
  name    = "${module.vpc.network_name}-nat-router"
  network = module.vpc.network_self_link
  region  = var.region

  bgp {
    asn = 64514
  }
}

resource "google_compute_router_nat" "nat_gateway" {
  name                               = "${module.vpc.network_name}-nat-gw"
  router                             = google_compute_router.nat_router.name
  region                             = google_compute_router.nat_router.region
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"

  log_config {
    enable = true
    filter = "ERRORS_ONLY"
  }
}

# Firewall for nginx
resource "google_compute_firewall" "nginx_admission" {
  name        = "${local.cluster_name}-master-to-worker"
  network     = module.vpc.network_self_link
  description = "Creates a nginx firewall rule from master to workers"

  allow {
    protocol = "tcp"
    ports    = ["80", "443", "8443", "10254"]
  }

  source_ranges = [local.cluster_ip_ranges.master]
  target_tags   = [local.cluster_name]
}
