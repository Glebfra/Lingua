from django.db import models


class Language(models.Model):
    """
    Represents a language supported by the platform.

    Attributes:
        code: ISO 639-1 language code (e.g., 'ja' for Japanese)
        name: Display name of the language
        is_source: Whether this language can be used as a source language
        is_target: Whether this language can be used as a target language
        created_at: Timestamp of creation
        updated_at: Timestamp of last update
    """
    code = models.CharField(max_length=2, unique=True, help_text="ISO 639-1 language code")
    name = models.CharField(max_length=100, help_text="Display name of the language")
    is_source = models.BooleanField(default=True, help_text="Whether this language can be used as a source language")
    is_target = models.BooleanField(default=True, help_text="Whether this language can be used as a target language")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Languages"
        ordering = ["code"]
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["is_source", "is_target"]),
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"


class LanguagePair(models.Model):
    """
    Represents a valid language pair for translation/learning.

    Attributes:
        source_language: The source language in the pair
        target_language: The target language in the pair
        created_at: Timestamp of creation
        updated_at: Timestamp of last update
    """
    source_language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name="source_language_pairs")
    target_language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name="target_language_pairs")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Language Pairs"
        ordering = ["source_language", "target_language"]

        constraints = [
            models.UniqueConstraint(
                fields=("source_language", "target_language"),
                name="unique_language_pair",
            ),
            models.CheckConstraint(
                condition=~models.Q(source_language=models.F("target_language")),
                name="different_languages_in_pair",
            ),
        ]

    def __str__(self):
        return f"{self.source_language.name} -> {self.target_language.name}"
