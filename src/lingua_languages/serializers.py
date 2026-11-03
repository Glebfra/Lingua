from typing import override

from rest_framework import serializers

from .models import Language, LanguagePair


class LanguageSerializer(serializers.ModelSerializer):
    """Serializer for Language model."""
    
    code = serializers.CharField(max_length=2)  # Override to remove UniqueValidator
    
    class Meta:
        model = Language
        fields = ["id", "code", "name", "is_source", "is_target", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]


class LanguageField(serializers.RelatedField):
    """Field that accepts either primary key, dict object, or model instance for Language."""
    
    def __init__(self, **kwargs):
        kwargs.setdefault("queryset", Language.objects.all())
        super().__init__(**kwargs)

    def get_queryset(self):
        return getattr(self, "queryset", Language.objects.all())

    def to_internal_value(self, data):
        if isinstance(data, Language):
            return data

        if isinstance(data, dict):
            data = data.get("id")

        try:
            return self.get_queryset().get(pk=data)
        except (Language.DoesNotExist, TypeError, ValueError):
            raise serializers.ValidationError(
                "Invalid language."
            )

    def to_representation(self, value: Language):
        return {
            "id": value.pk,
            "code": value.code,
            "name": value.name,
        }


class LanguagePairSerializer(serializers.ModelSerializer):
    """Serializer for LanguagePair model."""
    
    source_language = LanguageField()
    target_language = LanguageField()
    
    class Meta:
        model = LanguagePair
        fields = ["id", "source_language", "target_language", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
    