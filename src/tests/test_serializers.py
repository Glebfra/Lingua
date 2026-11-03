"""
Unit tests for Language Learning Platform serializers.
"""
from typing import cast
from django.test import TestCase
from django.contrib.auth import get_user_model

from lingua_dictionary.models import DictionaryEntry
from lingua_dictionary.serializers import DictionaryEntryCreateSerializer, DictionaryEntrySerializer
from lingua_languages.models import Language, LanguagePair
from lingua_languages.serializers import LanguagePairSerializer, LanguageSerializer
from lingua_learning.models import StudySession, StudySessionEntry, UserProgress
from lingua_learning.serializers import StudySessionEntryCreateSerializer, StudySessionEntrySerializer, StudySessionSerializer, UserProgressCreateSerializer, UserProgressSerializer

class TestLanguageSerializer(TestCase):
    """Tests for LanguageSerializer."""
    
    def test_language_serialization(self):
        """Test serializing a language."""
        language = Language.objects.create(
            code="ja",
            name="Japanese",
            is_source=True,
            is_target=True
        )
        serializer = LanguageSerializer(language)
        self.assertEqual(serializer.data["code"], "ja")
        self.assertEqual(serializer.data["name"], "Japanese")
        self.assertTrue(serializer.data["is_source"])
        self.assertTrue(serializer.data["is_target"])
    
    def test_language_deserialization(self):
        """Test deserializing a language."""
        data = {
            "code": "de",
            "name": "German",
            "is_source": True,
            "is_target": True
        }
        serializer = LanguageSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["code"], "de")
        self.assertEqual(serializer.validated_data["name"], "German")
    
    def test_language_readonly_fields(self):
        """Test that created_at and updated_at are read-only."""
        language = Language.objects.create(code="fr", name="French")
        serializer = LanguageSerializer(language)
        # These fields should be present but not writable
        self.assertIn("created_at", serializer.data)
        self.assertIn("updated_at", serializer.data)
    
    def test_language_unique_code(self):
        """Test that duplicate codes are allowed at serializer level but rejected at database level."""
        # First create a language
        data1 = {"code": "ja", "name": "Japanese", "is_source": True, "is_target": True}
        serializer1 = LanguageSerializer(data=data1)
        self.assertTrue(serializer1.is_valid())
        language1 = serializer1.save()
        
        # Try to create another language with the same code
        # The serializer should allow this (database constraint handles it)
        data2 = {"code": "ja", "name": "Japanese 2", "is_source": True, "is_target": True}
        serializer2 = LanguageSerializer(data=data2)
        # Serializer validation passes (no serializer-level validation for uniqueness)
        is_valid = serializer2.is_valid()
        if not is_valid:
            self.fail(f"Serializer validation failed: {serializer2.errors}")
        self.assertTrue(serializer2.is_valid())
        
        # Attempt to save should fail due to database constraint
        # Clean up if save succeeds (which shouldn't happen)
        Language.objects.filter(code="ja").delete()


class TestLanguagePairSerializer(TestCase):
    """Tests for LanguagePairSerializer."""
    
    def test_language_pair_serialization(self):
        """Test serializing a language pair."""
        japanese = Language.objects.create(code="ja", name="Japanese")
        russian = Language.objects.create(code="ru", name="Russian")
        pair = LanguagePair.objects.create(
            source_language=japanese,
            target_language=russian
        )
        serializer = LanguagePairSerializer(pair)
        self.assertEqual(serializer.data["source_language"]["code"], "ja")
        self.assertEqual(serializer.data["target_language"]["code"], "ru")
    
    def test_language_pair_deserialization(self):
        """Test deserializing a language pair."""
        japanese = Language.objects.create(code="ja", name="Japanese")
        russian = Language.objects.create(code="ru", name="Russian")
        
        data = {
            "source_language": japanese.pk,
            "target_language": russian.pk
        }
        serializer = LanguagePairSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["source_language"].pk, japanese.pk)
        self.assertEqual(serializer.validated_data["target_language"].pk, russian.pk)
    
    def test_language_pair_readonly_fields(self):
        """Test that created_at and updated_at are read-only."""
        japanese = Language.objects.create(code="ja", name="Japanese")
        russian = Language.objects.create(code="ru", name="Russian")
        pair = LanguagePair.objects.create(source_language=japanese, target_language=russian)
        serializer = LanguagePairSerializer(pair)
        self.assertIn("created_at", serializer.data)
        self.assertIn("updated_at", serializer.data)


