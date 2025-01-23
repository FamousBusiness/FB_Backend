from django.db import models
from users.models import User
from django.utils.translation import gettext_lazy as _
from .constants import PaymentStatus
import secrets
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from PremiumPlan.models import PremiumPlan
from Brands.models import BrandBusinessPage
from Ecommerce.models import ProductTag, ProductOffers, ProductSpecification, ProductImages
from Ecommerce.models import EMIOffers
from Ecommerce.models import PinCode




CATEGORY_TYPE = [
    ('B2B', 'B2B'),
    ('B2C', 'B2C')
]  

PRODUCT_RETURN_PERIOD = [
    ('1 Day', '1 Day'), 
    ('2 Days', '2 Days'),
    ('3 Days', '3 Days'),
    ('4 Days', '4 Days'),
    ('5 Days', '5 Days'),
    ('6 Days', '6 Days'),
    ('7 Days', '7 Days'),
    ('8 Days', '8 Days'),
    ('9 Days', '9 Days'),
    ('10 Days', '10 Days'),
    ('11 Days', '11 Days'),
    ('12 Days', '12 Days'),
    ('13 Days', '13 Days'),
    ('14 Days', '14 Days'),
    ('15 Days', '15 Days'),
    ('16 Days', '16 Days'),
    ('17 Days', '17 Days'),
    ('18 Days', '18 Days'),
    ('19 Days', '19 Days'),
    ('20 Days', '20 Days'),
    ('21 Days', '22 Days'),
    ('23 Days', '23 Days'),
    ('24 Days', '24 Days'),
    ('25 Days', '25 Days'),
    ('26 Days', '26 Days'),
    ('27 Days', '28 Days'),
    ('29 Days', '29 Days'),
    ('30 Days', '30 Days'),
    ('31 Days', '31 Days'),
]



### Category table
class Category(models.Model):
    type     = models.CharField(max_length=30, unique=True)
    B2B2C    = models.CharField(max_length=5, choices=CATEGORY_TYPE, null=True, blank=True)
    image    = models.FileField(default='category_pics/B2B.svg', upload_to='category_pics') 
    trending = models.BooleanField(default=False)
    is_store = models.BooleanField(_("Store Category"), default=False, null=True, blank=True)
    store_trending = models.BooleanField(_("Store Trending"), default=False)


    def __str__(self):
        return f'{self.type}'
    
    class Meta:
        ordering = ["type"]


class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name     = models.CharField(max_length=100, null=True, blank=True, unique=True)

    def __str__(self) -> str:
        return self.name
    
    class Meta:
        ordering = ["-id"]



