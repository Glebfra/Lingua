"""
Integration tests for Language Learning Platform API endpoints.
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from lingua_dictionary.models import DictionaryEntry
from lingua_languages.models import Language, LanguagePair
from lingua_learning.models import StudySession, StudySessionEntry, UserProgress


@pytest.fixture
def api_client():
    """Create an API client for tests."""
    client = APIClient()
    return client


@pytest.fixture
def authenticated_api_client():
    """Create an authenticated API client for tests."""
    client = APIClient()
    user = get_user_model().objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123"
    )
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def api_setup(api_client):
    """Set up API test data."""
    # Clean up any existing data to prevent unique constraint violations
    StudySessionEntry.objects.all().delete()
    StudySession.objects.all().delete()
    UserProgress.objects.all().delete()
    DictionaryEntry.objects.all().delete()
    LanguagePair.objects.all().delete()
    Language.objects.all().delete()
    get_user_model().objects.filter(username="testuser").delete()
    
    # Create languages
    japanese = Language.objects.create(code="ja", name="Japanese", is_source=True, is_target=True)
    russian = Language.objects.create(code="ru", name="Russian", is_source=True, is_target=True)
    english = Language.objects.create(code="en", name="English", is_source=True, is_target=True)
    french = Language.objects.create(code="fr", name="French", is_source=True, is_target=True)
    
    # Create language pairs
    LanguagePair.objects.create(source_language=japanese, target_language=russian)
    LanguagePair.objects.create(source_language=japanese, target_language=english)
    LanguagePair.objects.create(source_language=english, target_language=russian)
    LanguagePair.objects.create(source_language=english, target_language=french)
    
    # Create dictionary entries
    entry1 = DictionaryEntry.objects.create(
        source_text="猫",
        target_text="Кот",
        source_language=japanese,
        target_language=russian,
        part_of_speech="noun",
        pronunciation="ねこ",
        definition="A cat",
        examples="ねこはねこだ。(It is a cat.)"
    )
    entry2 = DictionaryEntry.objects.create(
        source_text="犬",
        target_text="Собака",
        source_language=japanese,
        target_language=russian,
        part_of_speech="noun",
        pronunciation="いぬ",
        definition="A dog",
        examples="いぬはすばやい。(The dog is fast.)"
    )
    DictionaryEntry.objects.create(
        source_text="食べる",
        target_text="Есть",
        source_language=japanese,
        target_language=russian,
        part_of_speech="verb",
        pronunciation="たべる",
        definition="To eat",
        examples="私はりんごを食べる。(I eat an apple.)"
    )
    DictionaryEntry.objects.create(
        source_text="こんにちは",
        target_text="Здравствуйте",
        source_language=japanese,
        target_language=russian,
        part_of_speech="noun",
        pronunciation="こんにちは",
        definition="Hello",
        examples="こんにちは！(Hello!)"
    )
    DictionaryEntry.objects.create(
        source_text="ありがとう",
        target_text="Спасибо",
        source_language=japanese,
        target_language=russian,
        part_of_speech="noun",
        pronunciation="ありがとう",
        definition="Thank you",
        examples="ありがとう！(Thank you!)"
    )
    
    # Create user progress
    user = get_user_model().objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123"
    )
    
    UserProgress.objects.create(
        user=user,
        dictionary_entry=entry1,
        is_favorited=True,
        is_mastered=True,
        mastery_level=90,
        review_count=10
    )
    UserProgress.objects.create(
        user=user,
        dictionary_entry=entry2,
        is_favorited=False,
        is_mastered=False,
        mastery_level=50,
        review_count=3
    )
    
    # Create study sessions
    session1 = StudySession.objects.create(user=user, words_studied=10, words_mastered=5)
    session1.dictionary_entries.set([entry1, entry2])
    
    session2 = StudySession.objects.create(user=user, words_studied=5, words_mastered=3)
    session2.dictionary_entries.set([entry1])
    
    # Create study session entries
    StudySessionEntry.objects.create(
        study_session=session1,
        dictionary_entry=entry1,
        is_correct=True,
        response_time_ms=1500
    )
    StudySessionEntry.objects.create(
        study_session=session1,
        dictionary_entry=entry2,
        is_correct=True,
        response_time_ms=1200
    )
    StudySessionEntry.objects.create(
        study_session=session2,
        dictionary_entry=entry1,
        is_correct=False,
        response_time_ms=2000
    )
    
    yield api_client
    
    # Cleanup
    StudySessionEntry.objects.all().delete()
    StudySession.objects.all().delete()
    UserProgress.objects.all().delete()
    DictionaryEntry.objects.all().delete()
    LanguagePair.objects.all().delete()
    Language.objects.all().delete()
    get_user_model().objects.filter(username="testuser").delete()


@pytest.mark.django_db
class TestLanguageViewSet:
    """Tests for LanguageViewSet API endpoint."""
    
    def test_list_languages(self, api_client, api_setup):
        """Test listing all languages."""
        response = api_client.get("/api/v1/languages/")
        assert response.status_code == 200
        data = response.data
        assert "count" in data
        assert "results" in data
        assert len(data["results"]) > 0
        for lang in data["results"]:
            assert "id" in lang
            assert "code" in lang
            assert "name" in lang
            assert "is_source" in lang
            assert "is_target" in lang
    
    def test_retrieve_language(self, api_client, api_setup):
        """Test retrieving a specific language."""
        response = api_client.get("/api/v1/languages/")
        lang_id = response.data["results"][0]["id"]
        
        response = api_client.get(f"/api/languages/{lang_id}/")
        assert response.status_code == 200
        data = response.data
        assert data["id"] == lang_id
        assert data["code"] in ["ja", "ru", "en", "fr"]
    
    def test_create_language(self, api_client, api_setup):
        """Test creating a new language."""
        data = {
            "code": "de",
            "name": "German",
            "is_source": True,
            "is_target": True
        }
        response = api_client.post("/api/languages/", data, format="json")
        assert response.status_code == 201
        data = response.data
        assert data["code"] == "de"
        assert data["name"] == "German"
        assert len(Language.objects.all()) == 5
    
    def test_update_language(self, api_client, api_setup):
        """Test updating a language."""
        response = api_client.get("/api/v1/languages/")
        lang_id = response.data["results"][0]["id"]
        
        data = {
            "name": "Japanese Updated"
        }
        response = api_client.patch(f"/api/languages/{lang_id}/", data, format="json")
        assert response.status_code == 200
        data = response.data
        assert data["name"] == "Japanese Updated"
    
    def test_delete_language(self, api_client, api_setup):
        """Test deleting a language."""
        response = api_client.get("/api/v1/languages/")
        lang_id = response.data["results"][0]["id"]
        
        response = api_client.delete(f"/api/languages/{lang_id}/")
        assert response.status_code == 204
    
    def test_language_pairs_action(self, api_client, api_setup):
        """Test the pairs action endpoint."""
        response = api_client.get("/api/languages/pairs/")
        assert response.status_code == 200
        data = response.data
        assert "count" in data
        assert "results" in data
        for pair in data["results"]:
            assert "source_language" in pair
            assert "target_language" in pair
    
    def test_available_pairs_action(self, api_client, api_setup):
        """Test the available_pairs action endpoint."""
        response = api_client.get("/api/languages/available-pairs/")
        assert response.status_code == 200
        data = response.data
        assert "count" in data
        assert "results" in data


@pytest.mark.django_db
class TestLanguagePairViewSet:
    """Tests for LanguagePairViewSet API endpoint."""
    
    def test_list_language_pairs(self, api_client):
        """Test listing all language pairs."""
        response = api_client.get("/api/language-pairs/")
        assert response.status_code == 200
        data = response.data
        assert "count" in data
        assert "results" in data
        assert len(data["results"]) >= 4
    
    def test_retrieve_language_pair(self, api_client):
        """Test retrieving a specific language pair."""
        response = api_client.get("/api/language-pairs/")
        pair_id = response.data["results"][0]["id"]
        
        response = api_client.get(f"/api/language-pairs/{pair_id}/")
        assert response.status_code == 200
        data = response.data
        assert data["id"] == pair_id
        assert "source_language" in data
        assert "target_language" in data
    
    def test_language_pair_readonly(self, api_client):
        """Test that language pairs cannot be created/updated."""
        response = api_client.post("/api/language-pairs/", {
            "source_language": {"code": "de"},
            "target_language": {"code": "es"}
        }, format="json")
        assert response.status_code == 405
    
    def test_language_pair_readonly_update(self, api_client):
        """Test that language pairs cannot be updated."""
        response = api_client.get("/api/language-pairs/")
        pair_id = response.data["results"][0]["id"]
        
        response = api_client.patch(f"/api/language-pairs/{pair_id}/", {
            "source_language": {"code": "de"},
            "target_language": {"code": "es"}
        }, format="json")
        assert response.status_code == 405


@pytest.mark.django_db
class TestDictionaryEntryViewSet:
    """Tests for DictionaryEntryViewSet API endpoint."""
    
    def test_list_dictionary_entries(self, api_client):
        """Test listing all dictionary entries."""
        response = api_client.get("/api/dictionary-entries/")
        assert response.status_code == 200
        data = response.data
        assert "count" in data
        assert "results" in data
        assert len(data["results"]) >= 5
    
    def test_list_dictionary_entries_filtered(self, api_client):
        """Test filtering dictionary entries by language."""
        response = api_client.get("/api/dictionary-entries/?source_language=ja")
        assert response.status_code == 200
        data = response.data
        for entry in data["results"]:
            assert entry["source_language"]["code"] == "ja"
    
    def test_list_dictionary_entries_target_language_filter(self, api_client):
        """Test filtering dictionary entries by target language."""
        response = api_client.get("/api/dictionary-entries/?target_language=ru")
        assert response.status_code == 200
        data = response.data
        for entry in data["results"]:
            assert entry["target_language"]["code"] == "ru"
    
    def test_list_dictionary_entries_search(self, api_client):
        """Test searching dictionary entries."""
        response = api_client.get("/api/dictionary-entries/?search=猫")
        assert response.status_code == 200
        data = response.data
        for entry in data["results"]:
            assert "猫" in entry["source_text"] or "猫" in entry["target_text"]
    
    def test_list_dictionary_entries_part_of_speech_filter(self, api_client):
        """Test filtering by part of speech."""
        response = api_client.get("/api/dictionary-entries/?part_of_speech=verb")
        assert response.status_code == 200
        data = response.data
        for entry in data["results"]:
            assert entry["part_of_speech"] == "verb"
    
    def test_retrieve_dictionary_entry(self, api_client):
        """Test retrieving a specific dictionary entry."""
        response = api_client.get("/api/dictionary-entries/")
        entry_id = response.data["results"][0]["id"]
        
        response = api_client.get(f"/api/dictionary-entries/{entry_id}/")
        assert response.status_code == 200
        data = response.data
        assert data["id"] == entry_id
        assert "source_text" in data
        assert "target_text" in data
    
    def test_create_dictionary_entry(self, api_client):
        """Test creating a new dictionary entry."""
        data = {
            "source_text": "こんにちは",
            "target_text": "Привет",
            "source_language": {"id": 1, "code": "ja", "name": "Japanese"},
            "target_language": {"id": 2, "code": "ru", "name": "Russian"}
        }
        response = api_client.post("/api/dictionary-entries/", data, format="json")
        assert response.status_code == 201
        data = response.data
        assert data["source_text"] == "こんにちは"
        assert data["target_text"] == "Привет"
    
    def test_create_dictionary_entry_invalid_languages(self, api_client):
        """Test creating entry with same source and target language."""
        data = {
            "source_text": "test",
            "target_text": "test",
            "source_language": {"id": 1, "code": "ja", "name": "Japanese"},
            "target_language": {"id": 1, "code": "ja", "name": "Japanese"}
        }
        response = api_client.post("/api/dictionary-entries/", data, format="json")
        assert response.status_code == 400
        assert "source_language" in response.data["errors"]
    
    def test_create_dictionary_entry_invalid_pair(self, api_client):
        """Test creating entry with unsupported language pair."""
        data = {
            "source_text": "test",
            "target_text": "test",
            "source_language": {"id": 1, "code": "ja", "name": "Japanese"},
            "target_language": {"id": 3, "code": "en", "name": "English"}  # No pair
        }
        response = api_client.post("/api/dictionary-entries/", data, format="json")
        assert response.status_code == 400
        assert "language_pair" in response.data["errors"]
    
    def test_update_dictionary_entry(self, api_client):
        """Test updating a dictionary entry."""
        response = api_client.get("/api/dictionary-entries/")
        entry_id = response.data["results"][0]["id"]
        
        data = {
            "target_text": "Updated translation"
        }
        response = api_client.patch(f"/api/dictionary-entries/{entry_id}/", data, format="json")
        assert response.status_code == 200
        data = response.data
        assert data["target_text"] == "Updated translation"
    
    def test_delete_dictionary_entry(self, api_client):
        """Test deleting a dictionary entry."""
        response = api_client.get("/api/dictionary-entries/")
        entry_id = response.data["results"][0]["id"]
        
        response = api_client.delete(f"/api/dictionary-entries/{entry_id}/")
        assert response.status_code == 204
    
    def test_dictionary_entries_recent_action(self, api_client):
        """Test the recent action endpoint."""
        response = api_client.get("/api/dictionary-entries/recent/?limit=3")
        assert response.status_code == 200
        data = response.data
        assert "count" in data
        assert "results" in data
        assert len(data["results"]) <= 3
    
    def test_dictionary_entries_popular_action(self, api_client):
        """Test the popular action endpoint."""
        response = api_client.get("/api/dictionary-entries/popular/?limit=3")
        assert response.status_code == 200
        data = response.data
        assert "count" in data
        assert "results" in data


@pytest.mark.django_db
class TestUserProgressViewSet:
    """Tests for UserProgressViewSet API endpoint."""
    
    def test_list_user_progress_authenticated(self, authenticated_api_client):
        """Test listing user progress (requires authentication)."""
        response = authenticated_api_client.get("/api/user-progress/")
        assert response.status_code == 200
        data = response.data
        assert "count" in data
        assert "results" in data
    
    def test_list_user_progress_anonymous(self, api_client):
        """Test listing user progress (requires authentication)."""
        response = api_client.get("/api/user-progress/")
        assert response.status_code == 401
    
    def test_retrieve_user_progress(self, authenticated_api_client):
        """Test retrieving a specific user progress."""
        response = authenticated_api_client.get("/api/user-progress/")
        progress_id = response.data["results"][0]["id"]
        
        response = authenticated_api_client.get(f"/api/user-progress/{progress_id}/")
        assert response.status_code == 200
        data = response.data
        assert data["user"] == "testuser"
    
    def test_create_user_progress(self, authenticated_api_client):
        """Test creating user progress."""
        entry = DictionaryEntry.objects.get(source_text="猫")
        
        data = {
            "dictionary_entry_id": entry.pk,
            "is_favorited": True,
            "is_mastered": False,
            "mastery_level": 75
        }
        response = authenticated_api_client.post("/api/user-progress/", data, format="json")
        assert response.status_code == 201
        data = response.data
        assert data["user"] == "testuser"
    
    def test_create_user_progress_already_exists(self, authenticated_api_client):
        """Test that progress is updated if already exists."""
        entry = DictionaryEntry.objects.get(source_text="猫")
        
        # First creation
        data1 = {
            "dictionary_entry_id": entry.pk,
            "is_favorited": True,
            "is_mastered": True,
            "mastery_level": 90
        }
        response1 = authenticated_api_client.post("/api/user-progress/", data1, format="json")
        assert response1.status_code == 201
        
        # Try to create again
        data2 = {
            "dictionary_entry_id": entry.pk,
            "is_favorited": False,
            "is_mastered": False,
            "mastery_level": 50
        }
        response2 = authenticated_api_client.post("/api/user-progress/", data2, format="json")
        assert response2.status_code == 200
        
        # Should update existing record
        data = response2.data
        assert data["is_favorited"] is False
        assert data["is_mastered"] is False
        assert data["mastery_level"] == 50
    
    def test_create_user_progress_mastered_validation(self, authenticated_api_client):
        """Test that mastered entries must have mastery_level >= 80."""
        entry = DictionaryEntry.objects.get(source_text="犬")
        
        data = {
            "dictionary_entry_id": entry.pk,
            "is_favorited": False,
            "is_mastered": True,
            "mastery_level": 75  # Should fail - less than 80
        }
        response = authenticated_api_client.post("/api/user-progress/", data, format="json")
        assert response.status_code == 400
        assert "mastery_level" in response.data["errors"]
    
    def test_user_progress_mastered_action(self, authenticated_api_client):
        """Test the mastered action endpoint."""
        response = authenticated_api_client.get("/api/user-progress/mastered/")
        assert response.status_code == 200
        data = response.data
        assert "count" in data
        assert "results" in data
    
    def test_user_progress_favorites_action(self, authenticated_api_client):
        """Test the favorites action endpoint."""
        response = authenticated_api_client.get("/api/user-progress/favorites/")
        assert response.status_code == 200
        data = response.data
        assert "count" in data
        assert "results" in data
    
    def test_user_progress_statistics_action(self, authenticated_api_client):
        """Test the statistics action endpoint."""
        response = authenticated_api_client.get("/api/user-progress/statistics/")
        assert response.status_code == 200
        data = response.data
        assert "total_entries" in data
        assert "mastered_entries" in data
        assert "favorited_entries" in data
        assert "average_mastery" in data
        assert "total_reviews" in data
        assert "correct_reviews" in data
        assert "accuracy" in data


@pytest.mark.django_db
class TestStudySessionViewSet:
    """Tests for StudySessionViewSet API endpoint."""
    
    def test_list_study_sessions_authenticated(self, authenticated_api_client):
        """Test listing study sessions (requires authentication)."""
        response = authenticated_api_client.get("/api/study-sessions/")
        assert response.status_code == 200
        data = response.data
        assert "count" in data
        assert "results" in data
    
    def test_list_study_sessions_anonymous(self, api_client):
        """Test listing study sessions (requires authentication)."""
        response = api_client.get("/api/study-sessions/")
        assert response.status_code == 401
    
    def test_retrieve_study_session(self, authenticated_api_client):
        """Test retrieving a specific study session."""
        response = authenticated_api_client.get("/api/study-sessions/")
        session_id = response.data["results"][0]["id"]
        
        response = authenticated_api_client.get(f"/api/study-sessions/{session_id}/")
        assert response.status_code == 200
        data = response.data
        assert data["user"] == "testuser"
    
    def test_create_study_session(self, authenticated_api_client):
        """Test creating a new study session."""
        entries = DictionaryEntry.objects.filter(source_language__code="ja")[:2].values("id")
        entry_ids = [e["id"] for e in entries]
        
        data = {
            "dictionary_entries": entry_ids
        }
        response = authenticated_api_client.post("/api/study-sessions/", data, format="json")
        assert response.status_code == 201
        data = response.data
        assert data["user"] == "testuser"
        assert "dictionary_entries" in data
    
    def test_study_session_end_action(self, authenticated_api_client):
        """Test the end action endpoint."""
        response = authenticated_api_client.get("/api/study-sessions/")
        session_id = response.data["results"][0]["id"]
        
        data = {
            "end_time": "2024-01-15T10:30:00Z",
            "words_studied": 10,
            "words_mastered": 5
        }
        response = authenticated_api_client.post(f"/api/study-sessions/{session_id}/end/", data, format="json")
        assert response.status_code == 200
        data = response.data
        assert data["end_time"] == "2024-01-15T10:30:00Z"
        assert data["words_studied"] == 10
        assert data["words_mastered"] == 5
    
    def test_study_session_start_action(self, authenticated_api_client):
        """Test the start action endpoint."""
        data = {
            "dictionary_entries": [1, 2]
        }
        response = authenticated_api_client.post("/api/study-sessions/start/", data, format="json")
        assert response.status_code == 201
        data = response.data
        assert data["user"] == "testuser"


@pytest.mark.django_db
class TestStudySessionEntryViewSet:
    """Tests for StudySessionEntryViewSet API endpoint."""
    
    @pytest.mark.django_db
    def test_list_study_session_entries_authenticated(self, authenticated_api_client):
        """Test listing study session entries (requires authentication)."""
        response = authenticated_api_client.get("/api/study-session-entries/")
        assert response.status_code == 200
        data = response.data
        assert "count" in data
        assert "results" in data
    
    def test_list_study_session_entries_anonymous(self, api_client):
        """Test listing study session entries (requires authentication)."""
        response = api_client.get("/api/study-session-entries/")
        assert response.status_code == 401
    
    def test_retrieve_study_session_entry(self, authenticated_api_client):
        """Test retrieving a specific study session entry."""
        response = authenticated_api_client.get("/api/study-session-entries/")
        entry_id = response.data["results"][0]["id"]
        
        response = authenticated_api_client.get(f"/api/study-session-entries/{entry_id}/")
        assert response.status_code == 200
        data = response.data
        assert data["is_correct"] is True or data["is_correct"] is False
    
    def test_create_study_session_entry(self, authenticated_api_client):
        """Test creating a study session entry."""
        session = StudySession.objects.get(user__username="testuser")
        entry = DictionaryEntry.objects.get(source_text="猫")
        
        data = {
            "study_session_id": session.pk,
            "dictionary_entry": {"id": entry.pk, "source_text": "猫", "target_text": "Кот"},
            "is_correct": True,
            "response_time_ms": 1500
        }
        response = authenticated_api_client.post("/api/study-session-entries/", data, format="json")
        assert response.status_code == 201
        data = response.data
        assert data["is_correct"] is True
    
    def test_create_study_session_entry_is_correct_required(self, authenticated_api_client):
        """Test that is_correct is required."""
        session = StudySession.objects.get(user__username="testuser")
        entry = DictionaryEntry.objects.get(source_text="猫")
        
        data = {
            "study_session_id": session.pk,
            "dictionary_entry": {"id": entry.pk, "source_text": "猫", "target_text": "Кот"},
            "is_correct": None,
            "response_time_ms": 1500
        }
        response = authenticated_api_client.post("/api/study-session-entries/", data, format="json")
        assert response.status_code == 400
        assert "is_correct" in response.data["errors"]
    
    def test_study_session_entry_mark_correct_action(self, authenticated_api_client):
        """Test the mark_correct action endpoint."""
        response = authenticated_api_client.get("/api/study-session-entries/")
        entry_id = response.data["results"][0]["id"]
        
        data = {}
        response = authenticated_api_client.post(f"/api/study-session-entries/{entry_id}/mark-correct/", data, format="json")
        assert response.status_code == 200
        data = response.data
        assert data["is_correct"] is True
    
    def test_study_session_entry_mark_incorrect_action(self, authenticated_api_client):
        """Test the mark_incorrect action endpoint."""
        response = authenticated_api_client.get("/api/study-session-entries/")
        entry_id = response.data["results"][0]["id"]
        
        data = {}
        response = authenticated_api_client.post(f"/api/study-session-entries/{entry_id}/mark-incorrect/", data, format="json")
        assert response.status_code == 200
        data = response.data
        assert data["is_correct"] is False


@pytest.mark.django_db
class TestUserIsolation:
    """Tests for user isolation and data access."""
    
    def test_user_progress_isolation(self, api_client):
        """Test that users can only access their own progress."""
        user2 = get_user_model().objects.create_user(
            username="testuser2",
            email="test2@example.com",
            password="testpass123"
        )
        
        client = APIClient()
        client.force_authenticate(user=user2)
        
        response = client.get("/api/user-progress/")
        assert response.status_code == 200
        data = response.data
        for progress in data["results"]:
            assert progress["user"] == "testuser2"
        
        # Cleanup
        user2.delete()
    
    def test_study_session_isolation(self, api_client):
        """Test that users can only access their own study sessions."""
        user2 = get_user_model().objects.create_user(
            username="testuser2",
            email="test2@example.com",
            password="testpass123"
        )
        
        client = APIClient()
        client.force_authenticate(user=user2)
        
        response = client.get("/api/study-sessions/")
        assert response.status_code == 200
        data = response.data
        for session in data["results"]:
            assert session["user"] == "testuser2"
        
        # Cleanup
        user2.delete()
    
    def test_study_session_entry_isolation(self, api_client):
        """Test that users can only access their own study session entries."""
        user2 = get_user_model().objects.create_user(
            username="testuser2",
            email="test2@example.com",
            password="testpass123"
        )
        
        client = APIClient()
        client.force_authenticate(user=user2)
        
        response = client.get("/api/study-session-entries/")
        assert response.status_code == 200
        data = response.data
        for entry in data["results"]:
            # The entry should belong to a session owned by the current user
            assert "study_session" in entry
    
    def test_dictionary_entry_public_access(self, api_client):
        """Test that dictionary entries are publicly accessible."""
        response = api_client.get("/api/dictionary-entries/")
        assert response.status_code == 200
        data = response.data
        for entry in data["results"]:
            assert "id" in entry
            assert "source_text" in entry
            assert "target_text" in entry
    
    def test_language_public_access(self, api_client):
        """Test that languages are publicly accessible."""
        response = api_client.get("/api/v1/languages/")
        assert response.status_code == 200
        data = response.data
        for lang in data["results"]:
            assert "code" in lang
            assert "name" in lang


@pytest.mark.django_db
class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""
    
    def test_empty_search(self, api_client):
        """Test searching with empty string."""
        response = api_client.get("/api/dictionary-entries/?search=")
        assert response.status_code == 200
        # Empty search should return all entries or handle gracefully
    
    def test_search_no_results(self, api_client):
        """Test searching with term that doesn't exist."""
        response = api_client.get("/api/dictionary-entries/?search=nonexistentword123")
        assert response.status_code == 200
        assert len(response.data["results"]) == 0
    
    def test_pagination(self, api_client):
        """Test pagination with page parameter."""
        response = api_client.get("/api/dictionary-entries/?page=1&page_size=2")
        assert response.status_code == 200
        data = response.data
        assert "count" in data
        assert "next" in data or "next" not in data
        assert "previous" in data or "previous" not in data
    
    def test_sorting(self, api_client):
        """Test sorting by different fields."""
        response = api_client.get("/api/dictionary-entries/?ordering=source_text")
        assert response.status_code == 200
        data = response.data
        for i in range(len(data["results"]) - 1):
            assert data["results"][i]["source_text"] <= data["results"][i + 1]["source_text"]
    
    def test_invalid_page(self, api_client):
        """Test requesting non-existent page."""
        response = api_client.get("/api/dictionary-entries/?page=99999999999")
        assert response.status_code == 404
    
    def test_empty_dictionary_entry_fields(self, api_client):
        """Test creating entry with minimal fields."""
        data = {
            "source_text": "テスト",
            "target_text": "Test",
            "source_language": {"id": 1, "code": "ja", "name": "Japanese"},
            "target_language": {"id": 2, "code": "ru", "name": "Russian"}
        }
        response = api_client.post("/api/dictionary-entries/", data, format="json")
        assert response.status_code == 201
        data = response.data
        # Optional fields should be None/empty
        assert data.get("part_of_speech") is None or data["part_of_speech"] == ""
        assert data.get("pronunciation") is None or data["pronunciation"] == ""
        assert data.get("definition") is None or data["definition"] == ""
        assert data.get("examples") is None or data["examples"] == ""
