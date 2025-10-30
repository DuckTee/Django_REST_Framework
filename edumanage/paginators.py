from rest_framework.pagination import PageNumberPagination

class StandardResultsSetPagination(PageNumberPagination):
    """
    Стандартная пагинация для списков курсов и уроков
    """
    page_size = 10  # Количество элементов на странице по умолчанию
    page_size_query_param = 'page_size'  # Параметр для изменения размера страницы через URL
    max_page_size = 100  # Максимальный размер страницы (ограничение)