class Business(models.Model):
    owner           = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Business Owner', related_name='business')
    business_name   = models.CharField(max_length=255, unique=False,
                                     verbose_name='Business Name')
    brand           = models.ManyToManyField(BrandBusinessPage, verbose_name='Brand Name', blank=True)
    mobile_number   = models.CharField(max_length=16, null=True, blank=True, unique=True)
    whatsapp_number = models.CharField(max_length=16, null=True, blank=True, unique=True)
    email           = models.EmailField(max_length=200, null=True, blank=True, unique=True)
    category        = models.ForeignKey(Category,on_delete=models.SET_NULL, verbose_name='Category', null=True)
    subcategory     = models.ManyToManyField(SubCategory, verbose_name='Sub Category', blank=True)
    state           = models.CharField(max_length=80, null=True, blank=True)
    city            = models.CharField(max_length=50, null=True, blank=True)
    pincode         = models.CharField(max_length=25, null=True, blank=True)
    locality        = models.CharField(max_length=250, null=True, blank=True)
    address         = models.CharField(max_length=1000, null=True, blank=True)
    website_url     = models.URLField(max_length=200, null=True, blank=True, verbose_name='Website URL')
    GSTIN           = models.CharField(max_length=50, null=True, blank=True, unique=True, verbose_name='GST No')
    CIN_No          = models.CharField(max_length=50, null=True, blank=True, unique=True, verbose_name='CIN No')
    DIN             = models.CharField(max_length=100, null=True, blank=True, unique=True)
    company_No      = models.CharField(max_length=100, null=True, blank=True, verbose_name='Company Number', unique=True)
    RoC             = models.CharField(max_length=50, null=True, blank=True, verbose_name='RoC')
    director        = models.CharField(max_length=200, null=True, blank=True)
    business_info   = models.TextField(null=True, blank=True, verbose_name='About my Business')
    established_on  = models.IntegerField(null=True,blank=True,
        validators=[
            MaxValueValidator(9999),
            MinValueValidator(1000)
        ], verbose_name='Establishment Year')
    services        = models.TextField(blank=True, null=True, verbose_name='Product and Service')
    picture         = models.ImageField(upload_to='Business_pics', default='Business_pics/cart.png', verbose_name='Profile Pic')
    verified        = models.BooleanField(default=False, null=True, blank=True)
    trusted         = models.BooleanField(default=False, null=True, blank=True)
    trending        = models.BooleanField(default=False, null=True, blank=True)
    likes           = models.IntegerField(default=0, null=True, blank=True)
    reviews         = models.IntegerField(default=0, null=True, blank=True)
    keywords        = models.TextField(verbose_name='Search Keywords', null=True, blank=True)
    opening_time    = models.TimeField(null=True, blank=True, verbose_name='Opening Time')
    closing_time    = models.TimeField(null=True, blank=True, verbose_name='Closing Time')
    nature          = models.CharField(max_length=500, null=True, blank=True, verbose_name='Nature of business')
    turn_over       = models.CharField(max_length=200, null=True, blank=True, verbose_name='Annual turn over')
    employee_count  = models.CharField(max_length=225,null=True, blank=True, verbose_name='Number of Employee')
    authorized      = models.BooleanField(default=False, verbose_name='Authorized Dealer')
    industry_leader = models.BooleanField(default=False, verbose_name='Industry Leader')
    sponsor         = models.BooleanField(default=False, verbose_name='Sponsor Listings')
    super           = models.BooleanField(default=False, verbose_name='Super Seller')
    premium         = models.BooleanField(default=False, verbose_name='Premium Seller')



    def __str__(self):
        return f'{self.business_name}'
    
    class Meta:
        ordering = ['-id']
    

class BusinessMobileNumbers(models.Model):
    business      = models.ForeignKey(Business, on_delete=models.CASCADE)
    mobile_number = models.CharField(max_length=40, verbose_name='Mobile Number', unique=True)

    def __str__(self):
        return f"{self.mobile_number}"
    
    class Meta:
        ordering = ["-id"]
    

class BusinessEmailID(models.Model):
    business      = models.ForeignKey(Business, on_delete=models.CASCADE)
    email         = models.EmailField(max_length=250, verbose_name='Email ID', unique=True)


    def __str__(self):
        return f"{self.email}"
    
    class Meta:
        ordering = ["-id"]



class Image(models.Model):
    image = models.ImageField(upload_to='Business_pics/', default='Business_pics/cat-img.png')

    def __str__(self):
        return f"Image {self.id}"
    
    class Meta:
        ordering = ["-id"]
    


