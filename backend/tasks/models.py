from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import hashlib
import time


def generate_custom_id(prefix=''):
    """
    Generate a custom ID without using UUID, random, postgres functions, or auto-increment.
    Uses timestamp + counter + hash combination.
    """
    timestamp = str(int(time.time() * 1000000))  # microseconds
    data = f"{prefix}{timestamp}{id(object())}"
    hash_value = hashlib.sha256(data.encode()).hexdigest()[:16]
    return f"{prefix}{timestamp[-12:]}{hash_value}"


class Category(models.Model):
    """
    Category (tag) for organizing tasks.
    """
    id = models.CharField(
        max_length=50, 
        primary_key=True, 
        editable=False,
        default=lambda: generate_custom_id('cat_')
    )
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name


class Task(models.Model):
    """
    Task model for ToDo items.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    id = models.CharField(
        max_length=50,
        primary_key=True,
        editable=False,
        default=lambda: generate_custom_id('task_')
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    categories = models.ManyToManyField(Category, related_name='tasks', blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    due_date = models.DateTimeField(null=True, blank=True)
    notification_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def is_overdue(self):
        """Check if task is overdue."""
        if self.due_date and self.status not in ['completed', 'cancelled']:
            return timezone.now() > self.due_date
        return False

