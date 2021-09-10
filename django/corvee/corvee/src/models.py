from django.db import models
from django.utils.timezone import now
from datetime import date


class Persoon(models.Model):
    class Meta:
        ordering = ["first_name", "last_name"]
        verbose_name_plural = "Personen"

    def is_absent(self):
        return self.absent == date.today()

    def __str__(self):
        return f"{self.first_name} {self.last_name} : {self.selected}"

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    picture = models.TextField(blank=True, null=True, verbose_name='Foto', editable=True)
    day_friday = models.BooleanField(null=False, default=False)
    day_saturday = models.BooleanField(null=False, default=False)
    latest = models.DateTimeField(default=now, blank=False, editable=True)
    absent = models.DateField(blank=True, null=True, default=None)
    selected = models.BooleanField(null=False, default=False)
    marked_for_deletion = models.BooleanField(null=False, default=False)


class AuditLog(models.Model):

    def __str__(self):
        return "{0}: {1} {2} {3} by {4}".format(self.datetime, self.first_name, self.last_name, self.action,
                                                self.performed_by)

    datetime = models.DateField(blank=True, null=True, default=None)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    action = models.CharField(max_length=20)
    performed_by = models.CharField(max_length=255, default='')


class LastSync(models.Model):
    last_sync_date = models.DateField(blank=True, null=True, default='2000-01-01')
