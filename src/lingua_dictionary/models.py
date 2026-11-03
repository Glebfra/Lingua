from django.db import models

from lingua_languages.models import Language


class DictionaryEntry(models.Model):
    """
    Represents a dictionary entry with translations.

    Attributes:
        source_text: The source text/word to translate
        target_text: The target language translation
        source_language: The language of the source text
        target_language: The language of the target text
        part_of_speech: Grammatical category (e.g., noun, verb, adjective)
        pronunciation: Pronunciation guide for the source text
        definition: Definition or explanation of the word
        examples: Example usage sentences
        created_at: Timestamp of creation
        updated_at: Timestamp of last update
    """
    SOURCE_TEXT_MAX_LENGTH = 255
    TARGET_TEXT_MAX_LENGTH = 500
    DEFINITION_MAX_LENGTH = 1000
    EXAMPLE_MAX_LENGTH = 1000

    source_text = models.CharField(
        max_length=SOURCE_TEXT_MAX_LENGTH,
        help_text="Source text/word to translate"
    )
    target_text = models.CharField(
        max_length=TARGET_TEXT_MAX_LENGTH,
        help_text="Target language translation"
    )
    source_language = models.ForeignKey(
        Language,
        on_delete=models.CASCADE,
        related_name="source_dictionary_entries"
    )
    target_language = models.ForeignKey(
        Language,
        on_delete=models.CASCADE,
        related_name="target_dictionary_entries"
    )
    part_of_speech = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Grammatical category (e.g., noun, verb, adjective)"
    )
    pronunciation = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Pronunciation guide for the source text"
    )
    definition = models.TextField(
        blank=True,
        null=True,
        max_length=DEFINITION_MAX_LENGTH,
        help_text="Definition or explanation of the word"
    )
    examples = models.TextField(
        blank=True,
        null=True,
        max_length=EXAMPLE_MAX_LENGTH,
        help_text="Example usage sentences"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Dictionary Entries"
        unique_together = ["source_text", "source_language", "target_language"]
        ordering = ["source_language__code", "source_text"]
        indexes = [
            models.Index(fields=["source_language", "source_text"]),
            models.Index(fields=["target_language", "target_text"]),
            models.Index(fields=["source_language", "target_language"]),
        ]

    def __str__(self):
        return f"{self.source_text} ({self.source_language.code} -> {self.target_language.code})"
