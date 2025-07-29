terraform {
  required_providers {
    kubernetes = {
      source                = "hashicorp/kubernetes"
      configuration_aliases = [kubernetes]
    }
  }
}

locals {
  nginx_port = 8080
}

resource "kubernetes_config_map" "nginx_config_file" {
  metadata {
    name      = "appcd-proxy-config-file"
    namespace = var.namespace
  }

  data = {
    "default.conf" = <<EOF
server {
  listen 8080;listen [::]:8080;

  server_tokens off;

  server_name localhost;

  add_header Strict-Transport-Security 'max-age=31536000; includeSubDomains; preload';
  add_header Content-Security-Policy "default-src 'self' 'unsafe-inline' https: data:; base-uri 'self';";
  add_header X-XSS-Protection "1; mode=block";
  add_header X-Frame-Options "SAMEORIGIN";
  add_header X-Content-Type-Options nosniff;
  add_header Referrer-Policy "strict-origin";
  add_header Permissions-Policy "geolocation=(),midi=(),sync-xhr=(),microphone=(),camera=(),magnetometer=(),gyroscope=(),fullscreen=(self),payment=()";

  location = /favicon.ico {
    return 301 https://appcd.com/favicon.ico;
  }

  location = /mode.json {
    return 200 '{"mode":"ci", "main": "/"}';
  }

  location = /path.json {
    return 200 '{"auth":{"path":"/auth"},"appcd": {"path": "/appcd"}, "iac-gen": {"path": "/iac-gen"}, "exporter": {"path": "/exporter"}}';
  }

  location = /version.json {
    return 200 '{"appcd": "main", "iac-gen": "main", "ui": "main" }';
  }

  location = /auth {
    internal;
    proxy_pass http://appcd:8080/api/v1/auth/me;
    proxy_method HEAD;
    proxy_pass_request_body off;
    proxy_set_header X-Original-URI $request_uri;
    proxy_set_header X-Original-Method $request_method;
  }

  location /appcd {
          proxy_http_version 1.1;

          auth_request /auth;
          auth_request_set $login $upstream_http_x_appcd_login;
          proxy_set_header X-Appcd-Login $login;

          auth_request_set $appcd_session $upstream_http_x_appcd_session;
          proxy_set_header X-Appcd-Session $appcd_session;

          auth_request_set $session_type $upstream_http_x_appcd_session_type;
          proxy_set_header X-Appcd-Session-Type $session_type;

          auth_request_set $appcd_org $upstream_http_x_appcd_org;
          proxy_set_header X-Appcd-Org $appcd_org;

          auth_request_set $appcd_scopes $upstream_http_x_appcd_scopes;
          proxy_set_header X-Appcd-Scopes $appcd_scopes;

          auth_request_set $stackgen_tenant $upstream_http_x_stackgen_tenant;
          proxy_set_header X-Stackgen-Tenant $stackgen_tenant;

          rewrite /appcd/(.*) /$1  break;

          proxy_connect_timeout 30s;
          proxy_read_timeout 120s;
          proxy_send_timeout 60s;
          client_max_body_size 4m;
          proxy_set_header Host $host;
          proxy_set_header X-Real-IP $remote_addr;
          proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
          proxy_set_header X-Forwarded-Host $host;
          proxy_set_header X-Forwarded-Port $server_port;
          proxy_set_header X-Forwarded-Proto $scheme;
          proxy_buffering on;
          proxy_pass http://appcd:8080;
  }

  location / {
          proxy_http_version 1.1;

          proxy_connect_timeout 30s;
          proxy_read_timeout 20s;
          proxy_send_timeout 60s;
          client_max_body_size 4m;
          proxy_set_header Host $host;
          proxy_set_header X-Real-IP $remote_addr;
          proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
          proxy_set_header X-Forwarded-Host $host;
          proxy_set_header X-Forwarded-Port $server_port;
          proxy_set_header X-Forwarded-Proto $scheme;
          proxy_buffering on;
          proxy_pass http://appcd-appcd-ui:8000;
  }

  location /exporter {
          proxy_http_version 1.1;

          auth_request /auth;

          auth_request_set $login $upstream_http_x_appcd_login;
          proxy_set_header X-Appcd-Login $login;

          auth_request_set $appcd_org $upstream_http_x_appcd_org;
          proxy_set_header X-Appcd-Org $appcd_org;

          auth_request_set $appcd_scopes $upstream_http_x_appcd_scopes;
          proxy_set_header X-Appcd-Scopes $appcd_scopes;

          auth_request_set $stackgen_tenant $upstream_http_x_stackgen_tenant;
          proxy_set_header X-Stackgen-Tenant $stackgen_tenant;

          rewrite /exporter/(.*) /$1  break;

          proxy_connect_timeout 30s;
          proxy_read_timeout 20s;
          proxy_send_timeout 60s;
          client_max_body_size 4m;
          proxy_set_header Host $host;
          proxy_set_header X-Real-IP $remote_addr;
          proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
          proxy_set_header X-Forwarded-Host $host;
          proxy_set_header X-Forwarded-Port $server_port;
          proxy_set_header X-Forwarded-Proto $scheme;
          proxy_buffering on;
          proxy_pass http://appcd-exporter:8080;
  }

  location /iac-gen {
          proxy_http_version 1.1;

          auth_request /auth;

          auth_request_set $login $upstream_http_x_appcd_login;
          proxy_set_header X-Appcd-Login $login;

          auth_request_set $appcd_org $upstream_http_x_appcd_org;
          proxy_set_header X-Appcd-Org $appcd_org;

          auth_request_set $appcd_scopes $upstream_http_x_appcd_scopes;
          proxy_set_header X-Appcd-Scopes $appcd_scopes;

          auth_request_set $stackgen_tenant $upstream_http_x_stackgen_tenant;
          proxy_set_header X-Stackgen-Tenant $stackgen_tenant;

          rewrite /iac-gen/(.*) /$1  break;

          proxy_connect_timeout 30s;
          proxy_read_timeout 20s;
          proxy_send_timeout 60s;
          client_max_body_size 4m;
          proxy_set_header Host $host;
          proxy_set_header X-Real-IP $remote_addr;
          proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
          proxy_set_header X-Forwarded-Host $host;
          proxy_set_header X-Forwarded-Port $server_port;
          proxy_set_header X-Forwarded-Proto $scheme;
          proxy_buffering on;
          proxy_pass http://appcd-iac-gen:9000;
  }
}
    EOF
  }
}

