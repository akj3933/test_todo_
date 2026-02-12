import os
from decouple import config

# Telegram Bot Token
BOT_TOKEN = config('TELEGRAM_BOT_TOKEN')

# Django API Configuration
API_BASE_URL = config('DJANGO_API_URL', default='http://localhost:8000/api')
