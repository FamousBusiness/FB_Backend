from django.db import models
from users.models import User
from Listings.models import Business
from Brands.models import BrandBusinessPage
from django import forms
from django.utils.translation import gettext_lazy as _


GENDER = (
    ('Male', 'Male'),
    ('Female', 'Female'),
    ('Other', 'Other'),
    ('None', 'None'),
)

COURSE_TYPE = (
    ('Fulle Time', 'Full Time'),
    ('Part Time', 'Part Time'),
    ('Correspondence/Distance Learning', 'Correspondence/Distance Learning')
)

JOB_APPLY_STATUS = (
    ('Selected', 'Selected'),
    ('Rejected', 'Rejected'),
    ('Pending', 'Pending'),
    ('Viewed', 'Viewed'),
    ('Applied', 'Applied'),
)


class JobSeekerProfile(models.Model):
    applicant      = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name     = models.CharField(max_length=100, verbose_name='First Name')
    last_name      = models.CharField(max_length=100, verbose_name='Last Name')
    mobile_number  = models.CharField(max_length=15, null=True, blank=True)
    email          = models.EmailField(null=True, blank=True)
    gender         = models.CharField(choices=GENDER, max_length=10, null=True, blank=True)
    image          = models.FileField(upload_to='Job_Seeker_Profile_Image', default='Job_Seeker_Profile_Image/default.jpeg')
    address        = models.CharField(max_length=200, verbose_name='Address')
    current_salary = models.CharField(max_length=15, verbose_name='Current Salary', null=True, blank=True)


    def __str__(self):
        return f"{self.first_name} ' ' {self.last_name} Profile" 
    

class ApplicantEducationDetails(models.Model):
    applicant      = models.ForeignKey(User, on_delete=models.CASCADE)
    education      = models.CharField(max_length=250, verbose_name='Certificate / Degree Name')
    university     = models.CharField(max_length=300, verbose_name='University or Institute Name')
    course         = models.CharField(max_length=300, verbose_name='Course Name')
    specialization = models.CharField(max_length=300, verbose_name='Specialization', null=True, blank=True)
    course_type    = models.CharField(choices=COURSE_TYPE, max_length=50, null=True, blank=True)
    start_year     = models.CharField(_("Start Year"), max_length=5, null=True, blank=True)
    end_year       = models.CharField(_("End Year"), max_length=5, null=True, blank=True)
    marks          = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.university}\'s {self.education} Education Details"
    
    class Meta:
        ordering = ['id']
    

class ApplicantexperienceDetail(models.Model):
    applicant            = models.ForeignKey(User, on_delete=models.CASCADE)
    job_title            = models.CharField(max_length=100, null=True, blank=True)
    start_date           = models.DateField(verbose_name='Start Date')
    end_date             = models.DateField(verbose_name='End Date')
    company_name         = models.CharField(max_length=225, verbose_name='Current Company Name')
    job_location_city    = models.CharField(max_length=100, verbose_name='City')
    job_location_state   = models.CharField(max_length=100, verbose_name='State')
    job_location_country = models.CharField(max_length=100, verbose_name='Country')
    is_current_job       = models.BooleanField(default=False, verbose_name='Is this your current employment?')
    description          = models.CharField(max_length=500, verbose_name='Job Description')
    total_experience     = models.CharField(max_length=20, verbose_name='Total Years of Experience') 
    designation          = models.CharField(max_length=200, verbose_name='Designation') 
    salary               = models.CharField(max_length=50, verbose_name='Total Annual Salary')
    job_profile          = models.CharField(max_length=500, verbose_name='Job Profile')
    notice_period        = models.CharField(max_length=20, verbose_name='Notice Period')

    def __str__(self):
        return f"{self.job_title} of {self.company_name}"
    
    class Meta:
        ordering = ['id']



class ApplicantSkillSet(models.Model):
    applicant     = models.ForeignKey(User, on_delete=models.CASCADE)
    skill_name    = models.CharField(max_length=20, verbose_name='Skill Name')
    skill_level   = models.CharField(max_length=20, verbose_name='Skill Level')

    def __str__(self):
        return f"{self.applicant} Skills"
    
    class Meta:
        ordering = ['-id']


class ApplicantResume(models.Model):
    applicant   = models.ForeignKey(User, on_delete=models.CASCADE)
    resume      = models.FileField(upload_to='Applicant_Resume', default='Applicant_Resume/default.pdf')
    upload_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.applicant.name}\'s Resume"

    class Meta:
        ordering = ['-id']
    