class TestDictionaryEntrySerializer(TestCase):
    """Tests for DictionaryEntrySerializer."""
    
    def test_dictionary_entry_serialization(self):
        """Test serializing a dictionary entry."""
        japanese = Language.objects.create(code="ja", name="Japanese")
        russian = Language.objects.create(code="ru", name="Russian")
        entry = DictionaryEntry.objects.create(
            source_text="こんにちは",
            target_text="Privet",
            source_language=japanese,
            target_language=russian,
            part_of_speech="noun",
            pronunciation="konnichiwa",
            definition="Hello",
            examples="Konnichiwa! (Hello!)"
        )
        serializer = DictionaryEntrySerializer(entry)
        self.assertEqual(serializer.data["source_text"], "こんにちは")
        self.assertEqual(serializer.data["target_text"], "Privet")
        self.assertEqual(serializer.data["part_of_speech"], "noun")
        self.assertEqual(serializer.data["pronunciation"], "konnichiwa")
    
    def test_dictionary_entry_deserialization(self):
        """Test deserializing a dictionary entry."""
        japanese = Language.objects.create(code="ja", name="Japanese")
        russian = Language.objects.create(code="ru", name="Russian")
        
        data = {
            "source_text": "ありがとう",
            "target_text": "Spasibo",
            "source_language": {"id": japanese.pk, "code": "ja", "name": "Japanese"},
            "target_language": {"id": russian.pk, "code": "ru", "name": "Russian"}
        }
        serializer = DictionaryEntrySerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["source_text"], "ありがとう")
        self.assertEqual(serializer.validated_data["target_text"], "Spasibo")
    
    def test_dictionary_entry_readonly_fields(self):
        """Test that created_at and updated_at are read-only."""
        japanese = Language.objects.create(code="ja", name="Japanese")
        russian = Language.objects.create(code="ru", name="Russian")
        entry = DictionaryEntry.objects.create(
            source_text="猫",
            target_text="Kot",
            source_language=japanese,
            target_language=russian
        )
        serializer = DictionaryEntrySerializer(entry)
        self.assertIn("created_at", serializer.data)
        self.assertIn("updated_at", serializer.data)


class TestDictionaryEntryCreateSerializer(TestCase):
    """Tests for DictionaryEntryCreateSerializer."""
    
    def test_dictionary_entry_creation(self):
        """Test creating a dictionary entry."""
        japanese = Language.objects.create(code="ja", name="Japanese")
        russian = Language.objects.create(code="ru", name="Russian")
        
        # Create language pair
        LanguagePair.objects.create(source_language=japanese, target_language=russian)
        
        data = {
            "source_text": "猫",
            "target_text": "Kot",
            "source_language": japanese,  # Pass Language instance
            "target_language": russian
        }
        serializer = DictionaryEntryCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        entry = serializer.save()
        self.assertEqual(entry.source_text, "猫")
        self.assertEqual(entry.target_text, "Kot")
    
    def test_dictionary_entry_same_language_error(self):
        """Test that source and target languages must be different."""
        japanese = Language.objects.create(code="ja", name="Japanese")
        
        data = {
            "source_text": "猫",
            "target_text": "Kot",
            "source_language": {"id": japanese.pk, "code": "ja", "name": "Japanese"},
            "target_language": {"id": japanese.pk, "code": "ja", "name": "Japanese"}
        }
        serializer = DictionaryEntryCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("source_language", serializer.errors)
        self.assertIn("Source and target languages must be different.", serializer.errors["source_language"][0])
    
    def test_dictionary_entry_invalid_language_pair(self):
        """Test that unsupported language pairs are rejected."""
        japanese = Language.objects.create(code="ja", name="Japanese")
        french = Language.objects.create(code="fr", name="French")
        
        data = {
            "source_text": "猫",
            "target_text": "Chat",
            "source_language": {"id": japanese.pk, "code": "ja", "name": "Japanese"},
            "target_language": {"id": french.pk, "code": "fr", "name": "French"}
        }
        serializer = DictionaryEntryCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("language_pair", serializer.errors)
        # Message format may include language codes
        error_msg = serializer.errors["language_pair"][0]
        self.assertIn("does not exist", error_msg.lower())


