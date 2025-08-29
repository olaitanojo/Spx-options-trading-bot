# Monitoring Integration Setup Guide

This guide covers setting up comprehensive monitoring for your SPX Options Trading Bot using Grafana, Prometheus, and other observability tools.

## 📋 Prerequisites

- Kubernetes cluster (AKS/EKS/GKE)
- Helm 3.x installed
- kubectl configured
- Domain name for ingress (optional)

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   SPX Bot       │───▶│   Prometheus     │───▶│   Grafana       │
│   (Metrics)     │    │   (Collection)   │    │   (Visualization)│
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Jaeger        │    │   AlertManager   │    │   PagerDuty     │
│   (Tracing)     │    │   (Alerting)     │    │   (Incidents)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🎯 Step 1: Deploy Prometheus Stack

### Option A: Using Helm (Recommended)

1. **Add Prometheus Community Helm Repository**
   ```bash
   helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
   helm repo update
   ```

2. **Create Monitoring Namespace**
   ```bash
   kubectl create namespace monitoring
   ```

3. **Install kube-prometheus-stack**
   ```bash
   helm install prometheus prometheus-community/kube-prometheus-stack \
     --namespace monitoring \
     --create-namespace \
     --set prometheus.ingress.enabled=true \
     --set prometheus.ingress.hosts[0]=prometheus.yourdomain.com \
     --set grafana.ingress.enabled=true \
     --set grafana.ingress.hosts[0]=grafana.yourdomain.com \
     --set grafana.adminPassword=YourSecurePassword123
   ```

### Option B: Custom Installation

1. **Create Custom Values File**
   ```yaml
   # monitoring-values.yaml
   prometheus:
     prometheusSpec:
       retention: 15d
       storageSpec:
         volumeClaimTemplate:
           spec:
             storageClassName: managed-premium
             accessModes: ["ReadWriteOnce"]
             resources:
               requests:
                 storage: 100Gi
     ingress:
       enabled: true
       ingressClassName: nginx
       hosts:
         - prometheus.yourdomain.com
       tls:
         - secretName: prometheus-tls
           hosts:
             - prometheus.yourdomain.com
   
   grafana:
     adminPassword: YourSecurePassword123
     persistence:
       enabled: true
       size: 10Gi
       storageClassName: managed-premium
     ingress:
       enabled: true
       ingressClassName: nginx
       hosts:
         - grafana.yourdomain.com
       tls:
         - secretName: grafana-tls
           hosts:
             - grafana.yourdomain.com
   
   alertmanager:
     alertmanagerSpec:
       storage:
         volumeClaimTemplate:
           spec:
             storageClassName: managed-premium
             accessModes: ["ReadWriteOnce"]
             resources:
               requests:
                 storage: 10Gi
   ```

2. **Install with Custom Values**
   ```bash
   helm install prometheus prometheus-community/kube-prometheus-stack \
     --namespace monitoring \
     --create-namespace \
     -f monitoring-values.yaml
   ```

## 📊 Step 2: Configure Application Metrics

### Add Prometheus Metrics to Your App

1. **Install Prometheus Client Library**
   ```bash
   pip install prometheus-client
   ```

2. **Update Application Code**
   ```python
   # src/monitoring/metrics.py
   from prometheus_client import Counter, Histogram, Gauge, start_http_server
   import time
   
   # Define metrics
   REQUEST_COUNT = Counter('spx_requests_total', 'Total requests', ['method', 'endpoint'])
   REQUEST_DURATION = Histogram('spx_request_duration_seconds', 'Request duration')
   ACTIVE_TRADES = Gauge('spx_active_trades', 'Number of active trades')
   PORTFOLIO_VALUE = Gauge('spx_portfolio_value_usd', 'Current portfolio value')
   ERROR_COUNT = Counter('spx_errors_total', 'Total errors', ['type'])
   
   class MetricsMiddleware:
       def __init__(self):
           self.start_time = time.time()
   
       def record_request(self, method, endpoint):
           REQUEST_COUNT.labels(method=method, endpoint=endpoint).inc()
   
       def record_duration(self, duration):
           REQUEST_DURATION.observe(duration)
   
       def update_active_trades(self, count):
           ACTIVE_TRADES.set(count)
   
       def update_portfolio_value(self, value):
           PORTFOLIO_VALUE.set(value)
   
       def record_error(self, error_type):
           ERROR_COUNT.labels(type=error_type).inc()
   ```

