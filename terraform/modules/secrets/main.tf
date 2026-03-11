variable "project_id" {
  type = string
}

variable "secrets" {
  description = "Map of secret name to secret value"
  type        = map(string)
  sensitive   = true
}

resource "google_secret_manager_secret" "secrets" {
  for_each = var.secrets

  project   = var.project_id
  secret_id = each.key

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "versions" {
  for_each = var.secrets

  secret      = google_secret_manager_secret.secrets[each.key].id
  secret_data = each.value
}

output "secret_ids" {
  description = "Map of secret name to secret resource ID"
  value       = { for k, v in google_secret_manager_secret.secrets : k => v.id }
}

output "secret_version_ids" {
  description = "Map of secret name to latest version resource name"
  value       = { for k, v in google_secret_manager_secret_version.versions : k => v.name }
}
