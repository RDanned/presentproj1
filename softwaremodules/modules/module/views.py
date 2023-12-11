import os
import requests
import json
from threading import Thread

from django.conf import settings
from django.http import HttpResponse, HttpResponseNotFound

from shopgogo.rest.views import WhysGenericViewSet

from shopgogo.utils import get_current_site
from shop.softwaremodules.apps import SoftwaremodulesConfig
from shop.softwaremodules.models import Softwaremodule

class ModuleFeedXmlViewSet(WhysGenericViewSet):
    def retrieve(self, request):
        api_key = request.GET.get('key')
        feed_type = request.GET.get('type')

        if api_key:
            current_site = get_current_site()
            softwaremodule = Softwaremodule.objects.filter(code='module', site=current_site, published=True).first()
            if not softwaremodule:
                return HttpResponseNotFound('Wrong api key')
            if softwaremodule.data['apiKey'] != api_key:
                return HttpResponseNotFound('Wrong api key')
        else:
            return HttpResponseNotFound('Request does not have api key')

        path = os.path.abspath(settings.MEDIA_ROOT)
        file_name = f'/module-feed/module-feed-{feed_type}-{api_key}.xml'
        file_location = path + file_name

        try:
            with open(file_location, 'r', encoding='utf-8') as f:
                file_data = f.read()
            response = HttpResponse(file_data, content_type='application/xml')

        except IOError:
            response = HttpResponseNotFound('File not exist')

        return response


class ModuleEventsViewSet:
    api_base_url = SoftwaremodulesConfig.module_api_base_url + 'event/'

    @staticmethod
    def run_in_thread(worker_function, *args):
        if Softwaremodule.objects.filter(code='module', published=True).exists():
            thread = Thread(target=worker_function,args=args)
            thread.start()

    @staticmethod
    def get_api_url():
        module_softwaremodule = Softwaremodule.objects.filter(code='module', published=True).first()
        return ModuleEventsViewSet.api_base_url + module_softwaremodule.data['apiKey']

    @staticmethod
    def order_add(cart_id, order_id, profile_id, perm_id):
        try:
            data = {
                'name': 'order_add',
                'permId': perm_id,
                'sessionId': str(cart_id),
                'content': {'relatedId': str(order_id)},
                'contact': {'clientContactId': str(profile_id)}
            }
            result = requests.put(
                ModuleEventsViewSet.get_api_url(),
                data=json.dumps(data),
                headers={"Content-Type": "application/json"}
            )
        except requests.exceptions.RequestException as e:
            print("An error occurred during the Module request:", e)