3. **Add Health Check Endpoint**
   ```python
   # src/monitoring/health.py
   from flask import Flask, jsonify
   from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
   
   app = Flask(__name__)
   
   @app.route('/health')
   def health_check():
       return jsonify({
           'status': 'healthy',
           'timestamp': time.time(),
           'version': os.getenv('APP_VERSION', 'unknown')
       })
   
   @app.route('/metrics')
   def metrics():
       return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}
   
   if __name__ == '__main__':
       start_http_server(8080)  # Prometheus metrics port
       app.run(host='0.0.0.0', port=8000, debug=False)  # Health check port
   ```

### Configure ServiceMonitor

1. **Create ServiceMonitor Resource**
   ```yaml
   # k8s/monitoring/servicemonitor.yaml
   apiVersion: monitoring.coreos.com/v1
   kind: ServiceMonitor
   metadata:
     name: spx-options-trading-bot
     namespace: monitoring
     labels:
       app: spx-options-trading-bot
   spec:
     selector:
       matchLabels:
         app: spx-options-trading-bot
     endpoints:
     - port: metrics
       interval: 30s
       path: /metrics
   ```

## 📈 Step 3: Set Up Grafana Dashboards

### Access Grafana

1. **Get Admin Password**
   ```bash
   kubectl get secret --namespace monitoring prometheus-grafana \
     -o jsonpath="{.data.admin-password}" | base64 --decode
   ```

2. **Port Forward (if no ingress)**
   ```bash
   kubectl port-forward --namespace monitoring \
     svc/prometheus-grafana 3000:80
   ```

3. **Access Grafana**
   ```
   URL: http://localhost:3000 (or https://grafana.yourdomain.com)
   Username: admin
   Password: [from step 1]
   ```

### Configure Data Sources

1. **Add Prometheus Data Source**
   - Go to Configuration > Data Sources
   - Click "Add data source"
   - Select "Prometheus"
   - URL: `http://prometheus-prometheus:9090`
   - Click "Save & Test"

### Import Pre-built Dashboards

1. **Kubernetes Dashboards**
   ```bash
   # Popular dashboard IDs
   # 315 - Kubernetes cluster monitoring
   # 8588 - Kubernetes Deployment Statefulset Daemonset metrics
   # 6417 - Kubernetes cluster Prometheus
   ```

## 🚨 Step 4: Configure Alerting

### Create Alert Rules

1. **SPX Bot Specific Alerts**
   ```yaml
   # k8s/monitoring/alerts.yaml
   apiVersion: monitoring.coreos.com/v1
   kind: PrometheusRule
   metadata:
     name: spx-trading-bot-alerts
     namespace: monitoring
     labels:
       app: spx-options-trading-bot
   spec:
     groups:
     - name: spx-trading-bot
       rules:
       - alert: SPXBotDown
         expr: up{job="spx-options-trading-bot"} == 0
         for: 5m
         labels:
           severity: critical
         annotations:
           summary: "SPX Trading Bot is down"
           description: "SPX Trading Bot has been down for more than 5 minutes"
   
       - alert: SPXHighErrorRate
         expr: rate(spx_errors_total[5m]) > 0.1
         for: 2m
         labels:
           severity: warning
         annotations:
           summary: "High error rate in SPX Trading Bot"
           description: "Error rate is {{ $value }} errors per second"
   
       - alert: SPXPortfolioValueDrop
         expr: (spx_portfolio_value_usd - spx_portfolio_value_usd offset 1h) / spx_portfolio_value_usd offset 1h < -0.05
         for: 10m
         labels:
           severity: warning
         annotations:
           summary: "Portfolio value dropped significantly"
           description: "Portfolio value dropped by more than 5% in the last hour"
   ```

