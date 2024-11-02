from Listings.models import Category
from rest_framework import serializers
from users.models import User
from Lead.models import (
    LeadBucket, BusinessPageLead, BusinessPageLeadBucket, Lead, LeadPrice, LeadFrorm, LeadFormQuestion, 
    ComboLead, AssignedLeadPerPremiumPlan, BusinessPageLeadView,
    LeadBanner
    )
from django import forms
from decouple import config


IS_DEVELOPMENT = config('IS_DEVELOPMENT')


if IS_DEVELOPMENT == 'True':
    media_domain_name = 'http://127.0.0.1:8000'
else:
    media_domain_name = 'https://mdwebzotica.famousbusiness.in'


#Include in Client Lead
class LeadPriceSerializer(serializers.ModelSerializer):

    class Meta:
        model = LeadPrice
        fields = ['price',]


class LeadSerializer(serializers.ModelSerializer):
    price                 = LeadPriceSerializer()
    # remaining_lead_viewed = serializers.SerializerMethodField()
    # sum_lead_viewed       = serializers.SerializerMethodField()

    class Meta:
        model = Lead
        fields ='__all__'

    # def get_remaining_lead_viewed(self, obj):
    #     business_viewed_lead_count = BusinessPageLeadBucket.count_viewed_users(lead_id=obj.id)
    #     business_paid_lead_count = BusinessPageLeadBucket.count_paid_users(lead_id=obj.id)
    #     users_lead_count = LeadBucket.count_paid_users(lead_id=obj.id)
    #     sum_lead_viewed = business_viewed_lead_count + users_lead_count + business_paid_lead_count
    #     remaining_views_on_lead = max(0, sum_lead_viewed - 10)
    #     return remaining_views_on_lead
    
    # def get_sum_lead_viewed(self, obj):
    #     business_viewed_lead_count = BusinessPageLeadBucket.count_viewed_users(lead_id=obj.id)
    #     business_paid_lead_count = BusinessPageLeadBucket.count_paid_users(lead_id=obj.id)
    #     users_lead_count = LeadBucket.count_paid_users(lead_id=obj.id)
    #     sum_lead_viewed = business_viewed_lead_count + users_lead_count + business_paid_lead_count
       
    #     return sum_lead_viewed


class ClientLeadSerializer(serializers.ModelSerializer):

    class Meta:
        model = Lead
        fields = ['id']



# class CategoryLeadGenerateSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = Lead
#         fields = ['category']



class EnquiryFormSerializer(serializers.Serializer):
    name          = serializers.CharField()
    mobile_number = serializers.CharField()
    category      = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    requirements  = serializers.CharField()
    city          = serializers.CharField()
    state         = serializers.CharField()
    # email         = serializers.CharField()
    # pincode       = serializers.CharField()




class BusinessPageLeadSerializer(serializers.Serializer):
    name          = serializers.CharField()
    mobile_number = serializers.CharField()
    requirements  = serializers.CharField()



class IndividualLeadsSerializer(serializers.ModelSerializer):

    class Meta:
        model = BusinessPageLead
        fields = '__all__'



class LeadPaymentSerializer(serializers.Serializer):
    lead_id = serializers.IntegerField()
    amount  = serializers.IntegerField()



class ComboLeadPaymentSerializer(serializers.Serializer):
    amount  = serializers.IntegerField()




#User in(Show All Leads)
class IndividualPageLeadWithoutAllDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = BusinessPageLead
        fields = ['id', 'requirement', 'state', 'city', 'pincode', 'created_at', 'status', 'created_by' ]



#User in(Show All Leads)
class LeadWithoutAllDataSerializer(serializers.ModelSerializer):
    # remaining_lead_viewed = serializers.SerializerMethodField()
    # sum_lead_viewed       = serializers.SerializerMethodField()

    class Meta:
        model = Lead
        fields = ['id', 'requirement', 'state', 'city', 'created_at', 'status', 'pincode', 'views']


    # def get_remaining_lead_viewed(self, obj):
    #     business_viewed_lead_count = BusinessPageLeadBucket.count_viewed_users(lead_id=obj.id)
    #     business_paid_lead_count = BusinessPageLeadBucket.count_paid_users(lead_id=obj.id)
    #     users_lead_count = LeadBucket.count_paid_users(lead_id=obj.id)
    #     sum_lead_viewed = business_viewed_lead_count + users_lead_count + business_paid_lead_count
    #     remaining_views_on_lead = max(0, sum_lead_viewed - 10)
    #     return remaining_views_on_lead
    
    # def get_sum_lead_viewed(self, obj):
    #     business_viewed_lead_count = BusinessPageLeadBucket.count_viewed_users(lead_id=obj.id)
    #     business_paid_lead_count = BusinessPageLeadBucket.count_paid_users(lead_id=obj.id)
    #     users_lead_count = LeadBucket.count_paid_users(lead_id=obj.id)
    #     sum_lead_viewed = business_viewed_lead_count + users_lead_count + business_paid_lead_count
       
    #     return sum_lead_viewed



