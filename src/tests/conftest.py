"""
Test fixtures for the Language Learning Platform.
"""
import pytest
from django.contrib.auth import get_user_model

from lingua_dictionary.models import DictionaryEntry
from lingua_languages.models import Language, LanguagePair
from lingua_learning.models import StudySession, StudySessionEntry, UserProgress


@pytest.fixture
def language_japanese():
    """Japanese language fixture."""
    return Language.objects.get(code="ja", name="Japanese")


@pytest.fixture
def language_russian():
    """Russian language fixture."""
    return Language.objects.get(code="ru", name="Russian")


@pytest.fixture
def language_pair_ja_ru(language_japanese, language_russian):
    """Japanese-Russian language pair fixture."""
    return LanguagePair.objects.get(
        source_language=language_japanese,
        target_language=language_russian
    )


@pytest.fixture
def dictionary_entries(language_japanese, language_russian):
    """Dictionary entries for Japanese-Russian pair."""
    return DictionaryEntry.objects.filter(
        source_language=language_japanese,
        target_language=language_russian
    )


@pytest.fixture
def user(dj_db_setup):
    """Test user fixture."""
    return get_user_model().objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123"
    )


@pytest.fixture
def authenticated_user(user):
    """Authenticated user fixture."""
    from django.test import RequestFactory
    factory = RequestFactory()
    request = factory.get("/api/user-progress/")
    request.user = user
    return user


@pytest.fixture
def study_session(user):
    """Study session fixture."""
    entries = DictionaryEntry.objects.all()[:5]
    session = StudySession.objects.create(user=user)
    session.dictionary_entries.set(entries)
    return session


@pytest.fixture
def study_session_entry(study_session, dictionary_entries):
    """Study session entry fixture."""
    entry = dictionary_entries.first()
    return StudySessionEntry.objects.create(
        study_session=study_session,
        dictionary_entry=entry,
        is_correct=True,
        response_time_ms=1500
    )


@pytest.fixture
def user_progress(user, dictionary_entries):
    """User progress fixture."""
    entry = dictionary_entries.first()
    return UserProgress.objects.create(
        user=user,
        dictionary_entry=entry,
        is_favorited=True,
        is_mastered=False,
        mastery_level=75,
        review_count=3
    )
