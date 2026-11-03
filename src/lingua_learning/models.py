from django.db import models

from lingua_dictionary.models import DictionaryEntry

class UserProgress(models.Model):
    """
    Tracks user learning progress.
    
    Attributes:
        user: The user making progress
        dictionary_entry: The dictionary entry being learned
        is_favorited: Whether the user has favorited this entry
        is_mastered: Whether the user has mastered this entry
        mastery_level: Current mastery level (0-100)
        learned_at: First time learned
        last_reviewed_at: Last time reviewed
        review_count: Number of times reviewed
        created_at: Timestamp of creation
        updated_at: Timestamp of last update
    """
    USER_PROGRESS_MAX_LENGTH = 100
    USER_PROGRESS_MIN_LENGTH = 100
    
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='progress'
    )
    dictionary_entry = models.ForeignKey(
        DictionaryEntry,
        on_delete=models.CASCADE,
        related_name='user_progress'
    )
    is_favorited = models.BooleanField(default=False)
    is_mastered = models.BooleanField(default=False)
    mastery_level = models.IntegerField(default=0, help_text="Mastery level from 0 to 100")
    learned_at = models.DateTimeField(blank=True, null=True)
    last_reviewed_at = models.DateTimeField(blank=True, null=True)
    review_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "User Progress"
        unique_together = ["user", "dictionary_entry"]
        ordering = ["user", "last_reviewed_at"]
        indexes = [
            models.Index(fields=["user", "is_mastered"]),
            models.Index(fields=["user", "last_reviewed_at"]),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.dictionary_entry.source_text}"


class StudySession(models.Model):
    """
    Tracks a study session.
    
    Attributes:
        user: The user conducting the study session
        dictionary_entries: Dictionary entries studied in this session
        start_time: When the session started
        end_time: When the session ended
        words_studied: Number of words studied
        words_mastered: Number of words mastered
        created_at: Timestamp of creation
        updated_at: Timestamp of last update
    """
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='study_sessions'
    )
    dictionary_entries = models.ManyToManyField(
        DictionaryEntry,
        through='StudySessionEntry',
        related_name='study_sessions'
    )
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(blank=True, null=True)
    words_studied = models.IntegerField(default=0)
    words_mastered = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Study Sessions"
        ordering = ["-start_time"]
        indexes = [
            models.Index(fields=["user", "-start_time"]),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.start_time.strftime('%Y-%m-%d %H:%M')}"


class StudySessionEntry(models.Model):
    """
    Records a dictionary entry within a study session.
    
    Attributes:
        study_session: The study session this entry belongs to
        dictionary_entry: The dictionary entry
        is_correct: Whether the response was correct
        response_time_ms: Time taken to respond
        created_at: Timestamp of creation
        updated_at: Timestamp of last update
    """
    study_session = models.ForeignKey(
        StudySession,
        on_delete=models.CASCADE,
        related_name='entries'
    )
    dictionary_entry = models.ForeignKey(
        DictionaryEntry,
        on_delete=models.CASCADE,
        related_name='study_session_entries'
    )
    is_correct = models.BooleanField(default=False)
    response_time_ms = models.IntegerField(blank=True, null=True, help_text="Time taken to respond in milliseconds")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Study Session Entries"
        unique_together = ["study_session", "dictionary_entry"]
        ordering = ["study_session", "created_at"]
        indexes = [
            models.Index(fields=["study_session", "is_correct"]),
        ]
    
    def __str__(self):
        return f"{self.study_session} - {self.dictionary_entry.source_text}"
