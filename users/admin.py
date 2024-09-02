from django.contrib import admin
from users.models import User, UsersAgreement
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# from django.contrib.auth.forms import UserChangeForm, UserCreationForm


# class CustomUserChangeForm(UserChangeForm):
#     class Meta(UserChangeForm.Meta):
#         model = User
#         fields = ('email', 'name', 'mobile_number', 'business_name', 'location')


# class CustomUserCreationForm(UserCreationForm):
#     class Meta(UserCreationForm.Meta):
#         model = User
#         fields = ('email', 'name', 'mobile_number')


class UserModelAdmin(BaseUserAdmin):

    list_display = ('id', 'email', 'name', 'mobile_number', 'is_admin')
    
    list_filter = ('is_admin', 'name')
    
    fieldsets = (
        ('User Credentials', {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ( 'mobile_number', 'business_name', 'location', 'name')}),
        
        ('Permissions', {'fields': ('is_admin',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                       'email', 'mobile_number', 
                       'name', 'location', 'business_name', 
                       'is_active', 'password1', 'password2'
                       ),
            
        }),
    )
    search_fields = ('email',)
    ordering = ('id',)
    filter_horizontal = ()


class UserAgreementModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'termsandconditions',)
    ordering = ('id',)
    empty_value_display = "-empty-"


admin.site.register(User, UserModelAdmin)
admin.site.register(UsersAgreement, UserAgreementModelAdmin)

