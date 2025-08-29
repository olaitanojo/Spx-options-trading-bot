# SPX Options Trading Bot - Complete Deployment Guide

## 🚀 Deployment Options Overview

You now have **3 fully configured deployment options**:

### 1. **Local Docker Compose** (Quickest Start)
- ✅ Ready to use immediately
- ✅ Includes monitoring stack
- ✅ Perfect for development/testing

### 2. **Azure Kubernetes Service** (Production Ready)
- ✅ Enterprise-grade deployment
- ✅ Auto-scaling and high availability
- ✅ Advanced deployment strategies

### 3. **ArgoCD GitOps** (Advanced DevOps)
- ✅ Canary and Blue-Green deployments
- ✅ Automated rollbacks
- ✅ Progressive delivery

---

## 📋 **Option 1: Docker Compose Deployment**

### Prerequisites
- Docker and Docker Compose installed
- 8GB RAM available
- Ports 3000, 5432, 6379, 8080, 9090 available

### Quick Start
```bash
# Make deployment script executable
chmod +x deploy-docker-compose.sh

# Run deployment
./deploy-docker-compose.sh
```

### Services Access
- **Trading Bot API**: http://localhost:8080
- **Grafana Dashboard**: http://localhost:3000 (admin/your_password)
- **Prometheus**: http://localhost:9090
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

### Configuration
Update secrets in `deployment/secrets/`:
- `api_keys.env` - Your trading API keys
- `db_password.txt` - Database password
- `grafana_password.txt` - Grafana admin password

---

## 📋 **Option 2: Azure Kubernetes Service**

### Prerequisites Setup

#### 1. Create Azure Resources
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
```

#### 2. Configure GitHub Secrets
Go to **Repository Settings → Secrets and variables → Actions** and add:

```yaml
# Azure Credentials (from service principal)
AZURE_CREDENTIALS: |
  {
    "clientId": "your-client-id",
    "clientSecret": "your-client-secret",
    "subscriptionId": "your-subscription-id",
    "tenantId": "your-tenant-id"
  }

# Container Registry
ACR_USERNAME: your-registry-username
ACR_PASSWORD: your-registry-password

# AKS Cluster
AKS_RESOURCE_GROUP: spx-trading-rg
AKS_CLUSTER_NAME: spx-trading-cluster
```

#### 3. Update Secrets in Kubernetes
```bash
# Encode your secrets
echo -n "redis://spx-redis-service:6379" | base64
echo -n "postgresql://user:pass@spx-postgres-service:5432/trading_db" | base64
echo -n "your-api-key" | base64

# Update k8s/base/secrets.yaml with encoded values
```

#### 4. Deploy
```bash
# Push to main branch - automatic deployment via GitHub Actions
git push origin main

# Or manually deploy
kubectl apply -k k8s/overlays/production
```

### Monitoring Deployment
```bash
# Check deployment status
kubectl get pods -n spx-options-prod

# Check service status  
kubectl get services -n spx-options-prod

# View logs
kubectl logs -l app=spx-options-trading-bot -n spx-options-prod
```

---

## 📋 **Option 3: ArgoCD GitOps**

### Prerequisites
- AKS cluster from Option 2
- ArgoCD installed in cluster

### Install ArgoCD
```bash
# Install ArgoCD
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Install Argo Rollouts
kubectl create namespace argo-rollouts
kubectl apply -n argo-rollouts -f https://github.com/argoproj/argo-rollouts/releases/latest/download/install.yaml
```

### Deploy Application
```bash
# Apply ArgoCD application
kubectl apply -f argocd/application.yml

# Access ArgoCD UI
kubectl port-forward svc/argocd-server -n argocd 8080:443
# Open https://localhost:8080
```

### Deployment Strategies Available
- **Canary**: 10% → 25% → 50% → 100% with automated analysis
- **Blue-Green**: Instant switch with rollback capability  
- **Rolling**: Traditional rolling updates

---

## 🔧 **Environment Configurations**

### Development
```bash
kubectl apply -k k8s/overlays/development
# 1 replica, debug logging, trading disabled
```

### Staging  
```bash
kubectl apply -k k8s/overlays/staging  
# 2 replicas, debug logging, trading disabled
```

### Production
```bash
kubectl apply -k k8s/overlays/production
# 5+ replicas, info logging, trading enabled
```

---

## 📊 **Monitoring & Observability**

### Health Checks
- **Liveness**: `/health/live` - Is the app alive?
- **Readiness**: `/health/ready` - Is the app ready for traffic?  
- **Startup**: `/health/startup` - Is the app starting up?

### Metrics
- **Application**: `/metrics` - Prometheus metrics
- **Business**: Trading performance, P&L, positions
- **Infrastructure**: CPU, memory, network

### Dashboards
- **Grafana**: Application and business metrics
- **Prometheus**: Infrastructure metrics
- **Kubernetes Dashboard**: Cluster overview

---

## 🔒 **Security Features**

### Network Policies
- ✅ Ingress restrictions
- ✅ Egress filtering  
- ✅ Inter-service communication control

### RBAC
- ✅ Service accounts with minimal permissions
- ✅ Role-based access control
- ✅ Secret management

### Container Security
- ✅ Non-root user execution
- ✅ Read-only root filesystem
- ✅ No privilege escalation
- ✅ Minimal base image

---

## 🎯 **Next Steps**

### Immediate Actions
1. **Choose deployment option** (start with Docker Compose)
2. **Update secrets** with your actual API keys  
3. **Customize configuration** in ConfigMaps
4. **Set up monitoring alerts** in Prometheus

### Production Readiness
1. **Domain & SSL**: Update ingress with your domain
2. **Backup Strategy**: Database and configuration backups
3. **Disaster Recovery**: Multi-region deployment
4. **Compliance**: Audit logging and data encryption

### Scaling Considerations
- **Horizontal**: More replicas via HPA
- **Vertical**: Larger resource limits
- **Geographic**: Multi-region deployment
- **Performance**: Redis clustering, read replicas

---

## 🆘 **Troubleshooting**

### Common Issues

#### Docker Compose
```bash
# Check service logs
docker-compose logs spx-trading-bot

# Restart services
docker-compose restart

# Check resource usage
docker stats
```

#### Kubernetes
```bash
# Check pod status
kubectl describe pod -l app=spx-options-trading-bot

# Check events
kubectl get events --sort-by='.lastTimestamp'

# Check resource usage  
kubectl top pods
```

#### Health Check Failures
```bash
# Test health endpoints
curl http://localhost:8080/health
curl http://localhost:8080/health/ready

# Check dependency connectivity
kubectl exec -it deployment/spx-options-trading-bot -- nc -zv spx-redis-service 6379
```

---

## 🎉 **Success!**

Your SPX Options Trading Bot is now ready for deployment with:
- ✅ **Production-ready** Kubernetes manifests
- ✅ **Multi-environment** configurations  
- ✅ **Advanced deployment** strategies
- ✅ **Comprehensive monitoring** 
- ✅ **Enterprise security** features

Choose your deployment option and start trading! 🚀📈
