from django.db import models
from Listings.models import Category
from users.models import User
from django.utils.translation import gettext_lazy as _




class Banner(models.Model):
    category   = models.ForeignKey(Category, on_delete=models.CASCADE)
    user       = models.ForeignKey(User, on_delete=models.CASCADE)
    image      = models.FileField(upload_to='Category_Banner', default='Banner/default-banner.jpeg')
    state      = models.CharField(_("State"), max_length=25)
    city       = models.CharField(_("City"), max_length=25)
    verified   = models.BooleanField(default=False)
    expired    = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True, editable=False)

    def save(self, *args, **kwargs):
        if self.expired == True:
            self.verified = False
        super(Banner, self).save(*args, **kwargs)


    def __str__(self):
        return f'{self.user.name}\'s Banner' 