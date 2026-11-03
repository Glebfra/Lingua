from django.contrib import admin
from django.db.models import QuerySet

from .models import DictionaryEntry


@admin.register(DictionaryEntry)
class DictionaryEntryAdmin(admin.ModelAdmin):
    """Admin configuration for dictionary entries."""

    list_display = (
        "source_text",
        "target_text",
        "source_language",
        "target_language",
        "part_of_speech",
        "created_at",
    )

    list_display_links = (
        "source_text",
    )

    list_filter = (
        "source_language",
        "target_language",
        "part_of_speech",
        "created_at",
    )

    search_fields = (
        "source_text",
        "target_text",
        "pronunciation",
        "definition",
        "examples",
        "source_language__name",
        "source_language__code",
        "target_language__name",
        "target_language__code",
    )

    ordering = (
        "source_language__code",
        "source_text",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    list_per_page = 50
    date_hierarchy = "created_at"
    save_on_top = True

    fieldsets = (
        (
            "Translation",
            {
                "fields": (
                    ("source_language", "target_language"),
                    ("source_text", "target_text"),
                ),
            },
        ),
        (
            "Linguistic Information",
            {
                "fields": (
                    "part_of_speech",
                    "pronunciation",
                    "definition",
                    "examples",
                ),
            },
        ),
        (
            "Metadata",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    @admin.display(description="Translation")
    def translation(self, obj: DictionaryEntry) -> str:
        return f"{obj.source_text} → {obj.target_text}"

    def get_queryset(self, request) -> QuerySet[DictionaryEntry]:
        queryset = super().get_queryset(request)

        return queryset.select_related(
            "source_language",
            "target_language",
        )
