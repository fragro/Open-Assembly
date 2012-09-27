from django.contrib import admin
from pirate_badges.models import Badge, BadgeDimension, BadgeType
    
admin.site.register(Badge)
admin.site.register(BadgeDimension)
admin.site.register(BadgeType)
