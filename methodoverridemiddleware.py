from django.utils.deprecation import MiddlewareMixin
from method_override.middleware import MethodOverrideMiddleware as org

class MethodOverrideMiddleware(org, MiddlewareMixin):
    pass
