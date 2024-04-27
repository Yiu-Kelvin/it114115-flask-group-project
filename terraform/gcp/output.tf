# data "google_container_cluster" "cluster_data" {
#   name     = var.cluster_name
#   location = var.region
# }

# output "cluster_endpoint" {
#   description = "endpoint of the cluster"
#   value       = data.google_container_cluster.cluster_data.endpoint
# }

output "update_kubeconfig_command" {
  description = "command for updating kubeconfig"
  value       = "gcloud container clusters get-credentials ${var.cluster_name} --region=${var.region}"
}