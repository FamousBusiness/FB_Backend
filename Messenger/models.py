from django.db import models
from users.models import User


class ChatModel(models.Model):
    sender = models.CharField(max_length=100, default=None)
    receiver = models.CharField(max_length=100, default=None)
    message  = models.TextField(null=True, blank=True)
    thread_name = models.CharField(max_length=50, null=True, blank=True)
    time_stamp  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message
    

class ChatNotification(models.Model):
    chat = models.ForeignKey(ChatModel, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_seen = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.user.name
    

class UserProfileModel(models.Model):
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)
    name = models.CharField(blank=True, null=True, max_length=100)
    online_status = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.user.username