#!/bin/bash
# Quick deployment using Docker Compose
# Perfect for development and testing

echo "🚀 Deploying SPX Options Trading Bot with Docker Compose..."

# Create necessary directories
mkdir -p logs data deployment/secrets deployment/config

# Create default secrets (replace with actual values)
echo "your_db_password_here" > deployment/secrets/db_password.txt
echo "your_grafana_password_here" > deployment/secrets/grafana_password.txt

# Create API keys file
cat > deployment/secrets/api_keys.env << EOF
TRADING_API_KEY=your_trading_api_key
MARKET_DATA_API_KEY=your_market_data_api_key
EOF

# Build and start services
cd deployment
docker-compose up -d --build

echo "✅ Services started!"
echo "📊 Grafana: http://localhost:3000"
echo "📈 Prometheus: http://localhost:9090"
echo "🔍 Trading Bot API: http://localhost:8080"
echo "💾 PostgreSQL: localhost:5432"
echo "⚡ Redis: localhost:6379"

# Show running containers
echo ""
echo "Running containers:"
docker-compose ps
