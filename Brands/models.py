from django.db import models
from users.models import User
from django.core.validators import MaxValueValidator, MinValueValidator





class BrandBusinessPage(models.Model):
    owner           = models.OneToOneField(User, on_delete=models.CASCADE)
    brand_name      = models.CharField(max_length=1000, unique=True)
    business_name   = models.CharField(max_length=100, blank=True, null=True, unique=True)
    category        = models.ManyToManyField('Listings.Category')
    email           = models.EmailField(null=True, blank=True, unique=True)
    mobile_number   = models.CharField(max_length=16, null=True, blank=True, unique=True)
    whatsapp_number = models.CharField(max_length=16, null=True, blank=True, unique=True)
    GSTN            = models.CharField(max_length=50, null=True, blank=True, unique=True)
    CIN_No          = models.CharField(max_length=50, null=True, blank=True, unique=True)
    DIN             = models.CharField(max_length=100, null=True, blank=True, unique=True)
    RoC             = models.CharField(max_length=50, null=True, blank=True, verbose_name='RoC')
    company_No      = models.CharField(max_length=100, null=True, blank=True, verbose_name='Company Number', unique=True)
    director        = models.CharField(max_length=200, null=True, blank=True)
    address         = models.CharField(max_length=200, null=True, blank=True)
    about           = models.TextField(null=True, blank=True, verbose_name='About us')
    web_url         = models.URLField(null=True, blank=True)
    turn_over       = models.CharField(max_length=100, null=True, blank=True, verbose_name='Annual Turn Over')
    employee_count  = models.CharField(verbose_name='Total Number of Employee', null=True, blank=True, max_length=225)
    verified        = models.BooleanField(default=False, null=True, blank=True)
    trusted         = models.BooleanField(default=False, null=True, blank=True)
    trending        = models.BooleanField(default=False, null=True, blank=True)
    authorized      = models.BooleanField(default=False, verbose_name='Authorized Dealer')
    keywords        = models.TextField(verbose_name='Search Keywords', null=True, blank=True)
    establishment   = models.IntegerField(
        null=True,
        blank=True,
        validators=[
            MaxValueValidator(9999),
            MinValueValidator(1000)
        ],
        verbose_name='Establishment Year'
    )
    nature          = models.CharField(max_length=100, verbose_name='Nature of Business', null=True, blank=True)
    service         = models.TextField(null=True, blank=True, verbose_name='Product & Service')
    icons           = models.FileField(upload_to='Brand_Pics', verbose_name='Brand Icons', default='Brand_Pics/brand_icon.jpg')
    industry_leader = models.BooleanField(default=False, verbose_name='Industry Leader')
    sponsor         = models.BooleanField(default=False, verbose_name='Sponsor Listings')
    super           = models.BooleanField(default=False, verbose_name='Super Seller')
    premium         = models.BooleanField(default=False, verbose_name='Premium Seller')
    opening_time    = models.TimeField(null=True, blank=True, verbose_name='Opening Time')
    closing_time    = models.TimeField(null=True, blank=True, verbose_name='Closing Time')

    
    def __str__(self) -> str:
        return self.brand_name
    
    class Meta:
        ordering = ["-id"]


class BrandProducts(models.Model):
    brand       = models.ForeignKey(BrandBusinessPage, on_delete=models.CASCADE)
    name        = models.CharField(max_length=250, verbose_name='Product Name')
    price       = models.CharField(max_length=15, verbose_name='Product Price')
    image       = models.FileField(upload_to='Brand_Products', default='Brand_Products.default.jpg')
    description = models.TextField(null=True, blank=True)
    trending    = models.BooleanField(default=False)


    def __str__(self) -> str:
        return f'{self.name}'
    
    class Meta:
        ordering = ["-id"]
    


class BrandBanner(models.Model):
    brand = models.ForeignKey(BrandBusinessPage, on_delete=models.CASCADE)
    image = models.FileField(upload_to='Brand_Banners', default='brand_banner.jpg', verbose_name='Brand Banner')


    def __str__(self) -> str:
        return self.brand.brand_name
    
    
    class Meta:
        ordering = ["-id"]