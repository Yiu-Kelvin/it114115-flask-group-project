output "cluster_endpoint" {
  description = "endpoint of the cluster"
  value       = module.eks.cluster_endpoint
}

output "update_kubeconfig_command" {
  description = "command for updating kubeconfig"
  value       = "aws eks update-kubeconfig --region ${var.region} --name ${var.cluster_name}"
}