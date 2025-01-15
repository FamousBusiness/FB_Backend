from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from users.models import User
# from Listings.models import ProductService



USER_ADDRESS_TYPE = [
    ('HOME', 'Home'),
    ('WORK', 'Work'),
]



### Store home page banner
class StoreBanner(models.Model):
    image    = models.ImageField(_("Banner Image"), upload_to='store_banner_img/', null=True, blank=True)
    video    = models.FileField(_("Banner Video"), upload_to='store_banner_video/', null=True, blank=True)
    url      = models.URLField(verbose_name='Url', null=True, blank=True)

    def has_image_or_video(self):
        return self.image or self.video

    def save(self, *args, **kwargs):
        if not self.has_image_or_video():
            raise ValidationError("Please add any image or video")
        super(StoreBanner, self).save(*args, **kwargs)

    def __str__(self):
        return f'Store Banner {self.pk}'
    
    class Meta:
        ordering = ["-id"]




### Product Offer Tag
class ProductTag(models.Model):
    name       = models.CharField(_("Product Tag"), max_length=100)
    is_visible = models.BooleanField(_("Visible"), default=False, null=True, blank=True)

    def __str__(self) -> str:
        return f"Product Tag - {self.name}"
    


### Product offer name
class ProductOffers(models.Model):
    name = models.CharField(_("Offer Name"), max_length=100)

    def __str__(self):
        return f"Offer Name - {self.name}"
    

### Product Specification
class ProductSpecification(models.Model):
    name = models.CharField(_("Specification Name"), max_length=100)
    value = models.CharField(_("Specification Value"), max_length=100)
    

    def __str__(self) -> str:
        return f"Specification - {self.name}"
    

#### Multiple images of Product
class ProductImages(models.Model):
    name = models.CharField(_("Image Nae"), max_length=50)
    image = models.ImageField(upload_to='Productimages/', default='product_service/default.png')

    def __str__(self) -> str:
        return f'Image - {self.name}'
    


class Cart(models.Model):
    user     = models.ForeignKey(User, on_delete=models.CASCADE)
    product  = models.ForeignKey('Listings.ProductService', on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=0)
    

    def __str__(self):
        return f'{self.user.name} - {self.product} - {self.quantity}'
    
    
    class Meta:
        ordering = ['-id']




#### Delivery Address
class UserAddress(models.Model):
    user             = models.ForeignKey(User, on_delete=models.CASCADE)
    name             = models.CharField(_("Name"), max_length=30)
    mobile_number    = models.CharField(_("Mobile Number"), max_length=11)
    pincode          = models.CharField(_('PINCODE'), max_length=10)
    locality         = models.CharField(_("Locality"), max_length=50)
    address          = models.TextField(_("Address"))
    city             = models.CharField(_("City"), max_length=50)
    state            = models.CharField(_("State"), max_length=10)
    landmark         = models.CharField(_("Landmark"), max_length=30, blank=True, null=True)
    alternate_number = models.CharField(_("Alternate Mobile Number"), max_length=11, blank=True, null=True)
    address_tye      = models.CharField(choices=USER_ADDRESS_TYPE, max_length=5)



    def __str__(self):
        return f'{self.user} Address'
    




class ProductOrders(models.Model):
    user               = models.ForeignKey(User, on_delete=models.CASCADE)
    business           = models.ForeignKey('Listings.Business', on_delete=models.CASCADE, null=True)
    product            = models.ForeignKey('Listings.ProductService', on_delete=models.CASCADE)
    quantity           = models.PositiveIntegerField(default=0)
    is_paid            = models.BooleanField(_("Paid"), default=False)
    address            = models.ForeignKey(UserAddress, on_delete=models.SET_NULL, null=True)
    order_placed       = models.BooleanField(_("Order Placed"), null=True)
    order_placed_at    = models.DateTimeField(_("Order Placed Date"), null=True)
    shipped_at         = models.DateTimeField(_("Shipped Date"), null=True)
    is_shipped         = models.BooleanField(_("Order Shipped"), default=False)
    out_of_delivery    = models.BooleanField(_("Out of Delivery"), default=False)
    out_of_delivery_at = models.DateTimeField(_("Out Of Delivery Date"), null=True)
    is_delivered       = models.BooleanField(_("Delivered"), default=False)
    delivered_at       = models.DateTimeField(_("Delivered Date"), null=True)


    def __str__(self):
        return f'{self.product} order of {self.user}'
    



#### Razorpay Order
class EcomRazorPayOrders(models.Model):
    order_product    = models.CharField(_("Product"), max_length=100)
    order_amount     = models.CharField(_("Amount"), max_length=25)
    order_payment_id = models.CharField(_("Payment ID"), max_length=100)
    isPaid           = models.BooleanField(_("Is Paid"), default=False)
    order_date       = models.DateTimeField(_("Order Date"), auto_now=True)


    def __str__(self):
        return self.order_product
    



class EMIOffers(models.Model):
    name = models.CharField(_('EMI Offer Name'), max_length=100)

    def __str__(self):
        return f"{self.name}"



class PinCode(models.Model):
    name = models.CharField(_("Pincode"), max_length=10)

    def __str__(self):
        return f"{self.name}"



    




