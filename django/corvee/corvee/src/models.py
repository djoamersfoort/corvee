from django.db import models


class Persoon(models.Model):

    def __str__(self):
        return "{0} {1}".format(self.first_name, self.last_name)

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    picture = models.TextField(blank=True, null=True, verbose_name='Foto', editable=True)
    day_friday = models.BooleanField(null=False, default=False)
    day_saturday = models.BooleanField(null=False, default=False)
    latest = models.DateTimeField(auto_now_add=True, blank=False)
