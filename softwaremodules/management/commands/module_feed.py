import os
import xml.etree.ElementTree as XmlElementTree

from django.db.models import Q, Count, Prefetch
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.conf import settings

from shop.user.models import Profile
from shop.order.models import Order
from shop.product.models import Category, Product, Variant as ProductVariant
from shop.coupons.models import Coupon

from shop.softwaremodules.models import Softwaremodule
from shop.softwaremodules.modules.module.serializers import (ModuleCategorySerializer,
                                                                   ModuleProductSerializer,
                                                                   ModuleOrderSerializer,
                                                                   ModuleContactSerializer,
                                                                   ModuleCouponSerializer)


class Command(BaseCommand):
    help = 'Generates module xml feed for current site, saves it to /media/module-feed/.'
    allowed_types = ['product', 'category', 'order', 'contact', 'coupon']

    def add_arguments(self, parser):
        # python manage.py module_feed --type=product
        # product, category, order, contact, coupon
        parser.add_argument(
            '--type',
            type=str,
            choices=self.allowed_types,
            help='feed type'
        )

        parser.add_argument(
            '--id',
            type=str,
            help='Id of eshop that is taken from erp_shop_id property of shopcore.SiteSettings model.'
        )

    def handle(self, *args, **options):

        # check parameters
        if 'type' not in options:
            self.stdout.write(
                self.style.ERROR(f"Parameter --type is required!")
            )
            return

        # check if type is allowed
        if options['type'] not in self.allowed_types:
            self.stdout.write(
                self.style.ERROR(f"Parameter --type must be one of {self.allowed_types}!")
            )
            return

        if 'id' not in options:
            self.stdout.write(
                self.style.ERROR(f"Parameter --id is required!")
            )
            return

        feed_type = options['type']
        erp_shop_id = options['id']

        module_softwaremodules = Softwaremodule.objects.filter(
            site_settings__erp_shop_id=erp_shop_id,
            code='module',
            published=True
        )

        if module_softwaremodules.count() == 0:
            self.stdout.write(
                    self.style.ERROR(f"Softwaremodule module not found!")
                )
            return

        path = os.path.abspath(os.path.join(settings.MEDIA_ROOT, 'module-feed'))
        if not os.path.exists(path):
            os.makedirs(path)

        module_softwaremodule = module_softwaremodules.first()

        api_key = module_softwaremodule.data['apiKey']

        if not api_key:
            self.stdout.write(
                    self.style.ERROR(f"Parameter apiKey is not in module softwaremodules settings!")
                )
            return

        current_site = module_softwaremodule.site_settings
        xml_output = None

        self.stdout.write(self.style.NOTICE(f"Generating module {feed_type} feed for {current_site}..."))

        if feed_type == 'category':
            categories = Category.objects.prefetch_related('translations', 'urls') \
                .public(site=current_site.site.id)

            serializer = ModuleCategorySerializer(categories, many=True)
            xml_output = render_to_string(
                'softwaremodules/module/categories.xml',
                dict(categories=serializer.data, total_items=len(categories))
            );
        elif feed_type == 'product':
            products = ProductVariant.objects.prefetch_related(
                'translations',
                'urls') \
                .public(site=current_site.site.id,)

            serializer = ModuleProductSerializer(products, many=True)
            xml_output = render_to_string(
                'softwaremodules/module/products.xml',
                dict(products=serializer.data, total_items=len(products))
            )
        elif feed_type == 'order':
            orders = Order.objects.annotate(items_count=Count('items')) \
                .filter(site=current_site.site.id, items_count__gt=0, profile__isnull=False)

            serializer = ModuleOrderSerializer(orders, many=True)
            xml_output = render_to_string(
                'softwaremodules/module/orders.xml',
                dict(orders=serializer.data, total_items=len(orders))
            );
        elif feed_type == 'contact':
            contacts = Profile.objects.all()
            serializer = ModuleContactSerializer(contacts, many=True)
            xml_output = render_to_string(
                'softwaremodules/module/contacts.xml',
                dict(contacts=serializer.data, total_items=len(contacts))
            )
        elif feed_type == 'coupon':
            coupons = Coupon.objects.all()
            serializer = ModuleCouponSerializer(coupons, many=True)
            xml_output = render_to_string(
                'softwaremodules/module/coupons.xml',
                dict(coupons=serializer.data, total_items=len(coupons))
            )

        element = XmlElementTree.XML(xml_output)
        XmlElementTree.indent(element)
        xml_output = XmlElementTree.tostring(element, encoding='unicode')

        xml_path = os.path.join(path, f"module-feed-{feed_type}-{api_key}.xml")
        with open(xml_path, 'w',  encoding='utf-8') as f:
            f.write(xml_output)

        self.stdout.write(
                self.style.SUCCESS(f"Module {feed_type} feed for {current_site} saved to: {xml_path}")
            )
