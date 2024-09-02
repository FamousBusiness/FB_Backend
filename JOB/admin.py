from django.contrib import admin
from .models import (
    JobSeekerProfile, ApplicantEducationDetails, ApplicantexperienceDetail, ApplicantSkillSet,
    JOBCategory, BusinessPageJobPost, BrandJobPost, BusinessJobPostActivity, BrandJobPostActivity,
    ApplicantResume, JobBanner
    )


class JobSeekerProfileModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'applicant', 'mobile_number', 'email')

class ApplicantEducationDetailsModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'applicant', 'education')


class ApplicantexperienceDetailModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'applicant', 'job_title')



class ApplicantSkillSetModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'applicant', 'skill_name', 'skill_level')


class JOBCategoryModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'trending')


class BusinessPageJobPostModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'company', 'location', 'position')


class BrandJobPostModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'company', 'location', 'position')


class BusinessJobPostActivityModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'applicant', 'job_post', 'apply_date')


class BrandJobPostActivityModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'applicant', 'job_post', 'apply_date')


admin.site.register(JobSeekerProfile, JobSeekerProfileModelAdmin)
admin.site.register(ApplicantEducationDetails, ApplicantEducationDetailsModelAdmin)
admin.site.register(ApplicantexperienceDetail, ApplicantexperienceDetailModelAdmin)
admin.site.register(ApplicantSkillSet, ApplicantSkillSetModelAdmin)
admin.site.register(JOBCategory, JOBCategoryModelAdmin)
admin.site.register(BusinessPageJobPost, BusinessPageJobPostModelAdmin)
admin.site.register(BrandJobPost, BrandJobPostModelAdmin)
admin.site.register(BusinessJobPostActivity, BusinessJobPostActivityModelAdmin)
admin.site.register(BrandJobPostActivity, BrandJobPostActivityModelAdmin)
admin.site.register(ApplicantResume)
admin.site.register(JobBanner)

