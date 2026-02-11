"""
Usul Al-Din Educational Telegram Bot
Professional Telegram Bot with Admin Dashboard
Compatible with Render Free Tier Deployment
"""

import os
from pathlib import Path

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent

# Environment Variables
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
PORT = int(os.environ.get("PORT", 8080))
SECRET_KEY = os.environ.get("SECRET_KEY", "your-secret-key-here")

# Validate required environment variables
if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN environment variable is required!")
