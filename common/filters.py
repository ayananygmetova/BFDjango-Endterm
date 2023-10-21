from django_filters.rest_framework import FilterSet as DFFilterSet
from django_filters.rest_framework import DjangoFilterBackend


class FilterSet(DFFilterSet):

    def __init__(self, *args, **kwargs):
        self.request = kwargs['request']
        super().__init__(*args, **kwargs)


class FilterBackend(DjangoFilterBackend):

    def get_filterset_kwargs(self, request, queryset, view):
        kwargs = super().get_filterset_kwargs(request, queryset, view)

        if hasattr(view, 'get_filterset_kwargs'):
            kwargs.update(request=request)

        return kwargs