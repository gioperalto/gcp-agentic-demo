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

variable "github_app_installation_id" {
  type = string
}

variable "github_owner" {
  type = string
}

variable "github_repo" {
  type = string
}

variable "artifact_registry_repo_url" {
  description = "Full Artifact Registry repo URL (e.g., us-central1-docker.pkg.dev/project/repo)"
  type        = string
}

variable "cloud_run_service_name" {
  type = string
}

variable "frontend_bucket_name" {
  type = string
}

variable "url_map_name" {
  type = string
}

variable "domain" {
  type = string
}

variable "vite_dd_client_token_secret_id" {
  description = "Secret Manager secret ID for VITE_DD_CLIENT_TOKEN"
  type        = string
}

variable "vite_dd_app_id_secret_id" {
  description = "Secret Manager secret ID for VITE_DD_APP_ID"
  type        = string
}

variable "media_bucket_name" {
  description = "Private GCS bucket name for travel images"
  type        = string
}

variable "seeder_job_name" {
  description = "Cloud Run Job name for Firestore seeder"
  type        = string
}

variable "app_name" {
  type = string
}

# ---------------------------------------------------------------------------
# GitHub Connection (Cloud Build 2nd-gen)
# ---------------------------------------------------------------------------
resource "google_cloudbuildv2_connection" "github" {
  project  = var.project_id
  location = var.region
  name     = "github-${var.github_owner}"

  github_config {
    app_installation_id = var.github_app_installation_id
  }
}

resource "google_cloudbuildv2_repository" "repo" {
  project           = var.project_id
  location          = var.region
  name              = var.github_repo
  parent_connection = google_cloudbuildv2_connection.github.id
  remote_uri        = "https://github.com/${var.github_owner}/${var.github_repo}.git"
}

# ---------------------------------------------------------------------------
# Backend Build Service Account
# ---------------------------------------------------------------------------
resource "google_service_account" "backend_build" {
  project      = var.project_id
  account_id   = "cb-backend-build"
  display_name = "Cloud Build - Backend"
}

resource "google_project_iam_member" "backend_build_ar_writer" {
  project = var.project_id
  role    = "roles/artifactregistry.writer"
  member  = "serviceAccount:${google_service_account.backend_build.email}"
}

resource "google_project_iam_member" "backend_build_run_admin" {
  project = var.project_id
  role    = "roles/run.admin"
  member  = "serviceAccount:${google_service_account.backend_build.email}"
}

resource "google_project_iam_member" "backend_build_sa_user" {
  project = var.project_id
  role    = "roles/iam.serviceAccountUser"
  member  = "serviceAccount:${google_service_account.backend_build.email}"
}

resource "google_project_iam_member" "backend_build_log_writer" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.backend_build.email}"
}

# ---------------------------------------------------------------------------
# Frontend Build Service Account
# ---------------------------------------------------------------------------
resource "google_service_account" "frontend_build" {
  project      = var.project_id
  account_id   = "cb-frontend-build"
  display_name = "Cloud Build - Frontend"
}

resource "google_storage_bucket_iam_member" "frontend_build_storage" {
  bucket = var.frontend_bucket_name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.frontend_build.email}"
}

resource "google_project_iam_member" "frontend_build_lb_admin" {
  project = var.project_id
  role    = "roles/compute.loadBalancerAdmin"
  member  = "serviceAccount:${google_service_account.frontend_build.email}"
}

resource "google_project_iam_member" "frontend_build_log_writer" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.frontend_build.email}"
}

resource "google_project_iam_member" "frontend_build_secret_accessor" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.frontend_build.email}"
}

# ---------------------------------------------------------------------------
# Content Build Service Account (image sync + Firestore seeder)
# ---------------------------------------------------------------------------
resource "google_service_account" "content_build" {
  project      = var.project_id
  account_id   = "cb-content-build"
  display_name = "Cloud Build - Content (images + Firestore seed)"
}

resource "google_storage_bucket_iam_member" "content_build_media_admin" {
  bucket = var.media_bucket_name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.content_build.email}"
}

resource "google_project_iam_member" "content_build_run_developer" {
  project = var.project_id
  role    = "roles/run.developer"
  member  = "serviceAccount:${google_service_account.content_build.email}"
}

