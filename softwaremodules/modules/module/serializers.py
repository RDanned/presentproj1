import decimal

from rest_framework.serializers import (
    ModelSerializer,
    IntegerField,
    CharField,
    SerializerMethodField,
    DateTimeField,
DecimalField
)

from shopgogo.utils import get_current_site

from shop.utils.general import get_full_url
from shop.product.models import Category, Product, Variant as ProductVariant
from shop.order.models import Order
from shop.user.models import Profile
from shop.coupons.models import Coupon
from shop.price.models import Price

def to_decimal(value):
    return str(decimal.Decimal(value)).replace(',', '.')

class ModuleCategorySerializer(ModelSerializer):
    languages = SerializerMethodField()

    def get_languages(self, instance):
        urls = instance.urls.all()

        languages = []
        for translation in instance.translations.all():
            url = get_full_url(path='/');

            if urls.filter(lang=translation.language_code).first():
                url = get_full_url(path=urls.filter(lang=translation.language_code).first().get_absolute_url())

            # delete double slash at the end of url
            url = url.rstrip('/') + '/' if url.endswith('//') else url + '/'

            languages.append({
                'code': translation.language_code if translation.language_code else '',
                'name': translation.name if translation.name else 'No name',
                'url': url,
            })
        return languages
    class Meta:
        model = Category
        fields = ('id', 'name', 'parent_id', 'languages')

class ModuleProductSerializer(ModelSerializer):
    id = CharField()
    image_url = SerializerMethodField()
    categories = SerializerMethodField()
    languages = SerializerMethodField()
    vat_rate = DecimalField(max_digits=4, decimal_places=2, default=21)
    unit = SerializerMethodField()
    ean = CharField()
    active = IntegerField()
    url= CharField(source='product.get_absolute_url', default=None)
    stock  = DecimalField(source='supplier_stock', max_digits=4, decimal_places=2, default=21)
    prices = SerializerMethodField()
    custom_fields = SerializerMethodField()

    def get_prices(self, instance):
        current_site = get_current_site()

        serialized_prices = []
        prices_qs = Price.objects.filter(
            currency=current_site.currency,
            variant_id=instance.id,
            partner_id=""
            ).get_active().order_by("-partner_id")

        if prices_qs.exists():
            for price in prices_qs:
                serialized_prices.append({
                    'currency': current_site.currency.karat_id if current_site.currency else '',
                    'amount': to_decimal((price.price if price.price else '0.00')),
                })

        else:
            serialized_prices.append({
                'currency': current_site.currency.karat_id if current_site.currency else '',
                'amount': to_decimal('0.00'),
            })

        return  serialized_prices

    def get_custom_fields(self, instance):
        custom_fields = []

        if(instance.code):
            custom_fields.append({
                'key': 'code',
                'value': instance.code
            })

        return custom_fields

    def get_unit(self, instance):
        if instance.measure_unit:
            return instance.measure_unit.erp_id
        return None

    def get_image_url(self, instance):
        main_image = instance.get_main_image(get_attach=True)
        main_image_placeholder = instance.get_placeholder(get_attach=True)

        image_url = get_full_url(path='/');

        if main_image:
            image_url = get_full_url(path=main_image.file.url).rstrip('/')
        elif main_image_placeholder:
            image_url = get_full_url(path=main_image_placeholder.file.url).rstrip('/')
        return image_url

    def get_categories(self, instance):
        return  instance.variant_categories.all()

    def get_languages(self, instance):
        languages = []
        current_site = get_current_site()
        site_language = current_site.lang_default if current_site.lang_default else settings.LANGUAGE_CODE

        for translation in instance.translations.all():
            url_qs = instance.get_published_urls(language_code=translation.language_code)
            url = get_full_url(path='/');

            if url_qs:
                url = url_qs.first().get_absolute_url()
                url = "https://{domain}{url}".format(
                    domain=current_site.site.domain,
                    url=url,
                    lang=site_language + '/' if site_language != current_site.lang_default else ''
                )

            languages.append({
                'id': translation.language_code if translation.language_code else '',
                'name': translation.name if translation.name else 'No name',
                'description': translation.description_html if translation.description_html else '',
                'url': url,
            })
        return languages

    def get_brand(self, instance):
        if instance.brand:
            return instance.brand.code
        return None


    class Meta:
        model = ProductVariant
        fields = ('id', 'image_url', 'categories', 'languages', 'vat_rate', 'unit', 'brand', 'ean', 'active',
                  'product_id', 'url', 'added', 'stock', 'prices', 'custom_fields')


