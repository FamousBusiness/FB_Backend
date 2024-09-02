from .models import PremiumPlan, PlanDetail, PremiumPlanBenefits
from rest_framework import serializers


#Used(TO get all the plan Details)
class PlanDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = PlanDetail
        fields = "__all__"


#Used(TO get all the plan Details)
class PremiumPlanSerializer(serializers.ModelSerializer):
    plan = PlanDetailSerializer()

    class Meta:
        model = PremiumPlan
        fields = ['id', 'plan']


class PremiumPlanPaymentSerializer(serializers.Serializer):
    amount = serializers.IntegerField()
    


class PremiumPlanDashboardSerializer(serializers.ModelSerializer):
    plan = PremiumPlanSerializer()

    class Meta:
        model = PremiumPlanBenefits
        fields = ['id', 'user', 'plan', 'lead_assigned', 'ads_allowed', 'banner_allowed', 'jobpost_allowed', 'purchased_at', 'expired']

