from django.urls import path
from .views import (
    JobApplyView, AllJobPost, JobSeekerProfileview, CategoryWiseJobView, AllJobCategoryView,
    CandidateAppliedJobsView, CompanyPostedJobView, CompanyJobStatusUpdate, ApplicationStatusByCompanyView,
    JobDetailsView, JobSekerExperienceView, JobSeekerEducationView, CompaniesJobPOstView, JobSekerSkillSetView,
    JobSeekerResumeview, GetJobSeekerEducationView, GetJobSeekerExperienceView, GetJobSeekerSkillSetView,
    GetJobSeekerProfileView, GetJobSeekerResumeView, ApplicationPerJOBPost
    )



urlpatterns = [
    path('post-job/',  CompaniesJobPOstView.as_view(), name='post_job'),
    path('apply-job/', JobApplyView.as_view(), name='apply_job'),
    path('all-job/', AllJobPost.as_view(), name='all_job_post'),
    path('all-job-category/', AllJobCategoryView.as_view(), name='all_job_category'),
    path('category-wise-job/<int:pk>/', CategoryWiseJobView.as_view(), name='category_wise_jobs'),
    path('candidate-applied-jobs/', CandidateAppliedJobsView.as_view(), name='candidate_applied_jobs'),
    path('company-posted-jobs/', CompanyPostedJobView.as_view(), name='company_posted_jobs'),
    path('company-job-status-update/', CompanyJobStatusUpdate.as_view(), name='company_job_status_update'),
    path('application-status-by-company/', ApplicationStatusByCompanyView.as_view(), name='application_status_by_company'),
    path('job-details/', JobDetailsView.as_view(), name='application_status_by_company'),
    path('application-per-job/', ApplicationPerJOBPost.as_view(), name='applications_per_job'),

    path('aspirant-education/', GetJobSeekerEducationView.as_view(), name='applicant_education'),
    path('aspirant-education-create/', JobSeekerEducationView.as_view(), name='applicant_education_create'),
    path('aspirant-education-update/<int:profile>/', JobSeekerEducationView.as_view(), name='applicant_education_update'),
    path('aspirant-education-delete/<int:profile>/', JobSeekerEducationView.as_view(), name='applicant_education_delete'),

    path('aspirant-experience/', GetJobSeekerExperienceView.as_view(), name='applicant_experience'),
    path('aspirant-experience-create/', JobSekerExperienceView.as_view(), name='applicant_experience_create'),
    path('aspirant-experience-update/<int:profile>/', JobSekerExperienceView.as_view(), name='applicant_experience_update'),
    path('aspirant-experience-delete/<int:profile>/', JobSekerExperienceView.as_view(), name='applicant_experience_delete'),

    path('aspirant-skillset/', GetJobSeekerSkillSetView.as_view(), name='applicant_skillset'),
    path('aspirant-skillset-create/', JobSekerSkillSetView.as_view(), name='applicant_skillset_create'),
    path('aspirant-skillset-update/<int:profile>/', JobSekerSkillSetView.as_view(), name='applicant_skillset_update'),
    path('aspirant-skillset-delete/<int:profile>/', JobSekerSkillSetView.as_view(), name='applicant_skillset_delete'),

    path('aspirant-profile/', GetJobSeekerProfileView.as_view(), name='applicant_profile'),
    path('aspirant-profile-create/', JobSeekerProfileview.as_view(), name='applicant_profile_create'),
    path('aspirant-profile-update/<int:profile>/', JobSeekerProfileview.as_view(), name='applicant_profile_update'),
    path('aspirant-profile-delete/<int:profile>/', JobSeekerProfileview.as_view(), name='applicant_profile_delete'),

    path('aspirant-resume/', GetJobSeekerResumeView.as_view(), name='applicant_resume'),
    path('aspirant-resume-create/', JobSeekerResumeview.as_view(), name='applicant_resume_create'),
    path('aspirant-resume-update/<int:profile>/', JobSeekerResumeview.as_view(), name='applicant_resume_update'),
    path('aspirant-resume-delete/<int:profile>/', JobSeekerResumeview.as_view(), name='applicant_resume_delete'),

]



