import asyncio
import logging
from datetime import datetime

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from api_client import TodoAPIClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


class TaskStates(StatesGroup):
    """States for task creation dialog."""
    entering_title = State()
    entering_description = State()
    selecting_priority = State()
    entering_due_date = State()


async def format_task(task: dict) -> str:
    """Format task information for display."""
    categories = ', '.join(task.get('categories', [])) or 'No categories'
    created = datetime.fromisoformat(task['created_at'].replace('Z', '+00:00'))
    created_str = created.strftime('%Y-%m-%d %H:%M')
    
    status_emoji = {
        'pending': '⏳',
        'in_progress': '🔄',
        'completed': '✅',
        'cancelled': '❌'
    }
    
    priority_emoji = {
        'low': '🟢',
        'medium': '🟡',
        'high': '🟠',
        'urgent': '🔴'
    }
    
    text = f"{status_emoji.get(task.get('status', 'pending'), '❓')} *{task['title']}*\n"
    text += f"📊 Status: {task.get('status', 'N/A')}\n"
    text += f"{priority_emoji.get(task.get('priority', 'medium'), '⚪')} Priority: {task.get('priority', 'N/A')}\n"
    text += f"🏷 Categories: {categories}\n"
    text += f"📅 Created: {created_str}\n"
    
    if task.get('description'):
        text += f"📝 Description: {task['description']}\n"
    
    if task.get('due_date'):
        due_date = datetime.fromisoformat(task['due_date'].replace('Z', '+00:00'))
        text += f"⏰ Due: {due_date.strftime('%Y-%m-%d %H:%M')}\n"
    
    return text


@dp.message(CommandStart())
async def cmd_start(message: Message):
    """Handle /start command."""
    await message.answer(
        "👋 Welcome to ToDo List Bot!\n\n"
        "Available commands:\n"
        "/list - View your tasks\n"
        "/add - Add a new task\n"
        "/help - Show help message"
    )


@dp.message(Command("help"))
async def cmd_help(message: Message):
    """Handle /help command."""
    await message.answer(
        "🤖 *ToDo List Bot Help*\n\n"
        "Commands:\n"
        "/start - Start the bot\n"
        "/list - View all your tasks with categories and creation dates\n"
        "/add - Add a new task through interactive dialog\n"
        "/help - Show this help message\n\n"
        "When adding a task, you'll be guided through a step-by-step process to enter all details.",
        parse_mode="Markdown"
    )


@dp.message(Command("list"))
async def cmd_list_tasks(message: Message):
    """Handle /list command - show user's tasks."""
    user_id = message.from_user.id
    
    async with TodoAPIClient() as api:
        tasks = await api.get_tasks(user_id)
    
    if not tasks:
        await message.answer("📝 You don't have any tasks yet. Use /add to create one!")
        return
    
    response = f"📋 *Your Tasks ({len(tasks)}):*\n\n"
    
    for i, task in enumerate(tasks, 1):
        response += f"{i}. " + await format_task(task) + "\n"
    
    # Split message if too long
    if len(response) > 4000:
        chunks = [response[i:i+4000] for i in range(0, len(response), 4000)]
        for chunk in chunks:
            await message.answer(chunk, parse_mode="Markdown")
    else:
        await message.answer(response, parse_mode="Markdown")


@dp.message(Command("add"))
async def cmd_add_task(message: Message, state: FSMContext):
    """Start task creation process."""
    await state.set_state(TaskStates.entering_title)
    await message.answer(
        "🆕 *Creating a new task*\n\n"
        "Please enter the task title:",
        parse_mode="Markdown"
    )


@dp.message(TaskStates.entering_title)
async def process_title(message: Message, state: FSMContext):
    """Process task title input."""
    await state.update_data(title=message.text)
    await state.set_state(TaskStates.entering_description)
    await message.answer(
        "📝 Enter task description (or send '-' to skip):"
    )


@dp.message(TaskStates.entering_description)
async def process_description(message: Message, state: FSMContext):
    """Process task description input."""
    description = message.text if message.text != '-' else ''
    await state.update_data(description=description)
    await state.set_state(TaskStates.selecting_priority)
    
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="🟢 Low"), types.KeyboardButton(text="🟡 Medium")],
            [types.KeyboardButton(text="🟠 High"), types.KeyboardButton(text="🔴 Urgent")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    
    await message.answer(
        "📊 Select task priority:",
        reply_markup=keyboard
    )


@dp.message(TaskStates.selecting_priority)
async def process_priority(message: Message, state: FSMContext):
    """Process priority selection."""
    priority_map = {
        '🟢 Low': 'low',
        '🟡 Medium': 'medium',
        '🟠 High': 'high',
        '🔴 Urgent': 'urgent'
    }
    
    priority = priority_map.get(message.text, 'medium')
    await state.update_data(priority=priority)
    await state.set_state(TaskStates.entering_due_date)
    
    await message.answer(
        "⏰ Enter due date and time (format: YYYY-MM-DD HH:MM) or send '-' to skip:",
        reply_markup=types.ReplyKeyboardRemove()
    )


@dp.message(TaskStates.entering_due_date)
async def process_due_date(message: Message, state: FSMContext):
    """Process due date input."""
    due_date = None
    if message.text != '-':
        try:
            # Parse the date
            due_date = datetime.strptime(message.text, '%Y-%m-%d %H:%M').isoformat()
        except ValueError:
            await message.answer(
                "❌ Invalid date format. Please use YYYY-MM-DD HH:MM or send '-' to skip:"
            )
            return
    
    await state.update_data(due_date=due_date)
    
    # Create the task
    data = await state.get_data()
    user_id = message.from_user.id
    
    task_data = {
        'title': data['title'],
        'description': data.get('description', ''),
        'user_id': user_id,
        'priority': data.get('priority', 'medium'),
        'status': 'pending',
    }
    
    if due_date:
        task_data['due_date'] = due_date
    
    async with TodoAPIClient() as api:
        result = await api.create_task(task_data)
    
    if result:
        await message.answer(
            f"✅ Task created successfully!\n\n" + await format_task(result),
            parse_mode="Markdown"
        )
    else:
        await message.answer(
            "❌ Failed to create task. Please try again later."
        )
    
    await state.clear()


async def main():
    """Start the bot."""
    logger.info("Starting bot...")
    
    # Start polling
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