resource "kubernetes_deployment" "appcd_proxy" {
  metadata {
    name      = "appcd-proxy"
    namespace = var.namespace
    labels = {
      "app.kubernetes.io/instance" = "appcd-proxy"
      "app.kubernetes.io/name"     = "appcd-proxy"
    }
  }

  spec {
    selector {
      match_labels = {
        "app.kubernetes.io/name"     = "appcd-proxy"
        "app.kubernetes.io/instance" = "appcd-proxy"
      }
    }

    template {
      metadata {
        labels = {
          "app.kubernetes.io/instance" = "appcd-proxy"
          "app.kubernetes.io/name"     = "appcd-proxy"
        }
      }

      spec {
        container {
          name  = "appcd-proxy"
          image = "nginxinc/nginx-unprivileged:alpine"

          port {
            container_port = local.nginx_port
          }

          volume_mount {
            name       = "nginx-config-file"
            mount_path = "/etc/nginx/conf.d/"
          }
        }

        volume {
          name = "nginx-config-file"

          config_map {
            name = kubernetes_config_map.nginx_config_file.metadata[0].name
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "nginx_svc" {
  metadata {
    name      = "nginx-svc"
    namespace = var.namespace
  }

  spec {
    port {
      name        = "http"
      port        = local.nginx_port
      target_port = local.nginx_port
    }

    selector = {
      "app.kubernetes.io/instance" = "appcd-proxy"
      "app.kubernetes.io/name"     = "appcd-proxy"
    }

    type = "ClusterIP"
  }
}

resource "kubernetes_ingress_v1" "nginx" {
  metadata {
    name      = "nginx"
    namespace = var.namespace
  }

  spec {
    rule {
      host = var.domain

      http {
        path {
          path = "/"
          backend {
            service {
              name = kubernetes_service.nginx_svc.metadata[0].name
              port {
                number = local.nginx_port
              }
            }
          }
        }
      }
    }
  }
}
