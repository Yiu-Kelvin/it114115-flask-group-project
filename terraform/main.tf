# havent figured out how to use Presistance volume in aws
# module "aws" {
#     source = "./aws"
# } 

module "gcp" {
  source = "./gcp"
}

terraform {
  required_version = ">= 0.13"

  required_providers {
    kubectl = {
      source  = "gavinbunney/kubectl"
      version = ">= 1.7.0"
    }
    kubernetes = {
      source  = "registry.terraform.io/hashicorp/kubernetes"
      version = "2.29.0"
    }
    http = {
      source = "registry.terraform.io/hashicorp/http"
    }
    null = {
      source = "registry.terraform.io/hashicorp/null"
    }
  }
}