class JOBCategory(models.Model):
    name     = models.CharField(max_length=250, verbose_name='Job Category Name')
    image    = models.FileField(upload_to='Job_Category', default='Job_Category/default.jpeg')
    trending = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.name}"

    class Meta:
        ordering = ['-id']


class BusinessPageJobPost(models.Model):
    # posted_by    = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Posted By')
    company        = models.ForeignKey(Business, on_delete=models.CASCADE, verbose_name='Company Name')
    job_type       = models.ForeignKey(JOBCategory, on_delete=models.CASCADE, verbose_name='Job Type')
    created_date   = models.DateField(auto_now_add=True, verbose_name='Posted Date')
    description    = models.TextField(verbose_name='Job Descrption')
    location       = models.CharField(max_length=500, verbose_name='Job Location')
    salary         = models.CharField(max_length=20, verbose_name='Salary')
    experience     = models.CharField(max_length=20, verbose_name='Experience')
    position       = models.CharField(max_length=100, verbose_name='Designation')
    full_time      = models.BooleanField(default=False)
    part_time      = models.BooleanField(default=False)
    work_from_home = models.BooleanField(default=False)
    internship     = models.BooleanField(default=False)
    work_abroad    = models.BooleanField(default=False)
    is_active      = models.BooleanField(default=True)


    def __str__(self):
        return f"{self.company.business_name}\'s Job Post for {self.position}"
    
    class Meta:
        ordering = ['-id']
    

class BrandJobPost(models.Model):
    # posted_by    = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Posted By')
    company        = models.ForeignKey(BrandBusinessPage, on_delete=models.CASCADE, verbose_name='Company Name')
    job_type       = models.ForeignKey(JOBCategory, on_delete=models.CASCADE, verbose_name='Job Type')
    created_date   = models.DateField(auto_now_add=True, verbose_name='Created Date')
    description    = models.TextField(verbose_name='Job Descrption')
    location       = models.CharField(max_length=500, verbose_name='Job Location')
    salary         = models.CharField(max_length=20, verbose_name='Salary')
    experience     = models.CharField(max_length=20, verbose_name='Experience')
    position       = models.CharField(max_length=100, verbose_name='Designation')
    full_time      = models.BooleanField(default=False)
    part_time      = models.BooleanField(default=False)
    work_from_home = models.BooleanField(default=False)
    internship     = models.BooleanField(default=False)
    work_abroad    = models.BooleanField(default=False)
    is_active      = models.BooleanField(default=True)

    
    def __str__(self):
        return f"{self.company.business_name}\'s Job Post for {self.position}"
    
    class Meta:
        ordering = ['-id']
    


class BusinessJobPostActivity(models.Model):
    applicant  = models.ForeignKey(JobSeekerProfile, on_delete=models.CASCADE)
    job_post   = models.ForeignKey(BusinessPageJobPost, on_delete=models.CASCADE)
    apply_date = models.DateField(auto_now_add=True, verbose_name='Apply Date')
    resume     = models.FileField(upload_to='Applicant_Resume', default='Applicant_Business_Resume/default.jpeg')
    message    = models.TextField(null=True, blank=True)
    status     = models.CharField(choices=JOB_APPLY_STATUS, default='Applied', max_length=20, verbose_name='Job Status')

    def __str__(self):
        return f"{self.applicant}\'s application for {self.job_post}"
    
    class Meta:
        ordering = ['-id']
    

class BrandJobPostActivity(models.Model):
    applicant  = models.ForeignKey(JobSeekerProfile, on_delete=models.CASCADE, verbose_name='Applicant')
    job_post   = models.ForeignKey(BrandJobPost, on_delete=models.CASCADE, verbose_name='Job Post')
    apply_date = models.DateField(auto_now_add=True, verbose_name='Apply Date')
    resume     = models.FileField(upload_to='Applicant_Resume', default='Applicant_Brand_Resume/default.jpeg')
    message    = models.TextField(null=True, blank=True)
    status     = models.CharField(choices=JOB_APPLY_STATUS, default='Applied', max_length=20, verbose_name='Job Status')


    def __str__(self):
        return f"{self.applicant}\'s application for {self.job_post}"
    
    class Meta:
        ordering = ['-id']




class JobBanner(models.Model):
    name   = models.CharField(_("Banner Name"))
    banner = models.FileField(default='JobBanner/default.jpg', upload_to='JobBanner/', verbose_name='Banner')

    def __str__(self):
        return f"{self.name}"


    


