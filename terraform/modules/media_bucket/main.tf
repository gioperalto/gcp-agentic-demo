variable "project_id" { type = string }
variable "region" { type = string }
variable "environment" {
  type    = string
  default = "prod"
}
variable "cloud_run_sa_email" {
  description = "Cloud Run service account email — granted objectViewer for signed URL generation"
  type        = string
}

# ---------------------------------------------------------------------------
# Private media bucket — images are NOT publicly accessible.
# The Cloud Run service account uses signed URLs to serve images.
# ---------------------------------------------------------------------------
resource "google_storage_bucket" "media" {
  project       = var.project_id
  name          = "${var.project_id}-media-${var.environment}"
  location      = var.region
  force_destroy = false

  uniform_bucket_level_access = true

  cors {
    origin          = ["*"]
    method          = ["GET", "HEAD"]
    response_header = ["Content-Type"]
    max_age_seconds = 3600
  }
}

# Cloud Run SA: objectViewer so it can generate signed URLs and stream objects
resource "google_storage_bucket_iam_member" "cloud_run_viewer" {
  bucket = google_storage_bucket.media.name
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${var.cloud_run_sa_email}"
}

output "bucket_name" {
  value = google_storage_bucket.media.name
}

output "bucket_url" {
  value = google_storage_bucket.media.url
}
