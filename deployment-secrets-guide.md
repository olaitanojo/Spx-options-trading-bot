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
