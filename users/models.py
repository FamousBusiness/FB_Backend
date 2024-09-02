from django.db import models
import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import BaseUserManager,AbstractBaseUser
# from rest_framework.response import Response
# from django.utils.translation import ugettext_lazy as _

AUTH_PROVIDERS = {'facebook': 'facebook', 'google': 'google',
                  'twitter': 'twitter', 'email': 'email'}


class UserManager(BaseUserManager):

  def create_user(self, mobile_number,  password=None, **extra_fields):

    #   if not email:
    #       raise ValueError('User must have an email address')
      if not mobile_number:
          raise ValueError('User must have an Mobile Number')


    #   user = self.model(
    #       email=self.normalize_email(email),
    #       **extra_fields
    #     #   username=username
    #   )
      user = self.model(
          mobile_number=mobile_number,
          **extra_fields
        #   username=username
      )
 
      user.set_password(password)
      user.save(using=self._db)
      return user


  def create_superuser(self,name, mobile_number, password=None):
      user = self.create_user(
        #   email,
          mobile_number=mobile_number,
          password=password,
          name=name
      )

      user.is_admin = True
    #   user.is_staff = True
      user.is_superuser= True
      user.save(using=self._db)
      return user



class User(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='Email',
        max_length=255,
        unique=True, null=True, blank=True
        )
    name          = models.CharField(verbose_name='User Name',max_length=200)
    password2     = models.CharField(max_length=30, blank=True, null=True)
    mobile_number = models.CharField(max_length=16, blank=True, null=True, unique=True)
    business_name = models.CharField(max_length=255, blank=True, null=True, unique=True)
    location      = models.CharField(max_length=255, blank=True, null=True)
    # auth_provider = models.CharField(
    #     max_length=255, blank=False,
    #     null=False, default=AUTH_PROVIDERS.get('email'))
    # has_business = models.BooleanField(default=False)

    is_staff   = models.BooleanField(default=False)
    is_active  = models.BooleanField(default=True)
    is_admin   = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    # USERNAME_FIELD = 'email'
    USERNAME_FIELD = 'mobile_number'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return f'{self.name}'

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin

    @property
    def has_business(self):
        return self.business is not None



class UsersAgreement(models.Model):
    user               = models.ForeignKey(User, on_delete=models.CASCADE)
    termsandconditions = models.BooleanField(default=False, verbose_name = 'Agreement Signed')
    termspage          = models.URLField(null=True, blank=True, verbose_name = "Terms and Condition\'s ", default='https://famousbusiness.in/about/Terms-Condition')

    def __str__(self) -> str:
        return f'{self.user.name}\'s Agreement'