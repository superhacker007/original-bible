# Paleo Hebrew Bible - Deployment Guide

## 🚀 Quick Deployment

### Automatic Deployment (Recommended)

1. **Clone the repository on your server:**
   ```bash
   git clone https://github.com/superhacker007/original-bible.git
   cd original-bible
   ```

2. **Run the deployment script:**
   ```bash
   ./deploy.sh
   ```

This will automatically set up everything including:
- Python virtual environment
- Dependencies installation
- Database initialization  
- Systemd service
- Nginx reverse proxy
- SSL/TLS (optional)
- Firewall configuration

## 🔧 Manual Deployment

### Prerequisites
- Ubuntu/Debian server
- Python 3.9+
- Git
- Sudo privileges

### Step-by-Step Setup

1. **Install system dependencies:**
   ```bash
   sudo apt update && sudo apt upgrade -y
   sudo apt install -y python3 python3-pip python3-venv git nginx
   ```

2. **Clone repository:**
   ```bash
   sudo mkdir -p /var/www/paleo-hebrew-bible
   sudo chown $USER:$USER /var/www/paleo-hebrew-bible
   git clone https://github.com/superhacker007/original-bible.git /var/www/paleo-hebrew-bible
   cd /var/www/paleo-hebrew-bible
   ```

3. **Set up Python environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Initialize database:**
   ```bash
   python -c "from app import app; from models import db; app.app_context().push(); db.create_all()"
   ```

5. **Set up systemd service:**
   ```bash
   sudo cp paleo-hebrew-bible.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable paleo-hebrew-bible
   sudo systemctl start paleo-hebrew-bible
   ```

6. **Configure Nginx:**
   ```bash
   sudo cp nginx.conf /etc/nginx/sites-available/paleo-hebrew-bible
   sudo ln -s /etc/nginx/sites-available/paleo-hebrew-bible /etc/nginx/sites-enabled/
   sudo rm /etc/nginx/sites-enabled/default
   sudo systemctl restart nginx
   ```

## 🔒 CI/CD with GitHub Actions

### Required Secrets

Set up these secrets in your GitHub repository settings:

- `HOST` - Your server IP address
- `USERNAME` - SSH username  
- `SSH_PRIVATE_KEY` - Your private SSH key
- `PORT` - SSH port (usually 22)
- `PROJECT_PATH` - Path to project on server (/var/www/paleo-hebrew-bible)

### SSH Key Setup

1. **Generate SSH key pair on your local machine:**
   ```bash
   ssh-keygen -t ed25519 -C "github-actions-deploy"
   ```

2. **Copy public key to server:**
   ```bash
   ssh-copy-id -i ~/.ssh/id_ed25519.pub user@your-server-ip
   ```

3. **Add private key to GitHub secrets:**
   - Copy the content of `~/.ssh/id_ed25519` 
   - Add it as `SSH_PRIVATE_KEY` in GitHub repository secrets

### Workflow Features

- **Automated testing** on every push/PR
- **Deployment** only on main branch pushes
- **Health checks** after deployment
- **Service restart** via systemd
- **Dependency updates** automatically

## 🔑 Admin Access

Once deployed, you can access the admin panel at:

- **URL:** `http://your-server-ip/login`
- **Username:** `admin`  
- **Password:** `paleo_admin_2025`

## 📊 Monitoring

### Check Application Status
```bash
sudo systemctl status paleo-hebrew-bible
```

### View Application Logs
```bash
sudo journalctl -u paleo-hebrew-bible -f
```

### Check Nginx Status
```bash
sudo systemctl status nginx
```

### Test Application Health
```bash
curl http://localhost/api/test
```

## 🛠️ Maintenance

### Update Application
```bash
cd /var/www/paleo-hebrew-bible
git pull origin main
source venv/bin/activate  
pip install -r requirements.txt
sudo systemctl restart paleo-hebrew-bible
```

### Database Operations
```bash
cd /var/www/paleo-hebrew-bible
source venv/bin/activate
python add_sample_facts.py  # Add sample God Facts
```

### Backup Database
```bash
cp /var/www/paleo-hebrew-bible/paleo_bible.db /backup/location/
```

## 🔐 Security Considerations

1. **Change default admin password** after first login
2. **Set up SSL/TLS** with Let's Encrypt:
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx
   ```
3. **Configure firewall** properly
4. **Keep system updated** regularly
5. **Use strong SSH keys** only
6. **Disable password authentication** in SSH

## 🆘 Troubleshooting

### Service Won't Start
```bash
sudo journalctl -u paleo-hebrew-bible --no-pager
```

### Port Already in Use
```bash
sudo lsof -i :5002
sudo kill -9 <PID>
```

### Permission Issues
```bash
sudo chown -R $USER:$USER /var/www/paleo-hebrew-bible
```

### Database Issues
```bash
cd /var/www/paleo-hebrew-bible
rm paleo_bible.db
python -c "from app import app; from models import db; app.app_context().push(); db.create_all()"
python add_sample_facts.py
```

## 📞 Support

For issues and questions:
- Check GitHub Issues
- Review application logs
- Test with curl commands
- Verify service status