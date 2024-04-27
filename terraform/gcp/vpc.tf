resource "google_compute_network" "main" {
  name                            = "main"
  routing_mode                    = "REGIONAL"
  auto_create_subnetworks         = false
  mtu                             = 1460
  delete_default_routes_on_create = false

  depends_on = [
    google_project_service.compute,
    google_project_service.container
  ]
}

resource "google_compute_subnetwork" "public-subnetwork" {
  name          = "terraform-public-subnetwork"
  ip_cidr_range = "10.2.0.0/16"
  region        = var.region
  network       = google_compute_network.main.name
}

resource "google_compute_subnetwork" "private-subnetwork" {
  name                     = "terraform-private-subnetwork"
  ip_cidr_range            = "10.3.0.0/16"
  region                   = var.region
  network                  = google_compute_network.main.name
  private_ip_google_access = true
}

resource "google_compute_router" "router" {
  name    = "nat-router"
  network = "main"
  region  = var.region
  
  depends_on = [google_compute_network.main]
}

resource "google_compute_router_nat" "nat" {
  name                               = "my-router-nat"
  router                             = google_compute_router.router.name
  region                             = var.region
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"

  log_config {
    enable = true
    filter = "ERRORS_ONLY"
  }
  depends_on = [google_compute_network.main]
}
