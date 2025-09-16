from django import forms
from django.contrib.auth import get_user_model
User = get_user_model()


class EmailNotificationForm(forms.ModelForm):
    email_nots = forms.ChoiceField(
        choices=[(0, 'Notifications off')] + [(i, f'{i}:00') for i in range(1, 25)],
        label='Notification hour',
        required=True
    )

    class Meta:
        model = User
        fields = ['email', 'email_nots']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'email_nots': forms.Select(attrs={'class': 'form-control'})
        }
