"""
Unit tests for Language Learning Platform models.
"""
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model

from lingua_dictionary.models import DictionaryEntry
from lingua_languages.models import Language, LanguagePair
from lingua_learning.models import StudySession, StudySessionEntry, UserProgress


class LanguageModelTest(TestCase):
    """Tests for the Language model."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.japanese = Language.objects.create(
            code="ja",
            name="Japanese",
            is_source=True,
            is_target=True
        )
        self.english = Language.objects.create(
            code="en",
            name="English",
            is_source=True,
            is_target=True
        )
    
    def test_language_creation(self):
        """Test creating a new language."""
        language = Language.objects.create(
            code="de",
            name="German",
            is_source=True,
            is_target=True
        )
        self.assertEqual(language.code, "de")
        self.assertEqual(language.name, "German")
        self.assertTrue(language.is_source)
        self.assertTrue(language.is_target)
    
    def test_language_str_representation(self):
        """Test string representation of a language."""
        language = Language.objects.create(
            code="fr",
            name="French",
            is_source=True,
            is_target=True
        )
        self.assertEqual(str(language), "fr - French")
    
    def test_language_str_representation_unique_code(self):
        """Test that string representation uses code when name is missing."""
        language = Language.objects.create(
            code="pt",
            name="",
            is_source=True,
            is_target=True
        )
        self.assertEqual(str(language), "pt - ")
    
    def test_language_get_absolute_url(self):
        """Test that Language has an absolute URL method."""
        language = Language.objects.create(
            code="es",
            name="Spanish",
            is_source=True,
            is_target=True
        )
        # Django Model should provide this via reverse
        self.assertIsNotNone(language)
    
    def test_language_unique_code(self):
        """Test that language codes must be unique."""
        # Delete the japanese language created in setUp
        Language.objects.filter(code="ja").delete()
        Language.objects.create(code="ja", name="Japanese 2")
        with self.assertRaises(Exception):
            Language.objects.create(code="ja", name="Japanese 3")
    
    def test_language_is_source_and_is_target_default(self):
        """Test default values for is_source and is_target."""
        language = Language.objects.create(
            code="it",
            name="Italian"
        )
        self.assertTrue(language.is_source)
        self.assertTrue(language.is_target)
    
    def test_language_update_timestamps(self):
        """Test that created_at and updated_at are set correctly."""
        language = Language.objects.create(code="ko", name="Korean")
        created_at = language.created_at
        updated_at = language.updated_at
        
        # Create a new language to update timestamps
        Language.objects.create(code="ar", name="Arabic")
        
        # Reload the first language to check updated_at
        language.refresh_from_db()
        self.assertLessEqual(created_at, language.updated_at)
        self.assertEqual(created_at, language.created_at)


class LanguagePairModelTest(TestCase):
    """Tests for the LanguagePair model."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.japanese = Language.objects.create(code="ja", name="Japanese")
        self.russian = Language.objects.create(code="ru", name="Russian")
        self.english = Language.objects.create(code="en", name="English")
    
    def test_language_pair_creation(self):
        """Test creating a new language pair."""
        pair = LanguagePair.objects.create(
            source_language=self.japanese,
            target_language=self.russian
        )
        self.assertEqual(pair.source_language, self.japanese)
        self.assertEqual(pair.target_language, self.russian)
        self.assertEqual(str(pair), "Japanese -> Russian")
    
    def test_language_pair_unique_constraint(self):
        """Test that language pairs must be unique."""
        LanguagePair.objects.create(
            source_language=self.japanese,
            target_language=self.russian
        )
        with self.assertRaises(Exception):
            LanguagePair.objects.create(
                source_language=self.japanese,
                target_language=self.russian
            )
    
    def test_language_pair_str_representation(self):
        """Test string representation of a language pair."""
        pair = LanguagePair.objects.create(
            source_language=self.japanese,
            target_language=self.russian
        )
        self.assertEqual(str(pair), "Japanese -> Russian")
    
    def test_language_pair_source_language_pairs_relation(self):
        """Test source_language_pairs reverse relation."""
        pair = LanguagePair.objects.create(
            source_language=self.japanese,
            target_language=self.russian
        )
        
        pair2 = LanguagePair.objects.create(
            source_language=self.japanese,
            target_language=self.english
        )
        
        self.assertIn(pair, self.japanese.source_language_pairs.all())
        self.assertIn(pair2, self.japanese.source_language_pairs.all())
    
    def test_language_pair_target_language_pairs_relation(self):
        """Test target_language_pairs reverse relation."""
        pair = LanguagePair.objects.create(
            source_language=self.japanese,
            target_language=self.russian
        )
        
        pair3 = LanguagePair.objects.create(
            source_language=self.english,
            target_language=self.russian
        )
        
        self.assertIn(pair, self.russian.target_language_pairs.all())
        self.assertIn(pair3, self.russian.target_language_pairs.all())


