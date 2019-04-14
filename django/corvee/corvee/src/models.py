from django.db import models
from django.utils.timezone import now


class Persoon(models.Model):

    class Meta:
        ordering = ["first_name", "last_name"]
        verbose_name_plural = "Personen"

    def __str__(self):
        return "{0} {1}".format(self.first_name, self.last_name)

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    picture = models.TextField(blank=True, null=True, verbose_name='Foto', editable=True)
    day_friday = models.BooleanField(null=False, default=False)
    day_saturday = models.BooleanField(null=False, default=False)
    latest = models.DateTimeField(default=now, blank=False, editable=True)
    absent = models.DateField(blank=True, null=True, default=None)
    selected = models.BooleanField(null=False, default=False)
