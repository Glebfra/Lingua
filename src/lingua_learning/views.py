from typing import override

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import StudySession, StudySessionEntry, UserProgress
from .serializers import StudySessionEntryCreateSerializer, StudySessionEntrySerializer, StudySessionSerializer, UserProgressCreateSerializer, UserProgressSerializer


class UserProgressViewSet(viewsets.ModelViewSet):
    """
    API endpoint for user progress.
    
    Supports:
        - List user progress
        - Retrieve user progress details
        - Create user progress
        - Update user progress
        - Delete user progress
    
    Requires authentication.
    """
    queryset = UserProgress.objects.all()
    serializer_class = UserProgressSerializer
    permission_classes = [IsAuthenticated]

    @override
    def get_queryset(self):
        """Return user's progress entries."""
        return UserProgress.objects.filter(user=self.request.user)

    @override
    def get_serializer_class(self):
        """Use different serializers for create operations."""
        if self.action == "create":
            return UserProgressCreateSerializer
        return self.serializer_class
    
    @action(detail=False, methods=["get"])
    def mastered(self, request):
        """Get all mastered dictionary entries."""
        mastered = UserProgress.objects.filter(
            user=request.user,
            is_mastered=True
        )
        serializer = self.get_serializer(mastered, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=["get"])
    def favorites(self, request):
        """Get all favorited dictionary entries."""
        favorites = UserProgress.objects.filter(
            user=request.user,
            is_favorited=True
        )
        serializer = self.get_serializer(favorites, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=["get"])
    def statistics(self, request):
        """Get user learning statistics."""
        progress = UserProgress.objects.filter(user=request.user)
        
        total_entries = progress.count()
        mastered_entries = progress.filter(is_mastered=True).count()
        favorited_entries = progress.filter(is_favorited=True).count()
        average_mastery = progress.aggregate(avg=models__Avg("mastery_level"))["avg_mastery_level"] # type: ignore
        
        # Get review statistics
        reviews = StudySessionEntry.objects.filter(
            dictionary_entry__in=progress.all()
        )
        total_reviews = reviews.count()
        correct_reviews = reviews.filter(is_correct=True).count()
        
        response = {
            "total_entries": total_entries,
            "mastered_entries": mastered_entries,
            "favorited_entries": favorited_entries,
            "average_mastery": round(average_mastery, 2) if average_mastery else 0,
            "total_reviews": total_reviews,
            "correct_reviews": correct_reviews,
            "accuracy": round((correct_reviews / total_reviews * 100), 2) if total_reviews else 0,
        }
        
        return Response(response)


class StudySessionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for study sessions.
    
    Supports:
        - List study sessions
        - Retrieve study session details
        - Create new study session
        - Update study session
        - Delete study session
    
    Requires authentication.
    """
    queryset = StudySession.objects.all()
    serializer_class = StudySessionSerializer
    permission_classes = [IsAuthenticated]

    @override
    def get_queryset(self):
        """Return the current user's study sessions."""
        return StudySession.objects.filter(user=self.request.user)

    @override
    def get_serializer_class(self):
        """Use different serializers for create operations."""
        if self.action == "create":
            return StudySessionSerializer
        return self.serializer_class
    
    @action(detail=False, methods=["get"])
    def recent(self, request):
        """Get recent study sessions."""
        limit = request.query_params.get("limit", 10)
        try:
            limit = int(limit)
        except ValueError:
            limit = 10
        
        sessions = StudySession.objects.filter(
            user=request.user
        ).order_by("-start_time")[:limit]
        
        serializer = self.get_serializer(sessions, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=["post"])
    def end(self, request, pk=None):
        """End a study session."""
        session = self.get_object()
        session.end_time = request.data.get("end_time")
        session.words_studied = request.data.get("words_studied", session.words_studied)
        session.words_mastered = request.data.get("words_mastered", session.words_mastered)
        session.save()
        
        serializer = self.get_serializer(session)
        return Response(serializer.data)
    
    @action(detail=False, methods=["post"])
    def start(self, request):
        """Start a new study session."""
        dictionary_entry_ids = request.data.get("dictionary_entries", [])
        
        session = StudySession.objects.create(user=request.user)
        session.dictionary_entries.set(dictionary_entry_ids)
        
        serializer = self.get_serializer(session)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class StudySessionEntryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for study session entries.
    
    Supports:
        - List study session entries
        - Retrieve study session entry details
        - Create new study session entry
        - Update study session entry
        - Delete study session entry
    
    Requires authentication.
    """
    queryset = StudySessionEntry.objects.all()
    serializer_class = StudySessionEntrySerializer
    permission_classes = [IsAuthenticated]

    @override
    def get_queryset(self):
        """Return study session entries for the current user's sessions."""
        return StudySessionEntry.objects.filter(
            study_session__user=self.request.user
        )

    @override
    def get_serializer_class(self):
        """Use different serializers for create operations."""
        if self.action == "create":
            return StudySessionEntryCreateSerializer
        return self.serializer_class
    
    @action(detail=False, methods=["get"])
    def recent(self, request):
        """Get recent study session entries."""
        limit = request.query_params.get("limit", 20)
        try:
            limit = int(limit)
        except ValueError:
            limit = 20
        
        entries = StudySessionEntry.objects.filter(
            study_session__user=request.user
        ).order_by("-created_at")[:limit]
        
        serializer = self.get_serializer(entries, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=["post"])
    def mark_correct(self, request, pk=None):
        """Mark a study session entry as correct."""
        entry = self.get_object()
        entry.is_correct = True
        entry.save()
        
        serializer = self.get_serializer(entry)
        return Response(serializer.data)
    
    @action(detail=True, methods=["post"])
    def mark_incorrect(self, request, pk=None):
        """Mark a study session entry as incorrect."""
        entry = self.get_object()
        entry.is_correct = False
        entry.save()
        
        serializer = self.get_serializer(entry)
        return Response(serializer.data)
