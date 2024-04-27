provider "aws" {
  region = var.region
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
  default = "us-east-1"
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