from pirate_forum.models import View, ForumDimension, DimensionTracker, Question, Nomination, cached_url, Edit
from django.contrib import admin

admin.site.register(View)
admin.site.register(ForumDimension)
admin.site.register(DimensionTracker)
admin.site.register(Question)
admin.site.register(Nomination)
admin.site.register(cached_url)
admin.site.register(Edit)
