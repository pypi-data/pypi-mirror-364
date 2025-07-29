resource "kubernetes_namespace" "otel" {
  count = var.region == "us-west-2" ? 1 : 0

  metadata {
    name = "open-telemetry"
  }
}

resource "kubernetes_secret" "ghcr_pkg" {
  depends_on = [kubernetes_namespace.otel]
  metadata {
    name      = "ghcr-pkg"
    namespace = kubernetes_namespace.otel[0].metadata[0].name
  }

  data = {
    ".dockerconfigjson" = jsonencode({
      "auths" = {
        "https://ghcr.io" = {
          "username" = "github_username"
          "password" = var.STACKGEN_PAT
          "email"    = "support"
          "auth"     = base64encode("github_username:${var.STACKGEN_PAT}")
        }
      }
    })
  }

  type = "kubernetes.io/dockerconfigjson"
}

resource "helm_release" "otel_collector" {
  count      = var.region == "us-west-2" ? 1 : 0
  depends_on = [aws_vpc_endpoint.peer_to_signoz]
  name       = "otel-collector"
  namespace  = kubernetes_namespace.otel[0].metadata[0].name
  repository = "https://open-telemetry.github.io/opentelemetry-helm-charts"
  chart      = "opentelemetry-collector"
  version    = "0.119.0"

  values = [
    templatefile("${path.module}/values/opentelemetry.yaml.tmpl", {
      otlp_endpoint    = aws_vpc_endpoint.peer_to_signoz.dns_entry[0].dns_name
      cluster_name     = "${local.cluster_name}"
      imagePullSecrets = kubernetes_secret.ghcr_pkg.metadata[0].name
    })
  ]
  set {
    name  = "podAnnotations.fluentbit\\.io/exclude"
    value = "true"
    type  = "string"
  }
}

resource "aws_security_group" "signoz_endpoint_sg" {
  name        = "signoz-endpoint-sg-${local.cluster_name}"
  description = "Allow OTLP traffic to VPC Endpoint"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port   = 4317
    to_port     = 4317
    protocol    = "tcp"
    cidr_blocks = [local.vpc_cidr]
    description = "Allow gRPC OTLP"
  }

  ingress {
    from_port   = 4318
    to_port     = 4318
    protocol    = "tcp"
    cidr_blocks = [local.vpc_cidr]
    description = "Allow HTTP OTLP"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(
    local.tags,
    {
      Name = "signoz-endpoint-sg-${local.cluster_name}"
    }
  )
}

data "aws_vpc_endpoint_service" "signoz" {
  filter {
    name   = "tag:Name"
    values = ["signoz-vpc-endpoint-service"]
  }

  service_type = "Interface"
}

resource "aws_vpc_endpoint" "peer_to_signoz" {
  depends_on          = [kubernetes_namespace.otel]
  vpc_id              = module.vpc.vpc_id
  vpc_endpoint_type   = "Interface"
  service_name        = data.aws_vpc_endpoint_service.signoz.service_name
  subnet_ids          = module.vpc.private_subnets
  security_group_ids  = [aws_security_group.signoz_endpoint_sg.id]
  private_dns_enabled = false

  tags = merge(
    local.tags,
    {
      Name = "signoz-endpoint-sg-${local.cluster_name}"
    }
  )
}
