from rest_framework.pagination import PageNumberPagination


class PostPageNumberPagination(PageNumberPagination):
	page_size = 10


class PostPageNumberPagination1000(PageNumberPagination):
	page_size = 1000