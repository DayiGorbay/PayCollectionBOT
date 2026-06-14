# HTTP — ACME challenge + redirect (used before SSL or as fallback)
server {
    listen 80;
    server_name __DOMAIN__;

    resolver 127.0.0.11 valid=10s ipv6=off;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location /health/live {
        set $backend_host backend;
        proxy_pass http://$backend_host:8000$request_uri;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 10s;
        proxy_read_timeout 30s;
    }

    location /health {
        set $backend_host backend;
        proxy_pass http://$backend_host:8000$request_uri;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 10s;
        proxy_read_timeout 30s;
    }

    location /api/ {
        set $backend_host backend;
        proxy_pass http://$backend_host:8000$request_uri;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 10s;
        proxy_read_timeout 120s;
        client_max_body_size 15m;
    }

    location / {
        set $frontend_host frontend;
        proxy_pass http://$frontend_host:80$request_uri;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 10s;
        proxy_read_timeout 60s;
    }
}
