variable "project_id" { type = string }
variable "region" { type = string }
variable "environment" {
  type    = string
  default = "prod"
}
variable "image" {
  description = "Container image (same as backend API image)"
  type        = string
}
variable "service_account_email" { type = string }
variable "media_bucket_name" { type = string }

# ---------------------------------------------------------------------------
# Cloud Run Job — Firestore seeder
# Executed from the content Cloud Build pipeline after images are synced.
# Idempotent: upserts catalog collections; never wipes users/applications.
# ---------------------------------------------------------------------------
resource "google_cloud_run_v2_job" "seeder" {
  project  = var.project_id
  location = var.region
  name     = "firestore-seeder-${var.environment}"

  template {
    template {
      service_account = var.service_account_email
      max_retries     = 1
      timeout         = "300s"

      containers {
        image   = var.image
        command = ["python", "scripts/seed_firestore.py"]

        env {
          name  = "GOOGLE_CLOUD_PROJECT"
          value = var.project_id
        }
        env {
          name  = "MEDIA_BUCKET_NAME"
          value = var.media_bucket_name
        }
        env {
          name  = "DD_TRACE_ENABLED"
          value = "false"
        }
        env {
          name  = "PYTHONUNBUFFERED"
          value = "1"
        }

        resources {
          limits = {
            cpu    = "1"
            memory = "512Mi"
          }
        }
      }
    }
  }

  lifecycle {
    ignore_changes = [
      template[0].template[0].containers[0].image,
    ]
  }
}

output "job_name" {
  value = google_cloud_run_v2_job.seeder.name
}
