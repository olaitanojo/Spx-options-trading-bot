# 🚀 SPX Options Trading Bot - Deployment Guide

> **Professional deployment guide for the SPX Options Trading Bot with advanced strategies and risk management.**

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Local Development](#local-development)
3. [Docker Deployment](#docker-deployment)
4. [Cloud Deployment](#cloud-deployment)
5. [Configuration](#configuration)
6. [Monitoring & Alerts](#monitoring--alerts)
7. [Security](#security)
8. [Troubleshooting](#troubleshooting)

---

## 🏃‍♂️ Quick Start

### Prerequisites
- Python 3.8+
- Interactive Brokers TWS/IB Gateway account
- Real-time market data subscription
- Sufficient capital for options trading

### 1-Minute Setup
```bash
# Clone and setup
git clone https://github.com/olaitanojo/spx-options-trading-bot.git
cd spx-options-trading-bot
pip install -r requirements.txt

# Configure credentials
cp config.example.yaml config.yaml
# Edit config.yaml with your IB credentials

# Run bot
python main.py
```

---

## 💻 Local Development

### Environment Setup
```bash
# Create virtual environment
python -m venv trading_env
source trading_env/bin/activate  # Windows: trading_env\Scripts\activate

# Install dependencies
pip install ib-insync pandas numpy scipy scikit-learn plotly dash

# Install development tools
pip install pytest black flake8 pre-commit
```

### IB TWS Setup
```bash
# Download and install IB TWS
# Configure API settings:
# - Enable API connections
# - Socket port: 7497 (paper) / 7496 (live)
# - Master API client ID: 1
# - Read-only API: No
```

### Configuration
```yaml
# config.yaml
trading:
  mode: "paper"  # or "live"
  host: "127.0.0.1"
  port: 7497
  client_id: 1
  
account:
  max_position_size: 10000
  risk_per_trade: 0.02
  max_daily_loss: 500

strategies:
  iron_condor:
    enabled: true
    dte_range: [30, 45]
    delta_threshold: 0.15
  
  bull_put_spread:
    enabled: true
    dte_range: [15, 30]
    target_premium: 0.3
```

---

## 🐳 Docker Deployment

### Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create non-root user
RUN useradd -m trader && chown -R trader:trader /app
USER trader

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8080/health')"

CMD ["python", "main.py"]
```

### Docker Compose
```yaml
version: '3.8'
services:
  spx-bot:
    build: .
    container_name: spx-options-bot
    environment:
      - TWS_HOST=host.docker.internal
      - TWS_PORT=7497
      - LOG_LEVEL=INFO
    volumes:
      - ./config:/app/config
      - ./logs:/app/logs
      - ./data:/app/data
    ports:
      - "8080:8080"
    restart: unless-stopped
    depends_on:
      - redis
      - postgres
    
  redis:
    image: redis:7-alpine
    container_name: spx-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    
  postgres:
    image: postgres:15
    container_name: spx-postgres
    environment:
      POSTGRES_DB: spx_trading
      POSTGRES_USER: trader
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  redis_data:
  postgres_data:
```

### Build and Run
```bash
# Build image
docker build -t spx-options-bot .

# Run with compose
docker-compose up -d

# Check logs
docker-compose logs -f spx-bot
```

---

## ☁️ Cloud Deployment

### AWS ECS Deployment

#### Task Definition
```json
{
  "family": "spx-options-bot",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::ACCOUNT:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::ACCOUNT:role/spxTradingRole",
  "containerDefinitions": [
    {
      "name": "spx-bot",
      "image": "your-ecr-repo/spx-options-bot:latest",
      "essential": true,
      "environment": [
        {"name": "TWS_HOST", "value": "your-tws-host"},
        {"name": "LOG_LEVEL", "value": "INFO"}
      ],
      "secrets": [
        {"name": "IB_USERNAME", "valueFrom": "arn:aws:secretsmanager:region:account:secret:ib-credentials"},
        {"name": "IB_PASSWORD", "valueFrom": "arn:aws:secretsmanager:region:account:secret:ib-credentials"}
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/spx-options-bot",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

#### CloudFormation Template
```yaml
AWSTemplateFormatVersion: '2010-09-09'
Resources:
  SPXCluster:
    Type: AWS::ECS::Cluster
    Properties:
      ClusterName: spx-trading-cluster
      
  SPXService:
    Type: AWS::ECS::Service
    Properties:
      Cluster: !Ref SPXCluster
      TaskDefinition: !Ref SPXTaskDefinition
      DesiredCount: 1
      LaunchType: FARGATE
      NetworkConfiguration:
        AwsvpcConfiguration:
          SecurityGroups:
            - !Ref SPXSecurityGroup
          Subnets:
            - !Ref PrivateSubnet
```

### Google Cloud Run
```bash
# Build and push to GCR
docker build -t gcr.io/PROJECT_ID/spx-options-bot .
docker push gcr.io/PROJECT_ID/spx-options-bot

# Deploy to Cloud Run
gcloud run deploy spx-options-bot \
  --image gcr.io/PROJECT_ID/spx-options-bot \
  --platform managed \
  --region us-central1 \
  --memory 1Gi \
  --cpu 1 \
  --set-env-vars TWS_HOST=your-host \
  --max-instances 1
```

### Azure Container Instances
```bash
# Create resource group
az group create --name spx-trading-rg --location eastus

# Deploy container
az container create \
  --resource-group spx-trading-rg \
  --name spx-options-bot \
  --image your-registry/spx-options-bot:latest \
  --cpu 1 \
  --memory 2 \
  --environment-variables TWS_HOST=your-host LOG_LEVEL=INFO \
  --secure-environment-variables IB_USERNAME=user IB_PASSWORD=pass \
  --restart-policy Always
```

---

## ⚙️ Configuration

### Environment Variables
```bash
# Trading Configuration
export TWS_HOST=127.0.0.1
export TWS_PORT=7497
export IB_CLIENT_ID=1
export TRADING_MODE=paper

# Risk Management
export MAX_POSITION_SIZE=10000
export RISK_PER_TRADE=0.02
export MAX_DAILY_LOSS=500

# Database
export DATABASE_URL=postgresql://user:pass@host:port/db
export REDIS_URL=redis://localhost:6379

# Monitoring
export SLACK_WEBHOOK_URL=your-webhook
export EMAIL_ALERTS=trader@example.com
```

### Advanced Configuration
```yaml
# config.yaml
trading:
  mode: "paper"  # paper, live
  host: "127.0.0.1"
  port: 7497
  client_id: 1
  timeout: 10
  
risk_management:
  max_position_size: 10000
  risk_per_trade: 0.02
  max_daily_loss: 500
  max_positions: 10
  stop_loss_pct: 0.5

strategies:
  iron_condor:
    enabled: true
    dte_range: [30, 45]
    delta_threshold: 0.15
    profit_target: 0.5
    max_loss: 2.0
    
  bull_put_spread:
    enabled: true
    dte_range: [15, 30]
    target_premium: 0.3
    delta_threshold: 0.20

monitoring:
  log_level: INFO
  slack_webhook: ${SLACK_WEBHOOK_URL}
  email_alerts: ${EMAIL_ALERTS}
  health_check_port: 8080
```

---

## 📊 Monitoring & Alerts

### Health Check Endpoint
```python
from flask import Flask, jsonify
import psutil
from datetime import datetime

app = Flask(__name__)

@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'uptime': time.time() - start_time,
        'active_positions': get_position_count(),
        'pnl_today': get_daily_pnl(),
        'memory_usage': psutil.virtual_memory().percent
    })

@app.route('/metrics')
def metrics():
    return jsonify({
        'trades_today': get_trades_count(),
        'success_rate': get_success_rate(),
        'total_pnl': get_total_pnl(),
        'risk_utilization': get_risk_utilization()
    })
```

### Prometheus Monitoring
```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'spx-options-bot'
    static_configs:
      - targets: ['spx-bot:8080']
    scrape_interval: 30s
```

### Grafana Dashboard
```json
{
  "dashboard": {
    "title": "SPX Options Trading Bot",
    "panels": [
      {
        "title": "Daily P&L",
        "type": "graph",
        "targets": [
          {
            "expr": "trading_pnl_total"
          }
        ]
      },
      {
        "title": "Active Positions",
        "type": "stat",
        "targets": [
          {
            "expr": "trading_positions_active"
          }
        ]
      }
    ]
  }
}
```

### Alerting Rules
```yaml
# alerts.yml
groups:
  - name: spx-trading-alerts
    rules:
      - alert: HighDrawdown
        expr: trading_drawdown_pct > 5
        for: 5m
        labels:
          severity: critical
        annotations:
          description: "Trading drawdown exceeded 5%"
      
      - alert: BotDisconnected
        expr: up{job="spx-options-bot"} == 0
        for: 2m
        labels:
          severity: critical
        annotations:
          description: "Trading bot is disconnected"
```

---

## 🔒 Security

### API Security
```python
# Secure configuration handling
import os
from cryptography.fernet import Fernet

def decrypt_credentials():
    key = os.environ.get('ENCRYPTION_KEY')
    cipher = Fernet(key)
    encrypted_creds = os.environ.get('ENCRYPTED_CREDENTIALS')
    return cipher.decrypt(encrypted_creds.encode()).decode()
```

### Network Security
```bash
# Firewall rules (AWS Security Group)
{
  "GroupName": "spx-trading-sg",
  "Description": "Security group for SPX trading bot",
  "SecurityGroupRules": [
    {
      "IpPermissions": [
        {
          "IpProtocol": "tcp",
          "FromPort": 7497,
          "ToPort": 7497,
          "IpRanges": [{"CidrIp": "10.0.0.0/8"}]
        }
      ]
    }
  ]
}
```

### Secrets Management
```yaml
# Docker secrets
version: '3.8'
services:
  spx-bot:
    image: spx-options-bot
    secrets:
      - ib_username
      - ib_password
    environment:
      - IB_USERNAME_FILE=/run/secrets/ib_username
      - IB_PASSWORD_FILE=/run/secrets/ib_password

secrets:
  ib_username:
    file: ./secrets/ib_username.txt
  ib_password:
    file: ./secrets/ib_password.txt
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. IB Connection Issues
```bash
# Check IB TWS status
curl -f http://localhost:7497 || echo "IB TWS not accessible"

# Verify API settings
python -c "
import ib_insync
ib = ib_insync.IB()
try:
    ib.connect('127.0.0.1', 7497, clientId=1)
    print('Connected successfully')
except Exception as e:
    print(f'Connection failed: {e}')
"
```

#### 2. Market Data Issues
```python
# Test market data subscription
def test_market_data():
    from ib_insync import IB, Stock
    
    ib = IB()
    ib.connect('127.0.0.1', 7497, clientId=1)
    
    spx = Stock('SPX', 'CBOE')
    ticker = ib.reqMktData(spx)
    ib.sleep(2)
    
    if ticker.last > 0:
        print(f"Market data working: SPX = {ticker.last}")
    else:
        print("Market data not available")
```

#### 3. Memory Issues
```bash
# Monitor memory usage
docker stats spx-options-bot

# Increase memory limit
docker run --memory=2g spx-options-bot
```

### Debugging Commands
```bash
# View logs
docker-compose logs -f spx-bot

# Execute commands in container
docker-compose exec spx-bot python -c "import main; main.test_connection()"

# Check positions
docker-compose exec spx-bot python -c "
from ib_insync import IB
ib = IB()
ib.connect()
positions = ib.positions()
print(f'Active positions: {len(positions)}')
"
```

### Performance Optimization
```python
# Optimize IB connection
ib = IB()
ib.connect('127.0.0.1', 7497, clientId=1, timeout=20)

# Use asyncio for better performance
import asyncio
from ib_insync import IB

async def main():
    ib = IB()
    await ib.connectAsync('127.0.0.1', 7497, clientId=1)
    # Your trading logic here

if __name__ == '__main__':
    asyncio.run(main())
```

---

## 📈 Performance Benchmarks

- **Latency**: < 100ms for order execution
- **Memory**: ~200MB base usage
- **CPU**: 1-2% during normal operation
- **Orders/day**: Up to 100 option strategies
- **Uptime**: 99.9% target availability

---

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/olaitanojo/spx-options-trading-bot/issues)
- **Documentation**: [Wiki](https://github.com/olaitanojo/spx-options-trading-bot/wiki)
- **Discord**: [Trading Community](https://discord.gg/spx-trading)

---

*Last updated: December 2024*
*Version: 1.0.0*
