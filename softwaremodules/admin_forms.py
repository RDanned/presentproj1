import requests

from django import forms
from django.core.exceptions import ValidationError

from shop.softwaremodules.apps import SoftwaremodulesConfig
from shop.softwaremodules.models import Softwaremodule
from shop.shopcore.models import SiteSettings


class DefaultSoftwaremoduleForm(forms.ModelForm):
    class Meta:
        model = Softwaremodule
        fields = '__all__'


class ModuleSoftwaremoduleForm(forms.ModelForm):
    login = forms.CharField(required=True, help_text="Please provide a valid email. This won't be stored in the database.")
    password = forms.CharField(widget=forms.PasswordInput, required=True, help_text="This won't be stored in the database.")
    site_settings = forms.ModelChoiceField(
                required=True,
        queryset=SiteSettings.objects.all(),
        widget=forms.Select,
    )
    data = forms.JSONField(required=False)

    class Meta:
        model = Softwaremodule
        fields = '__all__'
        fields = ('published', 'code', 'site_settings', 'login', 'password', 'data')

    def clean(self):
        cleaned_data = super().clean()

        login = cleaned_data.get('login')
        password = cleaned_data.get('password')

        if not login or not password:
            return cleaned_data

        current_site = cleaned_data.get('site_settings')

        site_root_url = 'https://' + current_site.site.domain
        params = {
            'login': login,
            'password': password,
            'url': site_root_url,
            'serverPalpUrl': site_root_url + '/api/softwaremodules/module/feed/',
            'pluginVersion': '2.15',
            'timeZone': current_site.timezone,
            'platformName': 'shop',
            'currency': current_site.currency.karat_id,
            'language': current_site.lang_default,
        }

        response = requests.get(SoftwaremodulesConfig.module_api_base_url + 'plugin/', params=params)

        if not response.ok:
            try:
                error = response.json().get('error')
                raise ValidationError(error)
            except ValueError:
                raise ValidationError('Unexpected error occurred. Please try again.')

        cleaned_data['api_response'] = response.json()

        return cleaned_data