variable "environment" {
  type    = string
  default = "prod"
}

variable "app_name" {
  type = string
}

variable "dd_api_key_secret_id" {
  description = "Secret Manager secret ID for DD_API_KEY"
  type        = string
}

output "env_vars" {
  description = "Non-secret Datadog environment variables for Cloud Run"
  value = {
    DD_ENV                      = var.environment
    DD_SERVICE                  = "${var.app_name}-api"
    DD_VERSION                  = "1.0.0"
    DD_LOGS_INJECTION           = "true"
    DD_PROFILING_ENABLED        = "true"
    DD_RUNTIME_METRICS_ENABLED  = "true"
    DD_LLMOBS_ENABLED           = "1"
    DD_LLMOBS_ML_APP            = var.app_name
    DD_LLMOBS_AGENTLESS_ENABLED                = "1"
    DD_TRACE_PROPAGATION_STYLE                 = "datadog,tracecontext"
    DD_REMOTE_CONFIG_ENABLED                   = "true"
    DD_EXPERIMENTAL_FLAGGING_PROVIDER_ENABLED  = "true"
  }
}

output "secret_env_vars" {
  description = "Datadog secret environment variable references for Cloud Run"
  value = {
    DD_API_KEY = var.dd_api_key_secret_id
  }
}
