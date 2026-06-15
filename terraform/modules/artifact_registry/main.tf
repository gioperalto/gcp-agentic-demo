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

variable "app_name" {
  type = string
}

resource "google_artifact_registry_repository" "backend" {
  project       = var.project_id
  location      = var.region
  repository_id = "${var.app_name}-${var.environment}"
  format        = "DOCKER"
  description   = "Docker images for ${var.app_name} backend"
}

output "repository_url" {
  value = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.backend.repository_id}"
}

output "repository_id" {
  value = google_artifact_registry_repository.backend.repository_id
}
