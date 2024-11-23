from rest_framework.pagination import PageNumberPagination



class StoreHomepageProductPagination(PageNumberPagination):
    page_size = 10
    