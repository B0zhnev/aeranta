from django.contrib.auth import get_user_model
from django.db import models
from django.conf import settings


class Notification(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='notifications')
    sender = models.CharField(max_length=150)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    local_date = models.CharField(null=True, blank=True)
    local_time = models.CharField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    is_sent = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.sender} -> {self.user.username} at {self.created_at}'


