from django.contrib import admin, messages

from shop.app.admin import WhyshopSiteAdmin
from shop.softwaremodules.models import Softwaremodule
from shop.softwaremodules.admin_forms import DefaultSoftwaremoduleForm, ModuleSoftwaremoduleForm


class SoftwaremoduleAdmin(WhyshopSiteAdmin):
    model = Softwaremodule
    list_display = ('code','site_settings', 'published',)
    change_form_template = 'admin/softwaremodules/change_form.html'

    def get_form(self, request, obj=None, **kwargs):
        code_param = request.GET.get('code', '')
        if obj and obj.code:
            code_value = obj.code
        else:
            code_value = code_param

        if code_value == 'module':
            return ModuleSoftwaremoduleForm
        else:
            return DefaultSoftwaremoduleForm

    def save_model(self, request, obj, form, change):
        obj.data = form.cleaned_data['api_response']
        super().save_model(request, obj, form, change)


admin.site.register(Softwaremodule, SoftwaremoduleAdmin)