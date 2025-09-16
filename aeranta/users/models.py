from django.conf import settings
from django.contrib.gis.db import models as gis_models
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    email = models.EmailField(unique=True)
    location = gis_models.PointField(geography=True, null=True, blank=True)
    last_active = models.DateTimeField(default=timezone.now)
    email_nots = models.IntegerField(default=0)
    email_confirmed = models.BooleanField(default=False)
    pending_email = models.EmailField(blank=True, null=True)




