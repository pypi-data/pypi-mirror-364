# Stackgen installtion on GKE (Onprem)

This Terraform configuration sets up a Google Kubernetes Engine (GKE) cluster and a Google Cloud database, utilizing Google Cloud Storage (GCS) as a backend for state management. The project uses the `tofu` tool for Terraform operations.

## Requirements

- [Tofu/Terraform]
- [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
- [Tofu](https://github.com/hashicorp/tofu) tool for managing Terraform workflows
- Google Cloud account and appropriate permissions to create resources in the desired project.

## Setup

### Install Dependencies

1. **Install Tofu**:  
   Make sure you have `tofu` installed. You can check by running:

   ```bash
   which -a tofu
   ```

   If `tofu` is not found, install it following the instructions from the [Tofu GitHub repository](https://github.com/hashicorp/tofu).

2. **Google Cloud SDK**:  
   Ensure the Google Cloud SDK is installed and authenticated with the appropriate credentials.

### Backend Configuration

This configuration uses **Google Cloud Storage (GCS)** as the backend to store the Terraform state. Ensure you have a GCS bucket created before running Terraform.

```hcl
terraform {
  backend "gcs" {
    bucket = "<your-gcs-bucket-name>"
    prefix = "terraform/state"
  }
}
```

Replace `<your-gcs-bucket-name>` with the name of your GCS bucket.

### Provider Configuration

The **Google Cloud provider** is configured to use project and region values set through input variables.

```hcl
provider "google" {
  project = var.project_id
  region  = var.region
}
```

### Modules

This configuration consists of two modules:

1. **GKE Cluster Module** (`gke`):
   - Creates a Google Kubernetes Engine cluster.
   - Configurable for project ID, region, environment, machine type, and networking options.

2. **Database Module** (`db`):
   - Creates a database and associates it with the GKE VPC network.

### GKE Module

This module sets up a GKE cluster with customizable settings for scaling, network CIDR, and other parameters.

```hcl
module "gke" {
  source              = "./modules/cluster"
  project_id          = var.project_id
  region              = var.region
  environment         = var.environment
  machine_type        = "e2-medium"
  min_count           = 1
  max_count           = 3
  zones               = var.zones
  suffix              = var.suffix
  name                = var.name
  pods_cidr           = var.pods_cidr
  services_cidr       = var.services_cidr
  service_account_name = var.service_account_name
  namespace           = "test"
}
```

### Database Module

This module creates a database within the GKE VPC network.

```hcl
module "db" {
  depends_on = [ module.gke ]
  source              = "./modules/database"
  project_id          = var.project_id
  region              = var.region
  db_subnet_id        = module.gke.vpc_network_id
}
```

## Variables

The following input variables are required for this configuration:

- `project_id`: Google Cloud Project ID.
- `region`: Google Cloud region.
- `environment`: Environment name (e.g., dev, prod).
- `zones`: List of zones in the region.
- `suffix`: Suffix for naming resources.
- `name`: Name for the resources.
- `pods_cidr`: CIDR block for pod networking.
- `services_cidr`: CIDR block for service networking.
- `service_account_name`: Service account for the GKE cluster.

## Usage

### Using the Makefile

You can use the `Makefile` to simplify the Terraform workflow. The `Makefile` contains targets to handle initialization, planning, applying, and destroying infrastructure with the `tofu` tool.

---

## Create a `tfvars` File

Create a `.tfvars` file in "/tfvars/ to define the variable values. The `.tfvars` file is used to configure variables that Terraform will use during deployment.

### Example `sample.tfvars`

```hcl
# GCP Project ID
project_id = "platform-439702"

# License Key (used for authentication)
licenseKey = "dev"

# GKE Cluster Settings
region     = "us-central1"
zones      = ["us-central1-a", "us-central1-b", "us-central1-c"]
name       = "test-cluster1"
namespace = "test"

# Service Account Name
service_account_name = "gke-service-account1"

# GitHub Personal Access Token (from stackgen team)
STACKGEN_PAT = "PAT_TOKEN"
domain = "appcd.test"

### Initialise dependancies

1. **Initialize dependancies **:   
   ```bash
   make deps
   ```

### Example Usage

1. **Initialize Terraform**:  
   Run the following command to initialize Terraform and download required providers.

   ```bash
   make init
   ```

2. **Create a Plan**:  
   To create a plan for the environment `dev`, use:

   ```bash
   make plan/dev
   ```

3. **Apply the Plan**:  
   To apply the changes for the environment `dev`:

   ```bash
   make apply/dev
   ```

4. **Destroy the Infrastructure**:  
   If you wish to destroy the resources created for the environment `dev`, run:

   ```bash
   make destroy/dev
   ```

## Notes

- Ensure you have sufficient permissions to create and manage GKE clusters and databases in the Google Cloud project.
- The GKE cluster module requires a service account with appropriate IAM roles to create and manage resources.
