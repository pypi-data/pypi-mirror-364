location /auth {
    set $service "dex";
    set $resource_name "dex";
    set $resource_namespace ${namespace};
    proxy_http_version 1.1;
    proxy_connect_timeout 30s;
    proxy_read_timeout 120s;
    proxy_send_timeout 60s;
    client_max_body_size 5m;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Host $host;
    proxy_set_header X-Forwarded-Port $server_port;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_buffering on;
    proxy_pass http://dex:5556;
}