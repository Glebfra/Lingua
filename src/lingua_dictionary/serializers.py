from inspect import _empty

from rest_framework import serializers

from lingua_languages.models import Language, LanguagePair
from lingua_languages.serializers import LanguageField, LanguageSerializer

from .models import DictionaryEntry


class DictionaryEntrySerializer(serializers.ModelSerializer):
    """Serializer for DictionaryEntry model."""
    
    source_language = LanguageSerializer(read_only=True)
    target_language = LanguageSerializer(read_only=True)
    
    class Meta:
        model = DictionaryEntry
        fields = [
            "id",
            "source_text",
            "target_text",
            "source_language",
            "target_language",
            "part_of_speech",
            "pronunciation",
            "definition",
            "examples",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class DictionaryEntryField(serializers.RelatedField):
    """Field that accepts either primary key or dict object for DictionaryEntry."""
    
    queryset = DictionaryEntry.objects.all()
    
    def to_internal_value(self, data):
        """Accept either integer ID or dict object."""
        if isinstance(data, dict):
            # Extract ID from dict object
            return data.get("id")
        return super().to_internal_value(data)
    
    def run_validation(self, data=None):
        """Additional validation for dict objects."""
        if isinstance(data, dict):
            # Validate that dict has required fields
            if "id" not in data:
                raise serializers.ValidationError("DictionaryEntry dict must contain 'id'")
            if "source_text" not in data:
                raise serializers.ValidationError("DictionaryEntry dict must contain 'source_text'")
            if "target_text" not in data:
                raise serializers.ValidationError("DictionaryEntry dict must contain 'target_text'")
        
        return super().run_validation(data) # type: ignore


class DictionaryEntryCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating DictionaryEntry model."""
    
    source_language = LanguageField(queryset=Language.objects.all())
    target_language = LanguageField(queryset=Language.objects.all())
    
    class Meta:
        model = DictionaryEntry
        fields = [
            "source_text",
            "target_text",
            "source_language",
            "target_language",
            "part_of_speech",
            "pronunciation",
            "definition",
            "examples",
        ]
    
    def validate(self, attrs):
        attrs = super().validate(attrs)

        """Validate the dictionary entry."""
        source_language = attrs.get("source_language")
        target_language = attrs.get("target_language")

        if not source_language or not target_language:
            return attrs

        # A language cannot be translated into itself.
        if source_language == target_language:
            raise serializers.ValidationError({
                "source_language": (
                    "Source and target languages must be different."
                )
            })

        # Check whether the language pair is supported.
        language_pair_exists = LanguagePair.objects.filter(
            source_language=source_language,
            target_language=target_language,
        ).exists()

        if not language_pair_exists:
            raise serializers.ValidationError({
                "language_pair": (
                    "The specified language pair does not exist."
                )
            })

        return attrs
    
    def create(self, validated_data):
        """Create dictionary entry."""
        source_language = validated_data["source_language"]
        target_language = validated_data["target_language"]
        
        return DictionaryEntry.objects.create(
            source_text=validated_data["source_text"],
            target_text=validated_data["target_text"],
            source_language=source_language,
            target_language=target_language,
            part_of_speech=validated_data.get("part_of_speech"),
            pronunciation=validated_data.get("pronunciation"),
            definition=validated_data.get("definition"),
            examples=validated_data.get("examples"),
        )
