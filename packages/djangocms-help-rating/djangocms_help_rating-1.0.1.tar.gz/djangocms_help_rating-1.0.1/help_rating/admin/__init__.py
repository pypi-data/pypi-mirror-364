from django.contrib import admin

from ..models import Feedback, FeedbackSummary
from .feedback import FeedbackAdmin
from .summary import FeedbackSummaryAdmin

admin.site.register(Feedback, FeedbackAdmin)
admin.site.register(FeedbackSummary, FeedbackSummaryAdmin)
