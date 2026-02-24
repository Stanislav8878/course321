from rest_framework.pagination import PageNumberPagination


class DefaultPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class FivePerPagePagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 100


class HabitPagination(DefaultPagination):
    """
    Alias for backward compatibility:
    - habits.pagination.HabitPagination
    - habits.pagination.DefaultPagination
    """
    pass
