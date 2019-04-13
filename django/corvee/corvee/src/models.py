from django.db import models
import datetime

# Create your models here.

class Persoon(models.Model):
  first_name = models.CharField(max_length=255)
  last_name = models.CharField(max_length=255)
  picture = models.BinaryField(blank=True, null=True, verbose_name='Foto', editable=True)
  day = models.CharField(max_length=8, choices=(('vrijdag', 'Vrijdag'), ('zaterdag', 'Zaterdag')), blank=False, null=False, default='vrijdag')
  latest = models.DateField(auto_now=True, blank=False)