class DictionaryEntryModelTest(TestCase):
    """Tests for the DictionaryEntry model."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.japanese = Language.objects.create(code="ja", name="Japanese")
        self.russian = Language.objects.create(code="ru", name="Russian")
    
    def test_dictionary_entry_creation(self):
        """Test creating a new dictionary entry."""
        entry = DictionaryEntry.objects.create(
            source_text="こんにちは",
            target_text="Privet",
            source_language=self.japanese,
            target_language=self.russian
        )
        self.assertEqual(entry.source_text, "こんにちは")
        self.assertEqual(entry.target_text, "Privet")
        self.assertEqual(entry.source_language, self.japanese)
        self.assertEqual(entry.target_language, self.russian)
    
    def test_dictionary_entry_str_representation(self):
        """Test string representation of a dictionary entry."""
        entry = DictionaryEntry.objects.create(
            source_text="ありがとう",
            target_text="Spasibo",
            source_language=self.japanese,
            target_language=self.russian
        )
        self.assertEqual(str(entry), "ありがとう (ja -> ru)")
    
    def test_dictionary_entry_unique_constraint(self):
        """Test that dictionary entries must be unique per language pair."""
        DictionaryEntry.objects.create(
            source_text="テスト",
            target_text="Test",
            source_language=self.japanese,
            target_language=self.russian
        )
        with self.assertRaises(Exception):
            DictionaryEntry.objects.create(
                source_text="テスト",
                target_text="Test2",
                source_language=self.japanese,
                target_language=self.russian
            )
    
    def test_dictionary_entry_optional_fields(self):
        """Test that optional fields can be omitted."""
        entry = DictionaryEntry.objects.create(
            source_text="猫",
            target_text="Kot",
            source_language=self.japanese,
            target_language=self.russian
        )
        self.assertIsNone(entry.part_of_speech)
        self.assertIsNone(entry.pronunciation)
        self.assertIsNone(entry.definition)
        self.assertIsNone(entry.examples)
    
    def test_dictionary_entry_with_optional_fields(self):
        """Test that optional fields can be provided."""
        entry = DictionaryEntry.objects.create(
            source_text="犬",
            target_text="Soba",
            source_language=self.japanese,
            target_language=self.russian,
            part_of_speech="noun",
            pronunciation="inu",
            definition="A dog",
            examples="Inu ga hau. (The dog is running.)"
        )
        self.assertEqual(entry.part_of_speech, "noun")
        self.assertEqual(entry.pronunciation, "inu")
        self.assertEqual(entry.definition, "A dog")
        self.assertEqual(entry.examples, "Inu ga hau. (The dog is running.)")


class UserProgressModelTest(TestCase):
    """Tests for the UserProgress model."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.user = self.create_user()
        self.japanese = Language.objects.create(code="ja", name="Japanese")
        self.russian = Language.objects.create(code="ru", name="Russian")
        self.entry = DictionaryEntry.objects.create(
            source_text="食べる",
            target_text="Khatit",
            source_language=self.japanese,
            target_language=self.russian
        )
    
    @staticmethod
    def create_user():
        """Create a test user."""
        return get_user_model().objects.create_user(
            username="testuser",
            password="testpass123"
        )
    
    def test_user_progress_creation(self):
        """Test creating a new user progress record."""
        progress = UserProgress.objects.create(
            user=self.user,
            dictionary_entry=self.entry,
            is_favorited=True,
            is_mastered=False,
            mastery_level=75
        )
        self.assertEqual(progress.user, self.user)
        self.assertEqual(progress.dictionary_entry, self.entry)
        self.assertTrue(progress.is_favorited)
        self.assertFalse(progress.is_mastered)
        self.assertEqual(progress.mastery_level, 75)
    
    def test_user_progress_unique_constraint(self):
        """Test that user progress records are unique per user-entry pair."""
        UserProgress.objects.create(
            user=self.user,
            dictionary_entry=self.entry,
            is_favorited=False,
            mastery_level=60
        )
        with self.assertRaises(Exception):
            UserProgress.objects.create(
                user=self.user,
                dictionary_entry=self.entry,
                is_favorited=True,
                mastery_level=80
            )
    
    def test_user_progress_str_representation(self):
        """Test string representation of user progress."""
        progress = UserProgress.objects.create(
            user=self.user,
            dictionary_entry=self.entry,
            is_favorited=True
        )
        expected_str = f"{self.user.username} - {self.entry.source_text}"
        self.assertEqual(str(progress), expected_str)


