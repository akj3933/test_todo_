from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


@shared_task
def check_task_deadlines():
    """
    Check for tasks that are due soon or overdue and send notifications.
    This task runs periodically via Celery Beat.
    """
    from .models import Task
    
    now = timezone.now()
    # Check for tasks due within the next 30 minutes that haven't been notified
    upcoming_tasks = Task.objects.filter(
        due_date__lte=now + timedelta(minutes=30),
        due_date__gt=now,
        notification_sent=False,
        status__in=['pending', 'in_progress']
    )
    
    for task in upcoming_tasks:
        send_task_notification.delay(task.id, 'upcoming')
        task.notification_sent = True
        task.save()
    
    # Check for overdue tasks
    overdue_tasks = Task.objects.filter(
        due_date__lt=now,
        notification_sent=False,
        status__in=['pending', 'in_progress']
    )
    
    for task in overdue_tasks:
        send_task_notification.delay(task.id, 'overdue')
        task.notification_sent = True
        task.save()
    
    logger.info(f"Checked deadlines: {upcoming_tasks.count()} upcoming, {overdue_tasks.count()} overdue")
    return {
        'upcoming': upcoming_tasks.count(),
        'overdue': overdue_tasks.count()
    }


@shared_task
def send_task_notification(task_id, notification_type):
    """
    Send notification for a specific task.
    notification_type: 'upcoming' or 'overdue'
    """
    from .models import Task
    
    try:
        task = Task.objects.get(id=task_id)
        
        # Here you would integrate with your notification system
        # For now, we'll just log it
        message = f"Task '{task.title}' for user {task.user.username} is {notification_type}"
        logger.info(f"Notification: {message}")
        
        # In a real system, you might send an email, push notification, or Telegram message here
        return {'status': 'sent', 'task_id': task_id, 'type': notification_type}
    except Task.DoesNotExist:
        logger.error(f"Task {task_id} not found")
        return {'status': 'error', 'message': 'Task not found'}
