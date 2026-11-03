from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .models import Language, LanguagePair
from .serializers import LanguagePairSerializer, LanguageSerializer


class LanguageViewSet(viewsets.ModelViewSet):
    """
    API endpoint for languages.
    
    Supports:
        - List all languages
        - Retrieve language details
        - Create new language
        - Update language
        - Delete language
    """
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer
    permission_classes = [AllowAny,]
    
    @action(detail=False, methods=["get"])
    def pairs(self, request):
        """Get all supported language pairs."""
        pairs = LanguagePair.objects.all()
        serializer = LanguagePairSerializer(pairs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=["get"])
    def available_pairs(self, request):
        """Get available language pairs for the user's preference."""
        # This could be filtered based on user settings in future
        pairs = LanguagePair.objects.all()
        serializer = LanguagePairSerializer(pairs, many=True)
        return Response(serializer.data)


class LanguagePairViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for language pairs.
    
    Supports:
        - List all language pairs
        - Retrieve language pair details
    """
    queryset = LanguagePair.objects.all()
    serializer_class = LanguagePairSerializer
    permission_classes = [AllowAny,]
