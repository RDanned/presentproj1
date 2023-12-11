from django.db.models import (CharField, ForeignKey, SET_NULL, JSONField)
from django.utils.translation import (ugettext_lazy as _, )
from django.core.serializers.json import DjangoJSONEncoder

from shop.attachment.mixins import AttachmentMixin
from shop.shopcore.models import SiteSettings
from shop.app.models import WhyshopSiteModel


class Softwaremodule(AttachmentMixin, WhyshopSiteModel):
    SOFTWARE_CHOICES = (
        ('module', 'Module'),
    )
    code = CharField(_("code"), choices=SOFTWARE_CHOICES, max_length=255, null=False, blank=False)
    site_settings = ForeignKey(SiteSettings, on_delete=SET_NULL, null=True)
    data = JSONField(encoder=DjangoJSONEncoder, default=dict)

    class Meta:
        verbose_name = _("softwaremodule")
        verbose_name_plural = _("softwaremodules")

    def __str__(self):
        return self.code
