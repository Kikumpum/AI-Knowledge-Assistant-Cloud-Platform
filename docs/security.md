# Security Best Practices

Basic cloud security checklist for AI Chatbot Cloud deployments.

## Application Security

### Secrets Management

- Never commit `.env` to git
- Use strong `SECRET_KEY` (32+ random characters)
- Rotate `POSTGRES_PASSWORD` periodically
- Store production secrets in cloud secret managers (AWS Secrets Manager, GCP Secret Manager)

### Authentication

- JWT access tokens expire in 60 minutes (configurable)
- Passwords hashed with bcrypt
- HTTPS required in production (tokens in transit)

### API

- All chat/document routes require Bearer token
- User data isolated by `user_id` in vector search
- File upload restricted to PDF/TXT with size limits

## Server Hardening

### SSH

```bash
# Disable root login
sudo sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config

# Key-only authentication (after testing keys!)
# PasswordAuthentication no

sudo systemctl restart sshd
```

### Fail2ban

```bash
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
```

### Automatic Updates

```bash
sudo apt install unattended-upgrades -y
sudo dpkg-reconfigure -plow unattended-upgrades
```

## Network Security

| Rule | Action |
|------|--------|
| SSH | Allow only from trusted IPs if possible |
| HTTP/HTTPS | Public |
| PostgreSQL (5432) | **Never** expose publicly |
| ChromaDB (8000) | Internal Docker network only |
| Backend (8000) | Internal only — via Nginx |

## Nginx Security Headers

Already configured in `nginx/conf.d/default.conf`:

- `X-Frame-Options: SAMEORIGIN`
- `X-Content-Type-Options: nosniff`
- `X-XSS-Protection`

Add HSTS after enabling HTTPS:

```nginx
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

## Docker Security

- Run containers as non-root where possible
- Keep images updated: `docker compose pull && docker compose up -d`
- Scan images: `docker scout cves` or Trivy
- Limit container resources in production compose override

## Database

- Use strong passwords
- Regular backups (see deployment.md)
- Encrypt volumes at rest (cloud provider feature)

## Monitoring & Incident Response

- Review `docker compose logs` regularly
- Set up cloud alerts (CPU, disk, 5xx errors)
- Prometheus metrics at `/api/monitoring/metrics` — restrict in production

## Checklist Before Go-Live

- [ ] `.env` secrets changed from defaults
- [ ] HTTPS enabled
- [ ] Firewall configured (UFW)
- [ ] Database not publicly accessible
- [ ] SSH hardened
- [ ] Backups scheduled
- [ ] CORS limited to production domain
