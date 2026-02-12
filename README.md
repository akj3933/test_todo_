# ToDo List - Django + Telegram Bot

Комплексное приложение для управления задачами (ToDo List) с Django backend, Telegram ботом и Docker.

## 🚀 Быстрый старт

```bash
# 1. Клонируйте репозиторий
git clone <repository-url>
cd test_todo_

# 2. Настройте Telegram Bot Token в .env
# Получите токен у @BotFather в Telegram
nano .env  # Замените TELEGRAM_BOT_TOKEN=your-bot-token-here

# 3. Запустите все сервисы
docker-compose up --build

# 4. Готово! Откройте браузер:
# - Admin: http://localhost:8000/admin/ (admin/admin123)
# - API Docs: http://localhost:8000/api/docs/
# - Найдите бота в Telegram и отправьте /start
```

## Архитектура решения

### Компоненты системы

1. **Django Backend** - основной сервис управления задачами
   - RESTful API для CRUD операций с задачами и категориями
   - Административный интерфейс
   - Интеграция с PostgreSQL
   - Настроена временная зона America/Adak

2. **Celery + Redis** - система фоновых задач и уведомлений
   - Периодическая проверка дедлайнов задач (каждые 5 минут)
   - Отправка уведомлений при наступлении срока выполнения

3. **Telegram Bot (Aiogram)** - интерфейс пользователя
   - Просмотр задач с категориями и датами создания
   - Создание задач через диалоговое взаимодействие
   - Связь с Django через REST API

4. **PostgreSQL** - база данных
5. **Redis** - брокер сообщений для Celery
6. **Docker Compose** - оркестрация всех сервисов

### Особенности реализации

#### Кастомная стратегия первичных ключей
Согласно требованиям, для основных сущностей (Task, Category) не используются:
- UUID
- random модуль
- стандартные функции PostgreSQL
- целочисленные инкременты

Реализована собственная функция генерации ID на основе:
- Временной метки (timestamp в микросекундах)
- Хеширования SHA-256
- Префиксов для различения типов сущностей

```python
def generate_custom_id(prefix=''):
    timestamp = str(int(time.time() * 1000000))
    data = f"{prefix}{timestamp}{id(object())}"
    hash_value = hashlib.sha256(data.encode()).hexdigest()[:16]
    return f"{prefix}{timestamp[-12:]}{hash_value}"
```

#### API Endpoints

- `GET /api/tasks/` - список всех задач
- `POST /api/tasks/` - создание задачи
- `GET /api/tasks/{id}/` - детали задачи
- `PUT /api/tasks/{id}/` - обновление задачи
- `DELETE /api/tasks/{id}/` - удаление задачи
- `GET /api/tasks/my_tasks/?user_id={id}` - задачи пользователя
- `GET /api/tasks/overdue/` - просроченные задачи
- `GET /api/categories/` - список категорий
- `POST /api/categories/` - создание категории

#### Telegram Bot команды

- `/start` - приветствие и список команд
- `/help` - справка по командам
- `/list` - показать все задачи пользователя с категориями и датами
- `/add` - создать новую задачу через интерактивный диалог

## Инструкция по запуску

### Предварительные требования

