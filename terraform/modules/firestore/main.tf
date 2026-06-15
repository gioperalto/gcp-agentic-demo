variable "project_id" { type = string }
variable "firestore_location" {
  description = "Firestore multi-region or regional location (e.g., nam5, us-central)"
  type        = string
}

resource "google_firestore_database" "default" {
  project     = var.project_id
  name        = "(default)"
  location_id = var.firestore_location
  type        = "FIRESTORE_NATIVE"

  delete_protection_state = "DELETE_PROTECTION_DISABLED"
  deletion_policy         = "DELETE"
}

output "database_name" {
  value = google_firestore_database.default.name
}
