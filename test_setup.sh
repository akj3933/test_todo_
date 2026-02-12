#!/bin/bash
# Test script to verify the Django setup works

set -e

echo "=== Testing Django Backend Setup ==="
cd backend

echo "1. Checking Python syntax..."
python -m py_compile config/settings.py
python -m py_compile config/celery.py
python -m py_compile tasks/models.py
echo "✓ Python syntax OK"

echo ""
echo "2. Checking Django configuration..."
python manage.py check
echo "✓ Django configuration OK"

echo ""
echo "3. Verifying migrations..."
python manage.py makemigrations --check --dry-run
echo "✓ Migrations are up to date"

echo ""
echo "=== Testing Bot Setup ==="
cd ../bot

echo "4. Checking bot syntax..."
python -m py_compile main.py
python -m py_compile api_client.py
python -m py_compile config.py
echo "✓ Bot syntax OK"

echo ""
echo "=== All Tests Passed ==="
