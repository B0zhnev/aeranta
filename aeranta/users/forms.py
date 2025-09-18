from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model, authenticate
from django.core.exceptions import ValidationError
from django.views.decorators.debug import sensitive_variables

from .models import User
from django import forms
from django.contrib.gis.geos import Point


class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label='Login', widget=forms.TextInput(attrs={'class': 'form-input'}))
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': 'form-input'}))

    class Meta:
        model = User
        fields = ['username', 'password']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            return username.lower()
        return username


class RegisterUserForm(UserCreationForm):
    username = forms.CharField(label="Login", widget=forms.TextInput(attrs={'class': 'form-input'}))
    latitude = forms.FloatField(widget=forms.HiddenInput())
    longitude = forms.FloatField(widget=forms.HiddenInput())
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    password2 = forms.CharField(label="Repeat Password", widget=forms.PasswordInput(attrs={'class': 'form-input'}))

    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'password1', 'password2', 'latitude', 'longitude']
        labels = {'email': 'E-mail'}
        widgets = {
            'email': forms.TextInput(attrs={'class': 'form-input'}),
        }

    def clean_username(self):
        username = self.cleaned_data['username'].lower()
        qs = User.objects.filter(username=username)
        if self.user:
            qs = qs.exclude(pk=self.user.pk)
        if qs.exists():
            raise forms.ValidationError('This username is already taken.')
        return username

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        user = get_user_model()
        if user.objects.filter(email=email).exists():
            raise forms.ValidationError("This Email already exists")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        lat = self.cleaned_data.get('latitude')
        lon = self.cleaned_data.get('longitude')
        if lat is not None and lon is not None:
            user.location = Point(lon, lat)
        user.email_confirmed = False
        if commit:
            user.save()
        return user


class EditProfileForm(forms.ModelForm):
    latitude = forms.FloatField(widget=forms.HiddenInput(), required=False)
    longitude = forms.FloatField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'latitude', 'longitude']
        labels = {
            'first_name': 'Name',
            'last_name': 'Last name',
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input'}),
            'email': forms.TextInput(attrs={'class': 'form-input'}),
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_username(self):
        username = self.cleaned_data['username'].lower()
        qs = User.objects.filter(username=username)
        if self.user:
            qs = qs.exclude(pk=self.user.pk)
        if qs.exists():
            raise forms.ValidationError('This username is already taken.')
        return username

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if self.user and self.user.email != email:
            self.user.email_confirmed = False
        return email

    def save(self, commit=True):
        user = super().save(commit=False)

        lat = self.cleaned_data.get('latitude')
        lon = self.cleaned_data.get('longitude')
        if lat is not None and lon is not None:
            user.location = Point(lon, lat)

        if commit:
            user.save()
        return user


class ConfirmedEmailPasswordResetForm(PasswordResetForm):
    email = forms.EmailField()

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        try:
            user = User.objects.get(email=email)
            if not user.email_confirmed:
                raise ValidationError('Email is not confirmed')
        except User.DoesNotExist:
            pass
        return email