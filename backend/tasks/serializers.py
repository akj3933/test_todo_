from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Task, Category


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class CategorySerializer(serializers.ModelSerializer):
    tasks_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'tasks_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_tasks_count(self, obj):
        return obj.tasks.count()


class TaskSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)
    categories = CategorySerializer(many=True, read_only=True)
    category_ids = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False
    )
    is_overdue = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'user', 'user_id',
            'categories', 'category_ids', 'status', 'priority',
            'due_date', 'notification_sent', 'is_overdue',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'notification_sent', 'created_at', 'updated_at']

    def get_is_overdue(self, obj):
        return obj.is_overdue()

    def create(self, validated_data):
        category_ids = validated_data.pop('category_ids', [])
        task = Task.objects.create(**validated_data)
        if category_ids:
            task.categories.set(Category.objects.filter(id__in=category_ids))
        return task

    def update(self, instance, validated_data):
        category_ids = validated_data.pop('category_ids', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if category_ids is not None:
            instance.categories.set(Category.objects.filter(id__in=category_ids))
        
        return instance


class TaskListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views."""
    categories = serializers.StringRelatedField(many=True)
    user_username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'user_username', 'categories',
            'status', 'priority', 'due_date', 'created_at'
        ]
