from rest_framework.filters import BaseFilterBackend
from webapp.utils import request_to_synagogue


class FilterSynagogueBackend(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        return queryset.filter(synagogue=request_to_synagogue(request))
