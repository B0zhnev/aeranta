from django.contrib.auth import get_user_model
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone


class Checker(models.Model):
    parameter_name = models.CharField(max_length=30)
    api = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    description = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f'{self.parameter_name} checker'


class Alert(models.Model):
    name = models.CharField(max_length=30)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    checkers = models.ManyToManyField(Checker)
    users = models.ManyToManyField(get_user_model(), related_name='alerts', blank=True)
    image = models.ImageField(upload_to='alerts/', blank=True, null=True)
    is_published = models.BooleanField(default=False)
    last_checked = models.DateTimeField(default=timezone.now)
    check_interval = models.IntegerField(default=3600)

    @classmethod
    def create_alert(cls, name, slug, description, checkers_list):
        alert = cls.objects.create(name=name, slug=slug, description=description)
        checkers = Checker.objects.filter(parameter_name__in=checkers_list)
        alert.checkers.set(checkers)
        alert.save()
        return alert
