
data "aws_eks_cluster_auth" "this" {
  name = module.eks.cluster_name
}

data "aws_ecr_authorization_token" "token" {
  registry_id = 891377140475
}

provider "helm" {
  kubernetes {
    host                   = module.eks.cluster_endpoint
    cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)
    token                  = data.aws_eks_cluster_auth.this.token
  }
  registry {
    url      = "oci://891377140475.dkr.ecr.us-east-1.amazonaws.com"
    username = data.aws_ecr_authorization_token.token.user_name
    password = data.aws_ecr_authorization_token.token.password
  }
}

resource "helm_release" "latest" {
  name = "latest"

  repository = "oci://891377140475.dkr.ecr.us-east-1.amazonaws.com"
  chart      = "flask_chart"
}

