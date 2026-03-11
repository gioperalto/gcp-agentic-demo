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

resource "google_storage_bucket" "frontend" {
  project       = var.project_id
  name          = "${var.project_id}-frontend-${var.environment}"
  location      = var.region
  force_destroy = false

  uniform_bucket_level_access = true

  website {
    main_page_suffix = "index.html"
    not_found_page   = "index.html"
  }

  cors {
    origin          = ["*"]
    method          = ["GET", "HEAD"]
    response_header = ["Content-Type"]
    max_age_seconds = 3600
  }
}

resource "google_storage_bucket_iam_member" "public_read" {
  bucket = google_storage_bucket.frontend.name
  role   = "roles/storage.objectViewer"
  member = "allUsers"
}

output "bucket_name" {
  value = google_storage_bucket.frontend.name
}

output "bucket_url" {
  value = google_storage_bucket.frontend.url
}
