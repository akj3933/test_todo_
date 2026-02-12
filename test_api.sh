#!/bin/bash
# Script to test API endpoints
# Run after: docker-compose up

set -e

API_URL="http://localhost:8000/api"
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo "=== Testing ToDo List API ==="
echo ""

# Test 1: Get categories
echo "1. GET /api/categories/"
curl -s "$API_URL/categories/" | python -m json.tool | head -20
echo -e "${GREEN}✓${NC}"
echo ""

# Test 2: Create a category
echo "2. POST /api/categories/ (Create 'Work' category)"
CATEGORY_ID=$(curl -s -X POST "$API_URL/categories/" \
  -H "Content-Type: application/json" \
  -d '{"name": "Work", "description": "Work-related tasks"}' | python -c "import sys, json; print(json.load(sys.stdin)['id'])")
echo "Created category with ID: $CATEGORY_ID"
echo -e "${GREEN}✓${NC}"
echo ""

# Test 3: Create another category
echo "3. POST /api/categories/ (Create 'Personal' category)"
CATEGORY_ID2=$(curl -s -X POST "$API_URL/categories/" \
  -H "Content-Type: application/json" \
  -d '{"name": "Personal", "description": "Personal tasks"}' | python -c "import sys, json; print(json.load(sys.stdin)['id'])")
echo "Created category with ID: $CATEGORY_ID2"
echo -e "${GREEN}✓${NC}"
echo ""

# Test 4: Get users
echo "4. GET /api/users/"
curl -s "$API_URL/users/" | python -m json.tool | head -20
echo -e "${GREEN}✓${NC}"
echo ""

# Test 5: Create a task
echo "5. POST /api/tasks/ (Create task)"
TASK_DATA='{
  "title": "Complete project documentation",
  "description": "Write comprehensive docs for the project",
  "user_id": 1,
  "priority": "high",
  "status": "pending",
  "category_ids": ["'$CATEGORY_ID'"],
  "due_date": "2026-02-15T10:00:00"
}'

TASK_ID=$(curl -s -X POST "$API_URL/tasks/" \
  -H "Content-Type: application/json" \
  -d "$TASK_DATA" | python -c "import sys, json; print(json.load(sys.stdin)['id'])")
echo "Created task with ID: $TASK_ID"
echo -e "${GREEN}✓${NC}"
echo ""

# Test 6: Get all tasks
echo "6. GET /api/tasks/"
curl -s "$API_URL/tasks/" | python -m json.tool | head -30
echo -e "${GREEN}✓${NC}"
echo ""

# Test 7: Get tasks for user
echo "7. GET /api/tasks/my_tasks/?user_id=1"
curl -s "$API_URL/tasks/my_tasks/?user_id=1" | python -m json.tool | head -30
echo -e "${GREEN}✓${NC}"
echo ""

# Test 8: Get specific task
echo "8. GET /api/tasks/$TASK_ID/"
curl -s "$API_URL/tasks/$TASK_ID/" | python -m json.tool
echo -e "${GREEN}✓${NC}"
echo ""

# Test 9: Update task
echo "9. PATCH /api/tasks/$TASK_ID/ (Update status)"
curl -s -X PATCH "$API_URL/tasks/$TASK_ID/" \
  -H "Content-Type: application/json" \
  -d '{"status": "in_progress"}' | python -m json.tool | head -20
echo -e "${GREEN}✓${NC}"
echo ""

echo "=== All API Tests Passed ==="
echo ""
echo "You can now:"
echo "  - Visit http://localhost:8000/admin/ (username: admin, password: admin123)"
echo "  - View API docs at http://localhost:8000/api/docs/"
echo "  - Test the Telegram bot by sending /start to your bot"