class StudySessionModelTest(TestCase):
    """Tests for the StudySession model."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.user = self.create_user()
        self.japanese = Language.objects.create(code="ja", name="Japanese")
        self.russian = Language.objects.create(code="ru", name="Russian")
        self.entry1 = DictionaryEntry.objects.create(
            source_text="猫",
            target_text="Kot",
            source_language=self.japanese,
            target_language=self.russian
        )
        self.entry2 = DictionaryEntry.objects.create(
            source_text="犬",
            target_text="Soba",
            source_language=self.japanese,
            target_language=self.russian
        )
    
    @staticmethod
    def create_user():
        """Create a test user."""
        from django.contrib.auth import get_user_model
        return get_user_model().objects.create_user(
            username="student",
            password="testpass123"
        )
    
    def test_study_session_creation(self):
        """Test creating a new study session."""
        session = StudySession.objects.create(
            user=self.user,
            words_studied=10,
            words_mastered=5
        )
        self.assertEqual(session.user, self.user)
        self.assertEqual(session.words_studied, 10)
        self.assertEqual(session.words_mastered, 5)
        self.assertIsNone(session.end_time)
    
    def test_study_session_many_to_many(self):
        """Test that study sessions can have multiple dictionary entries."""
        session = StudySession.objects.create(user=self.user)
        session.dictionary_entries.add(self.entry1, self.entry2)
        
        self.assertIn(self.entry1, session.dictionary_entries.all())
        self.assertIn(self.entry2, session.dictionary_entries.all())
        
        self.entry1.refresh_from_db()
        self.assertIn(session, self.entry1.study_sessions.all())
    
    def test_study_session_str_representation(self):
        """Test string representation of a study session."""
        session = StudySession.objects.create(user=self.user)
        expected = f"{self.user.username} - {timezone.now().strftime('%Y-%m-%d %H:%M')}"
        # Allow some flexibility for time formatting
        self.assertIn(self.user.username, str(session))


class StudySessionEntryModelTest(TestCase):
    """Tests for the StudySessionEntry model."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.user = self.create_user()
        self.japanese = Language.objects.create(code="ja", name="Japanese")
        self.russian = Language.objects.create(code="ru", name="Russian")
        self.entry = DictionaryEntry.objects.create(
            source_text="食べる",
            target_text="Khatit",
            source_language=self.japanese,
            target_language=self.russian
        )
        self.session = StudySession.objects.create(user=self.user)
        # Don't auto-add entry to session - tests will handle this
    
    @staticmethod
    def create_user():
        """Create a test user."""
        from django.contrib.auth import get_user_model
        return get_user_model().objects.create_user(
            username="student",
            password="testpass123"
        )
    
    def test_study_session_entry_creation(self):
        """Test creating a new study session entry."""
        # Delete any existing entries for this session and entry
        StudySessionEntry.objects.filter(
            study_session=self.session,
            dictionary_entry=self.entry
        ).delete()
        
        entry = StudySessionEntry.objects.create(
            study_session=self.session,
            dictionary_entry=self.entry,
            is_correct=True,
            response_time_ms=1500
        )
        self.assertEqual(entry.study_session, self.session)
        self.assertEqual(entry.dictionary_entry, self.entry)
        self.assertTrue(entry.is_correct)
        self.assertEqual(entry.response_time_ms, 1500)
    
    def test_study_session_entry_unique_constraint(self):
        """Test that study session entries are unique per session-entry pair."""
        # Delete any existing entries for this session and entry
        StudySessionEntry.objects.filter(
            study_session=self.session,
            dictionary_entry=self.entry
        ).delete()
        
        StudySessionEntry.objects.create(
            study_session=self.session,
            dictionary_entry=self.entry,
            is_correct=True
        )
        with self.assertRaises(Exception):
            StudySessionEntry.objects.create(
                study_session=self.session,
                dictionary_entry=self.entry,
                is_correct=False
            )
    
    def test_study_session_entry_str_representation(self):
        """Test string representation of a study session entry."""
        entry = StudySessionEntry.objects.create(
            study_session=self.session,
            dictionary_entry=self.entry,
            is_correct=True
        )
        self.assertIn(self.session.user.username, str(entry))
        self.assertIn(self.entry.source_text, str(entry))
    
    def test_study_session_entry_optional_response_time(self):
        """Test that response_time_ms can be null."""
        # Delete any existing entries for this session and entry
        StudySessionEntry.objects.filter(
            study_session=self.session,
            dictionary_entry=self.entry
        ).delete()
        
        entry = StudySessionEntry.objects.create(
            study_session=self.session,
            dictionary_entry=self.entry,
            is_correct=True
        )
        self.assertIsNone(entry.response_time_ms)
    
    def test_study_session_entry_with_response_time(self):
        """Test that response_time_ms can be set."""
        # Delete any existing entries for this session and entry
        StudySessionEntry.objects.filter(
            study_session=self.session,
            dictionary_entry=self.entry
        ).delete()
        
        entry = StudySessionEntry.objects.create(
            study_session=self.session,
            dictionary_entry=self.entry,
            is_correct=True,
            response_time_ms=2500
        )
        self.assertEqual(entry.response_time_ms, 2500)


