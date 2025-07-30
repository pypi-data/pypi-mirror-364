from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _


class FeedbackSummaryAdmin(admin.ModelAdmin):
    list_display = [
        "subject",
        "view_on_page",
        "quantity",
        "avg",
        "median",
        "view_addresses_number",
    ]
    list_display_links = None

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.display(description=_("On the page"))
    def view_on_page(self, obj):
        return (
            format_html(
                '<a href="{}?help_rating={}#help-rating-{}" target="_top">{}</a>',
                obj.subject.last_plugin.page.get_absolute_url(),
                obj.subject.pk,
                obj.subject.pk,
                obj.subject.last_plugin.page,
            )
            if obj.subject.last_plugin is not None and obj.subject.last_plugin.page is not None
            else ""
        )

    @admin.display(description=_("Number of addresses"))
    def view_addresses_number(self, obj) -> int:
        return len(obj.subject.feedback_set.values("remote_addr").annotate(remote_addr_count=Count("remote_addr")))
