from django.contrib import admin
from oa_cache.models import UserSaltCache, ListCache, ModelCache, SideEffectCache

admin.site.register(UserSaltCache)
admin.site.register(ListCache)
admin.site.register(ModelCache)
admin.site.register(SideEffectCache)
