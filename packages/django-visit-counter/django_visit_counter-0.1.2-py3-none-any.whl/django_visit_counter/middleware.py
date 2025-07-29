# django_visit_counter/middleware.py
from django.core.cache import cache

class GlobalVisitCountMiddleware:
    """
    Compte toutes les visites (toutes pages) globalement dans le cache.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        count = cache.get('global_visit_count', 0)
        cache.set('global_visit_count', count + 1, None)
        response = self.get_response(request)
        return response
