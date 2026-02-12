from django.contrib import admin
from .models import Task, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'created_at', 'updated_at']
    search_fields = ['name', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'user', 'status', 'priority', 'due_date', 'created_at']
    list_filter = ['status', 'priority', 'created_at', 'due_date']
    search_fields = ['title', 'description', 'user__username']
    filter_horizontal = ['categories']
    readonly_fields = ['id', 'created_at', 'updated_at', 'notification_sent']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'title', 'description', 'user')
        }),
        ('Task Details', {
            'fields': ('status', 'priority', 'categories', 'due_date')
        }),
        ('Metadata', {
            'fields': ('notification_sent', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

