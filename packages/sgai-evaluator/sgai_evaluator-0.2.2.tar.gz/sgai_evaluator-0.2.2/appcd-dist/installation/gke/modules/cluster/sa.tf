resource "google_service_account" "project_service_account" {
  project      = var.project_id
  account_id   = local.service_account_name
  display_name = "Project Service Account"
}

# Grant container.clusterAdmin role to service account
resource "google_project_iam_member" "project_service_account_container_cluster_admin" {
  project = var.project_id
  role    = "roles/container.clusterAdmin"
  member  = "serviceAccount:${google_service_account.project_service_account.email}"
}

# Grant storage.admin role to service account
resource "google_project_iam_member" "project_service_account_storage_admin" {
  project = var.project_id
  role    = "roles/storage.admin"
  member  = "serviceAccount:${google_service_account.project_service_account.email}"
}
