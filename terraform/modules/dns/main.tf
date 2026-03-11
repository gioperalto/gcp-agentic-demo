variable "project_id" {
  type = string
}

variable "domain" {
  description = "Domain name (e.g., travel.example.com)"
  type        = string
}

variable "lb_ip_address" {
  description = "IP address of the load balancer"
  type        = string
}

locals {
  # Convert domain to a DNS zone name (e.g., travel.example.com -> travel-example-com)
  zone_name = replace(var.domain, ".", "-")
}

resource "google_dns_managed_zone" "main" {
  project     = var.project_id
  name        = local.zone_name
  dns_name    = "${var.domain}."
  description = "DNS zone for Travel Planner"
}

resource "google_dns_record_set" "a" {
  project      = var.project_id
  managed_zone = google_dns_managed_zone.main.name
  name         = "${var.domain}."
  type         = "A"
  ttl          = 300
  rrdatas      = [var.lb_ip_address]
}

output "name_servers" {
  value = google_dns_managed_zone.main.name_servers
}

output "zone_name" {
  value = google_dns_managed_zone.main.name
}
