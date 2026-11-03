"""
Command to populate initial dictionary data.
"""
import sys
from django.core.management.base import BaseCommand

from lingua_dictionary.models import DictionaryEntry
from lingua_languages.models import Language, LanguagePair


class Command(BaseCommand):
    help = "Populate initial dictionary data for Japanese language learning"

    def handle(self, *args, **kwargs):
        # Ensure UTF-8 encoding for console output
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stdout.write("Starting data population...\n")

        # Create Japanese and Russian languages
        japanese, created = Language.objects.get_or_create(
            code="ja",
            defaults={
                "name": "Japanese",
                "is_source": True,
                "is_target": True,
            }
        )

        russian, created = Language.objects.get_or_create(
            code="ru",
            defaults={
                "name": "Russian",
                "is_source": True,
                "is_target": True,
            }
        )

        if created:
            sys.stdout.write(f"Created {japanese.code}: {japanese.name}\n")
        else:
            sys.stdout.write(f"{japanese.code}: {japanese.name} already exists\n")

        # Create language pair
        pair, created = LanguagePair.objects.get_or_create(
            source_language=japanese,
            target_language=russian,
        )

        if created:
            sys.stdout.write("Created language pair: Japanese -> Russian\n")
        else:
            sys.stdout.write("Language pair already exists\n")

        # Populate dictionary entries
        entries = [
            {
                "source_text": "こんにちは",
                "target_text": "Привет",
                "part_of_speech": "interjection",
                "pronunciation": "konnichiwa",
                "definition": "Hello, a common greeting",
                "examples": "こんにちは、元気ですか？ (Hello, how are you?)",
            },
            {
                "source_text": "ありがとう",
                "target_text": "Спасибо",
                "part_of_speech": "interjection",
                "pronunciation": "arigatou",
                "definition": "Thank you",
                "examples": "ありがとう、助かります (Thank you, I appreciate it)",
            },
            {
                "source_text": "さようなら",
                "target_text": "До свидания",
                "part_of_speech": "interjection",
                "pronunciation": "sayounara",
                "definition": "Goodbye",
                "examples": "さようなら、また会いましょう (Goodbye, see you again)",
            },
            {
                "source_text": "猫",
                "target_text": "Кошка",
                "part_of_speech": "noun",
                "pronunciation": "neko",
                "definition": "Cat",
                "examples": "猫がベッドで寝ています (The cat is sleeping on the bed)",
            },
            {
                "source_text": "食べる",
                "target_text": "Есть",
                "part_of_speech": "verb",
                "pronunciation": "taberu",
                "definition": "To eat",
                "examples": "私は寿司を食べる (I eat sushi)",
            },
            {
                "source_text": "行く",
                "target_text": "Идти",
                "part_of_speech": "verb",
                "pronunciation": "iku",
                "definition": "To go",
                "examples": "明日学校に行く (I will go to school tomorrow)",
            },
            {
                "source_text": "美しい",
                "target_text": "Красивый",
                "part_of_speech": "adjective",
                "pronunciation": "utsukushii",
                "definition": "Beautiful",
                "examples": "この花は美しい (This flower is beautiful)",
            },
            {
                "source_text": "水",
                "target_text": "Вода",
                "part_of_speech": "noun",
                "pronunciation": "mizu",
                "definition": "Water",
                "examples": "水を飲む (Drink water)",
            },
            {
                "source_text": "学生",
                "target_text": "Студент",
                "part_of_speech": "noun",
                "pronunciation": "gakusei",
                "definition": "Student",
                "examples": "私は学生です (I am a student)",
            },
            {
                "source_text": "日本",
                "target_text": "Япония",
                "part_of_speech": "noun",
                "pronunciation": "nihon",
                "definition": "Japan",
                "examples": "日本はとても美しい国です (Japan is a very beautiful country)",
            },
        ]

        for entry_data in entries:
            entry, created = DictionaryEntry.objects.get_or_create(
                source_text=entry_data["source_text"],
                source_language=japanese,
                target_language=russian,
                defaults=entry_data
            )

            if created:
                sys.stdout.write(f"Created entry: {entry.source_text}\n")
            else:
                sys.stdout.write(f"Entry exists: {entry.source_text}\n")

        sys.stdout.write("\nData population completed!\n")
