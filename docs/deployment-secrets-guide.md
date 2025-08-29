# GitHub Secrets Configuration Guide

This comprehensive guide covers all the GitHub repository secrets needed for the SPX Options Trading Bot CI/CD pipeline.

## 📋 Overview

The CI/CD pipeline uses GitHub repository secrets to securely store sensitive configuration data. This guide organizes secrets by category and provides setup instructions for each.

## 🔒 Required Secrets by Category

### 🏢 Azure Cloud Infrastructure

These secrets are required for Azure Kubernetes Service (AKS) deployment:

| Secret Name | Description | How to Get | Required |
|-------------|-------------|------------|----------|
| `AZURE_CREDENTIALS` | Service Principal JSON for Azure authentication | [Azure CLI Setup](#azure-credentials) | ✅ Yes |
| `AKS_CLUSTER_NAME` | Name of your AKS cluster | AKS resource name | ✅ Yes |
| `AKS_RESOURCE_GROUP` | Azure Resource Group containing AKS | Resource Group name | ✅ Yes |

### 🐳 Container Registry

These secrets are required for Docker image building and pushing:

| Secret Name | Description | How to Get | Required |
|-------------|-------------|------------|----------|
| `ACR_USERNAME` | Azure Container Registry username | [ACR Setup](#container-registry-secrets) | ✅ Yes |
| `ACR_PASSWORD` | Azure Container Registry password | [ACR Setup](#container-registry-secrets) | ✅ Yes |

### 💬 Notifications

These secrets enable Slack notifications and alerting:

| Secret Name | Description | How to Get | Required |
|-------------|-------------|------------|----------|
| `SLACK_WEBHOOK` | Slack webhook URL for notifications | [Slack Setup](slack-integration-guide.md) | 🔶 Optional |
| `SLACK_BOT_TOKEN` | Slack bot token (alternative to webhook) | [Slack Setup](slack-integration-guide.md) | 🔶 Optional |

### 📊 Monitoring & Observability

These secrets enable monitoring and observability integrations:

| Secret Name | Description | How to Get | Required |
|-------------|-------------|------------|----------|
| `GRAFANA_URL` | Grafana dashboard URL | Your Grafana instance | 🔶 Optional |
| `GRAFANA_API_KEY` | Grafana API key for dashboard updates | [Grafana API](#grafana-secrets) | 🔶 Optional |
| `PROMETHEUS_PUSHGATEWAY_URL` | Prometheus Pushgateway URL | Your Prometheus instance | 🔶 Optional |
| `ALERTMANAGER_WEBHOOK_URL` | AlertManager webhook URL | Your AlertManager instance | 🔶 Optional |

### 📟 Incident Management

These secrets enable incident management integrations:

| Secret Name | Description | How to Get | Required |
|-------------|-------------|------------|----------|
| `PAGERDUTY_ROUTING_KEY` | PagerDuty integration routing key | [PagerDuty Setup](#pagerduty-secrets) | 🔶 Optional |

### 🔐 Security Scanning

These secrets enable security scanning in the pipeline:

| Secret Name | Description | How to Get | Required |
|-------------|-------------|------------|----------|
| `SNYK_TOKEN` | Snyk security scanning token | [Snyk Account](#snyk-secrets) | 🔶 Optional |

### 🚩 Feature Flags

These secrets enable feature flag management:

| Secret Name | Description | How to Get | Required |
|-------------|-------------|------------|----------|
| `CONFIGCAT_API_KEY` | ConfigCat feature flag service API key | [ConfigCat Setup](#feature-flag-secrets) | 🔶 Optional |
| `LAUNCHDARKLY_SDK_KEY` | LaunchDarkly SDK key | [LaunchDarkly Setup](#feature-flag-secrets) | 🔶 Optional |

## 🔧 Detailed Setup Instructions

### Azure Credentials

#### Option A: Using Azure CLI (Recommended)

1. **Install Azure CLI**
   ```bash
   # macOS
   brew install azure-cli
   
   # Ubuntu/Debian
   curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
   
   # Windows
   # Download from https://docs.microsoft.com/en-us/cli/azure/install-azure-cli
   ```

2. **Login to Azure**
   ```bash
   az login
   ```

3. **Create Service Principal**
   ```bash
   # Get your subscription ID
   az account show --query id --output tsv
   
   # Create service principal
   az ad sp create-for-rbac --name "spx-options-trading-bot" \
     --role contributor \
     --scopes /subscriptions/{subscription-id} \
     --sdk-auth
   ```

4. **Copy the JSON output** and add it as the `AZURE_CREDENTIALS` secret.

#### Option B: Using Azure Portal

1. **Navigate to Azure Active Directory** → **App registrations**
2. **Create new registration** named "spx-options-trading-bot"
3. **Create client secret** in Certificates & secrets
4. **Assign Contributor role** to the resource group
5. **Format the JSON:**
   ```json
   {
     "clientId": "your-client-id",
     "clientSecret": "your-client-secret",
     "subscriptionId": "your-subscription-id",
     "tenantId": "your-tenant-id",
     "resourceManagerEndpointUrl": "https://management.azure.com/"
   }
   ```

### Container Registry Secrets

#### Azure Container Registry (ACR)

1. **Create ACR (if not exists)**
   ```bash
   az acr create --resource-group myResourceGroup \
     --name spxoptionsregistry \
     --sku Basic
   ```

2. **Enable Admin User**
   ```bash
   az acr update -n spxoptionsregistry --admin-enabled true
   ```

3. **Get Credentials**
   ```bash
   az acr credential show --name spxoptionsregistry
   ```

4. **Add Secrets:**
   - `ACR_USERNAME`: The username from the credential output
   - `ACR_PASSWORD`: One of the passwords from the credential output

### Grafana Secrets

1. **Access Grafana Dashboard**
2. **Navigate to** Configuration → API Keys
3. **Create New API Key**
   - Name: "SPX Trading Bot CI/CD"
   - Role: Editor or Admin
   - Expires: Never (or set appropriate expiry)
4. **Copy the generated key** and add as `GRAFANA_API_KEY`
5. **Add your Grafana URL** as `GRAFANA_URL` (e.g., `https://your-grafana.example.com`)

### PagerDuty Secrets

1. **Login to PagerDuty**
2. **Navigate to** Services → Your Service
3. **Go to** Integrations tab
4. **Add Integration** → Events API v2
5. **Copy the Integration Key** and add as `PAGERDUTY_ROUTING_KEY`

### Snyk Secrets

1. **Create Snyk Account** at [snyk.io](https://snyk.io)
2. **Navigate to** Account Settings
3. **Copy your Auth Token**
4. **Add as** `SNYK_TOKEN` secret

### Feature Flag Secrets

#### ConfigCat

1. **Create ConfigCat Account** at [configcat.com](https://configcat.com)
2. **Navigate to** your product → SDK Keys
3. **Copy the API Key** and add as `CONFIGCAT_API_KEY`

#### LaunchDarkly

1. **Create LaunchDarkly Account** at [launchdarkly.com](https://launchdarkly.com)
2. **Navigate to** Account Settings → Projects
3. **Select your project** → Environments
4. **Copy the SDK Key** for your environment
5. **Add as** `LAUNCHDARKLY_SDK_KEY`

## 🔐 Adding Secrets to GitHub Repository

### Using GitHub Web Interface

1. **Navigate to your repository** on GitHub
2. **Go to Settings** → **Secrets and variables** → **Actions**
3. **Click "New repository secret"**
4. **Enter the secret name and value**
5. **Click "Add secret"**

### Using GitHub CLI

1. **Install GitHub CLI**
   ```bash
   # macOS
   brew install gh
   
   # Ubuntu/Debian
   curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
   echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
   sudo apt update
   sudo apt install gh
   ```

2. **Login to GitHub**
   ```bash
   gh auth login
   ```

3. **Add Secrets**
   ```bash
   # Add secrets from environment variables
   gh secret set AZURE_CREDENTIALS --body "$AZURE_CREDENTIALS"
   gh secret set ACR_USERNAME --body "$ACR_USERNAME"
   gh secret set ACR_PASSWORD --body "$ACR_PASSWORD"
   
   # Or from files
   gh secret set AZURE_CREDENTIALS < azure-credentials.json
   ```

## 📝 Secrets Configuration Template

Create a local template file to track which secrets you need:

```bash
# secrets-template.txt
# Copy this template and fill in your values
# DO NOT commit this file to version control!

# === REQUIRED SECRETS ===
AZURE_CREDENTIALS='{
  "clientId": "",
  "clientSecret": "",
  "subscriptionId": "",
  "tenantId": "",
  "resourceManagerEndpointUrl": "https://management.azure.com/"
}'
ACR_USERNAME=""
ACR_PASSWORD=""
AKS_CLUSTER_NAME=""
AKS_RESOURCE_GROUP=""

# === OPTIONAL SECRETS ===
SLACK_WEBHOOK=""
GRAFANA_URL=""
GRAFANA_API_KEY=""
PROMETHEUS_PUSHGATEWAY_URL=""
PAGERDUTY_ROUTING_KEY=""
SNYK_TOKEN=""
CONFIGCAT_API_KEY=""
LAUNCHDARKLY_SDK_KEY=""
```

## 🧪 Testing Secrets Configuration

Use this script to test if your secrets are correctly configured:

```bash
#!/bin/bash
# test-secrets.sh

echo "🔍 Testing GitHub Secrets Configuration..."

# Check required secrets
required_secrets=("AZURE_CREDENTIALS" "ACR_USERNAME" "ACR_PASSWORD" "AKS_CLUSTER_NAME" "AKS_RESOURCE_GROUP")
optional_secrets=("SLACK_WEBHOOK" "GRAFANA_URL" "GRAFANA_API_KEY" "PROMETHEUS_PUSHGATEWAY_URL")

echo ""
echo "✅ Required Secrets:"
for secret in "${required_secrets[@]}"; do
    if gh secret list | grep -q "$secret"; then
        echo "  ✅ $secret: Configured"
    else
        echo "  ❌ $secret: Missing"
    fi
done

echo ""
echo "🔶 Optional Secrets:"
for secret in "${optional_secrets[@]}"; do
    if gh secret list | grep -q "$secret"; then
        echo "  ✅ $secret: Configured"
    else
        echo "  ⚪ $secret: Not configured"
    fi
done

echo ""
echo "🚀 To add missing secrets:"
echo "  gh secret set SECRET_NAME --body 'SECRET_VALUE'"
echo "  Or use the GitHub web interface: Settings → Secrets and variables → Actions"
```

## ⚠️ Security Best Practices

### 1. **Principle of Least Privilege**
- Grant only necessary permissions to service principals
- Use separate credentials for different environments
- Regularly rotate secrets

### 2. **Secret Rotation**
```bash
# Set expiry reminders
# Azure Service Principal - Rotate every 6 months
# API Keys - Rotate every 3 months
# Container Registry - Rotate every 6 months
```

### 3. **Access Monitoring**
- Monitor secret usage in GitHub
- Set up alerts for failed authentication
- Regular access reviews

### 4. **Environment Separation**
- Use different secrets for different environments
- Consider separate Azure subscriptions for prod/non-prod

## 📊 Environment-Specific Configuration

### Development Environment
```bash
# Minimal secrets needed for development
AZURE_CREDENTIALS="{dev-service-principal}"
ACR_USERNAME="dev-registry-user"
ACR_PASSWORD="dev-registry-password"
AKS_CLUSTER_NAME="spx-dev-aks"
AKS_RESOURCE_GROUP="spx-dev-rg"
```

### Staging Environment
```bash
# Include monitoring for staging
AZURE_CREDENTIALS="{staging-service-principal}"
ACR_USERNAME="staging-registry-user"
ACR_PASSWORD="staging-registry-password"
AKS_CLUSTER_NAME="spx-staging-aks"
AKS_RESOURCE_GROUP="spx-staging-rg"
SLACK_WEBHOOK="https://hooks.slack.com/staging-webhook"
GRAFANA_URL="https://staging-grafana.example.com"
```

### Production Environment
```bash
# Full monitoring and alerting for production
AZURE_CREDENTIALS="{prod-service-principal}"
ACR_USERNAME="prod-registry-user"
ACR_PASSWORD="prod-registry-password"
AKS_CLUSTER_NAME="spx-prod-aks"
AKS_RESOURCE_GROUP="spx-prod-rg"
SLACK_WEBHOOK="https://hooks.slack.com/prod-webhook"
GRAFANA_URL="https://grafana.example.com"
GRAFANA_API_KEY="prod-grafana-key"
PAGERDUTY_ROUTING_KEY="prod-pagerduty-key"
```

## 🚨 Troubleshooting

### Common Issues

1. **Azure Authentication Failed**
   ```
   Error: AZURE_CREDENTIALS secret is invalid
   Solution: Verify JSON format and service principal permissions
   ```

2. **Container Registry Access Denied**
   ```
   Error: Unable to push to ACR
   Solution: Check ACR_USERNAME and ACR_PASSWORD, ensure admin user is enabled
   ```

3. **Kubernetes Cluster Access Denied**
   ```
   Error: kubectl authentication failed
   Solution: Verify service principal has AKS permissions
   ```

### Testing Commands

```bash
# Test Azure credentials
az login --service-principal -u $CLIENT_ID -p $CLIENT_SECRET --tenant $TENANT_ID

# Test ACR access
docker login spxoptionsregistry.azurecr.io -u $ACR_USERNAME -p $ACR_PASSWORD

# Test AKS access
az aks get-credentials --resource-group $AKS_RESOURCE_GROUP --name $AKS_CLUSTER_NAME
kubectl get nodes
```

## 📚 Additional Resources

- [GitHub Encrypted Secrets Documentation](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Azure Service Principal Documentation](https://docs.microsoft.com/en-us/azure/active-directory/develop/app-objects-and-service-principals)
- [Azure Container Registry Authentication](https://docs.microsoft.com/en-us/azure/container-registry/container-registry-authentication)
- [Kubernetes RBAC Documentation](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)

---

✅ **Secrets Setup Complete!** Your CI/CD pipeline now has access to all required services and integrations.
