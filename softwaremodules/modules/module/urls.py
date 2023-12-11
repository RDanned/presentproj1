from django.urls import path

from shop.softwaremodules.modules.module.views import (ModuleFeedViewSet,
                                                             ModuleRegisterViewSet,
    ModuleFeedXmlViewSet)

urlpatterns = [
    path('feed/', ModuleFeedXmlViewSet.as_view({'get': 'retrieve'}), name='module-feed-xml'),
]
