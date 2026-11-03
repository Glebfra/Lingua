from django.contrib import admin
from django.db.models import QuerySet

from .models import Language, LanguagePair


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "name",
        "is_source",
        "is_target",
        "created_at",
    )
    list_display_links = ("code", "name")

    list_filter = (
        "is_source",
        "is_target",
        "created_at",
    )

    search_fields = (
        "code",
        "name",
    )

    ordering = ("code",)
    readonly_fields = ("created_at", "updated_at")

    list_per_page = 50
    date_hierarchy = "created_at"
    save_on_top = True

    fieldsets = (
        ("Language Information", {
            "fields": (
                ("code", "name"),
                ("is_source", "is_target"),
            ),
        }),
        ("Metadata", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )


@admin.register(LanguagePair)
class LanguagePairAdmin(admin.ModelAdmin):
    list_display = (
        "source_language",
        "target_language",
        "created_at",
    )
    list_display_links = (
        "source_language",
        "target_language",
    )

    list_filter = (
        "source_language",
        "target_language",
        "created_at",
    )

    search_fields = (
        "source_language__code",
        "source_language__name",
        "target_language__code",
        "target_language__name",
    )

    ordering = (
        "source_language__code",
        "target_language__code",
    )

    readonly_fields = ("created_at", "updated_at")

    list_per_page = 50
    date_hierarchy = "created_at"
    save_on_top = True

    fieldsets = (
        ("Language Pair", {
            "fields": (
                "source_language",
                "target_language",
            ),
        }),
        ("Metadata", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    def get_queryset(self, request) -> QuerySet[LanguagePair]:
        return (
            super()
            .get_queryset(request)
            .select_related("source_language", "target_language")
        )