from rest_framework import serializers
from .models import (
    BusinessPageJobPost, BusinessJobPostActivity, BrandJobPostActivity, JobSeekerProfile,
    ApplicantexperienceDetail, ApplicantEducationDetails, BrandJobPost, JOBCategory, ApplicantSkillSet,
    ApplicantResume
    )
from Listings.models import BusinessPageReviewRating, BusinessPageLike, Business

class JOBCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = JOBCategory
        fields = '__all__'

class BusinessPageJobPostSerializer(serializers.ModelSerializer):

    class Meta:
        model = BusinessPageJobPost
        fields = ['company', 'job_type', 'description', 'location', 'salary', 'experience', 'position', 'full_time', 'part_time', 'work_from_home',  'internship', 'work_abroad']

class BrandJobPostSerializer(serializers.ModelSerializer):

    class Meta:
        model = BrandJobPost
        fields = ['company', 'job_type', 'description', 'location', 'salary', 'experience', 'position', 'full_time', 'part_time', 'work_from_home',  'internship', 'work_abroad']


class BusinessPageJobApplySerializer(serializers.ModelSerializer):
    resume = serializers.FileField()

    class Meta:
        model  = BusinessJobPostActivity
        fields = ['job_post', 'resume', 'message']


class BrandJobApplySerializer(serializers.ModelSerializer):
    resume = serializers.FileField()

    class Meta:
        model  = BrandJobPostActivity
        fields = ['job_post', 'resume', 'message']


class AllBusinessPageJobPostSerializer(serializers.ModelSerializer):
    business_name = serializers.SerializerMethodField()

    class Meta:
        model = BusinessPageJobPost
        fields = "__all__"

    def get_business_name(self, obj):
        return obj.company.business_name if obj.company else None


class AllBrandPageJobPostSerializer(serializers.ModelSerializer):
    brand_name = serializers.SerializerMethodField()

    class Meta:
        model = BrandJobPost
        fields = "__all__"

    def get_brand_name(self, obj):
        return obj.company.brand_name if obj.company else None



class JobSeekerProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = JobSeekerProfile
        fields = ['id', 'first_name', 'last_name', 'mobile_number', 'email', 'gender', 'image', 'address', 'current_salary']



class ApplicantResumeSerializer(serializers.ModelSerializer):

    class Meta:
        model = ApplicantResume
        fields = ['id', 'resume']


class ApplicantEducationDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = ApplicantEducationDetails
        fields = ['id', 'education', 'university', 'course', 'specialization', 'course_type', 'start_year', 'end_year', 'marks']


class ApplicantExperienceDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = ApplicantexperienceDetail
        fields = ['id', 'job_title', 'start_date', 'end_date', 'company_name', 'job_location_city', 'job_location_state', 'is_current_job', 'job_location_country', 'description', 'total_experience', 'designation', 'salary', 'job_profile', 'notice_period']


class ApplicantSkillSetSerializer(serializers.ModelSerializer):

    class Meta:
        model = ApplicantSkillSet
        fields = ['id', 'skill_name', 'skill_level']



class CandidateAppliedBusinessJobsSerializer(serializers.ModelSerializer):
    job_post = AllBusinessPageJobPostSerializer(read_only=True)

    class Meta:
        model = BusinessJobPostActivity
        fields = ['applicant', 'job_post', 'apply_date', 'status']


class CandidateAppliedBrandJobsSerializer(serializers.ModelSerializer):
    job_post = AllBrandPageJobPostSerializer(read_only=True)

    class Meta:
        model = BrandJobPostActivity
        fields = ['applicant', 'job_post', 'apply_date', 'status']


class ApplicationStatusByCompanySerializers(serializers.ModelSerializer):

    class Meta:
        model  = BusinessJobPostActivity
        fields = ['applicant', 'job_post', 'status']


class ApplicationStatusByBrandSerializers(serializers.ModelSerializer):

    class Meta:
        model  = BrandJobPostActivity
        fields = ['applicant', 'job_post', 'status']



class BusinessPageReviewRatingSerializer(serializers.ModelSerializer):

    class Meta:
        model = BusinessPageReviewRating
        fields = ['rating']


class BusinessPageLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessPageLike
        fields = ['likes']


class BusinessImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Business
        fields = ['picture']


    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if instance.picture:
            picture_path = f"https://mdwebzotica.famousbusiness.in/{instance.picture.name}"
            representation["picture"] = picture_path

        return representation


class BusinessJobDetailSerializer(serializers.ModelSerializer):
    business_name = serializers.SerializerMethodField()
    state         = serializers.SerializerMethodField()
    city          = serializers.SerializerMethodField()
    category      = serializers.SerializerMethodField() 
    # picture       = serializers.SerializerMethodField()
    ratings       = BusinessPageReviewRatingSerializer(many=True, read_only=True, source='company.businesspagereviewrating_set')
    likes         = BusinessPageLikeSerializer(many=True, read_only=True, source='company.businesspagelike_set')


    class Meta:
        model = BusinessPageJobPost
        fields = "__all__"
        # fields = ['id', 'company', 'job_type', 'created_date', 'description', 'location', 'salary', 'experience', 'position', 'full_time', 'part_time', 'work_from_home', 'internship', 'work_abroad', 'ratings', 'city', 'state', 'business_name', 'category', 'likes', ]

    def get_business_name(self, obj):
        return obj.company.business_name if obj.company else None
    
    def get_state(self, obj):
        return obj.company.state if obj.company else None
    
    def get_city(self, obj):
        return obj.company.city if obj.company else None
    
    def get_category(self, obj):
        return obj.company.category.type if obj.company else None
    
    # def get_picture(self, obj):
    #     return obj.company.picture if obj.company else None
    
    # def get_business_picture(self, business):
    #     if business and business.picture:
    #         picture_path = f"https://mdwebzotica.famousbusiness.in/{business.picture.name}"
    #         return picture_path
    #     return None

    

class BrandJobDetailSerializer(serializers.ModelSerializer):
    brand_name    = serializers.SerializerMethodField()
    address       = serializers.SerializerMethodField()
    category      = serializers.SerializerMethodField()

    class Meta:
        model = BrandJobPost
        fields = "__all__"

    def get_brand_name(self, obj):
        return obj.company.brand_name if obj.company else None
    
    def get_address(self, obj):
        return obj.company.address if obj.company else None
    
    def get_category(self, obj):
        return [category.type for category in obj.company.category.all()] if obj.company else []


    

class ApplicationPerBusinessJobSerializer(serializers.ModelSerializer):
    aspirant_first_name     = serializers.SerializerMethodField()
    aspirant_last_name      = serializers.SerializerMethodField()
    aspirant_mobile_number  = serializers.SerializerMethodField()
    aspirant_email          = serializers.SerializerMethodField()
    address                 = serializers.SerializerMethodField()


    class Meta:
        model = BusinessJobPostActivity
        fields = "__all__"


    def get_aspirant_first_name(self, obj):
        return obj.applicant.first_name if obj.applicant else None
    
    def get_aspirant_last_name(self, obj):
        return obj.applicant.last_name if obj.applicant else None
    
    def get_aspirant_mobile_number(self, obj):
        return obj.applicant.mobile_number if obj.applicant else None
    
    def get_aspirant_email(self, obj):
        return obj.applicant.email if obj.applicant else None
    
    def get_address(self, obj):
        return obj.applicant.address if obj.applicant else None
    


class ApplicationPerBrandJobSerializer(serializers.ModelSerializer):
    aspirant_first_name     = serializers.SerializerMethodField()
    aspirant_last_name      = serializers.SerializerMethodField()
    aspirant_mobile_number  = serializers.SerializerMethodField()
    aspirant_email          = serializers.SerializerMethodField()
    address                 = serializers.SerializerMethodField()


    class Meta:
        model = BrandJobPostActivity
        fields = "__all__"


    def get_aspirant_first_name(self, obj):
        return obj.applicant.first_name if obj.applicant else None
    
    def get_aspirant_last_name(self, obj):
        return obj.applicant.last_name if obj.applicant else None
    
    def get_aspirant_mobile_number(self, obj):
        return obj.applicant.mobile_number if obj.applicant else None
    
    def get_aspirant_email(self, obj):
        return obj.applicant.email if obj.applicant else None
    
    def get_address(self, obj):
        return obj.applicant.address if obj.applicant else None

    



