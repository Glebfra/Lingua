from rest_framework import serializers

from lingua_dictionary.models import DictionaryEntry
from lingua_dictionary.serializers import DictionaryEntryField, DictionaryEntrySerializer
from .models import StudySession, StudySessionEntry, UserProgress


class UserProgressSerializer(serializers.ModelSerializer[UserProgress]):
    """Serializer for UserProgress model."""
    
    dictionary_entry = DictionaryEntrySerializer(read_only=True)
    user = serializers.ReadOnlyField(source="user.username")
    
    class Meta:
        model = UserProgress
        fields = [
            "id",
            "user",
            "dictionary_entry",
            "is_favorited",
            "is_mastered",
            "mastery_level",
            "learned_at",
            "last_reviewed_at",
            "review_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class UserProgressCreateSerializer(serializers.ModelSerializer[UserProgress]):
    """Serializer for creating UserProgress model."""
    
    dictionary_entry_id = serializers.IntegerField(source="dictionary_entry", required=True)
    
    class Meta:
        model = UserProgress
        fields = [
            "dictionary_entry_id",
            "is_favorited",
            "is_mastered",
            "mastery_level",
        ]
    
    def validate(self, attrs):
        """Validate user progress."""
        # Handle both dictionary_entry_id (int) and dictionary_entry (dict)
        dictionary_entry_id = attrs.get("dictionary_entry_id") or attrs.get("dictionary_entry")
        
        if not dictionary_entry_id:
            raise serializers.ValidationError({
                "dictionary_entry": "Dictionary entry ID is required."
            })
        
        # Get the dictionary entry instance
        try:
            dictionary_entry = DictionaryEntry.objects.get(id=dictionary_entry_id)
            attrs["dictionary_entry"] = dictionary_entry
        except DictionaryEntry.DoesNotExist:
            raise serializers.ValidationError({
                "dictionary_entry": "Dictionary entry not found."
            })
        
        is_mastered = attrs.get("is_mastered", False)
        mastery_level = attrs.get("mastery_level", 0)
        
        # If marked as mastered, mastery_level must be at least 80
        if is_mastered and mastery_level < 80:
            raise serializers.ValidationError({
                "mastery_level": "To mark as mastered, mastery_level must be at least 80."
            })
        
        return attrs
    
    def create(self, validated_data):
        """Create user progress."""
        # Get user from context if not in validated_data
        user = validated_data.get("user") or self.context.get("user")
        if not user:
            raise serializers.ValidationError("User is required.")
        
        # dictionary_entry is already an instance from validate()
        dictionary_entry = validated_data["dictionary_entry"]
        
        # Check if progress already exists
        progress, created = UserProgress.objects.get_or_create(
            user=user,
            dictionary_entry=dictionary_entry,
            defaults=validated_data
        )
        
        if not created:
            # Update existing progress
            for key, value in validated_data.items():
                if key not in ["user", "dictionary_entry", "dictionary_entry_id"]:
                    setattr(progress, key, value)
            progress.save()
        
        return progress


class StudySessionSerializer(serializers.ModelSerializer[StudySession]):
    """Serializer for StudySession model."""
    
    user = serializers.ReadOnlyField(source="user.username")
    
    class Meta:
        model = StudySession
        fields = [
            "id",
            "user",
            "dictionary_entries",
            "start_time",
            "end_time",
            "words_studied",
            "words_mastered",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class StudySessionEntrySerializer(serializers.ModelSerializer[StudySessionEntry]):
    """Serializer for StudySessionEntry model."""
    
    dictionary_entry = DictionaryEntrySerializer(read_only=True)
    study_session = StudySessionSerializer(read_only=True)
    
    class Meta:
        model = StudySessionEntry
        fields = [
            "id",
            "study_session",
            "dictionary_entry",
            "is_correct",
            "response_time_ms",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class StudySessionEntryCreateSerializer(serializers.ModelSerializer[StudySessionEntry]):
    """Serializer for creating StudySessionEntry model."""
    
    dictionary_entry = DictionaryEntryField()
    study_session = serializers.PrimaryKeyRelatedField(queryset=StudySession.objects.all(), write_only=True)
    
    class Meta:
        model = StudySessionEntry
        fields = [
            "study_session",
            "dictionary_entry",
            "is_correct",
            "response_time_ms",
        ]
    
    def to_internal_value(self, data):
        """Accept either integer ID or StudySession instance."""
        if isinstance(data, StudySession):
            return data.pk
        return data
    
    def to_representation(self, instance):
        """Convert StudySession to dict for representation."""
        if isinstance(instance, StudySession):
            return {
                "id": instance.pk,
                "user": instance.user.username,
                "start_time": instance.start_time,
                "end_time": instance.end_time,
                "words_studied": instance.words_studied,
                "words_mastered": instance.words_mastered,
            }
        return instance
    
    def validate(self, attrs):
        """Validate study session entry."""
        if attrs.get("is_correct") is None:
            raise serializers.ValidationError({
                "is_correct": "This field is required."
            })
        
        return attrs
    
    def create(self, validated_data):
        """Create study session entry."""
        # Get study session instance from ID
        study_session_id = validated_data["study_session"]
        study_session = StudySession.objects.get(id=study_session_id)
        
        # Get dictionary_entry instance from dict or ID
        dictionary_entry = validated_data["dictionary_entry"]
        if isinstance(dictionary_entry, dict):
            dictionary_entry = DictionaryEntry.objects.get(id=dictionary_entry["id"])
        elif isinstance(dictionary_entry, int):
            dictionary_entry = DictionaryEntry.objects.get(id=dictionary_entry)
        
        # Check if entry already exists
        defaults = {key: value for key, value in validated_data.items() 
                    if key not in ["study_session", "dictionary_entry"]}
        entry, created = StudySessionEntry.objects.get_or_create(
            study_session=study_session,
            dictionary_entry=dictionary_entry,
            defaults=defaults
        )
        
        if not created:
            # Update existing entry
            for key, value in validated_data.items():
                if key != "study_session":
                    setattr(entry, key, value)
            entry.save()
        
        return entry