resource "google_project_iam_member" "content_build_log_writer" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.content_build.email}"
}

resource "google_project_iam_member" "content_build_sa_user" {
  project = var.project_id
  role    = "roles/iam.serviceAccountUser"
  member  = "serviceAccount:${google_service_account.content_build.email}"
}

# ---------------------------------------------------------------------------
# Backend Trigger
# ---------------------------------------------------------------------------
resource "google_cloudbuild_trigger" "backend" {
  project  = var.project_id
  location = var.region
  name     = "backend-deploy-${var.environment}"

  repository_event_config {
    repository = google_cloudbuildv2_repository.repo.id
    push {
      branch = "^main$"
    }
  }

  included_files = ["backend/**", "tribune_concierge/**", "legionnaire_concierge/**", "insecure_concierge/**"]
  filename       = "backend/cloudbuild.yaml"

  substitutions = {
    _AR_HOST      = "${var.region}-docker.pkg.dev"
    _AR_REPO      = var.artifact_registry_repo_url
    _IMAGE_NAME   = "${var.app_name}-api"
    _SERVICE_NAME = var.cloud_run_service_name
    _RUN_REGION   = var.region
  }

  service_account = google_service_account.backend_build.id
}

# ---------------------------------------------------------------------------
# Frontend Trigger
# ---------------------------------------------------------------------------
resource "google_cloudbuild_trigger" "frontend" {
  project  = var.project_id
  location = var.region
  name     = "frontend-deploy-${var.environment}"

  repository_event_config {
    repository = google_cloudbuildv2_repository.repo.id
    push {
      branch = "^main$"
    }
  }

  included_files = ["frontend/**"]
  filename       = "frontend/cloudbuild.yaml"

  substitutions = {
    _DEPLOY_BUCKET                 = var.frontend_bucket_name
    _URL_MAP_NAME                  = var.url_map_name
    _VITE_API_BASE_URL             = "https://${var.domain}"
    _VITE_DD_CLIENT_TOKEN_SECRET   = "${var.vite_dd_client_token_secret_id}/versions/latest"
    _VITE_DD_APP_ID_SECRET         = "${var.vite_dd_app_id_secret_id}/versions/latest"
  }

  service_account = google_service_account.frontend_build.id
}

# ---------------------------------------------------------------------------
# Load-Gen Trigger (build image only — job execution is on-demand)
# ---------------------------------------------------------------------------
resource "google_cloudbuild_trigger" "load_gen" {
  project  = var.project_id
  location = var.region
  name     = "load-gen-build-${var.environment}"

  repository_event_config {
    repository = google_cloudbuildv2_repository.repo.id
    push {
      branch = "^main$"
    }
  }

  included_files = ["load-gen/**"]

  build {
    step {
      name = "gcr.io/cloud-builders/docker"
      args = [
        "build",
        "-t", "${var.artifact_registry_repo_url}/${var.app_name}-load-gen:$SHORT_SHA",
        "-t", "${var.artifact_registry_repo_url}/${var.app_name}-load-gen:latest",
        "-f", "load-gen/Dockerfile",
        ".",
      ]
    }
    step {
      name = "gcr.io/cloud-builders/docker"
      args = ["push", "--all-tags", "${var.artifact_registry_repo_url}/${var.app_name}-load-gen"]
    }
    options {
      logging = "CLOUD_LOGGING_ONLY"
    }
  }

  service_account = google_service_account.backend_build.id
}

# ---------------------------------------------------------------------------
# Content Trigger (image upload + Firestore reseed)
# ---------------------------------------------------------------------------
resource "google_cloudbuild_trigger" "content" {
  project  = var.project_id
  location = var.region
  name     = "content-seed-${var.environment}"

  repository_event_config {
    repository = google_cloudbuildv2_repository.repo.id
    push {
      branch = "^main$"
    }
  }

  included_files = [
    "backend/data/**",
    "frontend/public/img/**",
    "backend/scripts/**",
  ]
  filename = "backend/cloudbuild.content.yaml"

  substitutions = {
    _MEDIA_BUCKET    = var.media_bucket_name
    _SEEDER_JOB_NAME = var.seeder_job_name
    _RUN_REGION      = var.region
  }

  service_account = google_service_account.content_build.id
}
