# Azure AKS Deployment Guide

## Prerequisites Setup

### 1. Create Azure Resources
```bash
# Login to Azure
az login

# Create Resource Group
az group create --name spx-trading-rg --location eastus

# Create Container Registry
az acr create --resource-group spx-trading-rg --name spxoptionsregistry --sku Basic

# Create AKS Cluster
az aks create \
  --resource-group spx-trading-rg \
  --name spx-trading-cluster \
  --node-count 3 \
  --enable-addons monitoring \
  --attach-acr spxoptionsregistry \
  --generate-ssh-keys

# Get AKS credentials
az aks get-credentials --resource-group spx-trading-rg --name spx-trading-cluster
```

### 2. Create Service Principal for GitHub Actions
```bash
# Create service principal
az ad sp create-for-rbac --name "spx-github-actions" --role contributor \
  --scopes /subscriptions/{subscription-id}/resourceGroups/spx-trading-rg \
  --sdk-auth
```

### 3. Configure GitHub Secrets
Add these secrets to your GitHub repository:
- `AZURE_CREDENTIALS`: Output from service principal command
- `ACR_USERNAME`: Registry username
- `ACR_PASSWORD`: Registry password
- `AKS_RESOURCE_GROUP`: spx-trading-rg
- `AKS_CLUSTER_NAME`: spx-trading-cluster

### 4. Enable Deployment in Workflow
Edit `.github/workflows/ci-cd.yml`:
```yaml
# Change these lines from:
if: needs.setup.outputs.should_deploy == 'true' && false

# To:
if: needs.setup.outputs.should_deploy == 'true'
```

### 5. Create Kubernetes Manifests
You'll need to create the `k8s/` directory structure referenced in your workflow:
```
k8s/
├── base/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── configmap.yaml
│   └── secrets.yaml
└── overlays/
    ├── development/
    ├── staging/
    └── production/
```

## Deployment Process
1. Push to `main` branch
2. GitHub Actions will automatically:
   - Run tests and quality checks
   - Build and push Docker image to ACR
   - Deploy to AKS using chosen strategy (canary/blue-green/rolling)
   - Run post-deployment validation
