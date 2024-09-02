from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import (
    JOBCategory, JobSeekerProfile, BusinessPageJobPost, BrandJobPost, BusinessJobPostActivity,
    BrandJobPostActivity, ApplicantEducationDetails, ApplicantexperienceDetail, ApplicantSkillSet,
    ApplicantResume
    )
from .serializers import (
    BusinessPageJobPostSerializer, BusinessPageJobApplySerializer, BrandJobApplySerializer,
    AllBrandPageJobPostSerializer, AllBusinessPageJobPostSerializer,JobSeekerProfileSerializer,
    ApplicantEducationDetailSerializer, ApplicantExperienceDetailSerializer, CandidateAppliedBusinessJobsSerializer,
    CandidateAppliedBrandJobsSerializer, ApplicationStatusByCompanySerializers, ApplicationStatusByBrandSerializers,
    JOBCategorySerializer, BusinessJobDetailSerializer, BrandJobDetailSerializer, BrandJobPostSerializer,
    ApplicantSkillSetSerializer, ApplicantResumeSerializer, ApplicationPerBrandJobSerializer, ApplicationPerBusinessJobSerializer
    )
from Listings.models import Business, Assigned_Benefits
from Brands.models import BrandBusinessPage
from .tasks import send_mail_to_company_job_post, send_mail_to_candidate_apply_job, send_mail_to_company_apply_job
from users.models import User
from .permissions import CustomeTokenPermission
from django.contrib.auth import authenticate
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from django.utils.decorators import method_decorator



#Companies will be able to Post Job

class CompaniesJobPOstView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user

        try:
            business = Business.objects.get(owner=user)

            serializer = BusinessPageJobPostSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            company     = serializer.validated_data['company']
            job_type    = serializer.validated_data['job_type']
            description = serializer.validated_data['description']
            location    = serializer.validated_data['location'] 
            salary      = serializer.validated_data['salary'] 
            experience  = serializer.validated_data['experience'] 
            position    = serializer.validated_data['position'] 

            try:
                job_category = JOBCategory.objects.get(name=job_type)
            except JOBCategory.DoesNotExist:
                return Response({'msg': 'Please Create the Job Category'})
            
            try:
                company_id = Business.objects.get(business_name=company)
            except Business.DoesNotExist:
                return Response({'msg': 'Company id does not exists'})
            
            if business == company_id:
                try:
                    assigned_benefits_list = Assigned_Benefits.objects.filter(user=user)
                    if not assigned_benefits_list:
                        return Response({'msg': 'Please purchase any premium plan to post free jobs'})
                # job_post_allowed = sum(assigned_benefits.jobpost_allowed for assigned_benefits in assigned_benefits_list)
                except Exception as e:
                    return Response({'msg': 'Please purchase any premium plan to post free jobs', 'suggestion': f'{str(e)}'})
                
                for assigned_benefits in assigned_benefits_list:
                    
                    if assigned_benefits.jobpost_allowed > 0:
                        serializer.save()
                        business_email = business.email

                        data = {
                            'business_name': business.business_name,
                            'mail': business_email,
                            'jobcategory': job_category.name,
                            'jobdescription': description,
                            'joblocation': location,
                            'job_salary': salary,
                            'job_experience': experience,
                            'job_position': position
                        }
                        # send_mail_to_company_job_post.delay(data)

                        assigned_benefits.jobpost_allowed -= 1
                        assigned_benefits.save()
                        break
                    else:
                        return Response({'msg': 'Job Post quantity has expired please recharge to post new job'})
                    
            else:
                return Response({'msg': 'Only the Company owner can post a job'})
            
            return Response({'msg': 'Date Saved Successfully'})     

        except Business.DoesNotExist:
            
            try:
                brand      = BrandBusinessPage.objects.get(owner=user)
            except:
                return Response({'msg': 'Only Brand and Business owner can Post Jobs'})

            serializer = BrandJobPostSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            company     = serializer.validated_data['company']
            job_type    = serializer.validated_data['job_type']
            description = serializer.validated_data['description']
            location    = serializer.validated_data['location'] 
            salary      = serializer.validated_data['salary'] 
            experience  = serializer.validated_data['experience'] 
            position    = serializer.validated_data['position'] 

            try:
                job_category = JOBCategory.objects.get(name=job_type)
            except JOBCategory.DoesNotExist:
                return Response({'msg': 'Please Create the Job Category'})
            
            try:
                company_id = BrandBusinessPage.objects.get(brand_name=company)
            except BrandBusinessPage.DoesNotExist:
                return Response({'msg': 'Company id does not exists'})

            if brand == company_id:
                try:
                    assigned_benefits_list = Assigned_Benefits.objects.filter(user=user)
                    if not assigned_benefits_list:
                        return Response({'msg': 'Please purchase any premium plan to post free jobs'})
                # job_post_allowed = sum(assigned_benefits.jobpost_allowed for assigned_benefits in assigned_benefits_list)
                except Exception as e:
                    return Response({'msg': 'Please purchase any premium plan to post free jobs', 'suggestion': f'{str(e)}'})
                
                for assigned_benefits in assigned_benefits_list:
                    
                    if assigned_benefits.jobpost_allowed > 0:
                        serializer.save()
                        brand_email = brand.email

                        data = {
                            'business_name': brand.business_name,
                            'mail': brand_email,
                            'jobcategory': brand.brand_name,
                            'jobdescription': description,
                            'joblocation': location,
                            'job_salary': salary,
                            'job_experience': experience,
                            'job_position': position
                        }
                        # send_mail_to_company_job_post.delay(data)

                        assigned_benefits.jobpost_allowed -= 1
                        assigned_benefits.save()
                        break

                    else:
                        return Response({'msg': 'Job Post quantity has expired please recharge to post new job'})
                    
                else:
                    return Response({'msg': 'Only the Company owner can post a job'})
            
            return Response({'msg': 'Date Saved Successfully'})     
        
        # return Response({'msg':'Not able to Post any Job'})  



