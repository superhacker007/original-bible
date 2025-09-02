# Paleo Hebrew Bible - Deployment Guide

This guide will help you deploy the Paleo Hebrew Bible application to Linode with a custom domain and CI/CD pipeline.

## 🚀 Overview

- **Application**: Flask-based Paleo Hebrew Bible with TTS
- **Database**: 66 books (39 Hebrew Bible + 27 New Testament)
- **Features**: Hebrew/Greek texts, Paleo Hebrew script, Strong's Concordance, TTS
- **Deployment**: Docker + Nginx + SSL on Linode
- **CI/CD**: GitHub Actions

## 📋 Prerequisites

1. **Linode Account** with a VPS (Nanode 1GB minimum recommended)
2. **Domain Name** pointed to your Linode server
3. **GitHub Account** for repository hosting
4. **SSL Certificate** (Let's Encrypt recommended)

## 🏗️ Step 1: Linode Server Setup

### 1.1 Create Linode Instance
```bash
# Create a Nanode 1GB instance with Ubuntu 20.04 LTS
# Note the IP address for DNS configuration
```

### 1.2 Initial Server Configuration
```bash
# SSH into your server
ssh root@YOUR_SERVER_IP

# Update system
apt update && apt upgrade -y

# Install Docker and Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
apt install docker-compose -y

# Create application user
adduser deployer
usermod -aG docker deployer
usermod -aG sudo deployer

# Setup SSH for deployer user
mkdir -p /home/deployer/.ssh
cp ~/.ssh/authorized_keys /home/deployer/.ssh/
chown -R deployer:deployer /home/deployer/.ssh
chmod 700 /home/deployer/.ssh
chmod 600 /home/deployer/.ssh/authorized_keys
```

### 1.3 Setup Application Directory
```bash
# Switch to deployer user
su - deployer

# Create application directory
sudo mkdir -p /var/www/paleo-bible
sudo chown deployer:deployer /var/www/paleo-bible
cd /var/www/paleo-bible

# Clone your repository (you'll set this up in Step 2)
git clone https://github.com/YOUR_USERNAME/paleo-bible.git .
```

## 🔧 Step 2: GitHub Repository Setup

### 2.1 Create GitHub Repository
1. Go to GitHub and create a new repository named `paleo-bible`
2. Make it public or private (your choice)

### 2.2 Initialize Local Git Repository
```bash
# From your local development directory
cd /Users/augustineodonkor/code/paleo

# Initialize git if not already done
git init
git add .
git commit -m "Initial commit: Complete Paleo Hebrew Bible application"

# Add GitHub remote
git remote add origin https://github.com/YOUR_USERNAME/paleo-bible.git
git branch -M main
git push -u origin main
```

### 2.3 Setup GitHub Secrets
Go to your GitHub repository → Settings → Secrets and variables → Actions

Add these secrets:
- `LINODE_HOST`: Your server IP address
- `LINODE_USER`: `deployer`
- `LINODE_SSH_KEY`: Your private SSH key content

## 🌐 Step 3: Domain Configuration

### 3.1 DNS Setup
Point your domain to your Linode server:
```
A record: @ → YOUR_SERVER_IP
A record: www → YOUR_SERVER_IP
```

### 3.2 SSL Certificate (Let's Encrypt)
```bash
# On your server, install certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Update nginx.conf with your actual domain
sed -i 's/your-domain.com/YOUR_ACTUAL_DOMAIN/g' /var/www/paleo-bible/nginx.conf
```

## 🚢 Step 4: Deployment

### 4.1 Manual First Deployment
```bash
# On your server
cd /var/www/paleo-bible

# Build and start the application
docker-compose up -d

# Check status
docker-compose ps
docker-compose logs web
```

### 4.2 Setup Systemd Service (Optional)
```bash
# Create systemd service file
sudo nano /etc/systemd/system/paleo-bible.service
```

Add this content:
```ini
[Unit]
Description=Paleo Bible Docker Compose
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/var/www/paleo-bible
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

Enable the service:
```bash
sudo systemctl enable paleo-bible.service
sudo systemctl start paleo-bible.service
```

## 🔄 Step 5: CI/CD Pipeline

The GitHub Actions workflow is already configured. It will:
1. Run tests on every push/PR
2. Deploy to your Linode server on pushes to main branch
3. Restart the application automatically

### 5.1 Test the Pipeline
```bash
# Make a small change and push
echo "# Paleo Hebrew Bible" > README.md
git add README.md
git commit -m "Add README"
git push origin main
```

## 📊 Step 6: Monitoring and Maintenance

### 6.1 Useful Commands
```bash
# View application logs
docker-compose logs -f web

# Restart application
docker-compose restart web

# Update application
git pull origin main
docker-compose build
docker-compose up -d

# Backup database
docker-compose exec web sqlite3 /app/data/paleo_bible.db ".backup /app/data/backup.db"
```

### 6.2 Monitoring
Set up basic monitoring:
```bash
# Install htop for server monitoring
sudo apt install htop -y

# Check disk usage
df -h

# Check memory usage
free -h

# Check Docker container stats
docker stats
```

## 🎯 Step 7: Custom Domain Features

Once deployed, your application will be available at:
- `https://your-domain.com` - Main application
- Automatic HTTPS redirect from HTTP
- Gzip compression for better performance
- Security headers for protection

## 🔧 Troubleshooting

### Common Issues:
1. **Port conflicts**: Ensure ports 80 and 443 are available
2. **SSL issues**: Check certificate paths in nginx.conf
3. **Database permissions**: Ensure Docker has write access to data directory
4. **Memory issues**: Monitor RAM usage, consider upgrading Linode plan

### Logs to Check:
```bash
# Application logs
docker-compose logs web

# Nginx logs
docker-compose logs nginx

# System logs
sudo journalctl -u paleo-bible.service
```

## 🎉 Success!

Your Paleo Hebrew Bible application should now be:
- ✅ Deployed on Linode
- ✅ Accessible via your custom domain
- ✅ Secured with HTTPS
- ✅ Automatically deployed via GitHub Actions
- ✅ Complete with 66 biblical books and Strong's Concordance

Visit your domain to access your biblical study platform!

## 📚 Features Available:
- Complete Hebrew Bible (39 books) with Paleo Hebrew script
- New Testament (27 books) with Greek text and KJV translations  
- Text-to-Speech with ancient Hebrew pronunciation
- Strong's Concordance integration
- Responsive web interface
- RESTful API for programmatic access