#User in(Show All Leads)
class PriceLeadWithoutAllDataSerializer(serializers.ModelSerializer):
    price = LeadPriceSerializer()
    # remaining_lead_viewed = serializers.SerializerMethodField()
    # sum_lead_viewed = serializers.SerializerMethodField()

    class Meta:
        model = Lead
        fields = ['id', 'requirement', 'state', 'city', 'created_at', 'price', 'status', 'pincode', 'views', 'created_by']

    # def get_remaining_lead_viewed(self, obj):
    #     business_viewed_lead_count = BusinessPageLeadBucket.count_viewed_users(lead_id=obj.id)
    #     business_paid_lead_count = BusinessPageLeadBucket.count_paid_users(lead_id=obj.id)
    #     users_lead_count = LeadBucket.count_paid_users(lead_id=obj.id)
    #     sum_lead_viewed = business_viewed_lead_count + users_lead_count + business_paid_lead_count
    #     remaining_views_on_lead = max(0, sum_lead_viewed - 10)
    #     return remaining_views_on_lead
    
    # def get_sum_lead_viewed(self, obj):
    #     business_viewed_lead_count = BusinessPageLeadBucket.count_viewed_users(lead_id=obj.id)
    #     business_paid_lead_count = BusinessPageLeadBucket.count_paid_users(lead_id=obj.id)
    #     users_lead_count = LeadBucket.count_paid_users(lead_id=obj.id)
    #     sum_lead_viewed = business_viewed_lead_count + users_lead_count + business_paid_lead_count
       
    #     return sum_lead_viewed




class PaidLeadSerializers(serializers.ModelSerializer):
    lead = LeadSerializer()

    class Meta:
        model = BusinessPageLeadBucket
        fields = ('lead',)



class LeadExcelUploadFrom(forms.Form):
    excel_file = forms.FileField()



class ComboLeadSerializer(serializers.ModelSerializer):

    class Meta:
        model = ComboLead
        fields = "__all__"


class AssignedPremiumPlanLeadSerializer(serializers.ModelSerializer):
    lead = LeadSerializer()

    class Meta:
        model = AssignedLeadPerPremiumPlan
        fields = ("lead",)



class UsersPaidLeadSerializer(serializers.ModelSerializer):
    lead = LeadSerializer()

    class Meta:
        model = LeadBucket
        fields = ('lead',)



## Send Viewed Lead to user
class BusinessPageleadViewSerializer(serializers.ModelSerializer):
    lead = LeadSerializer()

    class Meta:
        model = BusinessPageLeadView
        fields = ('lead',)


### Lead form questions
class GetLeadFormQuestionSerializer(serializers.ModelSerializer):

    class Meta:
        model = LeadFormQuestion
        fields = '__all__' 



### Serializer to get all Lead form data category wise
class GetLeadFormSerializer(serializers.ModelSerializer):
    question_1_data = GetLeadFormQuestionSerializer(source='question_1', read_only=True)
    question_2_data = GetLeadFormQuestionSerializer(source='question_2', read_only=True)
    question_3_data = GetLeadFormQuestionSerializer(source='question_3', read_only=True)
    question_4_data = GetLeadFormQuestionSerializer(source='question_4', read_only=True)

    class Meta:
        model = LeadFrorm
        fields = [
            'id', 'category', 'headline', 'description_1', 'd1_required',
            'description_2', 'd2_required', 'description_3', 'd3_required',
            'question_1_data', 'q1_required', 
            'question_2_data', 'q2_required', 
            'question_3_data', 'q3_required', 
            'question_4_data', 'q4_required', 
            'background_img', 'logo',
            'city', 'city_required', 'state', 'state_required',
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        domain_name = media_domain_name

        if representation.get('background_img'):
            representation['background_img'] = f"{representation['background_img']}"

        if representation.get('logo'):
            representation['logo'] = f"{representation['logo']}"

        return representation
    



### Serialize banner for Lead Banner
class LeadBannerSerializer(serializers.ModelSerializer):

    class Meta:
        model = LeadBanner
        fields = "__all__"