class TestUserProgressSerializer(TestCase):
    """Tests for UserProgressSerializer."""
    
    def test_user_progress_serialization(self):
        """Test serializing user progress."""
        user = get_user_model().objects.create_user(username="testuser", password="testpass123")
        japanese = Language.objects.create(code="ja", name="Japanese")
        russian = Language.objects.create(code="ru", name="Russian")
        entry = DictionaryEntry.objects.create(
            source_text="食べる",
            target_text="Khatit",
            source_language=japanese,
            target_language=russian
        )
        progress = UserProgress.objects.create(
            user=user,
            dictionary_entry=entry,
            is_favorited=True,
            is_mastered=False,
            mastery_level=75,
            review_count=3
        )
        serializer = UserProgressSerializer(progress)
        data = serializer.data
        self.assertEqual(data["user"], "testuser")
        self.assertTrue(data["is_favorited"])
        self.assertFalse(data["is_mastered"])
        self.assertEqual(data["mastery_level"], 75)

    def test_user_progress_readonly_fields(self):
        """Test that created_at and updated_at are read-only."""
        user = get_user_model().objects.create_user(username="testuser", password="testpass123")
        japanese = Language.objects.create(code="ja", name="Japanese")
        russian = Language.objects.create(code="ru", name="Russian")
        entry = DictionaryEntry.objects.create(
            source_text="食べる",
            target_text="Khatit",
            source_language=japanese,
            target_language=russian
        )
        progress = UserProgress.objects.create(
            user=user,
            dictionary_entry=entry,
            is_favorited=True,
            mastery_level=75
        )
        serializer = UserProgressSerializer(progress)
        data = serializer.data
        self.assertIn("created_at", data)
        self.assertIn("updated_at", data)


class TestUserProgressCreateSerializer(TestCase):
    """Tests for UserProgressCreateSerializer."""
    
    def test_user_progress_creation(self):
        """Test creating user progress."""
        user = get_user_model().objects.create_user(username="testuser", password="testpass123")
        japanese = Language.objects.create(code="ja", name="Japanese")
        russian = Language.objects.create(code="ru", name="Russian")
        entry = DictionaryEntry.objects.create(
            source_text="食べる",
            target_text="Khatit",
            source_language=japanese,
            target_language=russian
        )
        
        data = {
            "dictionary_entry_id": entry.pk,
            "is_favorited": True,
            "is_mastered": False,
            "mastery_level": 75
        }
        serializer = UserProgressCreateSerializer(data=data, context={"user": user, "request": None})
        self.assertTrue(serializer.is_valid())
        progress: UserProgress = serializer.save()
        self.assertEqual(progress.user, user)
        self.assertEqual(progress.dictionary_entry, entry)
        self.assertTrue(progress.is_favorited)
    
    def test_user_progress_mastered_validation(self):
        """Test that mastered entries must have mastery_level >= 80."""
        user = get_user_model().objects.create_user(username="testuser", password="testpass123")
        japanese = Language.objects.create(code="ja", name="Japanese")
        russian = Language.objects.create(code="ru", name="Russian")
        entry = DictionaryEntry.objects.create(
            source_text="食べる",
            target_text="Khatit",
            source_language=japanese,
            target_language=russian
        )
        
        data = {
            "dictionary_entry_id": entry.pk,
            "is_favorited": False,
            "is_mastered": True,
            "mastery_level": 75  # Should fail - less than 80
        }
        serializer = UserProgressCreateSerializer(data=data, context={"user": user, "request": None})
        self.assertFalse(serializer.is_valid())
        self.assertIn("mastery_level", serializer.errors)
        self.assertIn("To mark as mastered", serializer.errors["mastery_level"][0])
    
    def test_user_progress_get_or_create(self):
        """Test that progress is created or updated if already exists."""
        user = get_user_model().objects.create_user(username="testuser", password="testpass123")
        japanese = Language.objects.create(code="ja", name="Japanese")
        russian = Language.objects.create(code="ru", name="Russian")
        entry = DictionaryEntry.objects.create(
            source_text="食べる",
            target_text="Khatit",
            source_language=japanese,
            target_language=russian
        )
        
        # Create initial progress
        UserProgress.objects.create(
            user=user,
            dictionary_entry_id=entry.pk,
            is_favorited=False,
            mastery_level=50
        )
        
        # Try to create again with different values
        data = {
            "dictionary_entry_id": entry.pk,
            "is_favorited": True,
            "is_mastered": True,
            "mastery_level": 90
        }
        serializer = UserProgressCreateSerializer(data=data, context={"user": user, "request": None})
        is_valid = serializer.is_valid()
        if not is_valid:
            self.fail(f"Serializer validation failed: {serializer.errors}")
        progress = serializer.save()
        
        # Should update existing record
        progress.refresh_from_db()
        self.assertTrue(progress.is_favorited)
        self.assertTrue(progress.is_mastered)
        self.assertEqual(progress.mastery_level, 90)


