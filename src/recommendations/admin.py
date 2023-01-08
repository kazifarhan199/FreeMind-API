from django.contrib import admin

# Core models
from .models import Labels, Ratings

admin.site.register(Labels)
admin.site.register(Ratings)

# Tracker models
from .models import TrackerPostRecommendation, TrackerGroupRecommendation

admin.site.register(TrackerPostRecommendation)
admin.site.register(TrackerGroupRecommendation)

# Sender models
from .models import SenderGroupRecommendation, SenderPostRecommendation

class ReadOnlyDateAdmin(admin.ModelAdmin):
    readonly_fields = ('date_time',)

admin.site.register(SenderGroupRecommendation, ReadOnlyDateAdmin)
admin.site.register(SenderPostRecommendation, ReadOnlyDateAdmin)