class BusinessImage(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    image    = models.ManyToManyField(Image, verbose_name='Profile Pic')

    def __str__(self):
        return f"Profile Pics of {self.business.business_name}"
    
    class Meta:
        ordering = ["-id"]
    
    


class Assigned_Benefits(models.Model):
    user                      = models.ForeignKey(User, on_delete=models.CASCADE)
    plan                      = models.ForeignKey(PremiumPlan, related_name='Plan_benefits', on_delete=models.SET_NULL, null=True)
    jobpost_allowed           = models.PositiveIntegerField(default=0)
    job_posted                = models.PositiveIntegerField(default=0)
    assigned_lead             = models.PositiveIntegerField(default=0)
    ads_allowed               = models.PositiveIntegerField(default=0)
    ads_posted                = models.PositiveIntegerField(default=0)
    ads_views                 = models.PositiveIntegerField(default=0)
    email_allowed             = models.PositiveIntegerField(default=0)
    email_used                = models.PositiveIntegerField(default=0)
    message_allowed           = models.PositiveIntegerField(default=0)
    messages_used             = models.PositiveIntegerField(default=0)
    messenger_message_allowed = models.PositiveIntegerField(default=0)
    messenger_messege_used    = models.PositiveIntegerField(default=0)
    banner_allowed            = models.PositiveIntegerField(default=0)
    banner_used               = models.PositiveIntegerField(default=0)


    @property
    def remaining_ads(self):
        if self.ads_allowed and self.ads_posted:
            return self.ads_posted - self.ads_allowed
        else:
            return None
        

    def __str__(self):
        return f"{self.user.name} Allowed Benefit List"
    
    class Meta:
        ordering = ["-id"]



#Premium Plan Purchase Orders For Business Owner
class Order(models.Model):
    user       = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    plan       = models.ForeignKey(PremiumPlan, on_delete=models.SET_NULL, null=True, blank=True)
    amount     = models.FloatField(_("Amount"), null=False, blank=False)
    order_date = models.DateTimeField(auto_now=True)
    isPaid     = models.BooleanField(default=False)
    details    = models.CharField(max_length=225, blank=True, null=True, verbose_name='Payment Details')
    status     = models.CharField(_("Payment Status"),default=PaymentStatus.PENDING, max_length=254,
        blank=False,
        null=False,
    )
    provider_order_id = models.CharField(
        _("Order ID"), max_length=40, null=False, blank=False
    )
    payment_id = models.CharField(
        _("Payment ID"), max_length=36, null=False, blank=False
    )
    signature_id = models.CharField(
        _("Signature ID"), max_length=128, null=False, blank=False
    )


    def __str__(self):
        return f"{self.id}-{self.status}"
    
    class Meta:
        ordering = ["-id"]




#Client Orders(Whose donot have Business Page)
class ClientOrder(models.Model):
    user   = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.FloatField(_("Amount"), null=True, blank=False)
    isPaid = models.BooleanField(default=False)
    status = models.CharField(_("Payment Status"),default=PaymentStatus.PENDING, max_length=254,
        blank=False,
        null=False,
    )
    details  = models.CharField(max_length=255, null=True, blank=True)
    currency = models.CharField(max_length=50, default='INR')
    provider_order_id  = models.CharField(
        _("Order ID"), max_length=40, null=False, blank=False
    )
    payment_id = models.CharField(
        _("Payment ID"), max_length=36, null=False, blank=False
    )
    signature_id = models.CharField(
        _("Signature ID"), max_length=128, null=False, blank=False
    )  


    def __str__(self):
        return f"{self.id}-{self.status}"
    
    class Meta:
        ordering = ["-id"]
    


class TextMessage(models.Model):
    sender   = models.ForeignKey(User, on_delete=models.CASCADE)
    receiver = models.ManyToManyField(User, related_name='Received_Message')
    message  = models.TextField()
    sent_on  = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    verified = models.BooleanField(default=False)
    # is_read = models.BooleanField(default=False)


    def __str__(self):
        return f"{self.sender.name} Messages"
    
    class Meta:
        ordering = ["-id"]



class Email(models.Model):
    sender    = models.EmailField()
    receiver  =  models.EmailField()
    sent_date = models.DateField(auto_now_add=True)
    sent_time = models.TimeField(auto_now_add=True)
    subject   = models.CharField(max_length=1000)
    verified  = models.BooleanField(default=False)


    def __str__(self):
        return f'From {self.sender} to {self.receiver}'
    
    class Meta:
        ordering = ["-id"]

    


class FrontCarousel(models.Model):
    image    = models.ImageField(upload_to='carousel_images', null=True, blank=True)
    video    = models.FileField(upload_to='FrontCarousel_videos/', null=True, blank=True)
    url      = models.URLField(verbose_name='Page Url', null=True, blank=True)

    def has_image_or_video(self):
        return self.image or self.video

    def save(self, *args, **kwargs):
        if not self.has_image_or_video():
            raise ValidationError("Please add any image or video")
        super(FrontCarousel, self).save(*args, **kwargs)

    def __str__(self):
        return f'Font Carousel{self.id}'
    
    class Meta:
        ordering = ["-id"]
    



class ProductService(models.Model):
    business     = models.ForeignKey(Business, on_delete=models.CASCADE)
    name         = models.CharField(max_length=200, verbose_name='Product & Service Name')
    picture      = models.FileField(upload_to='product_service/', default='product_service/default.png')
    multiple_img = models.ManyToManyField(ProductImages, blank=True, related_name="product_images", verbose_name="Product Images")
    price        = models.CharField(max_length=15, verbose_name='Product Price', null=True, blank=True)
    description  = models.TextField(null=True, blank=True, verbose_name='Product Small Description')
    description2 = models.TextField(_("Extra Description"), null=True, blank=True)
    product_tag  = models.ForeignKey(ProductTag, on_delete=models.CASCADE, null=True, blank=True)
    category     = models.ForeignKey(Category, null=True, blank=True, on_delete=models.CASCADE, verbose_name=_("Category")) 
    subcategory  = models.ForeignKey(SubCategory, null=True, blank=True, on_delete=models.CASCADE, verbose_name=_("Sub Category"))
    rating       = models.FloatField(_("Product Rating"), null=True, blank=True)
    reviews      = models.CharField(max_length=20, null=True, blank=True)
    discount_price = models.CharField(_("Discount Price"), max_length=20,  null=True, blank=True)
    percentage_off = models.CharField(_("Percentage Off"), max_length=30, null=True, blank=True)
    emi_amount     = models.CharField(_("EMI Amount"), max_length=10, null=True, blank=True)
    offers         = models.ManyToManyField(ProductOffers, blank=True, related_name='product_offers')
    brand          = models.ForeignKey(BrandBusinessPage, null=True, blank=True, on_delete=models.CASCADE, verbose_name='Brand Name')
    specification  = models.ManyToManyField(ProductSpecification, blank=True, related_name='product_specifications')
    is_sponsored   = models.BooleanField(default=False, null=True, blank=True)
    is_available   = models.BooleanField(default=True, null=True, blank=True)
    emi_offers     = models.ManyToManyField(EMIOffers)
    pincode        = models.ManyToManyField(PinCode)
    return_period  = models.CharField(_('Return Period'), max_length=20, choices=PRODUCT_RETURN_PERIOD, default='1 Day')
    return_policy  = models.TextField(_("Return Policy"), null=True)


    def __str__(self):
        return f"{self.name} of {self.business.business_name}"
    
    class Meta:
        ordering = ["-id"]
    


class BusinessPageLike(models.Model):
    user          = models.ForeignKey(User, on_delete=models.CASCADE)
    business_page = models.ForeignKey(Business, on_delete=models.CASCADE)
    likes         = models.IntegerField(default=0)


    def __str__(self) -> str:
        return f"{self.business_page.business_name} has {self.likes} likes"
    
    class Meta:
        ordering = ["-id"]



class BusinessPageReviewRating(models.Model):
    RATING_CHOICES = [
        (1,1),
        (2,2),
        (3,3),
        (4,4),
        (5,5)
    ]
    user          = models.ForeignKey(User, on_delete=models.CASCADE)
    business_page = models.ForeignKey(Business, on_delete=models.CASCADE)
    post_date     = models.DateTimeField(auto_now=True)
    rating        = models.IntegerField(choices=RATING_CHOICES,default=1)
    review        = models.TextField(null=True, blank=True)


    def __str__(self) -> str:
        return f"{self.business_page.business_name} Reviews"  

    class Meta:
        ordering = ["-id"]  



class FooterImage(models.Model):
    image       = models.FileField(upload_to='Footer_Images', default='Footer_Images/default1.svg')
    image2      = models.FileField(upload_to='Footer_Images', default='Footer_Images/default.svg', null=True, blank=True)
    description = models.CharField(max_length=200, null=True, blank=True, verbose_name='Image Description')


    def __str__(self):
        return f"{self.image}"
    
    class Meta:
        ordering = ["-id"]
    

class CategoryWiseBusinessSideImage(models.Model):
    category  = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='categywisebannersideimages')
    image1    = models.FileField(upload_to='CatagoryWiseBusinessSideImages', default='CatagoryWiseBusinessSideImages/default.png')
    image2    = models.FileField(upload_to='CatagoryWiseBusinessSideImages', default='CatagoryWiseBusinessSideImages/default2.png')

    def __str__(self) -> str:
        return f"{self.category.type}\'s Image"
    
    
    class Meta:
        ordering = ["-id"]
    




    

