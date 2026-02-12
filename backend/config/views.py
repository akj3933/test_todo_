from django.http import JsonResponse
from django.utils import timezone


def health_check(request):
    """Simple health check endpoint."""
    return JsonResponse({
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'timezone': 'America/Adak'
    })
