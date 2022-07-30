from django.contrib import admin
from corvee.src.models import Persoon, AuditLog, LastSync

# Register your models here.

admin.site.register(Persoon)
admin.site.register(AuditLog)
admin.site.register(LastSync)
