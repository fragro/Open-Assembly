from django.contrib import admin
from pirate_reputation.models import Reputation, ReputationEvent, ReputationDimension, AbuseTicket

admin.site.register(Reputation)
admin.site.register(ReputationEvent)
admin.site.register(ReputationDimension)
admin.site.register(AbuseTicket)
