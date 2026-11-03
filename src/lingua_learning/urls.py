from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import StudySessionEntryViewSet, StudySessionViewSet, UserProgressViewSet

router = DefaultRouter()
router.register(r"user-progress", UserProgressViewSet, basename="user-progress")
router.register(r"study-sessions", StudySessionViewSet, basename="study-session")
router.register(r"study-session-entries", StudySessionEntryViewSet, basename="study-session-entry")

urlpatterns = [
    path("", include(router.urls)),
]
