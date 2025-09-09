from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
import redis
from django.conf import settings


def health_check(request):
    """Comprehensive health check endpoint"""
    health_status = {
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'services': {}
    }
    
    try:
        # Database health
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            health_status['services']['database'] = 'healthy'
    except Exception as e:
        health_status['services']['database'] = f'unhealthy: {str(e)}'
        health_status['status'] = 'unhealthy'
    
    try:
        # Redis health
        cache.set('health_check', 'test', 30)
        if cache.get('health_check') == 'test':
            health_status['services']['redis'] = 'healthy'
        else:
            raise Exception('Cache test failed')
    except Exception as e:
        health_status['services']['redis'] = f'unhealthy: {str(e)}'
        health_status['status'] = 'unhealthy'
    
    # Add more service checks as needed
    
    status_code = 200 if health_status['status'] == 'healthy' else 503
    return JsonResponse(health_status, status=status_code)