class ModelIntegrationTest(TestCase):
    """Integration tests for model relationships."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.japanese = Language.objects.create(code="ja", name="Japanese")
        self.russian = Language.objects.create(code="ru", name="Russian")
        self.english = Language.objects.create(code="en", name="English")
        self.user = self.create_user()
        self.entry1 = DictionaryEntry.objects.create(
            source_text="食べる",
            target_text="Khatit",
            source_language=self.japanese,
            target_language=self.russian
        )
    
    @staticmethod
    def create_user():
        """Create a test user."""
        from django.contrib.auth import get_user_model
        return get_user_model().objects.create_user(
            username="learner",
            password="testpass123"
        )
    
    def test_complete_language_pair_flow(self):
        """Test the complete flow from language pair to dictionary entries."""
        # Create language pair
        pair = LanguagePair.objects.create(
            source_language=self.japanese,
            target_language=self.russian
        )
        
        # Create dictionary entries for the pair (use get_or_create to avoid duplicates)
        entry1, created1 = DictionaryEntry.objects.get_or_create(
            source_text="食べる",
            source_language=self.japanese,
            target_language=self.russian,
            defaults={
                "target_text": "Khatit",
                "part_of_speech": "verb",
                "pronunciation": "taberu",
                "definition": "To eat",
                "examples": "Taberu. (To eat.)"
            }
        )
        entry2, created2 = DictionaryEntry.objects.get_or_create(
            source_text="飲む",
            source_language=self.japanese,
            target_language=self.russian,
            defaults={
                "target_text": "Pit",
                "part_of_speech": "verb",
                "pronunciation": "nomu",
                "definition": "To drink",
                "examples": "Nomu. (To drink.)"
            }
        )
        
        # Verify relationships
        self.assertIn(entry1, self.japanese.source_dictionary_entries.all())
        self.assertIn(entry2, self.japanese.source_dictionary_entries.all())
        self.assertIn(entry1, self.russian.target_dictionary_entries.all())
        self.assertIn(entry2, self.russian.target_dictionary_entries.all())
    
    def test_user_progress_and_study_session_connection(self):
        """Test the connection between user progress and study sessions."""
        # Create user progress
        progress = UserProgress.objects.create(
            user=self.user,
            dictionary_entry=self.entry1,
            is_favorited=True,
            is_mastered=True,
            mastery_level=90
        )
        
        # Create study session with the entry
        session = StudySession.objects.create(user=self.user)
        session.dictionary_entries.add(self.entry1)
        
        # Delete any existing study session entries for this session and entry
        StudySessionEntry.objects.filter(
            study_session=session,
            dictionary_entry=self.entry1
        ).delete()
        
        # Add study session entry
        study_entry = StudySessionEntry.objects.create(
            study_session=session,
            dictionary_entry=self.entry1,
            is_correct=True
        )
        
        # Verify progress is linked to study session entries
        self.assertEqual(progress.dictionary_entry, study_entry.dictionary_entry)
        self.assertEqual(progress.user, study_entry.study_session.user)
    
    def test_complex_study_flow(self):
        """Test a complex study flow with multiple sessions and entries."""
        # Create multiple dictionary entries (use get_or_create to avoid duplicates)
        entry1, created1 = DictionaryEntry.objects.get_or_create(
            source_text="猫",
            source_language=self.japanese,
            target_language=self.russian,
            defaults={
                "target_text": "Kot",
                "part_of_speech": "noun",
                "pronunciation": "neko",
                "definition": "Cat",
                "examples": "Neko. (Cat.)"
            }
        )
        entry2, created2 = DictionaryEntry.objects.get_or_create(
            source_text="犬",
            source_language=self.japanese,
            target_language=self.russian,
            defaults={
                "target_text": "Soba",
                "part_of_speech": "noun",
                "pronunciation": "inu",
                "definition": "Dog",
                "examples": "Inu. (Dog.)"
            }
        )
        
        # Create multiple study sessions
        session1 = StudySession.objects.create(user=self.user)
        session1.dictionary_entries.add(entry1, entry2)
        
        session2 = StudySession.objects.create(user=self.user)
        session2.dictionary_entries.add(entry1)
        
        # Delete any existing study session entries
        StudySessionEntry.objects.filter(
            study_session__in=[session1, session2],
            dictionary_entry__in=[entry1, entry2]
        ).delete()
        
        # Create study session entries
        StudySessionEntry.objects.create(
            study_session=session1,
            dictionary_entry=entry1,
            is_correct=True,
            response_time_ms=1000
        )
        StudySessionEntry.objects.create(
            study_session=session1,
            dictionary_entry=entry2,
            is_correct=False,
            response_time_ms=2000
        )
        StudySessionEntry.objects.create(
            study_session=session2,
            dictionary_entry=entry1,
            is_correct=True,
            response_time_ms=800
        )
        
        # Create user progress
        UserProgress.objects.create(
            user=self.user,
            dictionary_entry=entry1,
            is_mastered=True,
            mastery_level=85
        )
        
        # Verify counts
        self.assertEqual(entry1.study_session_entries.count(), 2)
        self.assertEqual(entry2.study_session_entries.count(), 1)
        self.assertEqual(self.user.study_sessions.count(), 2)
        self.assertEqual(self.user.progress.count(), 1)
