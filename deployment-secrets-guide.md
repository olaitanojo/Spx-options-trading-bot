# GitHub Secrets Configuration Guide

## Required Secrets for Deployment

Configure these secrets in your GitHub repository: **Settings → Secrets and variables → Actions**

### 🔐 **Container Registry Secrets**
```
ACR_USERNAME=<your-acr-username>
ACR_PASSWORD=<your-acr-password>
```

### ☁️ **Azure Secrets**
```
AZURE_CREDENTIALS=<service-principal-json>
AKS_RESOURCE_GROUP=<your-resource-group-name>
AKS_CLUSTER_NAME=<your-aks-cluster-name>
```

**Azure Credentials JSON format:**
```json
{
  "clientId": "<service-principal-client-id>",
  "clientSecret": "<service-principal-client-secret>",
  "subscriptionId": "<azure-subscription-id>",
  "tenantId": "<azure-tenant-id>",
  "activeDirectoryEndpointUrl": "https://login.microsoftonline.com",
  "resourceManagerEndpointUrl": "https://management.azure.com/",
  "activeDirectoryGraphResourceId": "https://graph.windows.net/",
  "sqlManagementEndpointUrl": "https://management.core.windows.net:8443/",
  "galleryEndpointUrl": "https://gallery.azure.com/",
  "managementEndpointUrl": "https://management.core.windows.net/"
}
```

### 🔒 **Security Scanning (Optional)**
```
SNYK_TOKEN=<your-snyk-token>
```

### 📊 **Monitoring (Optional)**
```
GRAFANA_URL=<your-grafana-instance-url>
GRAFANA_API_KEY=<your-grafana-api-key>
PROMETHEUS_PUSHGATEWAY_URL=<your-prometheus-pushgateway-url>
SLACK_WEBHOOK=<your-slack-webhook-url>
```

## 🚀 Pipeline Behavior

### ✅ **Graceful Degradation (Recently Fixed)**
The pipeline now handles missing secrets gracefully:

- **Code Quality, Testing, Security** - Always runs (no secrets needed)
- **Container Build** - Skips gracefully if ACR secrets missing  
- **Kubernetes Deployment** - Skips gracefully if Azure secrets missing
- **Monitoring Updates** - Skips gracefully if monitoring secrets missing
- **Slack Notifications** - Skips gracefully if webhook missing

### 🔧 **Recent Fixes Applied**
- Fixed monitoring job exit code 26 issue
- Fixed "SLACK_WEBHOOK_URL" reference issue  
- Fixed safety command syntax error
- Added comprehensive status logging

### 📊 **What This Means**
Your pipeline should now run successfully even without deployment secrets configured. It will:

1. ✅ Run all code quality checks
2. ✅ Run all tests  
3. ✅ Run security scans
4. ⏭️ Skip deployment steps (with clear logging)
5. ⏭️ Skip monitoring/notification steps (with clear logging)

## 🔍 Troubleshooting

If your pipeline is still failing:

1. **Check the latest commit** - Ensure these fixes are in your `main` branch
2. **View the Actions tab** - Look for detailed step-by-step logs  
3. **Check the "Deployment Status" job** - Shows which secrets are missing
4. **Verify branch triggers** - Pipeline runs on `main`, `develop`, `staging` branches

## 📝 Next Steps

To enable full deployment:
1. Configure **ACR_USERNAME** and **ACR_PASSWORD** for container builds
2. Configure **AZURE_CREDENTIALS**, **AKS_RESOURCE_GROUP**, **AKS_CLUSTER_NAME** for Kubernetes deployment
3. Optionally configure monitoring/notification secrets for enhanced features
