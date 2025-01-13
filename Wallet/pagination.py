from rest_framework.pagination import PageNumberPagination



### All user transaction pagination
class AllUserTransactionsPagination(PageNumberPagination):
    page_size = 15
    page_size_query_param = 'page_size'  
    max_page_size = 100 



class CustomPagination(PageNumberPagination):
    page_size = 2
    page_size_query_param = 'page_size'  
    max_page_size = 100 

