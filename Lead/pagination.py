from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response



#### Custom Pagination for Lead
class CustomPaginationForAllLeads(PageNumberPagination):
    page_size = 10  # Set default page size
    page_size_query_param = 'page_size'  # Allow the client to set the page size
    max_page_size = 100  # Set a maximum page size

    def get_paginated_response(self, data):
        """
        Customize the structure of the paginated response.
        """
        return Response({
            'total_leads': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })