variable "project_id" {
  type = string
}

resource "google_service_account" "cloud_run" {
  project      = var.project_id
  account_id   = "travel-planner-run"
  display_name = "Travel Planner Cloud Run Runtime"
}

resource "google_project_iam_member" "vertex_ai_user" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.cloud_run.email}"
}

resource "google_project_iam_member" "secret_accessor" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.cloud_run.email}"
}

resource "google_project_iam_member" "firestore_user" {
  project = var.project_id
  role    = "roles/datastore.user"
  member  = "serviceAccount:${google_service_account.cloud_run.email}"
}

# Allows the SA to sign GCS blob URLs (needed for v4 signed URLs on Cloud Run)
resource "google_service_account_iam_member" "token_creator_self" {
  service_account_id = google_service_account.cloud_run.name
  role               = "roles/iam.serviceAccountTokenCreator"
  member             = "serviceAccount:${google_service_account.cloud_run.email}"
}

output "cloud_run_sa_email" {
  value = google_service_account.cloud_run.email
}

output "cloud_run_sa_name" {
  value = google_service_account.cloud_run.name
}
