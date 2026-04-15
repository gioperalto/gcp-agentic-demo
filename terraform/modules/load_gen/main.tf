variable "project_id" {
  type = string
}

variable "region" {
  type = string
}

variable "environment" {
  type    = string
  default = "prod"
}

variable "image" {
  description = "Full Docker image URI for the load generator"
  type        = string
}

variable "service_account_email" {
  description = "Service account email to attach to the Cloud Run Job"
  type        = string
}

variable "env_vars" {
  description = "Non-secret environment variables"
  type        = map(string)
  default     = {}
}

variable "secret_env_vars" {
  description = "Map of env var name to Secret Manager secret ID"
  type        = map(string)
  default     = {}
}

variable "app_name" {
  type = string
}

resource "google_cloud_run_v2_job" "load_gen" {
  project  = var.project_id
  name     = "${var.app_name}-load-gen-${var.environment}"
  location = var.region

  template {
    template {
      service_account = var.service_account_email

      timeout = "3600s"

      max_retries = 0

      containers {
        image = var.image

        resources {
          limits = {
            cpu    = "2"
            memory = "2Gi"
          }
        }

        dynamic "env" {
          for_each = var.env_vars
          content {
            name  = env.key
            value = env.value
          }
        }

        dynamic "env" {
          for_each = var.secret_env_vars
          content {
            name = env.key
            value_source {
              secret_key_ref {
                secret  = env.value
                version = "latest"
              }
            }
          }
        }
      }
    }
  }
}

output "job_name" {
  value = google_cloud_run_v2_job.load_gen.name
}
