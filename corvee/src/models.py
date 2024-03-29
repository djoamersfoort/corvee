from django.db import models
from django.utils.timezone import now


class Persoon(models.Model):
    class Meta:
        ordering = ["first_name", "last_name"]
        verbose_name_plural = "Personen"

    def __str__(self):
        return f"{self.first_name} {self.last_name} : {self.selected}"

    @property
    def short_name(self):
        last_name = self.last_name.split()[-1]
        return f"{self.first_name} {last_name.upper()[0]}."

    idp_user_id = models.CharField(max_length=10, default='')
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    picture = models.TextField(blank=True, null=True, verbose_name='Foto', editable=True)
    latest = models.DateTimeField(default=now, blank=False, editable=True)
    absent = models.BooleanField(null=False, blank=False, default=False)
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
