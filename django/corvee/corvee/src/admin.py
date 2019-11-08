from django.contrib import admin
from .models import Persoon, AuditLog

# Register your models here.

admin.site.register(Persoon)
admin.site.register(AuditLog)
