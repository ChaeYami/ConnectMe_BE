# from django import forms
# from django.contrib import admin
# from django.contrib.auth.models import Group
# from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# from django.contrib.auth.forms import ReadOnlyPasswordHashField

# from django.core.exceptions import ValidationError

# from .models import User

# class UserCreationForm(forms.ModelForm):
#     password1 = forms.CharField(label="비밀번호", widget=forms.PasswordInput)
#     password2 = forms.CharField(label="비밀번호 재확인", widget=forms.PasswordInput)

#     class Meta:
#         model = User
#         fields = ( "account", "email", "phone",)

#     def clean_password2(self):
#         password1 = self.cleaned_data.get("password1")
#         password2 = self.cleaned_data.get("password2")

#         if password1 and password2 and password1 != password2:
#             raise ValidationError("비밀번호가 맞지 않습니다.")
#         return password2

#     def save(self, commit=True):
#         user = super().save(commit=False)
#         user.set_password(self.cleaned_data["password1"])

#         if commit:
#             user.save()

#         return user
    
    
# class UserChangeForm(forms.ModelForm):

#     password = ReadOnlyPasswordHashField()

#     class Meta:
#         model = User
#         fields = ["account", "password", "is_active", "is_admin", "email", "phone"]
        
    
# class UserAdmin(BaseUserAdmin):
#     form = UserChangeForm
#     add_form = UserCreationForm

#     list_display = ["id", "account", "email","phone", "is_active", "is_admin"]
#     list_filter = ["is_active", "is_admin"]
#     fieldsets = [
#         (None, {"fields": ["account", "email","phone", "password"]}),
#         ("Permissions", {"fields": ["is_active", "is_admin"]}),
#     ]

#     add_fieldsets = [
#         (
#             None,
#             {
#                 "classes": ["wide"],
#                 "fields": ["account", "password1", "password2"],
#             },
#         ),
#     ]
#     search_fields = ["account"]
#     ordering = ["account"]
#     filter_horizontal = []


# admin.site.register(User, UserAdmin)

# admin.site.unregister(Group)