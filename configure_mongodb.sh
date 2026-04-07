#!/bin/bash
# MongoDB Configuration Script
# This script helps you create a .env file with MongoDB credentials

echo "=========================================="
echo "MongoDB Configuration for Gamification"
echo "=========================================="
echo ""
echo "This will create/update your .env file with MongoDB settings"
echo ""

# Get MongoDB credentials
read -p "MongoDB Host: " MONGO_HOST
read -p "MongoDB Port [27017]: " MONGO_PORT
MONGO_PORT=${MONGO_PORT:-27017}
read -p "MongoDB Username: " MONGO_USER
read -sp "MongoDB Password: " MONGO_PASS
echo ""
read -p "MongoDB Database [devops_tooling]: " MONGO_DB
MONGO_DB=${MONGO_DB:-devops_tooling}

# Construct MongoDB URI
MONGODB_URI="mongodb://${MONGO_USER}:${MONGO_PASS}@${MONGO_HOST}:${MONGO_PORT}"

echo ""
echo "Creating .env file..."

# Create or append to .env
if [ -f .env ]; then
    echo "" >> .env
    echo "# MongoDB Configuration (added $(date))" >> .env
else
    echo "# Environment Configuration" > .env
    echo "# MongoDB Configuration" >> .env
fi

echo "MONGODB_URI=${MONGODB_URI}" >> .env
echo "MONGODB_DATABASE=${MONGO_DB}" >> .env

echo ""
echo "✅ Configuration saved to .env"
echo ""
echo "MongoDB URI: mongodb://${MONGO_USER}:****@${MONGO_HOST}:${MONGO_PORT}"
echo "Database: ${MONGO_DB}"
echo ""
echo "Next steps:"
echo "1. Install pymongo: pip install pymongo"
echo "2. Run: python main.py refresh"
echo ""