### Configure AlertManager

1. **Create AlertManager Configuration**
   ```yaml
   # k8s/monitoring/alertmanager-config.yaml
   apiVersion: v1
   kind: Secret
   metadata:
     name: alertmanager-prometheus-alertmanager
     namespace: monitoring
   type: Opaque
   stringData:
     alertmanager.yml: |
       global:
         smtp_smarthost: 'smtp.gmail.com:587'
         smtp_from: 'alerts@yourdomain.com'
         smtp_auth_username: 'alerts@yourdomain.com'
         smtp_auth_password: 'your-app-password'
   
       route:
         group_by: ['alertname']
         group_wait: 10s
         group_interval: 10s
         repeat_interval: 1h
         receiver: 'spx-alerts'
         routes:
         - match:
             severity: critical
           receiver: 'spx-critical'
   
       receivers:
       - name: 'spx-alerts'
         slack_configs:
         - api_url: 'YOUR_SLACK_WEBHOOK_URL'
           channel: '#spx-alerts'
           title: 'SPX Trading Bot Alert'
           text: '{{ range .Alerts }}{{ .Annotations.summary }}{{ end }}'
   
       - name: 'spx-critical'
         slack_configs:
         - api_url: 'YOUR_SLACK_WEBHOOK_URL'
           channel: '#spx-critical'
           title: 'CRITICAL: SPX Trading Bot'
           text: '{{ range .Alerts }}{{ .Annotations.summary }}{{ end }}'
         pagerduty_configs:
         - routing_key: 'YOUR_PAGERDUTY_KEY'
           description: '{{ range .Alerts }}{{ .Annotations.summary }}{{ end }}'
   ```

## 🔍 Step 5: Set Up Distributed Tracing (Optional)

### Deploy Jaeger

1. **Install Jaeger Operator**
   ```bash
   kubectl create namespace observability
   kubectl create -f https://github.com/jaegertracing/jaeger-operator/releases/download/v1.41.0/jaeger-operator.yaml -n observability
   ```

2. **Deploy Jaeger Instance**
   ```yaml
   # k8s/monitoring/jaeger.yaml
   apiVersion: jaegertracing.io/v1
   kind: Jaeger
   metadata:
     name: spx-jaeger
     namespace: observability
   spec:
     strategy: production
     storage:
       type: elasticsearch
     ```

### Add Tracing to Your App

1. **Install Jaeger Client**
   ```bash
   pip install jaeger-client opentracing
   ```

2. **Configure Tracing**
   ```python
   # src/monitoring/tracing.py
   from jaeger_client import Config
   import opentracing
   
   def init_tracer(service_name='spx-options-trading-bot'):
       config = Config(
           config={
               'sampler': {'type': 'const', 'param': 1},
               'logging': True,
           },
           service_name=service_name,
       )
       return config.initialize_tracer()
   
   tracer = init_tracer()
   opentracing.set_global_tracer(tracer)
   ```

## 📱 Step 6: Configure GitHub Secrets

Add these secrets to your GitHub repository:

```bash
# Monitoring Integration Secrets
GRAFANA_URL=https://grafana.yourdomain.com
GRAFANA_API_KEY=your-grafana-api-key
PROMETHEUS_PUSHGATEWAY_URL=http://prometheus-pushgateway.monitoring.svc.cluster.local:9091

# AlertManager Configuration
ALERTMANAGER_WEBHOOK_URL=http://alertmanager.monitoring.svc.cluster.local:9093

# PagerDuty Integration (Optional)
PAGERDUTY_ROUTING_KEY=your-pagerduty-routing-key
```

## 📊 Step 7: Create Custom Grafana Dashboard

### Dashboard JSON Configuration

The dashboard will be created in the next step with comprehensive panels for:
- Application health metrics
- Trading performance indicators
- System resource utilization
- Error rates and response times
- Portfolio value tracking

## 🔧 Step 8: Monitoring Scripts

