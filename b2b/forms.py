from django import forms
from .models import *
from registration.models import UserProfile
from django.core.validators import RegexValidator

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')


class UserProfileForm(forms.ModelForm):
    regex = RegexValidator(regex=r'^[789]\d{9}$', message="Invalid Mobile Number")
    mobile = forms.CharField(max_length=10, validators=[regex])

    def save(self, commit=True):
        mobile_number = self.cleaned_data['mobile']
        mobile = Mobile.objects.get_or_create(number=mobile_number)[0]
        self.instance.mobile = mobile

        return super(UserProfileForm, self).save(commit)

    class Meta:
        model = UserProfile
        fields = ('mobile', 'fax', 'age',)
        exclude = ('mobile',)


class BEntityForm(forms.ModelForm):
    regex = RegexValidator(regex=r'^[789]\d{9}$', message="Invalid Mobile Number")
    mobile = forms.CharField(max_length=10, validators=[regex])

    def save(self, commit=True):
        mobile_number = self.cleaned_data['mobile']
        mobile = Mobile.objects.get_or_create(number=mobile_number)[0]
        self.instance.mobile = mobile

        return super(BEntityForm, self).save(commit)

    class Meta:
        model = BEntity
        exclude = ('mobile',)


class EmployeeForm(forms.ModelForm):
    regex = RegexValidator(regex=r'^[789]\d{9}$', message="Invalid Mobile Number")
    mobile = forms.CharField(max_length=10, validators=[regex])

    def save(self, commit=True):
        mobile_number = self.cleaned_data['mobile']
        mobile = Mobile.objects.get_or_create(number=mobile_number)[0]
        self.instance.mobile = mobile

        return super(EmployeeForm, self).save(commit)

    class Meta:
        model = Employee
        fields = ('first_name', 'last_name', 'mobile')
        exclude = ('mobile',)
