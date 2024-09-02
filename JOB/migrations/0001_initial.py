# Generated by Django 4.2.5 on 2023-12-28 13:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("Listings", "0061_remove_job_posted_by_delete_jobcategory_delete_job"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="BrandJobPost",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_date",
                    models.DateField(auto_now_add=True, verbose_name="Created Date"),
                ),
                ("description", models.TextField(verbose_name="Job Descrption")),
                (
                    "location",
                    models.CharField(max_length=500, verbose_name="Job Location"),
                ),
                ("salary", models.CharField(max_length=20, verbose_name="Salary")),
                (
                    "experience",
                    models.CharField(max_length=20, verbose_name="Experience"),
                ),
                (
                    "position",
                    models.CharField(max_length=100, verbose_name="Designation"),
                ),
                ("is_active", models.BooleanField(default=True)),
                (
                    "company",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="Listings.brandbusinesspage",
                        verbose_name="Company Name",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="JOBCategory",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(max_length=250, verbose_name="Job Category Name"),
                ),
                (
                    "image",
                    models.FileField(
                        default="Job_Category/default.jpeg", upload_to="Job_Category"
                    ),
                ),
                ("trending", models.BooleanField(default=False)),
            ],
            options={
                "ordering": ["-id"],
            },
        ),
        migrations.CreateModel(
            name="JobSeekerProfile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "first_name",
                    models.CharField(max_length=100, verbose_name="First Name"),
                ),
                (
                    "last_name",
                    models.CharField(max_length=100, verbose_name="Last Name"),
                ),
                (
                    "mobile_number",
                    models.CharField(blank=True, max_length=15, null=True),
                ),
                ("email", models.EmailField(blank=True, max_length=254, null=True)),
                (
                    "gender",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("Male", "Male"),
                            ("Female", "Female"),
                            ("Other", "Other"),
                            ("None", "None"),
                        ],
                        max_length=10,
                        null=True,
                    ),
                ),
                (
                    "image",
                    models.FileField(
                        default="Job_Seeker_Profile_Image/default.jpeg",
                        upload_to="Job_Seeker_Profile_Image",
                    ),
                ),
                ("address", models.CharField(max_length=200, verbose_name="Address")),
                (
                    "current_salary",
                    models.CharField(max_length=15, verbose_name="Current Salary"),
                ),
                (
                    "applicant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="BusinessPageJobPost",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_date",
                    models.DateField(auto_now_add=True, verbose_name="Posted Date"),
                ),
                ("description", models.TextField(verbose_name="Job Descrption")),
                (
                    "location",
                    models.CharField(max_length=500, verbose_name="Job Location"),
                ),
                ("salary", models.CharField(max_length=20, verbose_name="Salary")),
                (
                    "experience",
                    models.CharField(max_length=20, verbose_name="Experience"),
                ),
                (
                    "position",
                    models.CharField(max_length=100, verbose_name="Designation"),
                ),
                ("is_active", models.BooleanField(default=True)),
                (
                    "company",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="Listings.business",
                        verbose_name="Company Name",
                    ),
                ),
                (
                    "job_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="JOB.jobcategory",
                        verbose_name="Job Type",
                    ),
                ),
                (
                    "posted_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Posted By",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="BusinessJobPostActivity",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "apply_date",
                    models.DateField(auto_now_add=True, verbose_name="Apply Date"),
                ),
                (
                    "resume",
                    models.FileField(
                        default="Applicant_Business_Resume/default.jpeg",
                        upload_to="Applicant_Resume",
                    ),
                ),
                ("message", models.TextField(blank=True, null=True)),
                (
                    "applicant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="JOB.jobseekerprofile",
                    ),
                ),
                (
                    "job_post",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="JOB.businesspagejobpost",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="BrandJobPostActivity",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "apply_date",
                    models.DateField(auto_now_add=True, verbose_name="Apply Date"),
                ),
                (
                    "resume",
                    models.FileField(
                        default="Applicant_Brand_Resume/default.jpeg",
                        upload_to="Applicant_Resume",
                    ),
                ),
                ("message", models.TextField(blank=True, null=True)),
                (
                    "applicant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="JOB.jobseekerprofile",
                        verbose_name="Applicant",
                    ),
                ),
                (
                    "job_post",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="JOB.brandjobpost",
                        verbose_name="Job Post",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="brandjobpost",
            name="job_type",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="JOB.jobcategory",
                verbose_name="Job Type",
            ),
        ),
        migrations.AddField(
            model_name="brandjobpost",
            name="posted_by",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
                verbose_name="Posted By",
            ),
        ),
        migrations.CreateModel(
            name="ApplicantSkillSet",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "skill_name",
                    models.CharField(max_length=20, verbose_name="Skill Name"),
                ),
                (
                    "skill_level",
                    models.CharField(max_length=20, verbose_name="Skill Level"),
                ),
                (
                    "applicant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="JOB.jobseekerprofile",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ApplicantexperienceDetail",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("job_title", models.CharField(blank=True, max_length=100, null=True)),
                ("start_date", models.DateField(verbose_name="Start Date")),
                ("end_date", models.DateField(verbose_name="End Date")),
                (
                    "company_name",
                    models.CharField(
                        max_length=225, verbose_name="Current Company Name"
                    ),
                ),
                (
                    "job_location_city",
                    models.CharField(max_length=100, verbose_name="City"),
                ),
                (
                    "job_location_state",
                    models.CharField(max_length=100, verbose_name="State"),
                ),
                (
                    "is_current_job",
                    models.BooleanField(
                        default=False, verbose_name="Is this your current employment?"
                    ),
                ),
                (
                    "job_location_country",
                    models.CharField(max_length=100, verbose_name="Country"),
                ),
                (
                    "description",
                    models.CharField(max_length=500, verbose_name="Job Description"),
                ),
                (
                    "total_experience",
                    models.CharField(
                        max_length=20, verbose_name="Total Years of Experience"
                    ),
                ),
                (
                    "designation",
                    models.CharField(max_length=200, verbose_name="Designation"),
                ),
                (
                    "salary",
                    models.CharField(max_length=50, verbose_name="Total Annual Salary"),
                ),
                (
                    "job_profile",
                    models.CharField(max_length=500, verbose_name="Job Profile"),
                ),
                (
                    "notice_period",
                    models.CharField(max_length=20, verbose_name="Notice Period"),
                ),
                (
                    "applicant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="JOB.jobseekerprofile",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ApplicantEducationDetails",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "education",
                    models.CharField(
                        max_length=250, verbose_name="Certificate / Degree Name"
                    ),
                ),
                (
                    "university",
                    models.CharField(
                        max_length=300, verbose_name="University or Institute Name"
                    ),
                ),
                (
                    "course",
                    models.CharField(max_length=300, verbose_name="Course Name"),
                ),
                (
                    "specialization",
                    models.CharField(
                        blank=True,
                        max_length=300,
                        null=True,
                        verbose_name="Specialization",
                    ),
                ),
                (
                    "course_type",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("Fulle Time", "Full Time"),
                            ("Part Time", "Part Time"),
                            (
                                "Correspondence/Distance Learning",
                                "Correspondence/Distance Learning",
                            ),
                        ],
                        max_length=50,
                        null=True,
                    ),
                ),
                ("start_year", models.DateField()),
                ("end_year", models.DateField()),
                ("marks", models.CharField(max_length=50)),
                (
                    "applicant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="JOB.jobseekerprofile",
                    ),
                ),
            ],
        ),
    ]