# Ubuntu Linux Server Installation

Guide for preparing an Ubuntu 22.04/24.04 server for AI Chatbot Cloud.

## 1. Initial System Update

```bash
sudo apt update && sudo apt upgrade -y
sudo timedatectl set-timezone Asia/Jakarta   # Adjust as needed
```

## 2. Create Deploy User (Optional)

```bash
sudo adduser deploy
sudo usermod -aG sudo deploy
sudo mkdir -p /home/deploy/.ssh
sudo cp ~/.ssh/authorized_keys /home/deploy/.ssh/
sudo chown -R deploy:deploy /home/deploy/.ssh
```

## 3. Install Docker

```bash
sudo apt install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker $USER
```

Log out and back in for group changes.

## 4. Verify Docker

```bash
docker --version
docker compose version
docker run hello-world
```

## 5. Firewall (UFW)

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
sudo ufw status
```

## 6. Swap (Recommended for 4GB RAM)

Embedding models benefit from swap during cold start:

```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

## 7. System Limits

```bash
# /etc/sysctl.conf
sudo tee -a /etc/sysctl.conf << EOF
vm.max_map_count=262144
net.core.somaxconn=1024
EOF
sudo sysctl -p
```

## 8. Log Rotation

Docker logs can grow large:

```bash
sudo tee /etc/docker/daemon.json << EOF
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
EOF
sudo systemctl restart docker
```

## 9. Clone and Run Application

```bash
sudo mkdir -p /opt/ai-chatbot
sudo chown $USER:$USER /opt/ai-chatbot
git clone <repo> /opt/ai-chatbot
cd /opt/ai-chatbot
cp .env.example .env
# Edit .env
docker compose up -d --build
```

## 10. Auto-start on Boot

Docker Compose with `restart: unless-stopped` handles container restart. Enable Docker service:

```bash
sudo systemctl enable docker
```

## Hardware Recommendations

| Workload | vCPU | RAM | Disk |
|----------|------|-----|------|
| Dev/Demo | 2 | 4 GB | 20 GB |
| Production | 4 | 8 GB | 40 GB |
| High traffic | 8+ | 16 GB+ | SSD 80 GB+ |

First backend start downloads ~90MB embedding model — allow 2–5 minutes.