- Docker
- Docker Compose
- Telegram Bot Token (получить у [@BotFather](https://t.me/botfather))

### Шаги запуска

1. **Клонируйте репозиторий**
```bash
git clone <repository-url>
cd test_todo_
```

2. **Настройте переменные окружения**

Отредактируйте файл `.env`:
```bash
# Обязательно измените эти параметры!
SECRET_KEY=your-secret-key-here
TELEGRAM_BOT_TOKEN=your-bot-token-from-botfather

# Остальные параметры можно оставить по умолчанию
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,backend

DB_NAME=todolist
DB_USER=todouser
DB_PASSWORD=todopassword
DB_HOST=db
DB_PORT=5432

REDIS_URL=redis://redis:6379/0
DJANGO_API_URL=http://backend:8000/api
```

3. **Запустите все сервисы**
```bash
docker-compose up --build
```

При первом запуске автоматически создастся тестовый суперпользователь:
- Username: `admin`
- Password: `admin123`

4. **Готово! Сервисы доступны по адресам:**
   - Django Admin: http://localhost:8000/admin/
   - API Documentation: http://localhost:8000/api/docs/
   - API Root: http://localhost:8000/api/
   - Telegram Bot: найдите своего бота в Telegram

5. **(Опционально) Протестируйте API**
```bash
# В отдельном терминале
./test_api.sh
```

### Остановка сервисов
```bash
docker-compose down
```

### Остановка и удаление всех данных
```bash
docker-compose down -v
```

## Тестирование

### Локальное тестирование (без Docker)
Перед запуском Docker можно протестировать синтаксис и конфигурацию:
```bash
./test_setup.sh
```

### Тестирование API (после запуска Docker)
После запуска сервисов с помощью docker-compose, можно протестировать API:
```bash
./test_api.sh
```

Этот скрипт:
- Создаст тестовые категории
- Создаст тестовые задачи
- Протестирует все основные API endpoints
- Покажет примеры использования API

## Использование

### Django Admin
1. Откройте http://localhost:8000/admin/
2. Войдите используя тестового суперпользователя:
   - Username: `admin`
   - Password: `admin123`
3. Управляйте задачами и категориями через интерфейс

### API
Документация API доступна по адресу http://localhost:8000/api/docs/ (Swagger UI)

Пример создания задачи через API:
```bash
curl -X POST http://localhost:8000/api/tasks/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Task",
    "description": "Task description",
    "user_id": 1,
    "priority": "high",
    "status": "pending"
  }'
```

### Telegram Bot
1. Найдите бота в Telegram по имени пользователя
2. Отправьте команду `/start`
3. Используйте команды для работы с задачами:
   - `/list` - посмотреть свои задачи
   - `/add` - создать новую задачу

## Полезные команды Docker

### Просмотр логов
```bash
# Все сервисы
docker-compose logs -f

# Конкретный сервис
docker-compose logs -f backend
docker-compose logs -f bot
docker-compose logs -f celery
```

### Выполнение команд Django
```bash
# Создать миграции
docker-compose exec backend python manage.py makemigrations

# Применить миграции
docker-compose exec backend python manage.py migrate

# Создать суперпользователя вручную
docker-compose exec backend python manage.py createsuperuser

# Запустить Django shell
docker-compose exec backend python manage.py shell
```

### Перезапуск сервисов
```bash
# Перезапустить один сервис
docker-compose restart backend

# Пересобрать и перезапустить
docker-compose up --build -d backend
```

### Очистка
```bash
# Остановить и удалить контейнеры, но сохранить данные
docker-compose down

# Удалить всё, включая volumes (БД будет очищена!)
docker-compose down -v

# Удалить неиспользуемые образы
docker system prune -a
```

## Учетные данные по умолчанию

### Django Admin
- URL: http://localhost:8000/admin/
- Username: `admin`
- Password: `admin123`

### PostgreSQL
- Host: `localhost` (или `db` внутри Docker)
- Port: `5432`
- Database: `todolist`
- Username: `todouser`
- Password: `todopassword`

### Тестовый пользователь
- Username: `testuser`
- Password: `test123`
- User ID: 2 (используйте для тестирования API)

## Структура проекта

```
test_todo_/
├── backend/                 # Django приложение
│   ├── config/             # Настройки Django
│   │   ├── settings.py     # Основные настройки
│   │   ├── celery.py       # Конфигурация Celery
│   │   └── urls.py         # URL маршруты
│   ├── tasks/              # Приложение задач
│   │   ├── models.py       # Модели Task и Category
│   │   ├── serializers.py  # DRF сериализаторы
│   │   ├── views.py        # API views
│   │   ├── admin.py        # Django Admin
│   │   ├── tasks.py        # Celery задачи
│   │   └── urls.py         # URL приложения
│   ├── Dockerfile
│   ├── requirements.txt
│   └── manage.py
├── bot/                    # Telegram бот
│   ├── main.py            # Основной файл бота
│   ├── api_client.py      # Клиент для Django API
│   ├── config.py          # Конфигурация бота
│   ├── Dockerfile
│   └── requirements.txt
├── docker-compose.yml      # Оркестрация сервисов
├── .env                    # Переменные окружения
├── .env.example           # Пример переменных окружения
├── test_setup.sh          # Скрипт проверки настроек
├── test_api.sh            # Скрипт тестирования API
└── README.md              # Этот файл
```

## Celery - фоновые задачи и уведомления

### Как это работает
Celery Beat запускает задачу `check_task_deadlines` каждые 5 минут. Эта задача:
1. Находит задачи с приближающимся дедлайном (в течение 30 минут)
2. Находит просроченные задачи
3. Отправляет уведомления (логирование) для каждой найденной задачи
4. Помечает задачи как уведомленные (`notification_sent=True`)

### Просмотр задач Celery
```bash
# Логи Celery worker
docker-compose logs -f celery

# Логи Celery beat (планировщик)
docker-compose logs -f celery-beat
```

### Запуск задачи вручную
```bash
# Войти в Django shell
docker-compose exec backend python manage.py shell

# Выполнить в shell:
from tasks.tasks import check_task_deadlines
result = check_task_deadlines.delay()
print(result.get())
```

### Управление периодическими задачами
Периодические задачи можно настроить через Django Admin:
1. Перейдите в http://localhost:8000/admin/
2. Найдите раздел "Periodic Tasks"
3. Добавьте или измените расписание задач

## Трудности и решения

### 1. Кастомные первичные ключи
**Трудность:** Требование не использовать UUID, random, функции PostgreSQL и auto-increment.

**Решение:** Реализована функция `generate_custom_id()`, которая создает уникальные идентификаторы на основе:
- Timestamp в микросекундах для временной уникальности
- Python `id(object())` для дополнительной энтропии
- SHA-256 хеширования для гарантии уникальности
- Префиксов для различения типов сущностей ('task_', 'cat_')

### 2. Временная зона America/Adak
**Трудность:** Необходимость настроить Django на работу в нестандартной временной зоне.

**Решение:** Установлена настройка `TIME_ZONE = 'America/Adak'` в settings.py и `USE_TZ = True` для корректной работы с часовыми поясами. Celery также настроена на использование этой зоны.

### 3. Интеграция Telegram Bot с Django API
**Трудность:** Асинхронный бот должен взаимодействовать с REST API Django.

**Решение:** Создан асинхронный API клиент на базе `aiohttp`, который обрабатывает все запросы к Django в асинхронном режиме. Использованы context managers для управления сессиями.

### 4. Уведомления через Celery
**Трудность:** Периодическая проверка дедлайнов и отправка уведомлений.

**Решение:** 
- Настроен Celery Beat для периодического выполнения задач
- Создана задача `check_task_deadlines()`, которая запускается каждые 5 минут
- Реализована логика проверки задач, которые подходят к дедлайну или уже просрочены
- Добавлено поле `notification_sent` для предотвращения дублирования уведомлений

### 5. Docker Compose зависимости
**Трудность:** Правильный порядок запуска сервисов и их зависимости.

**Решение:** 
- Добавлены health checks для PostgreSQL и Redis
- Настроены depends_on с условиями `service_healthy`
- Backend ждет готовности базы данных перед миграциями
- Celery и бот зависят от backend

### 6. Работа с категориями в Telegram Bot
**Трудность:** Создание задач с категориями через Telegram требует сложного UI.

**Решение:** Упрощенный flow создания задач через последовательные вопросы. В текущей версии категории можно добавлять через API или Django Admin, а бот показывает их при просмотре задач.

## Возможные улучшения

1. **Авторизация** - добавить JWT или OAuth для безопасного доступа к API
2. **Уведомления в Telegram** - интегрировать Celery с ботом для отправки уведомлений напрямую в Telegram
3. **Выбор категорий в боте** - добавить интерактивный выбор категорий при создании задачи
4. **Редактирование задач** - добавить команды для редактирования и удаления задач через бота
5. **Пагинация** - улучшить отображение большого количества задач
6. **Фильтры** - добавить фильтрацию задач по статусу, приоритету, категориям
7. **Тесты** - написать unit и integration тесты
8. **CI/CD** - настроить автоматическое тестирование и развертывание

## Технологический стек

- **Backend**: Django 4.2, Django REST Framework, PostgreSQL
- **Async Tasks**: Celery, Redis, django-celery-beat
- **Bot**: Aiogram 3.4
- **Containerization**: Docker, Docker Compose
- **API Documentation**: drf-spectacular (OpenAPI/Swagger)

## Лицензия

MIT License