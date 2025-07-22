#!/bin/bash

# UM-GemiFish Development Server Script
# This script helps you start the Flask app and ngrok tunnel

echo "UM-GemiFish WhatsApp Image Receiver"
echo "=================================="

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Virtual environment not activated. Activating now..."
    source venv/bin/activate
fi

# Check if .env file exists
if [[ ! -f .env ]]; then
    echo "❌ .env file not found. Please create it with your Twilio credentials:"
    echo "TWILIO_ACCOUNT_SID=your_account_sid_here"
    echo "TWILIO_AUTH_TOKEN=your_auth_token_here"
    exit 1
fi

# Install dependencies if needed
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Create uploads directory if it doesn't exist
mkdir -p uploads

echo ""
echo "🚀 Starting Flask application..."
echo "   The app will be available at: http://localhost:5002"
echo ""
echo "📡 Next steps:"
echo "   1. In another terminal, run: ngrok http 5002"
echo "   2. Copy the ngrok forwarding URL"
echo "   3. Configure it in Twilio console as: https://your-ngrok-url.ngrok.io/message"
echo "   4. Send a WhatsApp message with an image to test!"
echo ""

# Start Flask
export FLASK_APP=app.py
export FLASK_ENV=development
flask run
