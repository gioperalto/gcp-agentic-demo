output "load_balancer_ip" {
  description = "Global static IP address of the HTTPS load balancer"
  value       = module.load_balancer.static_ip
}

output "cloud_run_url" {
  description = "URL of the Cloud Run backend service"
  value       = module.cloud_run.service_url
}

output "frontend_bucket_name" {
  description = "Name of the GCS bucket hosting the frontend SPA"
  value       = module.frontend_bucket.bucket_name
}

output "artifact_registry_repo" {
  description = "Full path of the Artifact Registry Docker repository"
  value       = module.artifact_registry.repository_url
}

output "dns_name_servers" {
  description = "Name servers for the DNS zone (configure at your registrar)"
  value       = module.dns.name_servers
}
