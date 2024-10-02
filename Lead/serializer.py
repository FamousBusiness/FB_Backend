from Listings.models import Category
from rest_framework import serializers
from users.models import User
from Lead.models import (
    LeadBucket, BusinessPageLead, BusinessPageLeadBucket, Lead, LeadPrice,
    ComboLead, AssignedLeadPerPremiumPlan, BusinessPageLeadView
    )
from django import forms


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
    # category      = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    category      = serializers.CharField()
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
        fields = ['id', 'requirement', 'state', 'city', 'pincode', 'created_at', 'status' ]



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
        fields = ['id', 'requirement', 'state', 'city', 'created_at', 'price', 'status', 'pincode', 'views']

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


class BusinessPageleadViewSerializer(serializers.ModelSerializer):
    lead = LeadSerializer()

    class Meta:
        model = BusinessPageLeadView
        fields = ('lead',)






