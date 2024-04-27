
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
    google = {
      source  = "hashicorp/google"
      version = "4.51.0"
    }
  }
}
provider "google" {
  project = var.project_id
  region  = "us-central1"
  zone    = "us-central1-a"
}


variable "project_id" {
  type    = string
  default = "flask-proj-419005"
}

variable "cluster_name" {
  type    = string
  default = "flask-cluster"
}

variable "vpc_name" {
  type    = string
  default = "flask-vpc"
}

variable "region" {
  type    = string
  default = "us-central1"
}

variable "vpc_cidr" {
  type    = string
  default = "10.123.0.0/16"
}

variable "vpc_azs" {
  type    = list(string)
  default = ["us-east-1a", "us-east-1b"]
}

variable "subnets" {
  type = map(list(string))
  default = {
    "public_subnets"  = ["10.123.1.0/24", "10.123.2.0/24"],
    "private_subnets" = ["10.123.3.0/24", "10.123.4.0/24"],
    "intra_subnets"   = ["10.123.5.0/24", "10.123.6.0/24"]
  }
}