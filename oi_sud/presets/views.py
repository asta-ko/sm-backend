from rest_framework import permissions
from rest_framework import viewsets

from .serializers import PresetCategorySerializer, PresetSerializer


class FilterPresetViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    serializer_class = PresetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.request.user.presets.all()


class FilterPresetCategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    def get_queryset(self):
        return self.request.user.preset_categories.all()

    serializer_class = PresetCategorySerializer
    permission_classes = [permissions.IsAuthenticated]
