from pirate_permissions.models import Permission, PermissionsGroup
from django.contrib import admin

admin.site.register(PermissionsGroup)
admin.site.register(Permission)
