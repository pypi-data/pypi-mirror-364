locals {
  pv_name              = "s3-pv-${var.namespace}"
  should_lookup_bucket = var.data_bucket_name == "" && var.existing_cluster.lookup
  bucket_name          = local.should_lookup_bucket ? data.aws_s3_bucket.appcd_bucket[0].id : var.data_bucket_name
}

data "aws_s3_bucket" "appcd_bucket" {
  count  = local.should_lookup_bucket ? 1 : 0
  bucket = "appcd-blobs-${var.existing_cluster.created_for}-artifacts"
}


resource "kubernetes_manifest" "persistent_volume" {
  manifest = {
    apiVersion = "v1"
    kind       = "PersistentVolume"
    metadata = {
      name = local.pv_name
    }
    spec = {
      capacity = {
        storage = "1200Gi"
      }
      accessModes = [
        "ReadWriteMany"
      ]
      mountOptions = [
        "allow-delete",
        "region ${var.region}",
        "uid=1001",
        "gid=1001",
        "file-mode=0666",
        "allow-other"
      ]
      csi = {
        driver       = "s3.csi.aws.com"
        volumeHandle = "s3-csi-driver-volume"
        volumeAttributes = {
          bucketName = local.bucket_name
        }
      }
    }
  }
}

resource "kubernetes_manifest" "s3_claim" {
  depends_on = [
    kubernetes_namespace.appcd
  ]
  manifest = {
    apiVersion = "v1"
    kind       = "PersistentVolumeClaim"
    metadata = {
      name      = "storage-${local.namespace}"
      namespace = local.namespace
    }
    spec = {
      accessModes = [
        "ReadWriteMany"
      ]
      storageClassName = ""
      resources = {
        requests = {
          storage = "1200Gi"
        }
      }
      volumeName = local.pv_name
    }
  }
}
