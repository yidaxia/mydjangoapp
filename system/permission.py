from rest_framework.permissions import BasePermission
from django.core.cache import cache
from .models import Permission


def get_permission_list(user):
    if user.is_superuser:
        perms_list = ['admin']
    else:
        perms = Permission.object.none()
        roles = user.roles.all()
        if roles:
            for i in roles:
                perms = perms | i.perms.all()
        perms_list = perms.values_list('method', flat=True)
        perms_list = list(set(perms_list))
    cache.set(user.username + '__perms', perms_list)
    return perms_list


class RbacPermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user:
            perms = ['visitor']
        else:
            perms = cache.get(request.user.username + '__perms')
        if not perms:
            perms = get_permission_list(request.user)
        if perms:
            if 'admin' in perms:
                return True
            elif not hasattr(view, 'perms_map'):
                return True
            else:
                perms_map = view.perms_map
                _method = request._request.method.lower()
                if perms_map:
                    for key in perms_map:
                        if key == _method or key == '*':
                            if perms_map[key] in perms or perms[key] == '*':
                                return True
                return False
        else:
            return False