### Deployment Event Script

```bash
# scripts/send-deployment-event.sh
#!/bin/bash

PROMETHEUS_URL="${PROMETHEUS_PUSHGATEWAY_URL:-http://localhost:9091}"
ENVIRONMENT="${1:-development}"
STRATEGY="${2:-rolling}"
COMMIT_SHA="${3:-unknown}"

curl -X POST "${PROMETHEUS_URL}/metrics/job/github-actions" \
  --data-binary @- << EOF
# HELP deployment_info Deployment information
# TYPE deployment_info gauge
deployment_info{environment="${ENVIRONMENT}",strategy="${STRATEGY}",commit="${COMMIT_SHA}"} 1
deployment_timestamp $(date +%s)
EOF

echo "Deployment event sent to Prometheus"
```

## 🧪 Step 9: Testing Monitoring Setup

### Health Check Script

```python
# scripts/monitoring-health-check.py
#!/usr/bin/env python3

import requests
import sys
import time

def check_prometheus():
    try:
        response = requests.get('http://prometheus.monitoring.svc.cluster.local:9090/-/healthy')
        return response.status_code == 200
    except:
        return False

def check_grafana():
    try:
        response = requests.get('http://prometheus-grafana.monitoring.svc.cluster.local:80/api/health')
        return response.status_code == 200
    except:
        return False

def check_app_metrics():
    try:
        response = requests.get('http://spx-options-trading-bot.default.svc.cluster.local:8080/metrics')
        return response.status_code == 200
    except:
        return False

if __name__ == "__main__":
    checks = [
        ("Prometheus", check_prometheus),
        ("Grafana", check_grafana),
        ("App Metrics", check_app_metrics)
    ]
    
    all_healthy = True
    
    for name, check_func in checks:
        if check_func():
            print(f"✅ {name} is healthy")
        else:
            print(f"❌ {name} is not responding")
            all_healthy = False
    
    if all_healthy:
        print("🎉 All monitoring components are healthy!")
        sys.exit(0)
    else:
        print("🚨 Some monitoring components are failing")
        sys.exit(1)
```

## 🚨 Troubleshooting

### Common Issues

1. **ServiceMonitor Not Discovering Targets**
   ```bash
   # Check ServiceMonitor labels
   kubectl get servicemonitor -n monitoring -o yaml
   
   # Verify Prometheus configuration
   kubectl port-forward svc/prometheus-prometheus 9090:9090 -n monitoring
   # Visit http://localhost:9090/targets
   ```

2. **Grafana Data Source Connection Failed**
   ```bash
   # Check Prometheus service
   kubectl get svc -n monitoring | grep prometheus
   
   # Test connection from Grafana pod
   kubectl exec -it deployment/prometheus-grafana -n monitoring -- wget -O- http://prometheus-prometheus:9090/api/v1/label/__name__/values
   ```

3. **Metrics Not Appearing**
   ```bash
   # Check application metrics endpoint
   kubectl port-forward deployment/spx-options-trading-bot 8080:8080
   curl http://localhost:8080/metrics
   
   # Verify ServiceMonitor selector
   kubectl get svc -l app=spx-options-trading-bot --show-labels
   ```

## 🔒 Security Best Practices

1. **Secure Grafana**
   - Change default admin password
   - Enable HTTPS with proper certificates
   - Configure LDAP/OAuth integration
   - Regular security updates

2. **Prometheus Security**
   - Restrict access to Prometheus UI
   - Configure proper RBAC
   - Enable authentication for remote read/write

3. **Network Security**
   - Use NetworkPolicies to restrict access
   - Configure ingress with proper authentication
   - Regular security scans

## 📚 Additional Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Kubernetes Monitoring Guide](https://kubernetes.io/docs/concepts/cluster-administration/monitoring/)
- [kube-prometheus-stack](https://github.com/prometheus-community/helm-charts/tree/main/charts/kube-prometheus-stack)

---

✅ **Monitoring Setup Complete!** Your comprehensive observability stack is now ready.
