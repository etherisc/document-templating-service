---
layout: default
title: Installation Guide
nav_order: 2
description: "Complete setup instructions to get the Document Template Processing Service running in any environment."
---

# Installation Guide

This guide covers everything you need to get the Document Template Processing Service up and running.

## Prerequisites

- Docker and Docker Compose (recommended)
- OR Python 3.12+ (for manual installation)

## Quick Start with Docker Compose (Recommended)

The easiest way to get started is using Docker Compose, which sets up both the service and Gotenberg automatically.

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd document-templating-service
   ```

2. **Start the services:**
   ```bash
   docker compose up -d
   ```

3. **Verify the installation:**
   - Health check: http://localhost:8000/

4. **Stop the services:**
   ```bash
   # Stop services
   docker compose stop
   
   # Stop and remove services
   docker compose down
   ```

## Manual Installation

### Step 1: Setup Gotenberg

Gotenberg is required for PDF conversion. Start a Gotenberg instance:

```bash
docker run --name gotenberg -d -p 3000:3000 gotenberg/gotenberg:8
```

### Step 2: Setup the Python Service

1. **Clone and navigate to the project:**
   ```bash
   git clone <repository-url>
   cd document-templating-service
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate  # Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables:**
   ```bash
   export GOTENBERG_API_URL=http://localhost:3000
   ```

5. **Start the service:**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

## Docker Build from Source

1. **Build the Docker image:**
   ```bash
   docker build -t document-template-processing-service .
   ```

2. **Run the container:**
   ```bash
   docker run -d -p 8000:8000 -e GOTENBERG_API_URL=http://host.docker.internal:3000 --name dtps document-template-processing-service
   ```

## Kubernetes Deployment

For production deployments, Kubernetes manifests are available in the `k8s/` directory.

1. **Create the namespace:**
   ```bash
   kubectl apply -f k8s/namespace.yaml
   ```

2. **Deploy the services:**
   ```bash
   kubectl apply -f k8s/gotenberg -f k8s/document-template-processing
   ```

3. **Access the service:**
   ```bash
   kubectl port-forward svc/document-template-processing 8000:8000 -n utils
   ```

## Cloud Deployment Notes

### Google Cloud Run / Similar Platforms

For cloud deployments, use the cloud-optimized Gotenberg image:

```yaml
# In docker-compose.yaml
services:
  gotenberg:
    image: gotenberg/gotenberg:8-cloudrun
    # ... rest of configuration
```

This optimized image reduces cold start times and resource usage.

## Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `GOTENBERG_API_URL` | URL to Gotenberg service | `http://host.docker.internal:3000` | Yes |

**Note:** Only `GOTENBERG_API_URL` is used. For Docker Swarm, use the service DNS name, e.g. `http://gotenberg.web:3000` when the Gotenberg service is in the `web` stack.

## Verification

After installation, verify everything is working:

1. **Health Check:**
   ```bash
   curl http://localhost:8000/
   ```

2. **Test with a sample document:**
   See the [Usage Guide](usage.html) for examples.

## Troubleshooting

### Common Issues

1. **Connection refused to Gotenberg:**
   - Ensure Gotenberg is running on the specified port
   - Check firewall settings
   - Verify the GOTENBERG_API_URL is correct

2. **Permission errors:**
   - Ensure Docker daemon is running
   - Check user permissions for Docker

3. **Port already in use:**
   - Change the port mapping: `-p 8001:8000`
   - Check what's using the port: `netstat -tulpn | grep :8000`

### Getting Help

- Check the [Usage Guide](usage.html) for service usage examples
- Review the main [README](../)
- Open an issue on the GitHub repository 