from rest_framework.pagination import PageNumberPagination



class StoreHomepageProductPagination(PageNumberPagination):
    page_size = 10
    


class StoreCategoryWiseProductViewSetPagination(PageNumberPagination):
    page_size = 20  # Default page size
    page_size_query_param = 'page_size'  # Allow the client to set the page size in the URL
    max_page_size = 50  # Optional: Set a maximum limit for page size