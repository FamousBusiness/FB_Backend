from django.urls import path
from . import views
from .views import (
    BusinessAPIView, CategoryViewAPIView, CategoryUploadUpdateAPIView, IDWiseBusinessAPIView,
    CategoryWiseBusinessAPIView, BusinessPageSearchAPiView, BusinessMobileNumber, LandigPageAdTesting,
    LandingPageAPIView, SingleListingAPIView, CreateBusinessPageAPiView, StoreUsersView, AllBrandsAPIView,
    BusinessPageLikesView, BusinessPageReviewRatingView, BusinessPageUpdateView, ProductServiceDeleteView, 
    FooterImageAPiView, ProductServiceListCreateView, ProductServiceUpdateView, BusinessPageImageCreateUpdateView, 
   )




urlpatterns = [
    path('',LandingPageAPIView.as_view(), name='landing_page_api'),
    
    #Search Results
    path('page-search/<slug>/', BusinessPageSearchAPiView.as_view(), name='search_api'),
    
    #Category Wise Business
    path('category-wise-business/<city>/<category>/',CategoryWiseBusinessAPIView.as_view(), name='category_wise_business_api'),

    path('category/',CategoryViewAPIView.as_view(), name='category_api'),
    path('category-upload-update/<int:category_id>/', CategoryUploadUpdateAPIView.as_view(), name='category_update_api'),
    path('category-upload-update/', CategoryUploadUpdateAPIView.as_view(), name='category_upload_api'),

    #Businessness Owner Profile Page
    path('individual-business-page/<int:pk>/', IDWiseBusinessAPIView.as_view(), name='individual_business_page'),

    path('all-business-page-api/',BusinessAPIView.as_view(), name='all_business_page'),
    path('create-business-page/', CreateBusinessPageAPiView.as_view(), name='create_business_page'),
    path('single-listing/',SingleListingAPIView.as_view(), name='single_listings'),

    path('business-mobile-number/<int:pk>/', BusinessMobileNumber.as_view(), name='id_wise_business_mobile_number'),

    #Business page Likes and Review Ratings
    path('business-page-like/<int:business_page_id>/', BusinessPageLikesView.as_view(), name='business_page_like'),
    path('business-page-review-rating/<int:business_id>/', BusinessPageReviewRatingView.as_view(), name='business_page_review-rating'),

    #Update Business Page
    path('businesspage-update/<int:business_id>/', BusinessPageUpdateView.as_view(), name='business_page_update'),

    path('business-page-image-create-update/<int:pk>/', BusinessPageImageCreateUpdateView.as_view(), name='business_page_image_create_update'),
    
    path('footer-image/', FooterImageAPiView.as_view(), name='footer_image'),
    
    path('product-services/', ProductServiceListCreateView.as_view(), name='product_service_list_create'),
    path('product-services/<int:pk>/', ProductServiceUpdateView.as_view(), name='product-service-retrieve-update-destroy'),
    path('product-services-delete/', ProductServiceDeleteView.as_view(), name='product-service-retrieve-update-destroy'),

    path('capture-users-view/', StoreUsersView.as_view(), name='users_view'),
    path('landing-page-ad/', LandigPageAdTesting.as_view(), name='landing_page_view'),

    path('all-brands/', AllBrandsAPIView.as_view(), name='all-brands'),

    path('search/keyword/business/', views.SearchKeywordBusinessAPIView.as_view(), name='search_keyword_business'),

    path('location/city/sitemap/', views.LocationCitySitemapAPIView.as_view(), name='location_city_sitemap'),
]


