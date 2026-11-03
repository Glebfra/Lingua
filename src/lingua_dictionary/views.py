from django.db.models import Q
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import DictionaryEntry
from .serializers import DictionaryEntryCreateSerializer, DictionaryEntrySerializer


class DictionaryEntryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for dictionary entries.
    
    Supports:
        - List dictionary entries
        - Retrieve dictionary entry details
        - Create new dictionary entry
        - Update dictionary entry
        - Delete dictionary entry
    
    Query parameters:
        - source_language: Filter by source language code
        - target_language: Filter by target language code
        - search: Search by source text or target text
        - part_of_speech: Filter by part of speech
    """
    queryset = DictionaryEntry.objects.all()
    serializer_class = DictionaryEntrySerializer
    permission_classes = []  # Public access
    
    def get_serializer_class(self): # type: ignore
        """Use different serializers for create/update operations."""
        if self.action in ["create", "update", "partial_update"]:
            return DictionaryEntryCreateSerializer
        return self.serializer_class
    
    def get_queryset(self):
        """Apply filters based on query parameters."""
        queryset = super().get_queryset()
        
        # Filter by source language
        source_language = self.request.query_params.get("source_language", None)
        if source_language:
            queryset = queryset.filter(source_language__code=source_language)
        
        # Filter by target language
        target_language = self.request.query_params.get("target_language", None)
        if target_language:
            queryset = queryset.filter(target_language__code=target_language)
        
        # Search by source text or target text
        search = self.request.query_params.get("search", None)
        if search:
            queryset = queryset.filter(
                Q(source_text__icontains=search) | Q(target_text__icontains=search)
            )
        
        # Filter by part of speech
        part_of_speech = self.request.query_params.get("part_of_speech", None)
        if part_of_speech:
            queryset = queryset.filter(part_of_speech=part_of_speech)
        
        return queryset
    
    def retrieve(self, request, *args, **kwargs):
        """Retrieve a dictionary entry."""
        serializer = self.get_serializer(self.get_object())
        return Response(serializer.data)
    
    @action(detail=False, methods=["get"])
    def recent(self, request):
        """Get recently added dictionary entries."""
        limit = request.query_params.get("limit", 10)
        try:
            limit = int(limit)
        except ValueError:
            limit = 10
        
        entries = DictionaryEntry.objects.order_by("-created_at")[:limit]
        serializer = self.get_serializer(entries, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=["get"])
    def popular(self, request):
        """Get popular dictionary entries (most reviewed)."""
        limit = request.query_params.get("limit", 20)
        try:
            limit = int(limit)
        except ValueError:
            limit = 20
        
        entries = DictionaryEntry.objects.annotate(
            review_count=models__count("userprogress") # type: ignore
        ).order_by("-review_count")[:limit]
        serializer = self.get_serializer(entries, many=True)
        return Response(serializer.data)
