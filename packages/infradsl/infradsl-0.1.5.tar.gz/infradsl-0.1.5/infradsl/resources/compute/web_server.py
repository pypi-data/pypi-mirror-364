from typing import Optional, Self
from .virtual_machine import VirtualMachine, InstanceSize


class WebServer(VirtualMachine):
    """
    High-level web server abstraction with Rails-like conventions.
    
    Examples:
        # Simple web server
        web = WebServer("my-site").domain("example.com").create()
        
        # Production web server with auto-scaling
        web = (WebServer("prod-web")
               .domain("myapp.com")
               .environment("production")
               .ssl_cert("myapp.com")
               .auto_scale(min_size=2, max_size=10))
    """
    
    def __init__(self, name: str):
        super().__init__(name)
        
        # Web server defaults
        self.ubuntu("22.04")
        self.size(InstanceSize.SMALL)
        self.tag("http-server", "https-server")
        
        # Default nginx setup
        self.startup_script(self._get_default_web_script())
        
    def _get_default_web_script(self) -> str:
        """Get default web server setup script"""
        return """#!/bin/bash

# Update system
apt-get update
apt-get upgrade -y

# Install nginx
apt-get install -y nginx curl

# Start and enable nginx
systemctl start nginx
systemctl enable nginx

# Create a simple default page
cat > /var/www/html/index.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>InfraDSL Web Server</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .container { max-width: 800px; margin: 0 auto; }
        .header { background: #f0f0f0; padding: 20px; border-radius: 8px; }
        .status { color: #28a745; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 InfraDSL Web Server</h1>
            <p class="status">Status: Online</p>
            <p>This web server was created and configured with InfraDSL.</p>
        </div>
        <div style="margin-top: 20px;">
            <h2>Server Information</h2>
            <ul>
                <li><strong>Hostname:</strong> $(hostname)</li>
                <li><strong>Started:</strong> $(date)</li>
                <li><strong>Nginx Version:</strong> $(nginx -v 2>&1)</li>
            </ul>
        </div>
    </div>
</body>
</html>
EOF

# Configure firewall
ufw allow 22
ufw allow 80
ufw allow 443
ufw --force enable

echo "Web server setup complete!"
"""
    
    # High-level web server methods
    
    def domain(self, domain_name: str) -> Self:
        """Set the domain name for this web server (chainable)"""
        self.label("domain", domain_name)
        self.meta("domain", domain_name)
        return self
        
    def ssl_cert(self, domain_name: str, email: str = None) -> Self:
        """Configure SSL certificate with Let's Encrypt (chainable)"""
        self.label("ssl", "enabled")
        self.meta("ssl-domain", domain_name)
        
        if email:
            self.meta("ssl-email", email)
        
        # Add SSL setup to startup script
        ssl_script = f"""

# Install certbot for SSL
apt-get install -y certbot python3-certbot-nginx

# Configure SSL (requires domain to point to this server)
certbot --nginx -d {domain_name} --non-interactive --agree-tos \\
    -m {email or f"admin@{domain_name}"}

# Set up auto-renewal
systemctl enable certbot.timer
systemctl start certbot.timer
"""
        
        current_script = self.spec.user_data or ""
        self.startup_script(current_script + ssl_script)
        
        return self
        
    def application(self, git_url: str, port: int = 3000, language: str = "node") -> Self:
        """Deploy application from git repository (chainable)"""
        self.label("app-language", language)
        self.meta("app-git-url", git_url)
        self.meta("app-port", str(port))
        
        # Application deployment script
        if language.lower() in ["node", "nodejs", "javascript"]:
            app_script = f"""

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt-get install -y nodejs

# Clone and deploy application
cd /opt
git clone {git_url} app
cd app
npm install
npm run build || true

# Create systemd service for the app
cat > /etc/systemd/system/webapp.service << 'EOF'
[Unit]
Description=Web Application
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/app
ExecStart=/usr/bin/npm start
Restart=always
Environment=PORT={port}
Environment=NODE_ENV=production

[Install]
WantedBy=multi-user.target
EOF

# Start the application
systemctl enable webapp
systemctl start webapp

# Configure nginx proxy
cat > /etc/nginx/sites-available/default << 'EOF'
server {{
    listen 80 default_server;
    listen [::]:80 default_server;
    
    location / {{
        proxy_pass http://localhost:{port};
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
}}
EOF

systemctl reload nginx
"""
        elif language.lower() in ["python", "django", "flask"]:
            app_script = f"""

# Install Python and dependencies
apt-get install -y python3 python3-pip python3-venv

# Clone and deploy application
cd /opt
git clone {git_url} app
cd app
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create systemd service
cat > /etc/systemd/system/webapp.service << 'EOF'
[Unit]
Description=Python Web Application
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/app
Environment=PATH=/opt/app/venv/bin
ExecStart=/opt/app/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

systemctl enable webapp
systemctl start webapp

# Configure nginx proxy (same as Node.js)
cat > /etc/nginx/sites-available/default << 'EOF'
server {{
    listen 80 default_server;
    listen [::]:80 default_server;
    
    location / {{
        proxy_pass http://localhost:{port};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
}}
EOF

systemctl reload nginx
"""
        else:
            app_script = f"""

# Clone application
cd /opt
git clone {git_url} app

# Note: Manual configuration required for {language}
echo "Application cloned to /opt/app"
echo "Please configure {language} application manually"
"""
        
        current_script = self.spec.user_data or ""
        self.startup_script(current_script + app_script)
        
        return self
        
    def database_url(self, url: str) -> Self:
        """Set database connection URL (chainable)"""
        self.meta("database-url", url)
        return self
        
    def environment_vars(self, **env_vars) -> Self:
        """Set environment variables for the application (chainable)"""
        # Add environment variables to startup script
        env_script = "\n# Set environment variables\n"
        for key, value in env_vars.items():
            env_script += f'echo "export {key}={value}" >> /etc/environment\n'
            self.meta(f"env-{key.lower()}", str(value))
            
        current_script = self.spec.user_data or ""
        self.startup_script(current_script + env_script)
        
        return self
        
    def monitoring(self, enable: bool = True) -> Self:
        """Enable monitoring and logging (chainable)"""
        if enable:
            self.label("monitoring", "enabled")
            
            monitoring_script = """

# Install monitoring tools
apt-get install -y htop iotop nethogs

# Install and configure log rotation
cat > /etc/logrotate.d/webapp << 'EOF'
/var/log/webapp/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    sharedscripts
}
EOF

mkdir -p /var/log/webapp
chown www-data:www-data /var/log/webapp

echo "Monitoring setup complete!"
"""
            
            current_script = self.spec.user_data or ""
            self.startup_script(current_script + monitoring_script)
            
        return self
        
    def auto_scale(self, min_size: int = 2, max_size: int = 10, target_cpu: float = 0.7) -> "InstanceGroup":
        """Create auto-scaling instance group for high availability (chainable)"""
        # Create instance group with auto-scaling
        group = self.instance_group(f"{self.name}-group", size=min_size)
        group.auto_scale(min_size=min_size, max_size=max_size, target_cpu=target_cpu)
        
        # Label for production readiness
        self.label("high-availability", "enabled")
        self.label("auto-scaling", "enabled")
        
        return group
        
    def load_balancer(self, lb_type: str = "https") -> "LoadBalancer":
        """Create load balancer for the web server (chainable)"""
        from .load_balancer import LoadBalancer
        
        self.label("load-balancer", "enabled")
        
        # Create actual load balancer using parent method
        lb = super().load_balancer(f"{self.name}-lb", lb_type)
        
        # Add web-specific health check
        lb.health_check("/health", port=80)
        
        # If this is HTTPS, add redirect
        if lb_type.lower() == "https":
            lb.redirect_http(True)
            
        return lb
        
    # Environment-based conveniences
    
    def production(self) -> Self:
        """Configure for production environment (chainable)"""
        return (self
                .environment("production")
                .size(InstanceSize.LARGE)
                .deletion_protection()
                .shielded_vm()
                .monitoring())
                
    def staging(self) -> Self:
        """Configure for staging environment (chainable)"""
        return (self
                .environment("staging") 
                .size(InstanceSize.MEDIUM)
                .monitoring())
                
    def development(self) -> Self:
        """Configure for development environment (chainable)"""
        return (self
                .environment("development")
                .size(InstanceSize.SMALL)
                .preemptible())