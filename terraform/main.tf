terraform {
  required_version = ">= 1.5"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# ---------------------------------------------------------------------------
# Enable required GCP APIs
# ---------------------------------------------------------------------------
module "project_services" {
  source     = "./modules/project_services"
  project_id = var.project_id
}

# ---------------------------------------------------------------------------
# Artifact Registry (Docker repo)
# ---------------------------------------------------------------------------
module "artifact_registry" {
  source      = "./modules/artifact_registry"
  project_id  = var.project_id
  region      = var.region
  environment = var.environment

  depends_on = [module.project_services]
}

# ---------------------------------------------------------------------------
# Service Accounts + IAM
# ---------------------------------------------------------------------------
module "service_accounts" {
  source     = "./modules/service_accounts"
  project_id = var.project_id

  depends_on = [module.project_services]
}

# ---------------------------------------------------------------------------
# Secret Manager
# ---------------------------------------------------------------------------
module "secrets" {
  source     = "./modules/secrets"
  project_id = var.project_id

  secrets = {
    JWT_SECRET_KEY       = var.jwt_secret_key
    DATADOG_API_KEY      = var.datadog_api_key
    DD_APPLICATION_KEY   = var.dd_application_key
    VITE_DD_CLIENT_TOKEN = var.vite_dd_client_token
    VITE_DD_APP_ID       = var.vite_dd_app_id
  }

  depends_on = [module.project_services]
}

# ---------------------------------------------------------------------------
# Datadog env var configuration
# ---------------------------------------------------------------------------
module "datadog" {
  source               = "./modules/datadog"
  environment          = var.environment
  dd_api_key_secret_id = module.secrets.secret_ids["DATADOG_API_KEY"]
}

# ---------------------------------------------------------------------------
# Cloud Run Backend
# ---------------------------------------------------------------------------
module "cloud_run" {
  source                = "./modules/cloud_run"
  project_id            = var.project_id
  region                = var.region
  environment           = var.environment
  image                 = "${module.artifact_registry.repository_url}/travel-planner-api:latest"
  service_account_email = module.service_accounts.cloud_run_sa_email
  max_instance_count    = var.cloud_run_max_instances

  env_vars = merge(module.datadog.env_vars, {
    GOOGLE_GENAI_MODEL        = var.google_genai_model
    GOOGLE_GENAI_USE_VERTEXAI = "True"
    GOOGLE_CLOUD_LOCATION     = var.region
    GOOGLE_CLOUD_PROJECT      = var.project_id
    GOOGLE_GENAI_LIVE_MODEL   = var.google_genai_live_model
    ALLOWED_ORIGINS           = "https://${var.domain}"
    API_BASE_URL              = "http://localhost:8080"
    MEDIA_BUCKET_NAME         = module.media_bucket.bucket_name
    SIGNED_URL_TTL_MINUTES    = tostring(var.signed_url_ttl_minutes)
  })

  secret_env_vars = merge(module.datadog.secret_env_vars, {
    JWT_SECRET_KEY = module.secrets.secret_ids["JWT_SECRET_KEY"]
  })

  depends_on = [module.project_services, module.media_bucket]
}

# ---------------------------------------------------------------------------
# Media GCS Bucket (private — images served via signed URLs)
# ---------------------------------------------------------------------------
module "media_bucket" {
  source             = "./modules/media_bucket"
  project_id         = var.project_id
  region             = var.region
  environment        = var.environment
  cloud_run_sa_email = module.service_accounts.cloud_run_sa_email

  depends_on = [module.project_services, module.service_accounts]
}

# ---------------------------------------------------------------------------
# Firestore Database (native mode)
# ---------------------------------------------------------------------------
module "firestore" {
  source             = "./modules/firestore"
  project_id         = var.project_id
  firestore_location = var.firestore_location

  depends_on = [module.project_services]
}

# ---------------------------------------------------------------------------
# Firestore Seeder Job
# ---------------------------------------------------------------------------
module "seeder_job" {
  source                = "./modules/seeder_job"
  project_id            = var.project_id
  region                = var.region
  environment           = var.environment
  image                 = "${module.artifact_registry.repository_url}/travel-planner-api:latest"
  service_account_email = module.service_accounts.cloud_run_sa_email
  media_bucket_name     = module.media_bucket.bucket_name

  depends_on = [module.project_services, module.media_bucket, module.firestore]
}

# ---------------------------------------------------------------------------
# Frontend GCS Bucket
# ---------------------------------------------------------------------------
module "frontend_bucket" {
  source      = "./modules/frontend_bucket"
  project_id  = var.project_id
  region      = var.region
  environment = var.environment

  depends_on = [module.project_services]
}

# ---------------------------------------------------------------------------
# Global HTTPS Load Balancer + CDN
# ---------------------------------------------------------------------------
module "load_balancer" {
  source                 = "./modules/load_balancer"
  project_id             = var.project_id
  region                 = var.region
  domain                 = var.domain
  frontend_bucket_name   = module.frontend_bucket.bucket_name
  cloud_run_service_name = module.cloud_run.service_name
}

# ---------------------------------------------------------------------------
# DNS
# ---------------------------------------------------------------------------
module "dns" {
  source        = "./modules/dns"
  project_id    = var.project_id
  domain        = var.domain
  lb_ip_address = module.load_balancer.static_ip
}

# ---------------------------------------------------------------------------
# CI/CD (Cloud Build)
# ---------------------------------------------------------------------------
module "cicd" {
  source = "./modules/cicd"

  project_id                    = var.project_id
  region                        = var.region
  environment                   = var.environment
  github_app_installation_id    = var.github_app_installation_id
  github_owner                  = var.github_owner
  github_repo                   = var.github_repo
  artifact_registry_repo_url    = module.artifact_registry.repository_url
  cloud_run_service_name        = module.cloud_run.service_name
  frontend_bucket_name          = module.frontend_bucket.bucket_name
  url_map_name                  = module.load_balancer.url_map_name
  domain                        = var.domain
  vite_dd_client_token_secret_id = module.secrets.secret_ids["VITE_DD_CLIENT_TOKEN"]
  vite_dd_app_id_secret_id      = module.secrets.secret_ids["VITE_DD_APP_ID"]
  media_bucket_name              = module.media_bucket.bucket_name
  seeder_job_name                = module.seeder_job.job_name

  depends_on = [module.project_services, module.media_bucket, module.seeder_job]
}

# ---------------------------------------------------------------------------
# Load Generator (Cloud Run Job)
# ---------------------------------------------------------------------------
module "load_gen" {
  source     = "./modules/load_gen"
  project_id = var.project_id
  region     = var.region
  environment = var.environment
  image      = "${module.artifact_registry.repository_url}/travel-planner-load-gen:latest"
  service_account_email = module.service_accounts.cloud_run_sa_email

  env_vars = {
    DD_ENV                   = var.environment
    DD_SERVICE               = "travel-planner-load-gen"
    DD_LLMOBS_AGENTLESS_ENABLED = "1"
    DD_TRACE_PROPAGATION_STYLE = "datadog,tracecontext"
    LOAD_GEN_FRONTEND_URL    = "https://${var.domain}"
    LOAD_GEN_BACKEND_URL     = "https://${var.domain}"
    LOAD_GEN_HEADLESS        = "true"
  }

  secret_env_vars = {
    DD_API_KEY = module.secrets.secret_ids["DATADOG_API_KEY"]
  }

  depends_on = [module.project_services]
}
