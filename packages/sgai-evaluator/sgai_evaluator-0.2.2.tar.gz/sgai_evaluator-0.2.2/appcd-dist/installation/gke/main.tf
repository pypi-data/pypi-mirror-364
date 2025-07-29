locals {
  labels = merge(var.labels, {
    "maintainer" = "stackgen"
  })
}
# get my public IP
data "http" "my_ip" {
  url = "http://ipv4.icanhazip.com"
}

provider "google" {
  project = var.project_id
  region  = var.region
}

provider "helm" {
  kubernetes {
    host                   = "https://${module.gke.cluster_endpoint}"
    cluster_ca_certificate = base64decode(module.gke.cluster_ca_certificate)
    token                  = module.gke.cluster_access_token
  }
}

provider "kubernetes" {
  host                   = "https://${module.gke.cluster_endpoint}"
  cluster_ca_certificate = base64decode(module.gke.cluster_ca_certificate) # CA certificate to verify the connection
  token                  = module.gke.cluster_access_token                 # Access token for authentication
}

# get zones from the region
data "google_compute_zones" "available" {
  region = var.region
  status = "UP"
}

module "gke" {
  source           = "./modules/cluster"
  project_id       = var.project_id
  region           = var.region
  suffix           = var.suffix
  machine_type     = "e2-standard-8"
  max_count        = 3
  zones            = data.google_compute_zones.available.names
  labels           = local.labels
  retention_period = 2678400
  devops_ips = merge({
    chomp(data.http.my_ip.response_body) : "self"
  }, var.devops_ips)
}

module "db" {
  depends_on      = [module.gke]
  source          = "./modules/database"
  project_id      = var.project_id
  region          = var.region
  suffix          = var.suffix
  labels          = local.labels
  zones           = data.google_compute_zones.available.names
  private_network = module.gke.network_self_link
}

module "stackgen" {
  depends_on                        = [module.db, module.gke]
  source                            = "./modules/stackgen-installation"
  domain                            = var.domain
  postgresql_fqdn                   = module.db.postgresql_fqdn
  postgresql_administrator_password = module.db.postgresql_administrator_password
  postgresql_administrator_login    = module.db.postgresql_administrator_login
  STACKGEN_PAT                      = var.STACKGEN_PAT
  project_id                        = var.project_id
  suffix                            = var.suffix
  pre_shared_cert_name              = var.pre_shared_cert_name
  storage = {
    class  = module.gke.storage.class
    volume = module.gke.storage.pv
  }
}
