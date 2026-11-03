from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import LanguagePairViewSet, LanguageViewSet


router = DefaultRouter()
router.register(r"languages", LanguageViewSet, basename="language")
router.register(r"language-pairs", LanguagePairViewSet, basename="language-pair")

urlpatterns = [
    path("", include(router.urls)),
]
