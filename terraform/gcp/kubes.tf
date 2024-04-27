

data "google_client_config" "default" {}

data "google_artifact_registry_repository" "flask_chart" {
  location      = "us-central1"
  repository_id = "flask-chart"
  
}

data "http" "crd" {
  url = "https://raw.githubusercontent.com/mysql/mysql-operator/trunk/deploy/deploy-crds.yaml"
  request_headers = {
    Accept = "text/plain"
  }
}
locals {
  crd_yamls            = split("---", data.http.crd.body)
  mysql_operator_yamls = split("---", data.http.mysql-operator.body)
}



data "http" "mysql-operator" {
  url = "https://raw.githubusercontent.com/mysql/mysql-operator/trunk/deploy/deploy-operator.yaml"
  request_headers = {
    Accept = "text/plain"
  }
}


provider "kubectl" {
  host                   = google_container_cluster.primary.endpoint
  token                  = data.google_client_config.default.access_token
  cluster_ca_certificate = base64decode(google_container_cluster.primary.master_auth.0.cluster_ca_certificate)
  client_key             = base64decode(google_container_cluster.primary.master_auth.0.client_key)
  client_certificate     = base64decode(google_container_cluster.primary.master_auth.0.client_certificate)
  load_config_file = false
}



provider "helm" {
  kubernetes {
    host                   = google_container_cluster.primary.endpoint
    token                  = data.google_client_config.default.access_token
    client_certificate     = base64decode(google_container_cluster.primary.master_auth.0.client_certificate)
    client_key             = base64decode(google_container_cluster.primary.master_auth.0.client_key)
    cluster_ca_certificate = base64decode(google_container_cluster.primary.master_auth.0.cluster_ca_certificate)
  }
  registry {
    url      = "oci://us-central1-docker.pkg.dev/flask-proj-419005"
    username = "oauth2accesstoken"
    password = data.google_client_config.default.access_token
  }
}

resource "helm_release" "latest" {
  name = "helm"
  repository = "oci://us-central1-docker.pkg.dev/flask-proj-419005"
  chart      = "flask-chart/flask_chart"
}

resource "kubectl_manifest" "crd" {
  count     = length(local.crd_yamls)
  yaml_body = local.crd_yamls[count.index]
}

resource "kubectl_manifest" "mysql-operator" {
  count     = length(local.mysql_operator_yamls)
  yaml_body = local.mysql_operator_yamls[count.index]

  depends_on = [kubectl_manifest.crd]
  
}

resource "kubectl_manifest" "mycluster_cluster_secret" {
  yaml_body= <<YAML
apiVersion: v1
kind: Secret
metadata:
  name: mycluster-cluster-secret
namespace: default
stringData:
  rootUser: "root"
  rootHost: "%"
  rootPassword: "1234"
YAML
}
resource "kubectl_manifest" "mycluster_sa" {
  yaml_body= <<YAML
apiVersion: v1
kind: ServiceAccount
metadata:
  name: mycluster-sa
  namespace: default
YAML
}
# https://github.com/hashicorp/terraform-provider-ku`bernetes/issues/1380#issuecomment-967022975
resource "kubectl_manifest" "innodb" {
  yaml_body= <<YAML
apiVersion: mysql.oracle.com/v2
kind: InnoDBCluster
metadata:
  name: flask-db
  namespace: default
spec:
  instances: 3
  tlsUseSelfSigned: true
  router:
    instances: 1
  secretName: mycluster-cluster-secret
  imagePullPolicy : IfNotPresent
  baseServerId: 1000
  version: 8.3.0
  serviceAccountName: mycluster-sa
YAML
}