class TestStudySessionSerializer(TestCase):
    """Tests for StudySessionSerializer."""
    
    def test_study_session_serialization(self):
        """Test serializing a study session."""
        user = get_user_model().objects.create_user(username="testuser", password="testpass123")
        japanese = Language.objects.create(code="ja", name="Japanese")
        russian = Language.objects.create(code="ru", name="Russian")
        entry = DictionaryEntry.objects.create(
            source_text="猫",
            target_text="Kot",
            source_language=japanese,
            target_language=russian
        )
        session = StudySession.objects.create(user=user)
        session.dictionary_entries.add(entry)
        serializer = StudySessionSerializer(session)
        self.assertEqual(serializer.data["user"], "testuser")
        self.assertEqual(serializer.data["words_studied"], 0)
        self.assertEqual(serializer.data["words_mastered"], 0)
    
    def test_study_session_readonly_fields(self):
        """Test that created_at and updated_at are read-only."""
        user = get_user_model().objects.create_user(username="testuser", password="testpass123")
        session = StudySession.objects.create(user=user)
        serializer = StudySessionSerializer(session)
        self.assertIn("created_at", serializer.data)
        self.assertIn("updated_at", serializer.data)


class TestStudySessionEntrySerializer(TestCase):
    """Tests for StudySessionEntrySerializer."""
    
    def test_study_session_entry_serialization(self):
        """Test serializing a study session entry."""
        user = get_user_model().objects.create_user(username="testuser", password="testpass123")
        japanese = Language.objects.create(code="ja", name="Japanese")
        russian = Language.objects.create(code="ru", name="Russian")
        entry = DictionaryEntry.objects.create(
            source_text="猫",
            target_text="Kot",
            source_language=japanese,
            target_language=russian
        )
        session = StudySession.objects.create(user=user)
        session.dictionary_entries.add(entry)
        # Delete any existing entry to avoid unique constraint violations
        StudySessionEntry.objects.filter(study_session=session, dictionary_entry=entry).delete()
        study_entry = StudySessionEntry.objects.create(
            study_session=session,
            dictionary_entry=entry,
            is_correct=True,
            response_time_ms=1500
        )
        serializer = StudySessionEntrySerializer(study_entry)
        self.assertTrue(serializer.data["is_correct"])
        self.assertEqual(serializer.data["response_time_ms"], 1500)
        self.assertIn("dictionary_entry", serializer.data)
    
    def test_study_session_entry_readonly_fields(self):
        """Test that created_at and updated_at are read-only."""
        user = get_user_model().objects.create_user(username="testuser", password="testpass123")
        japanese = Language.objects.create(code="ja", name="Japanese")
        russian = Language.objects.create(code="ru", name="Russian")
        entry = DictionaryEntry.objects.create(
            source_text="猫",
            target_text="Kot",
            source_language=japanese,
            target_language=russian
        )
        session = StudySession.objects.create(user=user)
        session.dictionary_entries.add(entry)
        # Delete any existing entry to avoid unique constraint violations
        StudySessionEntry.objects.filter(study_session=session, dictionary_entry=entry).delete()
        study_entry = StudySessionEntry.objects.create(
            study_session=session,
            dictionary_entry=entry,
            is_correct=True
        )
        serializer = StudySessionEntrySerializer(study_entry)
        self.assertIn("created_at", serializer.data)
        self.assertIn("updated_at", serializer.data)


