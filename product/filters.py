from django.db.models import Q
from django_filters import rest_framework as filter


class ProductFilterSet(filter.FilterSet):
    price_range_max = filter.NumberFilter('price', lookup_expr='lte')
    price_range_min = filter.NumberFilter('price', lookup_expr='gte')
    q = filter.CharFilter(method='filter_search', distinct=True)
    ordering = filter.OrderingFilter(fields=('views', 'price', 'created'))

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(
                Q(name__icontains=value) |
                Q(seller__username__icontains=value) |
                Q(category__name__icontains=value)
            )
        )
