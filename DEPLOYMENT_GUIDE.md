# Hetzner Server Deployment Guide

## Prerequisites

1. **Hetzner Server Setup**:
   - Ubuntu 20.04+ or similar Linux distribution
   - At least 4GB RAM recommended
   - Docker and Docker Compose installed

2. **Domain/IP Configuration**:
   - Static IP address from Hetzner
   - Optional: Domain name pointing to your server

## Step-by-Step Deployment

### 1. Server Preparation

Connect to your Hetzner server via SSH:
```bash
ssh root@your-server-ip
```

Install Docker and Docker Compose if not already installed:
```bash
# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
apt install docker-compose-plugin -y

# Start Docker service
systemctl start docker
systemctl enable docker
```

### 2. Upload Your Application

You can upload your application using Git or SCP:

**Option A: Using Git (Recommended)**
```bash
# Clone your repository
git clone https://github.com/yourusername/your-repo.git
cd your-repo
```

**Option B: Using SCP**
```bash
# From your local machine, upload the project
scp -r /path/to/your/project root@your-server-ip:/opt/dairy-app
```

### 3. Configure Environment Variables

```bash
# Copy the environment template
cp production.env.template .env

# Edit the environment file
nano .env
```

Update the following values in `.env`:
- `POSTGRES_PASSWORD`: Set a strong database password
- `SECRET_KEY`: Generate a secure secret key for JWT tokens
- `API_URL`: Replace with `http://your-server-ip:8000`

### 4. Configure Firewall

Open the necessary ports:
```bash
# Allow SSH (if not already configured)
ufw allow 22

# Allow your application ports
ufw allow 3000  # Frontend
ufw allow 8000  # Backend
ufw allow 5432  # Database (optional, for external access)

# Enable firewall
ufw --force enable
```

### 5. Deploy the Application

```bash
# Build and start all services
docker compose -f docker-compose.prod.yml up -d --build

# Check if all services are running
docker compose -f docker-compose.prod.yml ps

# View logs if needed
docker compose -f docker-compose.prod.yml logs -f
```

### 6. Verify Deployment

1. **Check Backend**: Visit `http://your-server-ip:8000/health`
2. **Check Frontend**: Visit `http://your-server-ip:3000`
3. **Check Database**: Verify database connection in backend logs

## Important Security Considerations

### 1. Change Default Passwords
- Update PostgreSQL password in `.env`
- Generate a new SECRET_KEY

### 2. Use HTTPS (Recommended for Production)
Consider setting up a reverse proxy with SSL:

```bash
# Install Nginx
apt install nginx -y

# Configure Nginx with SSL (using Let's Encrypt)
apt install certbot python3-certbot-nginx -y
```

### 3. Database Security
- Consider not exposing PostgreSQL port (5432) to the internet
- Use strong passwords
- Regular backups

## Maintenance Commands

```bash
# View all services status
docker compose -f docker-compose.prod.yml ps

# View logs
docker compose -f docker-compose.prod.yml logs [service-name]

# Restart a specific service
docker compose -f docker-compose.prod.yml restart [service-name]

# Update application (after code changes)
docker compose -f docker-compose.prod.yml down
git pull  # if using git
docker compose -f docker-compose.prod.yml up -d --build

# Backup database
docker exec -t postgres_container_name pg_dump -U postgres dairy_operations > backup.sql
```

## Troubleshooting

### Common Issues:

1. **Services not starting**: Check logs with `docker compose logs`
2. **Database connection failed**: Verify PostgreSQL is healthy
3. **Frontend can't reach backend**: Check API_URL configuration
4. **Port already in use**: Check if other services are using the ports

### Health Checks:
- PostgreSQL: `docker exec container_name pg_isready -U postgres`
- Backend: `curl http://localhost:8000/health`
- Frontend: Check if port 3000 is accessible

## Performance Optimization

For production use, consider:
- Setting up proper logging with log rotation
- Implementing monitoring (Prometheus, Grafana)
- Database optimization and regular backups
- Using a CDN for static assets
- Implementing SSL/HTTPS

## Backup Strategy

Regular backups are crucial:
```bash
# Database backup
docker exec postgres_container pg_dump -U postgres dairy_operations > /backup/db_$(date +%Y%m%d).sql

# Application code backup (if not using git)
tar -czf /backup/app_$(date +%Y%m%d).tar.gz /opt/dairy-app
``` 