#Apply Job
class JobApplyView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user        = request.user
        job_id      = request.data.get('job_post')
        # company_name = request.data.get('company_name')
        business_id = request.data.get('business_id')
        brand_id    = request.data.get('brand_id')

        if business_id:
            try:
                candidate_profile = JobSeekerProfile.objects.get(applicant=user)
            except JobSeekerProfile.DoesNotExist:
                return Response({'msg': 'Before Applying for a job please make your job profile'})
            
            try:
                business = Business.objects.get(id=business_id)
            except Business.DoesNotExist:
                return Response({'msg': 'Business Does not exists'})
            
            # request.data['applicant'] = candidate_profile.pk
            serializer = BusinessPageJobApplySerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.validated_data['applicant'] = candidate_profile

            try:
                jobpost = BusinessPageJobPost.objects.get(id=job_id)
            except BusinessPageJobPost.DoesNotExist:
                return Response({'msg': 'Job Does not exists'})
            
            try:
                is_job_applied = BusinessJobPostActivity.objects.get(applicant=candidate_profile.pk, job_post=jobpost.pk)
            except:
                serializer.save()
                data = {
                'candidate_mail': candidate_profile.email,
                'candidate_first_name': candidate_profile.first_name,
                'candidate_last_name': candidate_profile.last_name,
                'business_email': business.email,
                'job_position'  : jobpost.position,
                'joblocation':  jobpost.location,
                'business_name': business.business_name
                }

                # send_mail_to_candidate_apply_job.delay(data)
                # send_mail_to_company_apply_job.delay(data)
                return Response({'msg': 'Job Applied Successfully', 'data': serializer.data})

        elif brand_id:
            try:
                candidate_profile = JobSeekerProfile.objects.get(applicant=user)
            except JobSeekerProfile.DoesNotExist:
                return Response({'msg': 'Before Applying for a job please make your job profile'})
            
            try:
                brand = BrandBusinessPage.objects.get(id=brand_id)
            except BrandBusinessPage.DoesNotExist:
                return Response({'msg': 'Brand Does not exists'})
            
            # request.data['applicant'] = candidate_profile.pk
            serializer = BrandJobApplySerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.validated_data['applicant'] = candidate_profile

            try:
                jobpost = BrandJobPost.objects.get(id=job_id)
            except BrandJobPost.DoesNotExist:
                return Response({'msg': 'Job Does not exists'})
            
            try:
                is_job_available = BrandJobPostActivity.objects.get(applicant=candidate_profile.pk, job_post=jobpost.pk)
            except:
                serializer.save()

                data = {
                    'candidate_mail'      : candidate_profile.email,
                    'candidate_first_name': candidate_profile.first_name,
                    'candidate_last_name' : candidate_profile.last_name,
                    'business_email'      : brand.email,
                    'business_name'       : brand.brand_name,
                    'job_position'        : jobpost.position,
                    'joblocation'         : jobpost.location
                }
        
                # send_mail_to_candidate_apply_job.delay(data)
                # send_mail_to_company_apply_job.delay(data)
                return Response({'msg': 'Job Applied Successfully', 'data': serializer.data})   

        return Response({'msg': 'You have already Applied for the job'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        
  


class AllJobPost(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        # fulltime     = request.query_params.get('full_time')
        # partime      = request.query_params.get('part_time')
        # workfromhome = request.query_params.get('work_from_home')
        # internship   = request.query_params.get('internship')
        # workabroad   = request.query_params.get('work_abroad')
        # city         = request.query_params.get('city')
        # category     = request.query_params.get('category')


        business_page_job = BusinessPageJobPost.objects.all()
        brand_page_job    = BrandJobPost.objects.all()
        # # print(business_page_job)

        # if any([fulltime or partime, workfromhome or internship or workabroad or city or category]) is not None:

        #     try:
        #         job_category = JOBCategory.objects.get(name=category)
        #     except JOBCategory.DoesNotExist:
        #         job_category = None

        #     business_page_job = business_page_job.filter(full_time=fulltime, part_time=partime, 
        #                                                  work_from_home=workfromhome, work_abroad=workabroad,
        #                                                  internship=internship, location=city, 
        #                                                  job_type=job_category)
            
        #     brand_page_job = brand_page_job.filter(full_time=fulltime, part_time=partime, 
        #                                           work_from_home=workfromhome, work_abroad=workabroad,
        #                                           internship=internship, location=city, 
        #                                           job_type=job_category)
            
        brand_serializer    = AllBrandPageJobPostSerializer(brand_page_job, many=True)
        business_serializer = AllBusinessPageJobPostSerializer(business_page_job, many=True)
    
        response_data = {
            'Busines_Page_Jobs': business_serializer.data,
            'Brand_Job_Post': brand_serializer.data
        }

        return Response({'msg': 'All Job data fetched succefully', 'data': response_data})



class CategoryWiseJobView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk):
        token = request.COOKIES.get('access_token')
        job_category = pk

        user = authenticate(request=request, token=token)
        # print(token)
        # user = request.user
      
        try:
            business_job_post            = BusinessPageJobPost.objects.filter(job_type=job_category)
            business_job_post_serializer = AllBusinessPageJobPostSerializer(business_job_post, many=True)
        except Exception as e:
            pass

        try:
            brand_job_post            = BrandJobPost.objects.filter(job_type=job_category)
            brand_job_post_serializer = AllBrandPageJobPostSerializer(brand_job_post, many=True)
        except:
            pass

        response = {}

        if business_job_post_serializer:
            response['business_jobs'] = business_job_post_serializer.data

        if brand_job_post_serializer:
            response['brand_jobs']  = brand_job_post_serializer.data

        return Response({'msg': 'All Job data fetched successfully', 'data': response})
        

#Candidate Will be able to View their Applied JObs
class CandidateAppliedJobsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        try:
            candidate_profile = JobSeekerProfile.objects.get(applicant=user)
        except JobSeekerProfile.DoesNotExist:
            return Response({'msg': 'Before Applying for a job please make your job profile'})
        
        try:
            available_business_jobs            = BusinessJobPostActivity.objects.filter(applicant=candidate_profile)
            available_business_jobs_serializer = CandidateAppliedBusinessJobsSerializer(available_business_jobs, many=True)
        except:
            pass

        try:
            available_brand_jobs            = BrandJobPostActivity.objects.filter(applicant=candidate_profile)
            available_brand_jobs_serializer = CandidateAppliedBrandJobsSerializer(available_brand_jobs, many=True)
        except:
            pass

        response = {}

        if available_business_jobs_serializer:
            response['business_jobs'] = available_business_jobs_serializer.data

        if available_brand_jobs_serializer:
            response['brand_jobs'] = available_brand_jobs_serializer.data

        return Response({'msg': 'All applied jobs for the user fetched successfully', 'data': response})
    

#Companies will be able to view their posted Jobs
class CompanyPostedJobView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class   =  PageNumberPagination

    def get(self, request,*args, **kwargs):
        user        = request.user
        # business_id = request.GET.get('business')
        # brand_id    = request.GET.get('brand')

        try:
            business_page = Business.objects.get(owner=user)

            try:
                available_jobs = BusinessPageJobPost.objects.filter(company=business_page)
                print(available_jobs)
            except BusinessPageJobPost.DoesNotExist:
                return Response({'msg': 'Donot have any job post'})
        
            if business_page.owner == user:
                job_page = self.paginate_queryset(available_jobs)
                available_jobs_serializer = AllBusinessPageJobPostSerializer(job_page, many=True)

                return self.get_paginated_response(available_jobs_serializer.data)
        
            return Response({'msg': 'Only the Page owner can view the Posted Jobs'})
        
        except Business.DoesNotExist:

            try:
                brand_page = BrandBusinessPage.objects.get(owner=user)
            except BrandBusinessPage.DoesNotExist:
                return Response({'msg': 'Donot have a Brand Page'})
            
            try:
                available_brand_jobs = BrandJobPost.objects.filter(company=brand_page)
            except BrandJobPost.DoesNotExist:
                return Response({'msg': 'Donot have any job post'})
            
            if brand_page.owner == user:
                brand_job_page = self.paginate_queryset(available_brand_jobs)
                available_brand_jobs_serializer = AllBrandPageJobPostSerializer(brand_job_page, many=True)

                return self.get_paginated_response(available_brand_jobs_serializer.data)
            
            return Response({'msg': 'Only the Page owner can view the Posted Jobs'})
        
        
        

#Companies will change the status of a particular job
class CompanyJobStatusUpdate(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request):
        user   = request.user
        job_id = request.data.get('job_id')


        try:
            business_page = Business.objects.get(owner=user)

            try:
                company_jobs  = BusinessPageJobPost.objects.get(company=business_page, id=job_id)
            except BusinessPageJobPost.DoesNotExist:
                return Response({'msg': 'Job Post is Unavailable'})
            
            company_job_serializer = AllBusinessPageJobPostSerializer(company_jobs, data=request.data, partial=True)
            company_job_serializer.is_valid(raise_exception=True)
            company_job_serializer.save()
            return Response({'msg': 'Business Data updated Successfully'}, status=status.HTTP_200_OK)
        
        except Business.DoesNotExist:
            brand_page = BrandBusinessPage.objects.get(owner=user)

            try:
                brand_jobs = BrandJobPost.objects.get(company=brand_page, id=job_id)
            except BrandJobPost.DoesNotExist:
                return Response({'msg': 'Job Post is unavailable'})

            brand_job_serializer = AllBrandPageJobPostSerializer(brand_jobs, data=request.data, partial=True)
            brand_job_serializer.is_valid(raise_exception=True)
            brand_job_serializer.save()

            return Response({'msg': 'Brand Data updated Successfully'}, status=status.HTTP_200_OK)

        
    
#Companies can change the status of any application
class ApplicationStatusByCompanyView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request):
        applicant_instance = request.data.get('applicant')
        job_post_instance = request.data.get('job_post')
        user = request.user

        business_page = None

        try:
            business_page = Business.objects.get(owner=user)
        except:
            pass
        
        if business_page:
            try:
                job_posted_by_company = BusinessPageJobPost.objects.get(id=job_post_instance, company=business_page)
            except BusinessPageJobPost.DoesNotExist:
                return Response({'msg': 'Only the Company who posted the Job can change the status of the job'})

            try:
                application = BusinessJobPostActivity.objects.get(applicant=applicant_instance, job_post=job_post_instance)
            except BusinessJobPostActivity.DoesNotExist:
                return Response({'msg': 'Applicant Job post doesnot exists'})
        
            serializers = ApplicationStatusByCompanySerializers(application, data=request.data, partial=True)
            serializers.is_valid(raise_exception=True)
            serializers.save()

            return Response({'msg': 'Application status changed successfully'}, status=status.HTTP_200_OK)
        
        elif business_page == None:
            brand_page = None

            try:
                brand_page = BrandBusinessPage.objects.get(owner=user)
            except BrandBusinessPage.DoesNotExist:
                pass  

            if brand_page:
                try:
                    job_posted_by_brand = BrandJobPost.objects.get(id=job_post_instance, company=brand_page)
                except BrandJobPost.DoesNotExist:
                    return Response({'msg': 'Only the Company who posted the Job can change the status of the job'})

                try:
                    application = BrandJobPostActivity.objects.get(applicant=applicant_instance, job_post=job_post_instance)
                except BrandJobPostActivity.DoesNotExist:
                    return Response({'msg': 'Applicant Job post doesnot exists'})
            
                serializers = ApplicationStatusByBrandSerializers(application, data=request.data, partial=True)
                serializers.is_valid(raise_exception=True)
                serializers.save()

                return Response({'msg': 'Application status changed successfully'}, status=status.HTTP_200_OK)
        
        return Response({'msg': 'Not Found'}, status=status.HTTP_404_NOT_FOUND)
    
    

#How many Applicant Applied for a Job Post can be viewed by the Business owner
class ApplicationPerJOBPost(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class   = PageNumberPagination

    def get(self, request, *args, **kwargs):
        user = request.user
        job_post = request.GET.get('job_post')

        try:
            try:
                business_page = Business.objects.get(owner = user.id)
            except Business.DoesNotExist:
                return Response({'msg': 'Business Page not available'})

            if business_page:
                
                try:
                    job = BusinessPageJobPost.objects.get(id=job_post)
                except BusinessPageJobPost.DoesNotExist:
                    return Response({'msg': 'Job Post Unavailable'}, status=status.HTTP_404_NOT_FOUND)
                
                try:
                    applications = BusinessJobPostActivity.objects.filter(job_post=job)
                    applications_page = self.paginate_queryset(applications)
                    serializers = ApplicationPerBusinessJobSerializer(applications_page, many=True)

                except BusinessJobPostActivity.DoesNotExist:
                    return Response({'msg': 'No Application for this job'}, status=status.HTTP_404_NOT_FOUND)
                
                return self.get_paginated_response(serializers.data)
            
        except Business.DoesNotExist:

            try:
                brand_page = BrandBusinessPage.objects.get(owner = user)
            except BrandBusinessPage.DoesNotExist:
                return Response({'msg': 'Brand page not available'})


            if brand_page:
                try:
                    job = BrandJobPost.objects.get(id=job_post)
                except BrandJobPost.DoesNotExist:
                    return Response({'msg': 'Job Post Unavailable'}, status=status.HTTP_404_NOT_FOUND)
                
                try:
                    brand_applications = BrandJobPostActivity.objects.filter(job_post=job)
                    brand_application_page = self.paginate_queryset(brand_applications)
                    brand_serializer = ApplicationPerBrandJobSerializer(brand_application_page, many=True)

                except BrandJobPostActivity.DoesNotExist:
                    return Response({'msg': 'No Application for this job'}, status=status.HTTP_404_NOT_FOUND)
                
                return self.get_paginated_response(brand_serializer.data)
            
        return Response({'msg': 'Not able to find any Business or Brand Page'})
            

class AllJobCategoryView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        job_category = JOBCategory.objects.all()
        serializer = JOBCategorySerializer(job_category, many=True)

        return Response({'msg': 'Data fetched Successfully', 'data': serializer.data})
    


class JobDetailsView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, *args, **kwargs):
        company_name = request.query_params.get('company')
        job_id       = request.query_params.get('job')

        if not job_id or not company_name:
                return Response({'msg': 'Both job and company parameters are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # company_serializer = None
        response_data = {
        }

        try:
            business_job            = BusinessPageJobPost.objects.filter(id=job_id, company__business_name=company_name)
            business_job_serializer = BusinessJobDetailSerializer(business_job, many=True)

            if business_job_serializer:
                response_data['business_page_jobs'] = business_job_serializer.data
            # return Response({'msg': 'Business Job Data Fetched Successfully', 'data': company_serializer.data})
        
        except Exception:
            brand_job          = BrandJobPost.objects.filter(id=job_id, company__brand_name=company_name)
            brand_job_serializer = BrandJobDetailSerializer(brand_job, many=True)

            if brand_job_serializer:
                response_data['brand_jobs'] = brand_job_serializer.data

        return Response({'msg': 'Brand Job Data Fetched Successfully', 'data': response_data})
        
        
    


class JobSeekerEducationView(generics.CreateAPIView, generics.UpdateAPIView, generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset           = ApplicantEducationDetails.objects.all()
    serializer_class   = ApplicantEducationDetailSerializer


    def perform_create(self, serializer):
        serializer.save(applicant=self.request.user)


    def perform_update(self, serializer, *args, **kwargs):
        profile_id          = self.kwargs.get('profile')

        try:
            applicant_education = ApplicantEducationDetails.objects.get(id=profile_id)
            applicant           = applicant_education.applicant
        except ApplicantEducationDetails.DoesNotExist:
            return Response({'msg': 'Aspirant Education detail not available first create one'})

        # if serializer.instance.applicant != self.request.user:
        if applicant != self.request.user:
            return Response({'detail': 'Permission Denied.'}, status=status.HTTP_403_FORBIDDEN)
        serializer.save(partial=True)


    def perform_destroy(self, instance, *args, **kwargs):
        profile_id          = self.kwargs.get('profile')

        try:
            applicant_education = ApplicantEducationDetails.objects.get(id=profile_id)
        except ApplicantEducationDetails.DoesNotExist:
            return Response({'msg': 'Aspirant Education detail not available first create one'})
        
        if applicant_education.applicant != self.request.user:
            return Response({'detail': 'Permission Denied.'}, status=status.HTTP_403_FORBIDDEN)
        instance.delete()


    def get_object(self, *args, **kwargs):
        profile_id          = self.kwargs.get('profile')

        try:
            applicant_education = ApplicantEducationDetails.objects.filter(id=profile_id)
        except ApplicantEducationDetails.DoesNotExist:
            return Response({'msg': 'Aspirant Education detail not available first create one'})
        
        return applicant_education
    


class GetJobSeekerEducationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        try:
            applicant_education = ApplicantEducationDetails.objects.filter(applicant=user)
        except ApplicantEducationDetails.DoesNotExist:
            return Response({'msg': 'Aspirant Education detail not available first create one'})
        
        serializer = ApplicantEducationDetailSerializer(applicant_education, many=True)

        return Response({'msg': 'Data fetched successfully', 'data': serializer.data})


    

class JobSekerExperienceView(generics.CreateAPIView, generics.UpdateAPIView, generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset           = ApplicantexperienceDetail.objects.all().order_by('id')
    serializer_class   = ApplicantExperienceDetailSerializer


    def perform_create(self, serializer):
        serializer.save(applicant=self.request.user)


    def perform_update(self, serializer):
        profile_id          = self.kwargs.get('profile')

        try:
            applicant_experience = ApplicantexperienceDetail.objects.get(id=profile_id)
            applicant           = applicant_experience.applicant
        except ApplicantexperienceDetail.DoesNotExist:
            return Response({'msg': 'Aspirant Experience detail not available first create one'})

        # if serializer.instance.applicant != self.request.user:
        if applicant != self.request.user:
            return Response({'detail': 'Permission Denied.'}, status=status.HTTP_403_FORBIDDEN)
        serializer.save(partial=True)

    def perform_destroy(self, instance):
        profile_id          = self.kwargs.get('profile')

        try:
            applicant_experience = ApplicantexperienceDetail.objects.get(id=profile_id)
        except ApplicantexperienceDetail.DoesNotExist:
            return Response({'msg': 'Aspirant Experience detail not available'})
        
        if applicant_experience.applicant != self.request.user:
            return Response({'detail': 'Permission Denied.'}, status=status.HTTP_403_FORBIDDEN)
        instance.delete()

    def get_object(self):
        profile_id = self.kwargs.get('profile')

        try:
            applicant_experience = ApplicantexperienceDetail.objects.get(id=profile_id)
        except ApplicantexperienceDetail.DoesNotExist:
            return Response({'msg': 'Aspirant Experience detail not available'})
        
        return applicant_experience
    



class GetJobSeekerExperienceView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        try:
            applicant_experience = ApplicantexperienceDetail.objects.filter(applicant=user)
        except ApplicantexperienceDetail.DoesNotExist:
            return Response({'msg': 'Aspirant Experience detail not available first create one'})
        
        serializer = ApplicantExperienceDetailSerializer(applicant_experience, many=True)

        return Response({'msg': 'Data fetched successfully', 'data': serializer.data})




class JobSekerSkillSetView(generics.CreateAPIView, generics.UpdateAPIView, generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset           = ApplicantSkillSet.objects.all()
    serializer_class   = ApplicantSkillSetSerializer


    def perform_create(self, serializer):
        serializer.save(applicant=self.request.user)


    def perform_update(self, serializer, *args, **kwargs):
        profile_id          = self.kwargs.get('profile')

        try:
            applicant_skill     = ApplicantSkillSet.objects.get(id=profile_id)
            applicant           = applicant_skill.applicant
        except ApplicantSkillSet.DoesNotExist:
            return Response({'msg': 'Aspirant Skillset detail not available first create one'})

        # if serializer.instance.applicant != self.request.user:
        if applicant != self.request.user:
            return Response({'detail': 'Permission Denied.'}, status=status.HTTP_403_FORBIDDEN)
        serializer.save(partial=True)

    def perform_destroy(self, instance, *args, **kwargs):
        profile_id          = self.kwargs.get('profile')

        try:
            applicant_skill = ApplicantSkillSet.objects.get(id=profile_id)
        except ApplicantSkillSet.DoesNotExist:
            return Response({'msg': 'Aspirant Skillset detail not available'})
        
        if applicant_skill.applicant != self.request.user:
            return Response({'detail': 'Permission Denied.'}, status=status.HTTP_403_FORBIDDEN)
        instance.delete()

    def get_object(self, *args, **kwargs):
        profile_id = self.kwargs.get('profile')

        try:
            applicant_experience = ApplicantSkillSet.objects.get(id=profile_id)
        except ApplicantSkillSet.DoesNotExist:
            return Response({'msg': 'Aspirant Skillset detail not available'})
        
        return applicant_experience
    



class GetJobSeekerSkillSetView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        try:
            applicant_skilleset = ApplicantSkillSet.objects.filter(applicant=user)
        except ApplicantSkillSet.DoesNotExist:
            return Response({'msg': 'Aspirant Skill detail not available first create one'})
        
        serializer = ApplicantSkillSetSerializer(applicant_skilleset, many=True)

        return Response({'msg': 'Data fetched successfully', 'data': serializer.data})
    



class JobSeekerProfileview(generics.CreateAPIView, generics.UpdateAPIView, generics.DestroyAPIView, generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset           = JobSeekerProfile.objects.all()
    serializer_class   = JobSeekerProfileSerializer


    def perform_create(self, serializer):
        serializer.save(applicant=self.request.user)

    def perform_update(self, serializer):
        profile_id          = self.kwargs.get('profile')

        try:
            jobseeker_profile   = JobSeekerProfile.objects.get(id=profile_id)
            applicant           = jobseeker_profile.applicant
        except JobSeekerProfile.DoesNotExist:
            return Response({'msg': 'Aspirant Profile detail not available first create one'})

        # if serializer.instance.applicant != self.request.user:
        if applicant != self.request.user:
            return Response({'detail': 'Permission Denied.'}, status=status.HTTP_403_FORBIDDEN)
        serializer.save(partial=True)

    def perform_destroy(self, instance):
        profile_id          = self.kwargs.get('profile')

        try:
            applicant_details = JobSeekerProfile.objects.get(id=profile_id)
        except JobSeekerProfile.DoesNotExist:
            return Response({'msg': 'Aspirant Profile detail not available'})
        
        if applicant_details.applicant != self.request.user:
            return Response({'detail': 'Permission Denied.'}, status=status.HTTP_403_FORBIDDEN)
        instance.delete()


    def get_object(self):
        profile_id = self.kwargs.get('profile')

        try:
            applicant_details = JobSeekerProfile.objects.get(id=profile_id)
        except JobSeekerProfile.DoesNotExist:
            return Response({'msg': 'Aspirant Profile detail not available'})
        
        return applicant_details
    



class GetJobSeekerProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        try:
            applicant_profile = JobSeekerProfile.objects.filter(applicant=user)
        except JobSeekerProfile.DoesNotExist:
            return Response({'msg': 'Aspirant Profile detail not available first create one'})
        
        serializer = JobSeekerProfileSerializer(applicant_profile, many=True)

        return Response({'msg': 'Data fetched successfully', 'data': serializer.data})
    



class JobSeekerResumeview(generics.CreateAPIView, generics.UpdateAPIView, generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset           = ApplicantResume.objects.all()
    serializer_class   = ApplicantResumeSerializer


    def perform_create(self, serializer):
        serializer.save(applicant=self.request.user)

    def perform_update(self, serializer):
        profile_id          = self.kwargs.get('profile')

        try:
            jobseeker_profile   = ApplicantResume.objects.get(id=profile_id)
            applicant           = jobseeker_profile.applicant
        except ApplicantResume.DoesNotExist:
            return Response({'msg': 'Aspirant Resume does not exist first create one'})

        # if serializer.instance.applicant != self.request.user:
        if applicant != self.request.user:
            return Response({'detail': 'Permission Denied.'}, status=status.HTTP_403_FORBIDDEN)
        serializer.save(partial=True)

    def perform_destroy(self, instance, *args, **kwargs):
        profile_id          = self.kwargs.get('profile')

        try:
            applicant_details = ApplicantResume.objects.get(id=profile_id)
        except ApplicantResume.DoesNotExist:
            return Response({'msg': 'Aspirant Profile detail not available'})
        
        if applicant_details.applicant != self.request.user:
            return Response({'detail': 'Permission Denied.'}, status=status.HTTP_403_FORBIDDEN)
        instance.delete()


    def get_object(self, *args, **kwargs):
        profile_id = self.kwargs.get('profile')

        try:
            applicant_details = ApplicantResume.objects.get(id=profile_id)
        except ApplicantResume.DoesNotExist:
            return Response({'msg': 'Aspirant Profile detail not available'})
        
        return applicant_details
    



class GetJobSeekerResumeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        try:
            applicant_profile = ApplicantResume.objects.filter(applicant=user)
        except ApplicantResume.DoesNotExist:
            return Response({'msg': 'Aspirant Profile detail not available first create one'})
        
        serializer = ApplicantResumeSerializer(applicant_profile, many=True)

        return Response({'msg': 'Data fetched successfully', 'data': serializer.data})


                    