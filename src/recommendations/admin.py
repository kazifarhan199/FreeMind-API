from django.contrib import admin

# Core models
from .models import Labels, Ratings

class RatingsAdmin(admin.ModelAdmin):
    search_fields = ('user__username', )
admin.site.register(Ratings, RatingsAdmin)
# admin.site.register(Ratings)


admin.site.register(Labels)

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

from .models import ScheduledGroupTaslk

admin.site.register(ScheduledGroupTaslk, ReadOnlyDateAdmin)