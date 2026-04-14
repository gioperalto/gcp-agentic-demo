variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region for regional resources"
  type        = string
  default     = "us-central1"
}

variable "domain" {
  description = "Domain name for the application (e.g., travel.example.com)"
  type        = string
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "prod"
}

variable "google_genai_model" {
  description = "Gemini model for text agents"
  type        = string
  default     = "gemini-3-flash-preview"
}

variable "google_genai_live_model" {
  description = "Gemini model for live/voice agents"
  type        = string
  default     = "gemini-live-2.5-flash-native-audio"
}

variable "cloud_run_max_instances" {
  description = "Maximum number of Cloud Run instances"
  type        = number
  default     = 10
}

variable "firestore_location" {
  description = "Firestore location (e.g., nam5 for US multi-region, us-central for Iowa)"
  type        = string
  default     = "nam5"
}

variable "signed_url_ttl_minutes" {
  description = "TTL in minutes for GCS signed image URLs returned by the API"
  type        = number
  default     = 60
}

variable "github_app_installation_id" {
  description = "GitHub App installation ID for Cloud Build connection"
  type        = string
  default     = ""
}

variable "github_owner" {
  description = "GitHub repository owner"
  type        = string
  default     = ""
}

variable "github_repo" {
  description = "GitHub repository name"
  type        = string
  default     = ""
}

# Secrets (passed via TF_VAR_* env vars or .tfvars - never commit values)
variable "jwt_secret_key" {
  description = "JWT signing secret"
  type        = string
  sensitive   = true
}

variable "datadog_api_key" {
  description = "Datadog API key"
  type        = string
  sensitive   = true
}

variable "dd_application_key" {
  description = "Datadog application key"
  type        = string
  sensitive   = true
}

variable "vite_dd_client_token" {
  description = "Datadog RUM client token (baked into frontend JS bundle)"
  type        = string
  sensitive   = true
}

variable "vite_dd_app_id" {
  description = "Datadog RUM application ID (baked into frontend JS bundle)"
  type        = string
  sensitive   = true
}