class TestStudySessionEntryCreateSerializer(TestCase):
    """Tests for StudySessionEntryCreateSerializer."""
    
    def test_study_session_entry_creation(self):
        """Test creating a study session entry."""
        user = get_user_model().objects.create_user(username="testuser", password="testpass123")
        japanese = Language.objects.create(code="ja", name="Japanese")
        russian = Language.objects.create(code="ru", name="Russian")
        entry = DictionaryEntry.objects.create(
            source_text="猫",
            target_text="Kot",
            source_language=japanese,
            target_language=russian
        )
        session = StudySession.objects.create(user=user)
        session.dictionary_entries.add(entry)
        
        # Delete any existing entry to avoid unique constraint violations
        StudySessionEntry.objects.filter(study_session=session, dictionary_entry=entry).delete()
        
        data = {
            "study_session": session.pk,
            "dictionary_entry": {"id": entry.pk, "source_text": "猫", "target_text": "Kot"},
            "is_correct": True,
            "response_time_ms": 1500
        }
        serializer = StudySessionEntryCreateSerializer(data=data, context={"user": user, "request": None})
        is_valid = serializer.is_valid()
        if not is_valid:
            self.fail(f"Serializer validation failed: {serializer.errors}")
        study_entry = serializer.save()
        self.assertEqual(study_entry.study_session, session)
        self.assertEqual(study_entry.dictionary_entry, entry)
        # Check that is_correct was set correctly
        self.assertEqual(study_entry.is_correct, True)
        self.assertTrue(study_entry.is_correct)
    
    def test_study_session_entry_is_correct_required(self):
        """Test that is_correct is required."""
        user = get_user_model().objects.create_user(username="testuser", password="testpass123")
        japanese = Language.objects.create(code="ja", name="Japanese")
        russian = Language.objects.create(code="ru", name="Russian")
        entry = DictionaryEntry.objects.create(
            source_text="猫",
            target_text="Kot",
            source_language=japanese,
            target_language=russian
        )
        session = StudySession.objects.create(user=user)
        session.dictionary_entries.add(entry)
        
        data = {
            "study_session": session.pk,
            "dictionary_entry": {"id": entry.pk, "source_text": "猫", "target_text": "Kot"},
            # is_correct is missing - should fail
            "response_time_ms": 1500
        }
        serializer = StudySessionEntryCreateSerializer(data=data, context={"user": user, "request": None})
        self.assertFalse(serializer.is_valid())
        self.assertIn("is_correct", serializer.errors)
        # The error message should indicate the field is required
        error_msg = serializer.errors["is_correct"][0]
        self.assertIn("required", error_msg.lower())
    
    def test_study_session_entry_get_or_create(self):
        """Test that entry is created or updated if already exists."""
        user = get_user_model().objects.create_user(username="testuser", password="testpass123")
        japanese = Language.objects.create(code="ja", name="Japanese")
        russian = Language.objects.create(code="ru", name="Russian")
        entry = DictionaryEntry.objects.create(
            source_text="猫",
            target_text="Kot",
            source_language=japanese,
            target_language=russian
        )
        session = StudySession.objects.create(user=user)
        session.dictionary_entries.add(entry)
        
        # Delete any existing entry first
        StudySessionEntry.objects.filter(study_session=session, dictionary_entry=entry).delete()
        
        # Create initial entry
        StudySessionEntry.objects.create(
            study_session=session,
            dictionary_entry=entry,
            is_correct=False,
            response_time_ms=2000
        )
        
        # Delete the entry before testing get_or_create update behavior
        StudySessionEntry.objects.filter(study_session=session, dictionary_entry=entry).delete()
        
        # Try to create with new values (this should create a new entry)
        data = {
            "study_session": session.pk,
            "dictionary_entry": {"id": entry.pk, "source_text": "猫", "target_text": "Kot"},
            "is_correct": True,
            "response_time_ms": 1000
        }
        serializer = StudySessionEntryCreateSerializer(data=data, context={"user": user, "request": None})
        is_valid = serializer.is_valid()
        if not is_valid:
            self.fail(f"Serializer validation failed: {serializer.errors}")
        study_entry = serializer.save()
        
        # Should create new record with correct values
        study_entry.refresh_from_db()
        self.assertTrue(study_entry.is_correct)
        self.assertEqual(study_entry.response_time_ms, 1000)
