variable "project_id" {
  type = string
}

variable "region" {
  type = string
}

variable "domain" {
  type = string
}

variable "frontend_bucket_name" {
  description = "Name of the GCS bucket for frontend static files"
  type        = string
}

variable "cloud_run_service_name" {
  description = "Name of the Cloud Run backend service"
  type        = string
}

variable "app_name" {
  type = string
}

# ---------------------------------------------------------------------------
# Static IP
# ---------------------------------------------------------------------------
resource "google_compute_global_address" "default" {
  project = var.project_id
  name    = "${var.app_name}-lb-ip"
}

# ---------------------------------------------------------------------------
# Google-managed SSL certificate
# ---------------------------------------------------------------------------
resource "google_compute_managed_ssl_certificate" "default" {
  project = var.project_id
  name    = "${var.app_name}-cert"

  managed {
    domains = [var.domain]
  }
}

# ---------------------------------------------------------------------------
# Frontend: backend bucket with CDN
# ---------------------------------------------------------------------------
resource "google_compute_backend_bucket" "frontend" {
  project     = var.project_id
  name        = "${var.app_name}-frontend"
  bucket_name = var.frontend_bucket_name
  enable_cdn  = true

  cdn_policy {
    cache_mode                   = "CACHE_ALL_STATIC"
    default_ttl                  = 3600
    max_ttl                      = 86400
    serve_while_stale            = 86400
    signed_url_cache_max_age_sec = 0
  }
}

# ---------------------------------------------------------------------------
# Backend: Serverless NEG -> backend service
# ---------------------------------------------------------------------------
resource "google_compute_region_network_endpoint_group" "cloud_run" {
  project               = var.project_id
  name                  = "${var.app_name}-neg"
  region                = var.region
  network_endpoint_type = "SERVERLESS"

  cloud_run {
    service = var.cloud_run_service_name
  }
}

resource "google_compute_backend_service" "backend" {
  project               = var.project_id
  name                  = "${var.app_name}-backend"
  protocol              = "HTTPS"
  load_balancing_scheme = "EXTERNAL_MANAGED"
  timeout_sec           = 3600

  backend {
    group = google_compute_region_network_endpoint_group.cloud_run.id
  }
}

# ---------------------------------------------------------------------------
# URL map: path-based routing
# ---------------------------------------------------------------------------
resource "google_compute_url_map" "default" {
  project         = var.project_id
  name            = "${var.app_name}-url-map"
  default_service = google_compute_backend_bucket.frontend.id

  host_rule {
    hosts        = [var.domain]
    path_matcher = "main"
  }

  path_matcher {
    name            = "main"
    default_service = google_compute_backend_bucket.frontend.id

    path_rule {
      paths   = ["/api/*"]
      service = google_compute_backend_service.backend.id
    }

    path_rule {
      paths   = ["/ws/*"]
      service = google_compute_backend_service.backend.id
    }
  }
}

# ---------------------------------------------------------------------------
# HTTPS proxy + forwarding rule
# ---------------------------------------------------------------------------
resource "google_compute_target_https_proxy" "default" {
  project          = var.project_id
  name             = "${var.app_name}-https-proxy"
  url_map          = google_compute_url_map.default.id
  ssl_certificates = [google_compute_managed_ssl_certificate.default.id]
}

resource "google_compute_global_forwarding_rule" "https" {
  project               = var.project_id
  name                  = "${var.app_name}-https-rule"
  load_balancing_scheme = "EXTERNAL_MANAGED"
  target                = google_compute_target_https_proxy.default.id
  ip_address            = google_compute_global_address.default.address
  port_range            = "443"
}

# ---------------------------------------------------------------------------
# HTTP -> HTTPS redirect
# ---------------------------------------------------------------------------
resource "google_compute_url_map" "http_redirect" {
  project = var.project_id
  name    = "${var.app_name}-http-redirect"

  default_url_redirect {
    https_redirect = true
    strip_query    = false
  }
}

resource "google_compute_target_http_proxy" "redirect" {
  project = var.project_id
  name    = "${var.app_name}-http-proxy"
  url_map = google_compute_url_map.http_redirect.id
}

resource "google_compute_global_forwarding_rule" "http" {
  project               = var.project_id
  name                  = "${var.app_name}-http-rule"
  load_balancing_scheme = "EXTERNAL_MANAGED"
  target                = google_compute_target_http_proxy.redirect.id
  ip_address            = google_compute_global_address.default.address
  port_range            = "80"
}

# ---------------------------------------------------------------------------
# Outputs
# ---------------------------------------------------------------------------
output "static_ip" {
  value = google_compute_global_address.default.address
}

output "url_map_name" {
  value = google_compute_url_map.default.name
}
