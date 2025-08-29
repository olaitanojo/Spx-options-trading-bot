# Slack Integration Setup Guide

This guide will help you set up Slack notifications for your SPX Options Trading Bot CI/CD pipeline.

## 📋 Prerequisites

- Slack workspace with admin permissions
- GitHub repository with Actions enabled
- SPX Options Trading Bot repository

## 🔧 Step 1: Create Slack App

1. **Go to Slack API Dashboard**
   ```
   https://api.slack.com/apps
   ```

2. **Create New App**
   - Click "Create New App"
   - Choose "From scratch"
   - App Name: `SPX Trading Bot CI/CD`
   - Select your workspace

3. **Configure App Permissions**
   - Go to "OAuth & Permissions"
   - Add Bot Token Scopes:
     - `chat:write`
     - `chat:write.public`
     - `files:write`

## 🪝 Step 2: Create Incoming Webhook

### Option A: Using Incoming Webhooks (Recommended)

1. **Enable Incoming Webhooks**
   - In your Slack app settings
   - Go to "Incoming Webhooks"
   - Turn on "Activate Incoming Webhooks"

2. **Add Webhook to Workspace**
   - Click "Add New Webhook to Workspace"
   - Select channel: `#spx-deployments` (create if doesn't exist)
   - Click "Allow"

3. **Copy Webhook URL**
   ```
   https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX
   ```

### Option B: Using Bot Token (Alternative)

1. **Install App to Workspace**
   - Go to "Install App"
   - Click "Install to Workspace"
   - Copy Bot User OAuth Token

## 📱 Step 3: Create Slack Channel

1. **Create Channel**
   ```
   Channel name: #spx-deployments
   Description: SPX Options Trading Bot deployment notifications
   ```

2. **Add Bot to Channel**
   - Type: `/invite @SPX Trading Bot CI/CD`
   - Or use the Apps section to add your bot

## 🔒 Step 4: Configure GitHub Secrets

1. **Navigate to Repository Settings**
   ```
   https://github.com/YOUR_USERNAME/spx-options-trading-bot/settings/secrets/actions
   ```

2. **Add Slack Webhook Secret**
   ```
   Name: SLACK_WEBHOOK
   Value: https://hooks.slack.com/services/YOUR/WEBHOOK/URL
   ```

3. **Optional: Add Bot Token (if using Option B)**
   ```
   Name: SLACK_BOT_TOKEN
   Value: xoxb-your-bot-token
   ```

## 🧪 Step 5: Test Integration

### Manual Test

1. **Test Webhook with curl**
   ```bash
   curl -X POST -H 'Content-type: application/json' \
     --data '{"text":"Test message from SPX Trading Bot CI/CD"}' \
     YOUR_WEBHOOK_URL
   ```

### GitHub Actions Test

2. **Create Test Workflow** (temporary)
   ```yaml
   # .github/workflows/test-slack.yml
   name: Test Slack Integration
   on:
     workflow_dispatch:
   
   jobs:
     test:
       runs-on: ubuntu-latest
       steps:
         - name: Test Slack Notification
           uses: 8398a7/action-slack@v3
           with:
             status: success
             channel: '#spx-deployments'
             text: 'Slack integration test successful! 🎉'
           env:
             SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
   ```

## 📬 Step 6: Customize Notifications

### Success Notification Example
```yaml
- name: Notify Slack on Success
  uses: 8398a7/action-slack@v3
  with:
    status: success
    channel: '#spx-deployments'
    custom_payload: |
      {
        channel: '#spx-deployments',
        attachments: [{
          color: 'good',
          title: '✅ Deployment Successful',
          text: 'SPX Options Trading Bot deployed successfully!',
          fields: [{
            title: 'Environment',
            value: '${{ needs.setup.outputs.environment }}',
            short: true
          }, {
            title: 'Strategy',
            value: '${{ needs.setup.outputs.deployment_strategy }}',
            short: true
          }, {
            title: 'Commit',
            value: '<https://github.com/${{ github.repository }}/commit/${{ github.sha }}|${{ github.sha }}>',
            short: true
          }, {
            title: 'Branch',
            value: '${{ github.ref_name }}',
            short: true
          }],
          footer: 'SPX Trading Bot CI/CD',
          ts: Math.floor(Date.now() / 1000)
        }]
      }
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

### Failure Notification Example
```yaml
- name: Notify Slack on Failure
  uses: 8398a7/action-slack@v3
  with:
    status: failure
    channel: '#spx-deployments'
    custom_payload: |
      {
        channel: '#spx-deployments',
        attachments: [{
          color: 'danger',
          title: '❌ Deployment Failed',
          text: 'SPX Options Trading Bot deployment failed!',
          fields: [{
            title: 'Environment',
            value: '${{ needs.setup.outputs.environment }}',
            short: true
          }, {
            title: 'Workflow Run',
            value: '<https://github.com/${{ github.repository }}/actions/runs/${{ github.run_id }}|View Details>',
            short: true
          }],
          footer: 'SPX Trading Bot CI/CD',
          ts: Math.floor(Date.now() / 1000)
        }]
      }
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

## 🔧 Advanced Configuration

### Channel Routing by Environment
```yaml
- name: Set Notification Channel
  id: set-channel
  run: |
    case "${{ needs.setup.outputs.environment }}" in
      production) echo "channel=#spx-prod-alerts" >> $GITHUB_OUTPUT ;;
      staging) echo "channel=#spx-staging" >> $GITHUB_OUTPUT ;;
      *) echo "channel=#spx-dev" >> $GITHUB_OUTPUT ;;
    esac

- name: Send Environment-Specific Notification
  uses: 8398a7/action-slack@v3
  with:
    channel: ${{ steps.set-channel.outputs.channel }}
    # ... rest of configuration
```

### Thread Replies for Related Messages
```yaml
- name: Get Thread Timestamp
  id: thread-ts
  run: |
    # Store thread timestamp for follow-up messages
    echo "thread_ts=$(date +%s)" >> $GITHUB_OUTPUT

- name: Send Deployment Start Notification
  uses: 8398a7/action-slack@v3
  with:
    status: custom
    custom_payload: |
      {
        channel: '#spx-deployments',
        ts: '${{ steps.thread-ts.outputs.thread_ts }}',
        text: '🚀 Starting deployment...'
      }
```

## 🎨 Notification Templates

### 1. Deployment Started
```json
{
  "channel": "#spx-deployments",
  "attachments": [{
    "color": "#ffcc00",
    "title": "🚀 Deployment Started",
    "text": "SPX Options Trading Bot deployment initiated",
    "fields": [
      {"title": "Environment", "value": "production", "short": true},
      {"title": "Strategy", "value": "canary", "short": true}
    ]
  }]
}
```

### 2. Deployment Success
```json
{
  "channel": "#spx-deployments",
  "attachments": [{
    "color": "good",
    "title": "✅ Deployment Successful",
    "text": "SPX Options Trading Bot is now live!",
    "fields": [
      {"title": "Environment", "value": "production", "short": true},
      {"title": "Duration", "value": "3m 45s", "short": true}
    ]
  }]
}
```

### 3. Deployment Failure
```json
{
  "channel": "#spx-deployments",
  "attachments": [{
    "color": "danger",
    "title": "❌ Deployment Failed",
    "text": "SPX Options Trading Bot deployment failed",
    "fields": [
      {"title": "Error", "value": "Health check timeout", "short": false},
      {"title": "Action", "value": "Auto-rollback initiated", "short": true}
    ]
  }]
}
```

### 4. Rollback Notification
```json
{
  "channel": "#spx-deployments",
  "attachments": [{
    "color": "warning",
    "title": "🔄 Rollback Completed",
    "text": "SPX Options Trading Bot rolled back to previous version",
    "fields": [
      {"title": "Reason", "value": "Deployment failure", "short": true},
      {"title": "Status", "value": "Service restored", "short": true}
    ]
  }]
}
```

## 🚨 Troubleshooting

### Common Issues

1. **Webhook URL Invalid**
   ```
   Error: Invalid webhook URL
   Solution: Verify the webhook URL is correct and active
   ```

2. **Channel Not Found**
   ```
   Error: channel_not_found
   Solution: Ensure the channel exists and the bot is added
   ```

3. **Permission Denied**
   ```
   Error: not_in_channel
   Solution: Add the Slack app to the target channel
   ```

### Validation Commands

1. **Test Webhook Connection**
   ```bash
   curl -X POST -H 'Content-type: application/json' \
     --data '{"text":"Connection test"}' \
     $SLACK_WEBHOOK_URL
   ```

2. **Validate JSON Payload**
   ```bash
   echo '{"text":"test"}' | jq .
   ```

## 📚 Additional Resources

- [Slack API Documentation](https://api.slack.com/)
- [GitHub Actions Slack Action](https://github.com/8398a7/action-slack)
- [Slack Message Formatting](https://api.slack.com/messaging/composing)
- [Webhook Best Practices](https://api.slack.com/messaging/webhooks)

## 🔒 Security Best Practices

1. **Protect Webhook URLs**
   - Never commit webhook URLs to code
   - Use GitHub Secrets for all sensitive data
   - Rotate webhooks periodically

2. **Limit App Permissions**
   - Only grant necessary scopes
   - Review app permissions regularly

3. **Monitor Usage**
   - Track webhook usage in Slack
   - Set up alerts for unusual activity

---

✅ **Setup Complete!** Your Slack integration is now ready for CI/CD notifications.