class ModuleOrderSerializer(ModelSerializer):
    id = CharField()
    created = DateTimeField(source='time_created', format='%Y-%m-%dT%H:%M:%S')
    payment = CharField(source='payment_method_name')
    contact_id = SerializerMethodField()
    items = SerializerMethodField()
    contact = SerializerMethodField()

    def get_contact_id(self, instance):
        contact_id = 'NO_CONTACT_ID'
        if instance.profile:
            contact_id = str(instance.profile.customer_id)
        return contact_id

    def get_items(self, instance):
        items = []
        for order_item in instance.items.all():
            if order_item.variant:
                items.append({
                    'id': str(order_item.variant.id),
                    'variantId': str(order_item.variant.id_nomenclature),
                    'quantity': to_decimal(order_item.quantity),
                    'price': {
                        'value': to_decimal(order_item.total_discount_price_gross),
                        'currency': instance.currency.karat_id  if instance.currency else ''
                    }
                })

        items = [items[0]]
        return items

    def get_contact(self, instance):
        profile = instance.profile
        if not instance.profile:
            return {}
        return {
            'email': profile.user.email,
            'first_name': profile.last_name,
            'first_name': profile.first_name,
            'phone_number1': profile.phone_number,
            'phone_number2': profile.mobile_number,
            'street': '',
            'street2': '',
            'zip_code': '',
            'city': '',
            'country': '',
        }

    class Meta:
        model = Order
        fields = ('id', 'created', 'payment', 'contact_id','items', 'contact')


class ModuleContactSerializer(ModelSerializer):
    id = CharField()
    first_name = CharField()
    last_name = CharField()
    email = CharField(source='user.email')
    newsletter = SerializerMethodField()
    partner_category = SerializerMethodField()
    language = CharField(source='language_preference')
    birthdate = DateTimeField(source='datetime_of_birth', format='%Y-%m-%d')
    phone_number1 = CharField(source='phone_number')
    phone_number2 = CharField(source='mobile_number')

    def get_newsletter(self, instance):
        if instance.is_consent_newsletter:
            return 1
        return 0

    def get_partner_category(self, instance):
        if instance.partner_category:
            return instance.partner_category.name
        return ''

    class Meta:
        model = Profile
        fields = ('id', 'first_name', 'last_name', 'email', 'newsletter', 'partner_category', 'language', 'birthdate',
                  'phone_number1','phone_number2')

class ModuleCouponSerializer(ModelSerializer):
    reusable = SerializerMethodField()
    discount_type = SerializerMethodField()
    discount = DecimalField(source='value', max_digits=4, decimal_places=2)
    valid_from = DateTimeField(format='%Y-%m-%dT%H:%M:%S')
    valid_to = DateTimeField(format='%Y-%m-%dT%H:%M:%S')
    def get_reusable(self, instance):
        return 1

    def get_discount_type(self, instance):
        if instance.coupon_type == 1:
            return 'MONETARY'
        else:
            return 'PERCENTUAL'
    class Meta:
        model = Coupon
        fields = ('id', 'code', 'coupon_type', 'value', 'valid_from', 'valid_to', 'minimum_order_value', 'currency',
                  'reusable', 'discount_type', 'discount')
