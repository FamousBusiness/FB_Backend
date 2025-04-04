from django.contrib import admin
from Listings.models import (
    Business,  BusinessImage, BusinessMobileNumbers, Category, SubCategory, BusinessEmailID, 
    Assigned_Benefits,Order, FooterImage, CategoryWiseBusinessSideImage, ClientOrder, TextMessage,  ProductService, Image,
    FrontCarousel, BusinessPageLike, BusinessPageReviewRating, LocalSchemaSearchKeywords, LocalSchemaSameAs, LocalBusinessSchemaAggregrateRating, LocalSchemaVideoInteractionStatitics, LocalBusinessSchemaVideo, LocalSchemaFacebookInteractionStatitics, LocalBusinessSchemaFaceBook, LocalSchemaInstagramInteractionStatitics, LocalBusinessSchemaInstagram, LocalBusinessSchemaReviews, FAQSchemaMainEntity, BreadCrumbSchamaItemListItem, ArticleSchema,
    BusinessProfileMetaTag, CategoryBreadCrumbSchamaItemListItem, CategoryItemListElementSchema, CategoryItemListSchema, CategoryFAQPageSchema, CategoryArticleSchema, CategoryVideoInteractionStatitics,
    CategoryVideoObjectSchema, CategoryMetaTag, SearchKeyword, SearchKeywordBusinessPosition, SearchKeywordArticleSchema, SearchkeywordMetaTag, SearchKeywordFAQSchemaMainEntity, SearchKeywordLink
)
# from django.core.exceptions import ValidationError
# from django.http import HttpResponseRedirect
# from django.urls import reverse
# from django import forms


@admin.register(SearchKeywordLink)
class SearchKeywordLinkModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'rel', 'href',)
    ordering = ('-id',)


@admin.register(SearchkeywordMetaTag)
class SearchkeywordMetaTagModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'property',)
    ordering = ('id',)



@admin.register(SearchKeywordBusinessPosition)
class SearchKeywordBusinessPositionModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'search_keyword', 'business_page',)
    ordering = ('id',)
    search_fields = ('search_keyword', 'business_page',)



@admin.register(SearchKeyword)
class SearchKeywordModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'city', 'keyword')
    ordering = ('-id',)
    search_fields = ('city', 'keyword',)



class BusinessModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'business_name', 'category', 'email', 'mobile_number', 'state', 'city','verified')
    ordering = ['id']
    empty_value_display = "-empty-"
    search_fields = ('email', 'mobile_number', 'business_name', 'whatsapp_number')




class CategoryModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'trending',)
    ordering = ('id',)
    empty_value_display = "-empty-"



class FrontCarouselModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'image', 'video')
    empty_value_display = "-empty-"


class SubCategoryModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'category', 'name')



class ProductServiceModelAdmin(admin.ModelAdmin):
    list_display = ('id','business', 'name')


class BusinessMobileNumberModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'mobile_number', 'business')


class BusinessEmailIDModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'business')


class BusinessImageModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'business')


class BusinessLikesModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'user','business_page', 'likes')


class BusinessReviewModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'user','business_page', 'rating', 'post_date')





admin.site.register(Image)
admin.site.register(SubCategory, SubCategoryModelAdmin)
admin.site.register(Business, BusinessModelAdmin)
admin.site.register(Category, CategoryModelAdmin)
admin.site.register(FrontCarousel, FrontCarouselModelAdmin)
admin.site.register(Assigned_Benefits)
admin.site.register(Order)
admin.site.register(ClientOrder)
admin.site.register(TextMessage)
admin.site.register(BusinessImage, BusinessImageModelAdmin)
admin.site.register(BusinessMobileNumbers, BusinessMobileNumberModelAdmin)
admin.site.register(BusinessEmailID, BusinessEmailIDModelAdmin)
admin.site.register(ProductService, ProductServiceModelAdmin)
admin.site.register(BusinessPageLike, BusinessLikesModelAdmin)
admin.site.register(BusinessPageReviewRating, BusinessReviewModelAdmin)
admin.site.register(FooterImage)
admin.site.register(CategoryWiseBusinessSideImage)


admin.site.register(LocalSchemaSearchKeywords)
admin.site.register(LocalSchemaSameAs)
admin.site.register(LocalBusinessSchemaAggregrateRating)
admin.site.register(LocalSchemaVideoInteractionStatitics)
admin.site.register(LocalBusinessSchemaVideo)
admin.site.register(LocalSchemaFacebookInteractionStatitics)
admin.site.register(LocalBusinessSchemaFaceBook)
admin.site.register(LocalSchemaInstagramInteractionStatitics)
admin.site.register(LocalBusinessSchemaInstagram)
admin.site.register(LocalBusinessSchemaReviews)
admin.site.register(FAQSchemaMainEntity)
admin.site.register(BreadCrumbSchamaItemListItem)
admin.site.register(ArticleSchema)
admin.site.register(BusinessProfileMetaTag)

admin.site.register(CategoryBreadCrumbSchamaItemListItem)
admin.site.register(CategoryItemListElementSchema)
admin.site.register(CategoryItemListSchema)
admin.site.register(CategoryFAQPageSchema)
admin.site.register(CategoryArticleSchema)
admin.site.register(CategoryVideoInteractionStatitics)
admin.site.register(CategoryVideoObjectSchema)
admin.site.register(CategoryMetaTag)

admin.site.register(SearchKeywordArticleSchema)
admin.site.register(SearchKeywordFAQSchemaMainEntity)







# def clean(self):
#     for obj in FrontCarousel.objects.all():
#         if not obj.has_image_or_video():
#             raise ValidationError('Please add any image or Video')
        
# def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
#     obj = self.get_object(request, object_id)
    
#     if obj and not obj.has_image_or_video():
#         self.message_user(request, "Please add any image or video for Front Carousel with ID {}".format(obj.id), level='ERROR')
#         return HttpResponseRedirect(reverse('admin:%s_%s_change' % (self.opts.app_label,  self.opts.model_name),  args=[object_id]))

# return super().changeform_view(request, object_id, form_url, extra_context)


