from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _


class FeedbackAdmin(admin.ModelAdmin):
    list_display = ["subject", "view_on_page", "score", "modified", "remote_addr"]
    readonly_fields = [
        "subject",
        "view_on_page",
        "remote_addr",
        "browser_fingerprint",
        "modified",
        "score",
    ]
    list_filter = ["subject__plugin", "modified"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
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
