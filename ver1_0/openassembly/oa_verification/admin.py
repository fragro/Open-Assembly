from django.contrib import admin
from oa_verification.models import ActionTaken, EmailVerification, arpv, Referral, PhotoVerificationTask, PhotoUserVerifications

admin.site.register(ActionTaken)
admin.site.register(EmailVerification)
admin.site.register(arpv)
admin.site.register(Referral)
admin.site.register(PhotoVerificationTask)
admin.site.register(PhotoUserVerifications)
