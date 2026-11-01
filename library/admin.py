from datetime import date

from django.contrib import admin, messages

from .models import Author, Book, Borrow, Member, Publisher, TechBook


class PriceRangeFilter(admin.SimpleListFilter):
    title = "price range"
    parameter_name = "price_range"

    def lookups(self, request, model_admin):
        return [
            ("low", "Under 20"),
            ("mid", "20 to 50"),
            ("high", "Over 50"),
        ]

    def queryset(self, request, queryset):
        if self.value() == "low":
            return queryset.filter(price__lt=20)
        if self.value() == "mid":
            return queryset.filter(price__gte=20, price__lte=50)
        if self.value() == "high":
            return queryset.filter(price__gt=50)
        return queryset


@admin.action(description="Mark selected books as unavailable")
def mark_unavailable(modeladmin, request, queryset):
    updated = queryset.update(is_available=False)
    modeladmin.message_user(request, f"{updated} book(s) marked unavailable.", messages.SUCCESS)


@admin.action(description="Mark selected books as available")
def mark_available(modeladmin, request, queryset):
    updated = queryset.update(is_available=True)
    modeladmin.message_user(request, f"{updated} book(s) marked available.", messages.SUCCESS)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "isbn", "genre", "price", "published_year", "publisher", "authors_list", "is_available")
    list_display_links = ("title",)
    list_editable = ("is_available",)
    list_filter = ("genre", "language", "is_available", "publisher", PriceRangeFilter)
    search_fields = ("title", "isbn", "authors__name", "publisher__name")
    ordering = ("title",)
    list_per_page = 20
    list_select_related = ("publisher",)
    filter_horizontal = ("authors",)
    readonly_fields = ("created_at", "updated_at")
    actions = [mark_unavailable, mark_available]

    fieldsets = (
        ("Basic info", {"fields": ("title", "isbn", "genre", "language")}),
        ("Pricing and rating", {"fields": ("price", "rating", "published_year")}),
        ("Relations", {"fields": ("publisher", "authors")}),
        ("Other", {"fields": ("description", "is_available")}),
        ("Timestamps", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("authors")

    @admin.display(description="Authors")
    def authors_list(self, obj):
        return ", ".join(a.name for a in obj.authors.all())


@admin.register(TechBook)
class TechBookAdmin(admin.ModelAdmin):
    list_display = ("title", "published_year")


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("name", "born_date")
    search_fields = ("name",)


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ("name", "website")
    search_fields = ("name",)


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ("user", "phone", "joined_on")
    search_fields = ("user__username", "phone")


@admin.action(description="Mark selected borrows as returned today")
def mark_returned(modeladmin, request, queryset):
    updated = queryset.filter(returned_on__isnull=True).update(returned_on=date.today())
    modeladmin.message_user(request, f"{updated} borrow(s) marked returned.", messages.SUCCESS)


@admin.register(Borrow)
class BorrowAdmin(admin.ModelAdmin):
    list_display = ("member", "book", "borrowed_on", "due_date", "returned_on", "overdue")
    list_filter = ("borrowed_on", "due_date")
    search_fields = ("member__user__username", "book__title")
    date_hierarchy = "borrowed_on"
    list_select_related = ("member__user", "book")
    actions = [mark_returned]

    @admin.display(boolean=True, description="Overdue")
    def overdue(self, obj):
        return obj.is_overdue