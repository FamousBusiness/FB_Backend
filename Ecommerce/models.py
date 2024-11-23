from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _




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