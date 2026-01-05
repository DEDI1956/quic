#!/bin/bash

# Quick Start Script - For Development/Testing

echo "======================================"
echo "  VPN Bot Quick Start"
echo "======================================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install Python 3.8+"
    exit 1
fi

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "📦 Installing requirements..."
pip install -r requirements.txt

# Setup environment
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file with your settings:"
    echo "   - BOT_TOKEN: Get from @BotFather"
    echo "   - ADMIN_IDS: Your Telegram User ID"
    echo "   - SERVER_DOMAIN: Your domain"
    echo "   - SERVER_IP: Your server IP"
    echo ""
    read -p "Press Enter to continue after editing .env..."
fi

# Initialize database
echo "💾 Initializing database..."
python3 manage.py init

# Make scripts executable
chmod +x manage.py
chmod +x cron_tasks.py

echo ""
echo "======================================"
echo "  ✅ Setup Complete!"
echo "======================================"
echo ""
echo "🚀 To start the bot:"
echo "   python3 bot.py"
echo ""
echo "🔧 Management commands:"
echo "   python3 manage.py add-admin <telegram_id>"
echo "   python3 manage.py add-balance <telegram_id> <amount>"
echo "   python3 manage.py list-users"
echo "   python3 manage.py list-accounts"
echo "   python3 manage.py stats"
echo ""
echo "📝 Note: This is for development only."
echo "   For production, use install.sh on a VPS."
echo ""
