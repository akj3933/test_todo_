from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import User
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .models import Task, Category
from .serializers import (
    TaskSerializer, TaskListSerializer,
    CategorySerializer, UserSerializer
)


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing categories.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing tasks.
    """
    queryset = Task.objects.all().select_related('user').prefetch_related('categories')
    serializer_class = TaskSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'user']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'due_date', 'priority']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return TaskListSerializer
        return TaskSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='user_id',
                type=int,
                location=OpenApiParameter.QUERY,
                description='Filter tasks by user ID'
            )
        ]
    )
    @action(detail=False, methods=['get'])
    def my_tasks(self, request):
        """Get tasks for a specific user."""
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response(
                {'error': 'user_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        tasks = self.queryset.filter(user_id=user_id)
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get all overdue tasks."""
        tasks = [task for task in self.queryset if task.is_overdue()]
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing users.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name']
