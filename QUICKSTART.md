# Quick Start Guide

## Prerequisites
- Docker and Docker Compose installed
- Telegram Bot Token (get it from [@BotFather](https://t.me/botfather))

## Setup Steps

### 1. Get Telegram Bot Token
1. Open Telegram and find [@BotFather](https://t.me/botfather)
2. Send `/newbot` command
3. Follow the instructions to create your bot
4. Copy the bot token you receive

### 2. Configure Environment
```bash
# Edit .env file
nano .env

# Update this line with your bot token:
TELEGRAM_BOT_TOKEN=your-actual-bot-token-here
```

### 3. Start All Services
```bash
docker-compose up --build
```

Wait for all services to start (about 1-2 minutes).

### 4. Access the Application

#### Django Admin
- URL: http://localhost:8000/admin/
- Username: `admin`
- Password: `admin123`

#### API Documentation
- URL: http://localhost:8000/api/docs/

#### Telegram Bot
1. Find your bot in Telegram
2. Send `/start` command
3. Use `/help` to see available commands

## Test the API

### Create a Category
```bash
curl -X POST http://localhost:8000/api/categories/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Work",
    "description": "Work-related tasks"
  }'
```

### Create a Task
```bash
curl -X POST http://localhost:8000/api/tasks/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Complete project documentation",
    "description": "Write comprehensive docs",
    "user_id": 1,
    "priority": "high",
    "status": "pending"
  }'
```

### Get All Tasks
```bash
curl http://localhost:8000/api/tasks/ | python -m json.tool
```

## Test the Bot

1. Open your bot in Telegram
2. Send `/list` to see your tasks
3. Send `/add` to create a new task
4. Follow the interactive dialog to fill in task details

## Common Issues

### Bot not responding
- Check bot token in `.env` file
- Check bot service logs: `docker-compose logs bot`
- Make sure backend service is running

### Database connection error
- Wait for database to be ready (check with `docker-compose logs db`)
- Restart backend service: `docker-compose restart backend`

### Port already in use
```bash
# Stop conflicting services or change ports in docker-compose.yml
docker-compose down
# Edit ports in docker-compose.yml if needed
docker-compose up
```

## Next Steps

- Explore the [full README](README.md) for detailed documentation
- Run API tests: `./test_api.sh`
- Check Celery logs for scheduled tasks: `docker-compose logs celery`
- Customize settings in `.env` file

## Stop the Application

```bash
# Stop all services
docker-compose down

# Stop and remove all data (including database)
docker-compose down -v
```
