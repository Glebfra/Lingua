from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import DictionaryEntryViewSet

router = DefaultRouter()
router.register(r"dictionary-entries", DictionaryEntryViewSet, basename="dictionary-entry")

urlpatterns = [
    path("", include(router.urls)),
]
