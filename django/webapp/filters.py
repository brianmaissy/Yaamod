from rest_framework.filters import BaseFilterBackend


class GetFromSynagogueFilterBackend(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        return queryset.filter(pk=view.kwargs['synagogue_pk'])
