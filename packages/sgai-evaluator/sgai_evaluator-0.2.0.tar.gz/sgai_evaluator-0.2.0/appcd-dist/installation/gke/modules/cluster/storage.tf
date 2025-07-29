locals {
  pv_name            = "gcs-fuse-csi-pv-${var.suffix}"
  storage_class_name = "storage-class-${var.suffix}"
}

# Resource: Cloud Storage Bucket
resource "google_storage_bucket" "this" {
  name                        = "stackgen-fuse-${var.suffix}"
  location                    = var.region
  uniform_bucket_level_access = true
  force_destroy               = true

  retention_policy {
    retention_period = var.retention_period
  }
}

output "blob_storage" {
  value = google_storage_bucket.this.name
}

resource "kubernetes_persistent_volume" "gcs_fuse_csi_pv" {
  metadata {
    name = local.pv_name
  }
  spec {
    access_modes = ["ReadWriteMany"]
    capacity = {
      storage = "1Ti"
    }
    storage_class_name = local.storage_class_name
    mount_options = [
      "implicit-dirs",
    ]
    persistent_volume_source {
      csi {
        driver        = "gcsfuse.csi.storage.gke.io"
        volume_handle = google_storage_bucket.this.name
        volume_attributes = {
          gcsfuseLoggingSeverity = "warning"
        }
      }
    }
  }
}

output "storage" {
  value = {
    class = local.storage_class_name
    pv    = local.pv_name
  }
}
