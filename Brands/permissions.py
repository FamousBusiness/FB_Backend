from rest_framework import permissions
from Brands.models import BrandBusinessPage



class IsBrandOwnerPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            brand_owner = BrandBusinessPage.objects.get(owner=request.user)
            return True
        except BrandBusinessPage.DoesNotExist:
            return False