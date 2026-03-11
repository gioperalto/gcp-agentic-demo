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

resource "google_artifact_registry_repository" "backend" {
  project       = var.project_id
  location      = var.region
  repository_id = "travel-planner-${var.environment}"
  format        = "DOCKER"
  description   = "Docker images for Travel Planner backend"
}

output "repository_url" {
  value = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.backend.repository_id}"
}

output "repository_id" {
  value = google_artifact_registry_repository.backend.repository_id
}
