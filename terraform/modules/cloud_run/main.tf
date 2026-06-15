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
  description = "Full Docker image URI (e.g., us-central1-docker.pkg.dev/project/repo/image:tag)"
  type        = string
}

variable "service_account_email" {
  description = "Service account email to attach to Cloud Run"
  type        = string
}

variable "max_instance_count" {
  description = "Maximum number of Cloud Run instances"
  type        = number
  default     = 10
}

variable "env_vars" {
  description = "Non-secret environment variables"
  type        = map(string)
  default     = {}
}

variable "secret_env_vars" {
  description = "Map of env var name to Secret Manager secret ID (projects/PROJECT/secrets/NAME)"
  type        = map(string)
  default     = {}
}

variable "app_name" {
  type = string
}

resource "google_cloud_run_v2_service" "backend" {
  project  = var.project_id
  name     = "${var.app_name}-api-${var.environment}"
  location = var.region
  ingress  = "INGRESS_TRAFFIC_INTERNAL_LOAD_BALANCER"

  template {
    service_account = var.service_account_email

    scaling {
      min_instance_count = 1
      max_instance_count = var.max_instance_count
    }

    timeout          = "3600s"
    session_affinity = true

    containers {
      image = var.image

      ports {
        container_port = 8080
      }

      resources {
        limits = {
          cpu    = "2"
          memory = "1Gi"
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

  depends_on = []
}

# Allow the load balancer to invoke the service
resource "google_cloud_run_v2_service_iam_member" "lb_invoker" {
  project  = var.project_id
  name     = google_cloud_run_v2_service.backend.name
  location = var.region
  role     = "roles/run.invoker"
  member   = "allUsers"
}

output "service_name" {
  value = google_cloud_run_v2_service.backend.name
}

output "service_url" {
  value = google_cloud_run_v2_service.backend.uri
}
