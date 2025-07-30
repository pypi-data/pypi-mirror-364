# InfraDSL

**The Rails of Modern Infrastructure - Enterprise DSL for Infrastructure Management**

[![PyPI version](https://badge.fury.io/py/infradsl.svg)](https://badge.fury.io/py/infradsl)
[![Python Versions](https://img.shields.io/pypi/pyversions/infradsl.svg)](https://pypi.org/project/infradsl/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

InfraDSL is a next-generation Infrastructure as Code (IaC) tool that brings Rails-like conventions and chainable APIs to cloud infrastructure management. It combines the simplicity of Python with powerful multi-cloud capabilities, intelligent caching, and self-healing infrastructure.

## ✨ Key Features

- **🚀 Rails-like DSL**: Chainable, intuitive APIs that feel natural to developers
- **☁️ Multi-Cloud Native**: AWS, GCP, Azure, DigitalOcean support with unified syntax
- **🧠 Intelligent Import**: Superior import system with dependency analysis and fingerprint-based caching
- **⚡ Performance First**: PostgreSQL-backed caching, parallel execution, and smart resource detection
- **🔄 Self-Healing**: Automatic drift detection and remediation with customizable policies
- **📊 Enterprise Ready**: RBAC, audit logging, cost optimization, and compliance features

## 🚀 Quick Start

### Installation

```bash
pip install infradsl
```

### Basic Example

```python
from infradsl import AWS

# Create a simple web server with Rails-like chainability
vm = (AWS.EC2("web-server")
      .instance_type("t3.micro")
      .ubuntu_24_04()
      .key_pair("my-key")
      .security_group("web-sg")
      .public_ip()
      .production())

# Create VPC with intelligent defaults
vpc = (AWS.VPC("main-vpc")
       .cidr("10.0.0.0/16")
       .enable_dns()
       .multi_az()
       .production())

# CloudFront CDN with S3 origin
cdn = (AWS.CloudFront("website-cdn")
       .s3_origin("my-website-bucket")
       .custom_domain("www.example.com")
       .ssl_certificate("arn:aws:acm:...")
       .gzip_compression()
       .production())
```

### CLI Usage

```bash
# Initialize a new project
infra init myproject

# Import existing infrastructure
infra import aws --region us-east-1

# Preview changes
infra preview infrastructure.py

# Apply changes
infra apply infrastructure.py --production

# Monitor drift and auto-heal
infra heal start --auto-remediate
```

## 🏗️ Architecture

InfraDSL is built on several core principles:

### 1. Rails-like Conventions
- **Convention over Configuration**: Intelligent defaults for common patterns
- **Chainable APIs**: Fluent interfaces that read like natural language
- **Environment Presets**: `.production()`, `.staging()`, `.development()` with optimized settings

### 2. Superior Import System
- **Dependency-Aware**: Automatically resolves resource relationships
- **Fingerprint Caching**: PostgreSQL-backed cache for instant resource recognition
- **Intelligent Organization**: Groups imported resources by function and dependencies

### 3. Multi-Cloud Abstraction
```python
# Same API across all clouds
AWS.VirtualMachine("web").ubuntu().production()
GCP.VirtualMachine("web").ubuntu().production() 
Azure.VirtualMachine("web").ubuntu().production()
```

## 📚 Documentation

- **[Official Documentation](https://docs.infradsl.dev)** - Complete guide and API reference
- **[Quick Start Guide](https://docs.infradsl.dev/getting-started/quick-start)** - Get up and running in minutes
- **[Import System Guide](https://docs.infradsl.dev/guides/import-system)** - Learn about our superior import capabilities
- **[CLI Reference](https://docs.infradsl.dev/guide/cli-reference)** - Complete command reference

## 🌟 Examples

### Multi-Cloud Application
```python
from infradsl import AWS, GCP

# AWS Infrastructure
app_server = (AWS.EC2("app")
              .instance_type("t3.medium")
              .ubuntu_24_04()
              .auto_scaling_group(2, 10)
              .production())

# GCP Database
database = (GCP.CloudSQL("app-db")
            .postgres_15()
            .high_availability()
            .backup_schedule("0 2 * * *")
            .production())

# Cross-cloud networking automatically configured
```

### Static Website with CDN
```python
from infradsl import AWS

# Website bucket
website = (AWS.S3("my-website")
           .website("index.html", "404.html")
           .public_read()
           .production())

# Global CDN
cdn = (AWS.CloudFront("website-cdn")
       .s3_origin("my-website")
       .custom_domain("www.example.com")
       .ssl_certificate("arn:aws:acm:...")
       .price_class_all()
       .production())

# DNS routing
dns = (AWS.Route53("example-dns")
       .use_existing_zone("example.com")
       .cloudfront_alias("www", cdn)
       .production())
```

### Self-Healing Infrastructure
```python
from infradsl import AWS, DriftAction

# Auto-healing web servers
web_servers = (AWS.EC2("web-cluster")
               .instance_type("t3.medium")
               .auto_scaling_group(3, 20)
               .health_check_grace_period(300)
               .drift_policy(DriftAction.AUTO_HEAL)
               .production())

# Automatic failover database
database = (AWS.RDS("app-db")
            .postgres_15()
            .multi_az()
            .backup_retention(30)
            .drift_policy(DriftAction.ALERT_AND_HEAL)
            .production())
```

## 🔧 Advanced Features

### Import Existing Infrastructure
```bash
# Import AWS resources with dependency analysis
infra import aws --region us-east-1 --analyze-dependencies

# Import specific resource types
infra import gcp --project my-project --resources compute,storage

# Import with custom organization
infra import aws --organize-by environment,function
```

### Intelligent Caching
```bash
# View cache statistics
infra cache stats

# Clear and rebuild cache
infra cache clear --rebuild

# Cache performance metrics
infra cache analyze --performance
```

### Cost Optimization
```python
# Built-in cost optimization
vm = (AWS.EC2("web")
      .cost_optimized()  # Automatically selects best instance type
      .spot_instances()   # Use spot instances when possible
      .production())

# Cost insights
infra insights cost --forecast 30d
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
git clone https://github.com/infradsl/infradsl.git
cd infradsl
pip install -e ".[dev]"
pre-commit install
```

### Running Tests

```bash
pytest
pytest --cov=infradsl --cov-report=html
```

## 📄 License

InfraDSL is released under the [MIT License](LICENSE).

## 🆘 Support

- **[GitHub Issues](https://github.com/infradsl/infradsl/issues)** - Bug reports and feature requests
- **[Documentation](https://docs.infradsl.dev)** - Complete guides and API reference
- **[Discord Community](https://discord.gg/infradsl)** - Chat with other users and maintainers

## 🗺️ Roadmap

- ✅ Multi-cloud resource management (AWS, GCP, Azure, DigitalOcean)
- ✅ Superior import system with dependency analysis
- ✅ PostgreSQL-backed intelligent caching
- ✅ Self-healing infrastructure capabilities
- 🚧 Kubernetes native integration
- 🚧 Terraform migration tools
- 🚧 Advanced security scanning
- 🚧 GitOps integration

---

**Made with ❤️ by the InfraDSL Team**

*InfraDSL - Infrastructure as Code, Redefined*