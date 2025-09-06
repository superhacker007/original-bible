#!/bin/bash

# Paleo Hebrew Bible Deployment Script
# This script sets up the application on a Ubuntu/Debian server

set -e

echo "🚀 Starting Paleo Hebrew Bible deployment..."

# Configuration
PROJECT_DIR="/var/www/paleo-hebrew-bible"
SERVICE_NAME="paleo-hebrew-bible"
PYTHON_VERSION="3.9"

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo "This script should not be run as root for security reasons"
   echo "Please run as a regular user with sudo privileges"
   exit 1
fi

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install required packages
echo "📦 Installing system dependencies..."
sudo apt install -y python3 python3-pip python3-venv git nginx supervisor

# Create project directory
echo "📁 Setting up project directory..."
sudo mkdir -p $PROJECT_DIR
sudo chown $USER:$USER $PROJECT_DIR

# Clone or update repository
if [ -d "$PROJECT_DIR/.git" ]; then
    echo "🔄 Updating existing repository..."
    cd $PROJECT_DIR
    git pull origin main
else
    echo "📥 Cloning repository..."
    git clone https://github.com/superhacker007/original-bible.git $PROJECT_DIR
    cd $PROJECT_DIR
fi

# Set up Python virtual environment
echo "🐍 Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Set up database
echo "🗄️ Setting up database..."
python -c "from app import app; from models import db; app.app_context().push(); db.create_all(); print('Database initialized')"

# Set up systemd service
echo "⚙️ Setting up systemd service..."
sudo cp paleo-hebrew-bible.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME
sudo systemctl start $SERVICE_NAME

# Set up Nginx reverse proxy
echo "🌐 Setting up Nginx reverse proxy..."
sudo tee /etc/nginx/sites-available/paleo-hebrew-bible > /dev/null <<EOF
server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://127.0.0.1:5002;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    location /static/ {
        alias $PROJECT_DIR/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# Enable Nginx site
sudo ln -sf /etc/nginx/sites-available/paleo-hebrew-bible /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

# Set up log rotation
echo "📝 Setting up log rotation..."
sudo tee /etc/logrotate.d/paleo-hebrew-bible > /dev/null <<EOF
$PROJECT_DIR/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 $USER $USER
}
EOF

# Create logs directory
mkdir -p $PROJECT_DIR/logs

# Set up firewall
echo "🔥 Setting up firewall..."
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

# Final checks
echo "✅ Running final checks..."
sudo systemctl status $SERVICE_NAME --no-pager
curl -f http://localhost/api/test && echo "✅ Application is responding correctly"

echo ""
echo "🎉 Deployment completed successfully!"
echo ""
echo "Your Paleo Hebrew Bible application is now running at:"
echo "  - Local: http://localhost"
echo "  - External: http://your-server-ip"
echo ""
echo "Admin access:"
echo "  - URL: http://your-server-ip/login"
echo "  - Username: admin"
echo "  - Password: paleo_admin_2025"
echo ""
echo "To check application status: sudo systemctl status $SERVICE_NAME"
echo "To view logs: sudo journalctl -u $SERVICE_NAME -f"
echo ""